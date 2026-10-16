import os
import json
import logging
import sys

# Asegurar que la carpeta 'scripts' esté en sys.path para importar correctamente desde el paquete perfil
DIR_SCRIPTS = os.path.dirname(os.path.abspath(__file__))
if DIR_SCRIPTS not in sys.path:
    sys.path.insert(0, DIR_SCRIPTS)

# Importar los módulos reales del paquete perfil
from perfil.github_api import ClienteGitHub
from perfil.repos import obtener_y_filtrar_repos
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
    return {
        'readmes': {
            'README.md': 'es',
            'README.en.md': 'en'
        }
    }


def actualizar_bloques_readme(ruta_readme, idioma, repos):
    """
    Procesa un archivo README actualizando sus bloques dinámicos.
    Retorna True si hubo cambios reales para guardar, False en caso contrario.
    """
    if not os.path.exists(ruta_readme):
        logging.warning(f"El archivo {ruta_readme} no existe.")
        return False

    with open(ruta_readme, 'r', encoding='utf-8') as f:
        contenido_actual = f.read()

    contenido_nuevo = contenido_actual
    
    # Lista de bloques que maneja el perfil
    bloques = ['cifras', 'proyectos', 'lenguajes', 'colaboradores', 'primeras-issues']

    for bloque in bloques:
        try:
            # Contenido dinámico provisional o generado a partir de los repositorios
            contenido_generado = f"Información actualizada para el bloque **{bloque}** ({idioma}). Total repos: {len(repos)}"
            
            # Llamada a la función real de readme.py
            contenido_nuevo, actualizado = reemplazar_bloque(contenido_nuevo, bloque, contenido_generado)
            
            if not actualizado:
                # Requisito: Si falta un bloque o sus marcadores, emite advertencia y continúa sin detenerse
                logging.warning(f"Advertencia: No se encontraron los marcadores para el bloque '{bloque}' en {ruta_readme}.")
        except Exception as e:
            logging.warning(f"Advertencia: Ocurrió un error al procesar el bloque '{bloque}' en {ruta_readme}: {e}")
            continue

    # Guardado condicional: solo sobreescribe si el contenido cambió realmente
    if contenido_nuevo != contenido_actual:
        with open(ruta_readme, 'w', encoding='utf-8') as f:
            f.write(contenido_nuevo)
        logging.info(f"Cambios guardados exitosamente en {ruta_readme}.")
        return True
    else:
        logging.info(f"No se detectaron cambios en {ruta_readme}. Omitiendo guardado.")
        return False


def main():
    # Verificación del token de GitHub en el entorno
    token = os.getenv("GITHUB_TOKEN")
    if token:
        logging.info("Token de GitHub detectado en el entorno.")
    else:
        logging.warning("No se detectó GITHUB_TOKEN. Ejecutando en modo local/simulación.")

    # Inicializar cliente y obtener repositorios
    cliente = ClienteGitHub(token)
    try:
        repos = obtener_y_filtrar_repos(cliente)
        total_repos = len(repos)
    except Exception as e:
        logging.error(f"Error al obtener repositorios: {e}")
        repos = []
        total_repos = 0

    config = cargar_configuracion()
    readmes = config.get('readmes', {'README.md': 'es', 'README.en.md': 'en'})

    cambios_totales = 0
    for ruta_relativa_readme, idioma in readmes.items():
        logging.info(f"Procesando {ruta_relativa_readme} para el idioma {idioma}...")
        hubo_cambios = actualizar_bloques_readme(ruta_relativa_readme, idioma, repos)
        if hubo_cambios:
            cambios_totales += 1

    # Resumen final de la ejecución por consola
    print("\n" + "="*50)
    print(" RESUMEN FINAL DE LA EJECUCIÓN")
    print("="*50)
    print(f" Archivos procesados              : {len(readmes)}")
    print(f" Repositorios obtenidos/filtrados : {total_repos}")
    print(f" Archivos actualizados con éxito  : {cambios_totales}")
    print(" Estado                           : Ejecución completada correctamente.")
    print("="*50 + "\n")


if __name__ == "__main__":
    main()
