
"""Consultas GraphQL y REST a la API de GitHub para las secciones del perfil.

Obtiene aportes (PRs y commits), lenguajes de repositorios y primeras issues.
"""

import logging
from typing import Any, Callable, Dict, List, Optional, Tuple
from urllib.parse import urlencode

import requests

logger = logging.getLogger(__name__)

MAX_INTENTOS = 2


QUERY_PRS = """
query($owner: String!, $name: String!, $cursor: String) {
  repository(owner: $owner, name: $name) {
    pullRequests(states: [MERGED], first: 100, after: $cursor) {
      pageInfo { hasNextPage endCursor }
      nodes { author { login } }
    }
  }
}
"""

QUERY_COMMITS = """
query($owner: String!, $name: String!, $cursor: String) {
  repository(owner: $owner, name: $name) {
    defaultBranchRef {
      target {
        ... on Commit {
          history(first: 100, after: $cursor) {
            pageInfo { hasNextPage endCursor }
            nodes {
              oid
              parents { totalCount }
              author { user { login } }
              associatedPullRequests { totalCount }
            }
          }
        }
      }
    }
  }
}
"""


def _con_reintentos(consulta: Callable[[], Any], descripcion: str) -> Any:
    """Ejecuta una consulta y reintenta cuando ocurre un Timeout."""
    for intento in range(1, MAX_INTENTOS + 1):
        try:
            return consulta()
        except requests.exceptions.Timeout:
            if intento < MAX_INTENTOS:
                logger.warning(
                    "Timeout en %s. Reintentando (%s/%s).",
                    descripcion,
                    intento,
                    MAX_INTENTOS - 1,
                )
            else:
                logger.error(
                    "Timeout en %s después de %s intentos.",
                    descripcion,
                    MAX_INTENTOS,
                )
    return None


def _rest(cliente: Any, endpoint: str) -> Any:
    """Ejecuta una consulta REST (GET) con el cliente."""
    return _con_reintentos(
        lambda: cliente.rest(endpoint),
        f"consulta REST {endpoint}",
    )


def _graphql(cliente: Any, consulta: str, variables: Dict[str, Any]) -> Any:
    """Ejecuta una consulta GraphQL con el cliente."""
    return _con_reintentos(
        lambda: cliente.graphql(consulta, variables),
        "consulta GraphQL",
    )


def _repositorio(respuesta: Any) -> Optional[Dict[str, Any]]:
    """Extrae el nodo 'repository' de una respuesta GraphQL.

    Tolera respuestas con 'data' nulo (errores) y clientes que devuelven
    directamente el contenido de 'data'.
    """
    if not isinstance(respuesta, dict):
        return None
    datos = respuesta["data"] if "data" in respuesta else respuesta
    if not isinstance(datos, dict):
        return None
    return datos.get("repository")


def _prs_fusionados(
    cliente: Any, repo: str, owner: str, name: str
) -> List[Dict[str, Any]]:
    """Devuelve los PRs MERGED de un repositorio, paginando de 100 en 100."""
    prs: List[Dict[str, Any]] = []
    cursor = None
    while True:
        variables = {"owner": owner, "name": name, "cursor": cursor}
        respuesta = _graphql(cliente, QUERY_PRS, variables)
        conexion = (_repositorio(respuesta) or {}).get("pullRequests")
        if not conexion:
            break

        for nodo in conexion.get("nodes") or []:
            if not nodo:
                continue
            autor = (nodo.get("author") or {}).get("login") or "ghost"
            prs.append({"repo": repo, "autor": autor})

        info = conexion.get("pageInfo") or {}
        if not info.get("hasNextPage"):
            break
        cursor = info.get("endCursor")
    return prs


