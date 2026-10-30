"""Orquestador del perfil de SIS-INF.

Lee config/perfil.json, consulta la API de GitHub, genera los bloques
automáticos y los reemplaza en los README. Solo escribe un archivo si cambió.
"""
import json
import logging
import os
import sys

# Asegurar que la carpeta 'scripts' esté en sys.path
DIR_SCRIPTS = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(DIR_SCRIPTS)
if DIR_SCRIPTS not in sys.path:
    sys.path.insert(0, DIR_SCRIPTS)

from perfil.aportes import contar_aportes
from perfil.consultas import (
    obtener_aportes,
    obtener_lenguajes,
    obtener_primeras_issues,
)
from perfil.github_api import ClienteGitHub
from perfil.lenguajes import porcentajes, sumar_lenguajes
from perfil.readme import reemplazar_bloque
from perfil.repos import filtrar_repos, obtener_repos
from perfil.secciones import cifras, colaboradores, primeras_issues, proyectos
from perfil.secciones import lenguajes as sec_lenguajes

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)


def cargar_configuracion():
    """Lee config/perfil.json. Devuelve None si no se puede leer."""
    ruta = os.path.join(RAIZ, "config", "perfil.json")
    try:
        with open(ruta, "r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError) as error:
        logging.error("No se pudo leer %s: %s", ruta, error)
        return None


def obtener_datos(cliente, config):
    """Consulta la API y calcula los datos que usan los bloques.

    Los repositorios y los aportes son imprescindibles: si fallan, se
    propaga la excepción. Los lenguajes y las primeras issues son
    opcionales: si fallan, se registra una advertencia y su bloque se omite.
    """
    usuario = config["usuario"]

    repos = filtrar_repos(obtener_repos(cliente, usuario), config)
    nombres = [repo["full_name"] for repo in repos]

    prs, commits = obtener_aportes(cliente, usuario, nombres)
    aportes = contar_aportes(prs, commits, config)

    try:
        por_repo = obtener_lenguajes(cliente, usuario, nombres)
        lista_porcentajes = porcentajes(sumar_lenguajes(por_repo))
    except Exception as error:
        logging.warning("No se pudieron obtener los lenguajes: %s", error)
        lista_porcentajes = None

    try:
        datos_issues = obtener_primeras_issues(cliente, usuario)
    except Exception as error:
        logging.warning("No se pudieron obtener las primeras issues: %s", error)
        datos_issues = None

    return {
        "repos": repos,
        "aportes": aportes,
        "cifras": cifras.calcular_cifras(repos, aportes),
        "porcentajes": lista_porcentajes,
        "primeras_issues": datos_issues,
    }


def generar_bloques(datos, config, idioma):
    """Devuelve {bloque: markdown} para un idioma, omitiendo lo que falle."""
    top = config.get("top_colaboradores", 20)
    max_issues = config.get("max_primeras_issues", 5)

    # (bloque, dato requerido, función que genera el Markdown)
    definiciones = [
        ("cifras", "cifras",
         lambda: cifras.generar(datos["cifras"], idioma)),
        ("proyectos", "repos",
         lambda: proyectos.generar(datos["repos"], idioma)),
        ("lenguajes", "porcentajes",
         lambda: sec_lenguajes.generar(datos["porcentajes"], idioma)),
        ("colaboradores", "aportes",
         lambda: colaboradores.generar(datos["aportes"], top, idioma)),
        ("primeras-issues", "primeras_issues",
         lambda: primeras_issues.generar(
             datos["primeras_issues"], max_issues, idioma)),
    ]

    bloques = {}
    for nombre, clave, generar in definiciones:
        if datos[clave] is None:
            logging.warning("Se omite el bloque '%s': faltan sus datos.", nombre)
            continue
        try:
            bloques[nombre] = generar()
        except Exception as error:
            logging.warning("No se pudo generar el bloque '%s': %s", nombre, error)
    return bloques


def actualizar_readme(ruta, idioma, datos, config):
    """Actualiza un README. Devuelve (bloques_actualizados, cambio_archivo)."""
    if not os.path.exists(ruta):
        logging.warning("El archivo %s no existe; se omite.", ruta)
        return 0, False

    with open(ruta, "r", encoding="utf-8") as f:
        original = f.read()

    texto = original
    actualizados = 0
    for nombre, contenido in generar_bloques(datos, config, idioma).items():
        texto, encontrado = reemplazar_bloque(texto, nombre, contenido)
        if encontrado:
            actualizados += 1
        else:
            logging.warning(
                "Falta el bloque '%s' en %s; se continúa.", nombre, ruta
            )

    if texto == original:
        logging.info("Sin cambios en %s.", ruta)
        return actualizados, False

    with open(ruta, "w", encoding="utf-8", newline="\n") as f:
        f.write(texto)
    logging.info("Cambios aplicados en %s.", ruta)
    return actualizados, True


def main():
    config = cargar_configuracion()
    if config is None:
        return 1

    token = os.getenv("GITHUB_TOKEN")
    if not token:
        logging.warning(
            "No se detectó GITHUB_TOKEN: la API limita a 60 consultas por hora."
        )
    cliente = ClienteGitHub(token)

    try:
        datos = obtener_datos(cliente, config)
    except Exception as error:
        logging.error("Falló la obtención de datos: %s", error)
        print("\nEjecución FALLIDA: no se modificó ningún archivo.\n")
        return 1

    bloques_actualizados = 0
    archivos_modificados = 0
    for nombre_archivo, idioma in config.get("readmes", {}).items():
        ruta = os.path.join(RAIZ, nombre_archivo)
        bloques, cambio = actualizar_readme(ruta, idioma, datos, config)
        bloques_actualizados += bloques
        archivos_modificados += int(cambio)

    print("\n" + "=" * 50)
    print(" RESUMEN FINAL DE LA EJECUCIÓN")
    print("=" * 50)
    print(f" Repositorios         : {len(datos['repos'])}")
    print(f" Colaboradores        : {len(datos['aportes'])}")
    print(f" Bloques actualizados : {bloques_actualizados}")
    print(f" Archivos modificados : {archivos_modificados}")
    print("=" * 50 + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
