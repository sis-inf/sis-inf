"""Sección "lenguajes" del perfil (bloque auto:lenguajes).

Genera una insignia de img.shields.io por lenguaje y una tabla con los
porcentajes. Solo genera Markdown/HTML: no accede a la red. Usa únicamente
la biblioteca estándar de Python.
"""

from html import escape
from urllib.parse import quote

IDIOMA_POR_DEFECTO = "es"
COLOR_POR_DEFECTO = "blue"
NOMBRE_OTROS = "Otros"

TEXTOS = {
    "es": {
        "lenguaje": "Lenguaje",
        "porcentaje": "%",
        "otros": "Otros",
        "vacio": "Aún no hay datos de lenguajes.",
    },
    "en": {
        "lenguaje": "Language",
        "porcentaje": "%",
        "otros": "Others",
        "vacio": "No language data yet.",
    },
}

# Nombre del lenguaje -> identificador del logo en simpleicons.org.
# Los lenguajes que no estén aquí se muestran sin logo.
LOGOS = {
    "Python": "python",
    "JavaScript": "javascript",
    "TypeScript": "typescript",
    "HTML": "html5",
    "CSS": "css3",
    "PHP": "php",
    "C": "c",
    "C++": "cplusplus",
    "Go": "go",
    "Rust": "rust",
    "Ruby": "ruby",
    "Kotlin": "kotlin",
    "Swift": "swift",
    "Dart": "dart",
    "Lua": "lua",
    "R": "r",
    "Shell": "gnubash",
    "Dockerfile": "docker",
    "Jupyter Notebook": "jupyter",
}


def _textos(idioma):
    """Devuelve el dict de textos del idioma, o el del idioma por defecto."""
    return TEXTOS.get(idioma, TEXTOS[IDIOMA_POR_DEFECTO])


def _nombre_visible(nombre, textos):
    """Traduce el nombre del grupo 'Otros'; los demás se dejan igual."""
    if nombre == NOMBRE_OTROS:
        return textos["otros"]
    return nombre


def _escapar_insignia(texto):
    """Escapa un texto para la ruta de img.shields.io/badge."""
    return quote(str(texto).replace("-", "--").replace("_", "__"), safe="")


def _formatear(porcentaje):
    """Devuelve el porcentaje con un decimal, por ejemplo '62.5'."""
    return f"{float(porcentaje):.1f}"


def _insignia(nombre, porcentaje, textos):
    """Genera la etiqueta <img> de la insignia de un lenguaje."""
    visible = _nombre_visible(nombre, textos)
    valor = _formatear(porcentaje) + "%"
    url = (
        "https://img.shields.io/badge/"
        f"{_escapar_insignia(visible)}-{_escapar_insignia(valor)}-{COLOR_POR_DEFECTO}"
    )
    logo = LOGOS.get(nombre)
    if logo:
        url += f"?logo={quote(logo, safe='')}&logoColor=white"
    alt = escape(f"{visible}: {valor}", quote=True)
    return f'<img src="{url}" alt="{alt}">'


def _tabla(porcentajes, textos):
    """Genera la tabla Markdown Lenguaje | % con encabezados traducidos."""
    lineas = [
        f"| {textos['lenguaje']} | {textos['porcentaje']} |",
        "|---|---|",
    ]
    for nombre, porcentaje in porcentajes:
        visible = _nombre_visible(nombre, textos).replace("|", "\\|")
        lineas.append(f"| {visible} | {_formatear(porcentaje)} |")
    return "\n".join(lineas)


def generar(porcentajes, idioma):
    """Genera la sección de lenguajes en Markdown/HTML.

    Args:
        porcentajes: lista de tuplas (lenguaje, porcentaje), por ejemplo
            [("Python", 62.5), ("HTML", 37.5)].
        idioma: "es" o "en"; cualquier otro valor usa "es".

    Returns:
        Una línea centrada con una insignia de img.shields.io/badge por
        lenguaje (nombre y porcentaje, con logo de simpleicons si existe) y,
        debajo, una tabla Lenguaje | % con los encabezados traducidos. Si no
        hay lenguajes, devuelve un texto traducido de "sin datos".
    """
    textos = _textos(idioma)
    filas = list(porcentajes or [])
    if not filas:
        return textos["vacio"]

    insignias = " ".join(_insignia(n, p, textos) for n, p in filas)
    return '<p align="center">' + insignias + "</p>\n\n" + _tabla(filas, textos) + "\n"
