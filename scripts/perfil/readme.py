"""Utilidades de manipulación de texto para el README del perfil.

Solo manipulación de texto: no lee ni escribe archivos, no usa red.
"""

import re

# Ajustar si los marcadores del README del perfil son otros.
# "{nombre}" se sustituye por el nombre de la sección.
MARCADOR_INICIO = "<!-- auto:{nombre} -->"
MARCADOR_FIN = "<!-- /auto:{nombre} -->"


def reemplazar_bloque(texto: str, nombre: str, contenido: str) -> tuple[str, bool]:
    """Reemplaza el contenido entre los marcadores de la sección ``nombre``.

    Lo que hay entre el marcador de inicio y el de fin se sustituye por un
    salto de línea, ``contenido`` y otro salto de línea, conservando ambos
    marcadores.

    Devuelve ``(texto_nuevo, True)`` si se reemplazó el bloque. Si falta
    alguno de los marcadores, devuelve ``(texto, False)`` sin cambios.
    """
    inicio = MARCADOR_INICIO.format(nombre=nombre)
    fin = MARCADOR_FIN.format(nombre=nombre)

    patron = re.compile(
        "(" + re.escape(inicio) + ")" + r".*?" + "(" + re.escape(fin) + ")",
        re.DOTALL,
    )
    if not patron.search(texto):
        return texto, False

    nuevo = patron.sub(
        lambda m: m.group(1) + "\n" + contenido + "\n" + m.group(2),
        texto,
        count=1,
    )
    return nuevo, True
