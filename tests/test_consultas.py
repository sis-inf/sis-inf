import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.perfil import consultas  # noqa: E402

USUARIO = "ana"
REPO = "proyecto"


# --------------------------------------------------------------------------
# Cliente falso
# --------------------------------------------------------------------------
class ClienteFalso:
    """Reemplaza a ClienteGitHub sin tocar la red."""

    def __init__(self, prs=None, commits=None, rest=None):
        self.colas = {
            "pullRequests": list(prs or []),
            "history": list(commits or []),
        }
        self.respuestas_rest = rest or {}
        self.llamadas_graphql = []
        self.llamadas_rest = []

    def graphql(self, consulta, variables):
        """Devuelve la siguiente página según el tipo de consulta."""
        self.llamadas_graphql.append((consulta, variables))
        clave = "pullRequests" if "pullRequests" in consulta else "history"
        if self.colas[clave]:
            return self.colas[clave].pop(0)
        # Sin páginas encoladas: página vacía (hasNextPage false, no pagina más).
        return _pagina_prs([]) if clave == "pullRequests" else _pagina_commits([])

    def rest(self, ruta, params=None):
        """Devuelve la respuesta REST registrada para la ruta."""
        self.llamadas_rest.append((ruta, params))
        return self.respuestas_rest[ruta]

    def llamadas_de(self, clave):
        """Llamadas GraphQL cuya consulta contiene la clave dada."""
        return [c for c in self.llamadas_graphql if clave in c[0]]


# --------------------------------------------------------------------------
# Fábricas de datos
# --------------------------------------------------------------------------
def _pr(autor, estado="MERGED"):
    return {"state": estado, "author": {"login": autor} if autor else None}


def _pagina_prs(nodos, siguiente=None):
    return {
        "repository": {
            "pullRequests": {
                "nodes": nodos,
                "pageInfo": {
                    "hasNextPage": siguiente is not None,
                    "endCursor": siguiente,
                },
            }
        }
    }


def _commit(sha, autor="ana", prs=0, padres=1):
    return {
        "oid": sha,
        "author": {"user": {"login": autor} if autor else None},
        "parents": {"totalCount": padres},
        "associatedPullRequests": {"totalCount": prs},
    }


def _pagina_commits(nodos, siguiente=None):
    return {
        "repository": {
            "defaultBranchRef": {
                "target": {
                    "history": {
                        "nodes": nodos,
                        "pageInfo": {
                            "hasNextPage": siguiente is not None,
                            "endCursor": siguiente,
                        },
                    }
                }
            }
        }
    }


def _aportes(cliente):
    return consultas.obtener_aportes(cliente, USUARIO, [REPO])


def _pide_de_100_en_100(consulta, variables):
    """True si la consulta GraphQL pide páginas de 100 elementos."""
    return "first: 100" in consulta or 100 in variables.values()


# --------------------------------------------------------------------------
# obtener_aportes: PRs
# --------------------------------------------------------------------------
def test_pagina_prs_cuando_has_next_page_es_true():
    cliente = ClienteFalso(
        prs=[
            _pagina_prs([_pr("ana")], siguiente="cursor-1"),
            _pagina_prs([_pr("beto")]),
        ]
    )

    prs, _ = _aportes(cliente)

    assert prs == [
        {"repo": REPO, "autor": "ana"},
        {"repo": REPO, "autor": "beto"},
    ]
    llamadas = cliente.llamadas_de("pullRequests")
    assert len(llamadas) == 2
    assert all(_pide_de_100_en_100(c, v) for c, v in llamadas)
    # La segunda llamada debe llevar el cursor de la primera página.
    assert "cursor-1" in llamadas[1][1].values()


def test_autor_null_de_pr_se_vuelve_ghost():
    cliente = ClienteFalso(prs=[_pagina_prs([_pr(None)])])

    prs, _ = _aportes(cliente)

    assert prs == [{"repo": REPO, "autor": "ghost"}]


def test_ignora_prs_no_fusionados():
    cliente = ClienteFalso(
        prs=[
            _pagina_prs(
                [
                    _pr("ana", estado="OPEN"),
                    _pr("beto", estado="CLOSED"),
                    _pr("carla", estado="MERGED"),
                ]
            )
        ]
    )

    prs, _ = _aportes(cliente)

    assert prs == [{"repo": REPO, "autor": "carla"}]


