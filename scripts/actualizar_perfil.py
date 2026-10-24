import os
import json
import logging
import sys

# Asegurar que la carpeta 'scripts' esté en sys.path
DIR_SCRIPTS = os.path.dirname(os.path.abspath(__file__))
if DIR_SCRIPTS not in sys.path:
    sys.path.insert(0, DIR_SCRIPTS)

from perfil.github_api import ClienteGitHub
from perfil.repos import obtener_repos, filtrar_repos
from perfil.readme import reemplazar_bloque

# Configurar logging básico
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def cargar_configuracion():
    """Lee la configuración desde config/perfil.json"""
    ruta_config = os.path.join(os.path.dirname(DIR_SCRIPTS), 'config', 'perfil.json')
    if os.path.exists(ruta_config):
        with open(ruta_config, 'r', encoding='utf-8') as f:
            return json.load(f)
    logging.warning("No se encontró config/perfil.json, usando configuración por defecto.")
    return {'readmes': {'README.md': 'es', 'README.en.md': 'en'}}


def main():
    token = os.getenv("GITHUB_TOKEN")
    if token:
        logging.info("Token de GitHub detectado en el entorno.")
    else:
        logging.warning("No se detectó GITHUB_TOKEN. Ejecutando en modo local/simulación.")

    config = cargar_configuracion()
    usuario = config.get("usuario", "usuario_por_defecto")

    cliente = ClienteGitHub(token)
    exito_repos = True
    repos = []
    total_repos = 0

    # Intento de obtención y filtrado de repositorios con control de errores
    try:
        repos_raw = obtener_repos(cliente, usuario)
        repos = filtrar_repos(repos_raw, config)
        total_repos = len(repos)
    except Exception as e:
        logging.error(f"Error al obtener o filtrar repositorios: {e}")
        exito_repos = False

    readmes = config.get('readmes', {'README.md': 'es', 'README.en.md': 'en'})
    bloques = ['cifras', 'proyectos', 'lenguajes', 'colaboradores', 'primeras-issues']
    
    cambios_totales = 0
    archivos_procesados = 0

    if exito_repos:
        for ruta_readme, idioma in readmes.items():
            logging.info(f"Procesando {ruta_readme} para el idioma {idioma}...")
            if not os.path.exists(ruta_readme):
                logging.warning(f"El archivo {ruta_readme} no existe.")
                continue

            with open(ruta_readme, 'r', encoding='utf-8') as f:
                contenido_actual = f.read()

            contenido_nuevo = contenido_actual
            archivos_procesados += 1

            for bloque in bloques:
                try:
                    # Generación de contenido para los bloques utilizando los datos obtenidos
                    contenido_generado = f"Información actualizada del bloque **{bloque}** ({idioma}). Total repos: {len(repos)}"
                    contenido_nuevo, actualizado = reemplazar_bloque(contenido_nuevo, bloque, contenido_generado)
                except Exception as ex:
                    logging.warning(f"No se pudieron actualizar los marcadores del bloque '{bloque}' en {ruta_readme}: {ex}")

            # Guardado condicional de cambios en el archivo README
            if contenido_nuevo != contenido_actual:
                with open(ruta_readme, 'w', encoding='utf-8') as f:
                    f.write(contenido_nuevo)
                logging.info(f"Cambios aplicados exitosamente en {ruta_readme}.")
                cambios_totales += 1
            else:
                logging.info(f"Sin cambios detectados en {ruta_readme}.")
    else:
        logging.error("Se omite la actualización de los archivos README debido a un fallo en la obtención de repositorios.")

    # Estado condicional final para el resumen
    if not exito_repos:
        estado = "Ejecución fallida (error en la obtención de repositorios)."
    elif archivos_procesados == 0:
        estado = "Ejecución completada con advertencias (sin archivos procesados)."
    else:
        estado = "Ejecución completada correctamente."

    # Resumen final por consola
    print("\n" + "="*50)
    print(" RESUMEN FINAL DE LA EJECUCIÓN")
    print("="*50)
    print(f" Archivos README procesados       : {archivos_procesados}")
    print(f" Repositorios obtenidos/filtrados : {total_repos}")
    print(f" Archivos actualizados            : {cambios_totales}")
    print(f" Estado                           : {estado}")
    print("="*50 + "\n")


if __name__ == "__main__":
    main()
    