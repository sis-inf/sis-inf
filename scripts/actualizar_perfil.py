import os
import sys
import json
import logging

# Agregar el directorio raíz del proyecto al path de Python
DIR_RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if DIR_RAIZ not in sys.path:
    sys.path.insert(0, DIR_RAIZ)

# Importaciones del paquete perfil
from perfil.github_api import ClienteGitHub
from perfil.repos import obtener_y_filtrar_repos
from perfil.consultas import obtener_aportes_lenguajes_issues
from perfil.aportes import contar_aportes_y_cifras
from perfil.lenguajes import calcular_porcentajes_lenguajes
from perfil.readme import reemplazar_bloque_si_cambio
from perfil import secciones

# Configuración básica de logs
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

def cargar_configuracion(ruta_config=None):
    """Lee el archivo de configuración JSON en la ruta por defecto o especificada."""
    if ruta_config is None:
        ruta_config = os.path.join(DIR_RAIZ, "config", "perfil.json")
    
    if not os.path.exists(ruta_config):
        logging.error(f"No se encontró el archivo de configuración en {ruta_config}")
        return None
    with open(ruta_config, "r", encoding="utf-8") as f:
        return json.load(f)

def main():
    # 1. Leer configuración
    config = cargar_configuracion()
    if not config:
        return

    # 2. Inicializar ClienteGitHub
    token = os.environ.get("GITHUB_TOKEN")
    cliente = ClienteGitHub(token=token)

    # 3. Obtener y filtrar repositorios
    logging.info("Obteniendo y filtrando repositorios...")
    repos = obtener_y_filtrar_repos(cliente, config)

    # 4. Obtener aportes, lenguajes e issues
    logging.info("Consultando datos de aportes, lenguajes e issues...")
    datos_extra = obtener_aportes_lenguajes_issues(cliente, repos)

    # 5. Calcular estadísticas
    aportes_cifras = contar_aportes_y_cifras(datos_extra)
    porcentajes_lenguajes = calcular_porcentajes_lenguajes(datos_extra)

    bloques_objetivo = ["cifras", "proyectos", "lenguajes", "colaboradores", "primeras-issues"]
    total_bloques_actualizados = 0
    total_colaboradores = len(datos_extra.get("colaboradores", []))

    # 6. Actualizar READMEs
    readmes = config.get("readmes", {})
    for ruta_relativa_readme, idioma in readmes.items():
        ruta_readme = os.path.join(DIR_RAIZ, ruta_relativa_readme)
        
        if not os.path.exists(ruta_readme):
            logging.warning(f"El archivo README '{ruta_readme}' para '{idioma}' no existe. Omitiendo.")
            continue

        for nombre_bloque in bloques_objetivo:
            try:
                generador = getattr(secciones, f"generar_{nombre_bloque.replace('-', '_')}", None)
                if not generador:
                    logging.warning(f"No existe generador para el bloque '{nombre_bloque}'")
                    continue

                nuevo_contenido = generador(
                    idioma=idioma,
                    repos=repos,
                    cifras=aportes_cifras,
                    lenguajes=porcentajes_lenguajes,
                    datos=datos_extra
                )

                actualizado = reemplazar_bloque_si_cambio(
                    ruta_archivo=ruta_readme,
                    nombre_bloque=nombre_bloque,
                    nuevo_contenido=nuevo_contenido
                )

                if actualizado:
                    total_bloques_actualizados += 1

            except Exception as e:
                logging.warning(f"No se pudo procesar el bloque '{nombre_bloque}' en '{ruta_readme}': {e}")

    # 7. Resumen final
    print("\n--- RESUMEN DE ACTUALIZACIÓN ---")
    print(f"Repositorios procesados: {len(repos)}")
    print(f"Colaboradores detectados: {total_colaboradores}")
    print(f"Bloques actualizados: {total_bloques_actualizados}")

if __name__ == "__main__":
    main()
    