# --------------------------------------------------------------------------
# obtener_aportes: commits
# --------------------------------------------------------------------------
def test_conserva_commit_directo_valido():
    cliente = ClienteFalso(commits=[_pagina_commits([_commit("abc123", "ana")])])

    _, commits = _aportes(cliente)

    assert commits == [{"repo": REPO, "autor": "ana", "sha": "abc123"}]


def test_pagina_commits_cuando_has_next_page_es_true():
    cliente = ClienteFalso(
        commits=[
            _pagina_commits([_commit("sha1", "ana")], siguiente="cursor-9"),
            _pagina_commits([_commit("sha2", "beto")]),
        ]
    )

    _, commits = _aportes(cliente)

    assert [c["sha"] for c in commits] == ["sha1", "sha2"]
    llamadas = cliente.llamadas_de("history")
    assert len(llamadas) == 2
    assert all(_pide_de_100_en_100(c, v) for c, v in llamadas)
    assert "cursor-9" in llamadas[1][1].values()


def test_descarta_commits_asociados_a_un_pr():
    cliente = ClienteFalso(
        commits=[
            _pagina_commits(
                [_commit("por-pr", prs=1), _commit("directo", prs=0)]
            )
        ]
    )

    _, commits = _aportes(cliente)

    assert [c["sha"] for c in commits] == ["directo"]


def test_descarta_commits_de_fusion():
    cliente = ClienteFalso(
        commits=[
            _pagina_commits(
                [_commit("fusion", padres=2), _commit("normal", padres=1)]
            )
        ]
    )

    _, commits = _aportes(cliente)

    assert [c["sha"] for c in commits] == ["normal"]


def test_descarta_commits_sin_usuario():
    cliente = ClienteFalso(
        commits=[
            _pagina_commits(
                [_commit("sin-cuenta", autor=None), _commit("con-cuenta", "ana")]
            )
        ]
    )

    _, commits = _aportes(cliente)

    assert [c["sha"] for c in commits] == ["con-cuenta"]


# --------------------------------------------------------------------------
# obtener_primeras_issues
# --------------------------------------------------------------------------
def test_obtener_primeras_issues_devuelve_total_e_items():
    cliente = ClienteFalso(
        rest={
            "/search/issues": {
                "total_count": 2,
                "items": [
                    {
                        "title": "Mejorar el README",
                        "html_url": "https://github.com/ana/proyecto/issues/1",
                        "repository_url": "https://api.github.com/repos/ana/proyecto",
                    },
                    {
                        "title": "Agregar pruebas",
                        "html_url": "https://github.com/ana/proyecto/issues/2",
                        "repository_url": "https://api.github.com/repos/ana/proyecto",
                    },
                ],
            }
        }
    )

    resultado = consultas.obtener_primeras_issues(cliente, USUARIO)

    assert resultado["total"] == 2
    assert [i["titulo"] for i in resultado["items"]] == [
        "Mejorar el README",
        "Agregar pruebas",
    ]
    assert resultado["items"][0]["url"] == "https://github.com/ana/proyecto/issues/1"
    assert resultado["items"][0]["repo"].endswith(REPO)

    ruta, params = cliente.llamadas_rest[0]
    assert ruta == "/search/issues"
    assert f"user:{USUARIO}" in params["q"]
    assert 'label:"good first issue"' in params["q"]
    assert "state:open" in params["q"]
    assert "is:issue" in params["q"]
    assert params.get("per_page") == 100


# --------------------------------------------------------------------------
# obtener_lenguajes
# --------------------------------------------------------------------------
def test_obtener_lenguajes_agrupa_bytes_por_repo():
    cliente = ClienteFalso(
        rest={f"/repos/{USUARIO}/{REPO}/languages": {"Python": 1200, "HTML": 300}}
    )

    resultado = consultas.obtener_lenguajes(cliente, USUARIO, [REPO])

    assert resultado == {REPO: {"Python": 1200, "HTML": 300}}
