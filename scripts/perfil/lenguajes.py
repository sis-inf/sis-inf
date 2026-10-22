"""Cálculo de lenguajes del perfil: suma de bytes por lenguaje y porcentajes.

Solo hace cálculos sobre los datos recibidos; no llama a ninguna API.
"""

NOMBRE_OTROS = "Otros"


def sumar_lenguajes(por_repo):
    """Suma los bytes de cada lenguaje de todos los repositorios.

    Args:
        por_repo: dict {repositorio: {lenguaje: bytes}}.

    Returns:
        dict {lenguaje: bytes totales} sumando todos los repositorios.
    """
    totales = {}
    for lenguajes in por_repo.values():
        for lenguaje, cantidad in lenguajes.items():
            totales[lenguaje] = totales.get(lenguaje, 0) + cantidad
    return totales


def porcentajes(totales, minimo=1.0):
    """Calcula el porcentaje de cada lenguaje, agrupando los pequeños en 'Otros'.

    Args:
        totales: dict {lenguaje: bytes}.
        minimo: porcentaje mínimo; los lenguajes por debajo se agrupan en 'Otros'.

    Returns:
        Lista de tuplas (lenguaje, porcentaje con 1 decimal) ordenada de mayor
        a menor. Lista vacía si no hay bytes.
    """
    suma = sum(cantidad for cantidad in totales.values() if cantidad > 0)
    if suma <= 0:
        return []

    grupos = {}
    otros = 0
    for lenguaje, cantidad in totales.items():
        if cantidad <= 0:
            continue
        if cantidad * 100 / suma < minimo:
            otros += cantidad
        else:
            grupos[lenguaje] = cantidad
    if otros > 0:
        grupos[NOMBRE_OTROS] = grupos.get(NOMBRE_OTROS, 0) + otros

    ordenados = sorted(grupos.items(), key=lambda par: (-par[1], par[0]))
    return [(lenguaje, round(cantidad * 100 / suma, 1)) for lenguaje, cantidad in ordenados]
