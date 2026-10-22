"""
Módulo para obtener y filtrar repositorios públicos de un usuario de GitHub.
"""

from typing import Any, Dict, List


def obtener_repos(cliente: Any, usuario: str) -> List[Dict[str, Any]]:
    """Obtiene la lista de repositorios públicos del usuario llamando a la API REST

    de GitHub en el endpoint '/users/{usuario}/repos'.

    Args:
        cliente: Cliente de la API de GitHub que implementa el método rest().
        usuario (str): Nombre de usuario de GitHub.

    Returns:
        List[Dict[str, Any]]: Lista de diccionarios con la información de los repositorios.
    """
    ruta = f"/users/{usuario}/repos"
    params = {"type": "owner", "per_page": 100}
    respuesta = cliente.rest(ruta, params)
    if isinstance(respuesta, list):
        return respuesta
    return []


def filtrar_repos(
    repos: List[Dict[str, Any]], config: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """Filtra una lista de repositorios eliminando privados, forks, archivados,

    repositorios excluidos y repositorios con topics excluidos, y los ordena

    por fecha de última actualización (pushed_at) en orden descendente.

    Args:
        repos (List[Dict[str, Any]]): Lista de diccionarios de repositorios.
        config (Dict[str, Any]): Diccionario de configuración.

    Returns:
        List[Dict[str, Any]]: Lista de repositorios filtrados y ordenados.
    """
    repos_excluidos = set(config.get("repos_excluidos", []))
    topic_exclusion_raw = config.get("topic_exclusion", [])
    if isinstance(topic_exclusion_raw, str):
        topics_excluidos = {topic_exclusion_raw}
    else:
        topics_excluidos = set(topic_exclusion_raw)

    repos_filtrados: List[Dict[str, Any]] = []

    for repo in repos:
        if not isinstance(repo, dict):
            continue

        # 1. Quitar privados
        if repo.get("private", False):
            continue

        # 2. Quitar forks
        if repo.get("fork", False):
            continue

        # 3. Quitar archivados
        if repo.get("archived", False):
            continue

        # 4. Quitar repositorios en repos_excluidos
        nombre = repo.get("name", "")
        full_name = repo.get("full_name", "")
        if nombre in repos_excluidos or full_name in repos_excluidos:
            continue

        # 5. Quitar si tienen topics excluidos
        topics = repo.get("topics", [])
        if topics and any(t in topics_excluidos for t in topics):
            continue

        repos_filtrados.append(repo)

    # Ordenar por pushed_at descendente (más reciente primero)
    repos_filtrados.sort(
        key=lambda x: x.get("pushed_at") or "", reverse=True
    )

    return repos_filtrados
