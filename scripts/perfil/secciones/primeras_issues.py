"""Sección "primeras issues" del perfil (bloque auto:primeras-issues).

Solo genera Markdown a partir de los datos recibidos: no accede a la red.
Usa únicamente la biblioteca estándar de Python.
"""

URL_BUSQUEDA = (
    "https://github.com/search?q=user%3Asis-inf"
    "+label%3A%22good+first+issue%22+state%3Aopen&type=issues"
)

IDIOMA_POR_DEFECTO = "es"

TEXTOS = {
    "es": {
        "total_cero": "No hay primeras issues abiertas por ahora (0).",
        "total_uno": "Hay **{total}** primera issue abierta para nuevos colaboradores:",
        "total_varias": "Hay **{total}** primeras issues abiertas para nuevos colaboradores:",
        "en": "en",
        "ver_todas": "Ver todas las primeras issues",
    },
    "en": {
        "total_cero": "There are no open first issues right now (0).",
        "total_uno": "There is **{total}** open first issue for new contributors:",
        "total_varias": "There are **{total}** open first issues for new contributors:",
        "en": "in",
        "ver_todas": "See all first issues",
    },
}


def _escapar(texto):
    """Escapa corchetes y barras invertidas para no romper un enlace Markdown."""
    texto = " ".join(str(texto).split())
    for caracter in ("\\", "[", "]"):
        texto = texto.replace(caracter, "\\" + caracter)
    return texto


def _frase_total(total, textos):
    """Devuelve la frase traducida que indica cuántas issues hay."""
    if total <= 0:
        return textos["total_cero"]
    if total == 1:
        return textos["total_uno"].format(total=total)
    return textos["total_varias"].format(total=total)


def generar(datos, max_items, idioma):
    """Genera la sección de primeras issues en Markdown.

    Args:
        datos: dict con 'total' (int) e 'items', una lista de dicts con las
            claves 'titulo', 'url' y 'repo'.
        max_items: cantidad máxima de issues que se listan.
        idioma: 'es' o 'en'; cualquier otro valor usa 'es'.

    Returns:
        Texto con la frase del total, la lista de hasta max_items issues
        enlazadas con su repo y un enlace a la búsqueda de todas las
        primeras issues.
    """
    textos = TEXTOS.get(idioma, TEXTOS[IDIOMA_POR_DEFECTO])
    datos = datos or {}
    items = list(datos.get("items") or [])
    try:
        total = int(datos.get("total", len(items)))
    except (TypeError, ValueError):
        total = len(items)

    try:
        limite = max(int(max_items), 0)
    except (TypeError, ValueError):
        limite = 0

    lineas = [_frase_total(total, textos), ""]
    for item in items[:limite]:
        titulo = _escapar(item.get("titulo", ""))
        url = item.get("url", "")
        repo = item.get("repo", "")
        lineas.append(f"- [{titulo}]({url}) {textos['en']} `{repo}`")
    if items[:limite]:
        lineas.append("")
    lineas.append(f"[{textos['ver_todas']}]({URL_BUSQUEDA})")
    return "\n".join(lineas) + "\n"
