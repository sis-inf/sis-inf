"""Sección de colaboradores del perfil: cuadrícula de avatares y tabla completa.

Solo genera Markdown/HTML a partir de los aportes recibidos; no accede a la red.
"""

from html import escape

COLUMNAS_CUADRICULA = 5

TEXTOS = {
    "es": {
        "ver_todos": "Ver todos",
        "puesto": "#",
        "colaborador": "Colaborador",
        "prs": "PRs aceptados",
        "commits": "Commits directos",
        "aportes": "Aportes de todos",
        "nota": "Cada PR aceptado y cada commit directo a main cuenta como 1 aporte.",
    },
    "en": {
        "ver_todos": "See all",
        "puesto": "#",
        "colaborador": "Contributor",
        "prs": "Accepted PRs",
        "commits": "Direct commits",
        "aportes": "Total contributions",
        "nota": "Each accepted PR and each direct commit to main counts as 1 contribution.",
    },
}


def _normalizar(aportes):
    """Devuelve los aportes como tuplas (login, prs, commits, total), ordenadas.

    El orden es por total descendente y, en empate, por login alfabético.
    Si un dict no trae "aportes", el total se calcula como prs + commits.
    """
    filas = []
    for item in aportes:
        prs = int(item.get("prs", 0))
        commits = int(item.get("commits", 0))
        total = int(item.get("aportes", prs + commits))
        filas.append((str(item["login"]), prs, commits, total))
    filas.sort(key=lambda f: (-f[3], f[0].lower()))
    return filas


def _celda(login, total):
    """Genera la celda HTML de un colaborador: avatar enlazado, login y aportes."""
    login_html = escape(login)
    return (
        '<td align="center">'
        f'<a href="https://github.com/{login_html}">'
        f'<img src="https://github.com/{login_html}.png?size=80" '
        f'width="60" alt="{login_html}"></a><br>'
        f"{login_html}<br>{total}"
        "</td>"
    )


def _cuadricula(filas):
    """Genera la tabla HTML con los avatares de los colaboradores dados."""
    lineas = ["<table>"]
    for i in range(0, len(filas), COLUMNAS_CUADRICULA):
        lineas.append("  <tr>")
        for login, _prs, _commits, total in filas[i:i + COLUMNAS_CUADRICULA]:
            lineas.append("    " + _celda(login, total))
        lineas.append("  </tr>")
    lineas.append("</table>")
    return "\n".join(lineas)


def _tabla(filas, t):
    """Genera la tabla Markdown completa con todos los colaboradores."""
    lineas = [
        f"| {t['puesto']} | {t['colaborador']} | {t['prs']} | "
        f"{t['commits']} | {t['aportes']} |",
        "|---|---|---|---|---|",
    ]
    for puesto, (login, prs, commits, total) in enumerate(filas, start=1):
        lineas.append(
            f"| {puesto} | [{login}](https://github.com/{login}) | "
            f"{prs} | {commits} | {total} |"
        )
    return "\n".join(lineas)


def generar(aportes, top, idioma):
    """Genera la sección de colaboradores en Markdown/HTML.

    Args:
        aportes: lista de dicts con las claves "login", "prs" (PRs aceptados),
            "commits" (commits directos) y, opcionalmente, "aportes" (total).
        top: cantidad de colaboradores que se muestran en la cuadrícula.
        idioma: "es" o "en"; cualquier otro valor usa "es".

    Returns:
        Texto con la cuadrícula de los primeros ``top``, el bloque desplegable
        "Ver todos (N)" con la tabla completa y la nota final traducida.
    """
    t = TEXTOS.get(idioma, TEXTOS["es"])
    filas = _normalizar(aportes)
    partes = [
        _cuadricula(filas[:max(top, 0)]),
        "",
        "<details>",
        f"<summary>{t['ver_todos']} ({len(filas)})</summary>",
        "",
        _tabla(filas, t),
        "",
        "</details>",
        "",
        t["nota"],
    ]
    return "\n".join(partes) + "\n"
