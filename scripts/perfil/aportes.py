"""
Módulo para procesar y contar aportes (pull requests y commits) de colaboradores
en los repositorios de GitHub.

Solo realiza cálculo: no hace llamadas a la API y usa únicamente la biblioteca
estándar de Python.
"""

from collections import Counter
from typing import Any

LOGIN_FANTASMA = "ghost"
SUFIJO_BOT = "[bot]"


def obtener_login(autor: Any) -> str:
    """Extrae de forma segura el login de un autor.

    Maneja valores nulos, cadenas, diccionarios, objetos con atributo
    ``login`` y estructuras inesperadas.

    Args:
        autor (Any): Objeto, diccionario o cadena que representa al autor.

    Returns:
        str: El login extraído (sin espacios en los extremos) o 'ghost'
            si no se puede determinar un login válido.
    """
    if isinstance(autor, str):
        login = autor
    elif isinstance(autor, dict):
        if "login" in autor:
            login = autor.get("login")
        elif "user" in autor:
            return obtener_login(autor.get("user"))
        elif "author" in autor:
            return obtener_login(autor.get("author"))
        else:
            login = None
    else:
        login = getattr(autor, "login", None)

    if isinstance(login, str) and login.strip():
        return login.strip()
    return LOGIN_FANTASMA


def _cuentas_excluidas(config: Any) -> set[str]:
    """Obtiene las cuentas excluidas de la configuración, en minúsculas.

    Args:
        config (Any): Diccionario de configuración con la clave opcional
            ``cuentas_excluidas``.

    Returns:
        set[str]: Conjunto de logins excluidos normalizados con casefold.
    """
    if not isinstance(config, dict):
        return set()

    cuentas = config.get("cuentas_excluidas") or []
    if isinstance(cuentas, str):
        cuentas = [cuentas]
    elif not isinstance(cuentas, (list, tuple, set, frozenset)):
        return set()

    return {
        cuenta.strip().casefold()
        for cuenta in cuentas
        if isinstance(cuenta, str) and cuenta.strip()
    }


def _es_contable(login: str, excluidas: set[str]) -> bool:
    """Indica si un login debe contarse como colaborador.

    Args:
        login (str): Login ya extraído del autor.
        excluidas (set[str]): Cuentas excluidas normalizadas con casefold.

    Returns:
        bool: False si es 'ghost', un bot ('[bot]') o una cuenta excluida.
    """
    clave = login.casefold()
    return (
        clave != LOGIN_FANTASMA
        and not clave.endswith(SUFIJO_BOT)
        and clave not in excluidas
    )


def _clave_orden(fila: dict[str, Any]) -> tuple[int, int, str, str]:
    """Clave de ordenamiento de una fila de aportes.

    Args:
        fila (dict[str, Any]): Fila con las claves ``login``, ``prs`` y ``aportes``.

    Returns:
        tuple[int, int, str, str]: Total de aportes en negativo (mayor primero),
            prs en negativo (mayor primero), login normalizado con casefold
            (orden alfabético sin distinguir mayúsculas) y login original
            para que el orden sea determinista.
    """
    login: str = fila["login"]
    return (-fila["aportes"], -fila["prs"], login.casefold(), login)


def contar_aportes(
    prs: list[dict[str, Any]],
    commits: list[dict[str, Any]],
    config: dict[str, Any],
) -> list[dict[str, Any]]:
    """Cuenta los aportes (PRs aceptados y commits directos) por usuario.

    Cada PR aceptado suma 1 aporte a su autor y cada commit directo suma
    1 aporte a su autor, sin puntos ni pesos. Nunca se incluyen las cuentas
    de ``config['cuentas_excluidas']``, 'ghost' ni logins que terminan en
    '[bot]' (esto excluye también los commits de la Action).

    Args:
        prs (list[dict]): Lista de Pull Requests aceptados.
        commits (list[dict]): Lista de commits directos.
        config (dict): Configuración; usa la clave ``cuentas_excluidas``.

    Returns:
        list[dict[str, Any]]: Lista de ``{'login', 'prs', 'commits',
            'aportes'}`` (aportes = prs + commits), ordenada por aportes
            (descendente) y, en caso de empate, por login en orden
            alfabético sin distinguir mayúsculas.
    """
    excluidas = _cuentas_excluidas(config)
    conteo_prs: Counter[str] = Counter()
    conteo_commits: Counter[str] = Counter()

    for elementos, contador in ((prs, conteo_prs), (commits, conteo_commits)):
        for elemento in elementos or []:
            if not isinstance(elemento, dict):
                continue
            autor = (
                elemento.get("autor")
                or elemento.get("user")
                or elemento.get("author")
            )
            login = obtener_login(autor)
            if _es_contable(login, excluidas):
                contador[login] += 1

    resultado: list[dict[str, Any]] = [
        {
            "login": login,
            "prs": conteo_prs[login],
            "commits": conteo_commits[login],
            "aportes": conteo_prs[login] + conteo_commits[login],
        }
        for login in set(conteo_prs) | set(conteo_commits)
    ]
    resultado.sort(key=_clave_orden)
    return resultado
