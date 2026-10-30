Probablemente la tarjeta del archivo no se te mostró, así que te pego el código completo aquí para que lo copies.

## Dónde va
El código **reemplaza todo el contenido** del archivo que ya existe en tu clon:

```
sis-inf/scripts/perfil/consultas.py
```

Si clonaste en Documentos, la ruta completa es `~/Documents/sis-inf/scripts/perfil/consultas.py`. No crees un archivo nuevo ni lo pongas en otra carpeta.

## Cómo ponerlo
1. En Git Bash, entra al clon y confirma que estás en la rama correcta:
   ```bash
   cd ~/Documents/sis-inf
   git branch
   ```
   Debe verse `* fix/consultas-manejo-timeouts`.
2. Abre el archivo en tu editor. Con VS Code:
   ```bash
   code scripts/perfil/consultas.py
   ```
   (Si no tienes el comando `code`, abre VS Code, luego **File > Open Folder** y elige la carpeta `sis-inf`. En el panel izquierdo abre `scripts` > `perfil` > `consultas.py`.)
3. Selecciona todo el contenido con **Ctrl + A** y bórralo.
4. Pega el código de abajo con **Ctrl + V** y guarda con **Ctrl + S**.
5. Verifica con `git status`. Debe aparecer solo `scripts/perfil/consultas.py` como modificado.

## Código completo

```python
"""Consultas GraphQL y REST a la API de GitHub para las secciones del perfil.

Obtiene aportes (PRs y commits), lenguajes de repositorios y primeras issues.
"""

import logging
from typing import Any, Callable, Dict, List, Optional, Tuple
from urllib.parse import urlencode

import requests

logger = logging.getLogger(__name__)

# Intentos totales por petición individual ante un Timeout (1 inicial + reintentos).
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


def _con_reintentos(llamada: Callable[[], Any], descripcion: str) -> Any:
    """Ejecuta una petición y reintenta si vence el tiempo de espera.

    Captura únicamente requests.exceptions.Timeout (incluye ConnectTimeout y
    ReadTimeout). Si se agotan los intentos devuelve None, que los llamadores
    tratan como una respuesta vacía, para no interrumpir la generación.

    Args:
        llamada: Función sin argumentos que realiza la petición.
        descripcion (str): Texto para identificar la petición en los logs.

    Returns:
        Any: La respuesta de la petición o None si todos los intentos fallan.
    """
    for intento in range(1, MAX_INTENTOS + 1):
        try:
            return llamada()
        except requests.exceptions.Timeout:
            logger.warning(
                "Timeout en %s (intento %d/%d)", descripcion, intento, MAX_INTENTOS
            )
    logger.error(
        "Se agotaron los intentos en %s; se continúa con un valor por defecto",
        descripcion,
    )
    return None


def _rest(cliente: Any, endpoint: str) -> Any:
    """Ejecuta una consulta REST (GET) con el cliente.

    Si el cliente expone otro nombre de método para REST, solo hay que
    cambiarlo aquí. Ante un Timeout reintenta y, si no hay éxito, devuelve None.
    """
    return _con_reintentos(lambda: cliente.rest(endpoint), f"REST {endpoint}")


def _graphql(
    cliente: Any, query: str, variables: Dict[str, Any], descripcion: str
) -> Any:
    """Ejecuta una consulta GraphQL con el cliente.

    Ante un Timeout reintenta y, si no hay éxito, devuelve None.
    """
    return _con_reintentos(
        lambda: cliente.graphql(query, variables), f"GraphQL {descripcion}"
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
    """Devuelve los PRs MERGED de un repositorio, paginando de 100 en 100.

    Si una página agota los intentos por Timeout, se detiene la paginación y
    se devuelven los PRs obtenidos hasta ese momento.
    """
    prs: List[Dict[str, Any]] = []
    cursor = None
    while True:
        variables = {"owner": owner, "name": name, "cursor": cursor}
        respuesta = _graphql(cliente, QUERY_PRS, variables, f"PRs de {repo}")
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
    cuenta de GitHub vinculada (author.user nulo). Si una página agota los
    intentos por Timeout, se devuelven los commits obtenidos hasta ese momento.
    """
    commits: List[Dict[str, Any]] = []
    cursor = None
    while True:
        variables = {"owner": owner, "name": name, "cursor": cursor}
        respuesta = _graphql(
            cliente, QUERY_COMMITS, variables, f"commits de {repo}"
        )
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

    Usa GraphQL con paginación de 100 en 100. Ante un Timeout reintenta la
    petición; si no hay éxito, continúa con los datos ya obtenidos.

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
    del usuario  # Requerido por el contrato; no interviene en las consultas.
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

    Llama al endpoint REST '/repos/{owner}/{repo}/languages'. Si la petición
    de un repositorio agota los intentos por Timeout, ese repositorio queda
    con un diccionario vacío.

    Args:
        cliente: Cliente REST.
        usuario (str): Usuario de GitHub (parte del contrato; no se usa).
        nombres_repos (List[str]): Lista de repositorios ('owner/name').

    Returns:
        Dict[str, Dict[str, int]]: {repo: {lenguaje: bytes}}.
    """
    del usuario  # Requerido por el contrato; no interviene en las consultas.
    resultado: Dict[str, Dict[str, int]] = {}

    for repo in nombres_repos:
        respuesta = _rest(cliente, f"/repos/{repo}/languages")
        resultado[repo] = respuesta if isinstance(respuesta, dict) else {}

    return resultado


def obtener_primeras_issues(cliente: Any, usuario: str) -> Dict[str, Any]:
    """Busca las issues abiertas con la etiqueta 'good first issue' del usuario.

    Usa la búsqueda REST '/search/issues'. Si la petición agota los intentos
    por Timeout, devuelve {'total': 0, 'items': []}.

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
```