def _commits_directos(
    cliente: Any, repo: str, owner: str, name: str
) -> List[Dict[str, Any]]:
    """Devuelve los commits directos de la rama por defecto de un repositorio.

    Descarta los que llegaron por un PR, los de fusión y los que no tienen
    cuenta de GitHub vinculada (author.user nulo).
    """
    commits: List[Dict[str, Any]] = []
    cursor = None
    while True:
        variables = {"owner": owner, "name": name, "cursor": cursor}
        respuesta = _graphql(cliente, QUERY_COMMITS, variables)
        rama = (_repositorio(respuesta) or {}).get("defaultBranchRef") or {}
        historial = (rama.get("target") or {}).get("history")
        if not historial:
            break

        for nodo in historial.get("nodes") or []:
            if not nodo:
                continue
            if (nodo.get("associatedPullRequests") or {}).get("totalCount") or 0:
                continue
            if ((nodo.get("parents") or {}).get("totalCount") or 0) > 1:
                continue
            cuenta = (nodo.get("author") or {}).get("user")
            if not cuenta or not cuenta.get("login"):
                continue
            commits.append(
                {"repo": repo, "autor": cuenta["login"], "sha": nodo.get("oid", "")}
            )

        info = historial.get("pageInfo") or {}
        if not info.get("hasNextPage"):
            break
        cursor = info.get("endCursor")
    return commits


def obtener_aportes(
    cliente: Any, usuario: str, nombres_repos: List[str]
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Obtiene los PRs fusionados y los commits directos de los repositorios.

    Usa GraphQL con paginación de 100 en 100.

    Args:
        cliente: Cliente con el método graphql(query, variables).
        usuario (str): Usuario de GitHub (parte del contrato; no se usa para
            filtrar, porque se cuentan los aportes de todos los autores).
        nombres_repos (List[str]): Lista de repositorios ('owner/name').

    Returns:
        Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]: (prs, commits) donde
        prs = [{'repo', 'autor'}] (autor nulo se vuelve 'ghost') y
        commits = [{'repo', 'autor', 'sha'}].
    """
    del usuario
    prs: List[Dict[str, Any]] = []
    commits: List[Dict[str, Any]] = []

    for repo in nombres_repos:
        if "/" not in repo:
            continue
        owner, name = repo.split("/", 1)
        prs.extend(_prs_fusionados(cliente, repo, owner, name))
        commits.extend(_commits_directos(cliente, repo, owner, name))

    return prs, commits


def obtener_lenguajes(
    cliente: Any, usuario: str, nombres_repos: List[str]
) -> Dict[str, Dict[str, int]]:
    """Obtiene los bytes por lenguaje de cada repositorio.

    Llama al endpoint REST '/repos/{owner}/{repo}/languages'.

    Args:
        cliente: Cliente REST.
        usuario (str): Usuario de GitHub (parte del contrato; no se usa).
        nombres_repos (List[str]): Lista de repositorios ('owner/name').

    Returns:
        Dict[str, Dict[str, int]]: {repo: {lenguaje: bytes}}.
    """
    del usuario
    resultado: Dict[str, Dict[str, int]] = {}

    for repo in nombres_repos:
        respuesta = _rest(cliente, f"/repos/{repo}/languages")
        resultado[repo] = respuesta if isinstance(respuesta, dict) else {}

    return resultado


def obtener_primeras_issues(cliente: Any, usuario: str) -> Dict[str, Any]:
    """Busca las issues abiertas con la etiqueta 'good first issue' del usuario.

    Usa la búsqueda REST '/search/issues'.

    Args:
        cliente: Cliente REST.
        usuario (str): Usuario de GitHub.

    Returns:
        Dict[str, Any]: {'total': int,
        'items': [{'titulo': str, 'url': str, 'repo': str}]}.
    """
    q = f'user:{usuario} label:"good first issue" state:open is:issue'
    respuesta = _rest(cliente, f"/search/issues?{urlencode({'q': q})}")
    if not isinstance(respuesta, dict):
        return {"total": 0, "items": []}

    items: List[Dict[str, str]] = []
    for item in respuesta.get("items") or []:
        repository_url = item.get("repository_url") or ""
        repo = repository_url.split("/repos/", 1)[1] if "/repos/" in repository_url else ""
        items.append(
            {
                "titulo": item.get("title", ""),
                "url": item.get("html_url", ""),
                "repo": repo,
            }
        )

    return {"total": respuesta.get("total_count", 0), "items": items}
