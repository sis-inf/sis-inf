import pytest
from unittest.mock import MagicMock

# Importamos las funciones desde el contrato indicado en el Issue
from scripts.perfil.repos import filtrar_repos, obtener_repos


def test_quita_privados():
    repos = [
        {"name": "public", "private": False, "fork": False, "archived": False, "topics": [], "pushed_at": "2023-01-01T00:00:00Z"},
        {"name": "private", "private": True, "fork": False, "archived": False, "topics": [], "pushed_at": "2023-01-02T00:00:00Z"}
    ]
    config = {"repos_excluidos": [], "topic_exclusion": []}
    res = filtrar_repos(repos, config)
    assert len(res) == 1
    assert res[0]["name"] == "public"


def test_quita_forks():
    repos = [
        {"name": "original", "private": False, "fork": False, "archived": False, "topics": [], "pushed_at": "2023-01-01T00:00:00Z"},
        {"name": "forked", "private": False, "fork": True, "archived": False, "topics": [], "pushed_at": "2023-01-02T00:00:00Z"}
    ]
    config = {"repos_excluidos": [], "topic_exclusion": []}
    res = filtrar_repos(repos, config)
    assert len(res) == 1
    assert res[0]["name"] == "original"


def test_quita_archivados():
    repos = [
        {"name": "active", "private": False, "fork": False, "archived": False, "topics": [], "pushed_at": "2023-01-01T00:00:00Z"},
        {"name": "archived", "private": False, "fork": False, "archived": True, "topics": [], "pushed_at": "2023-01-02T00:00:00Z"}
    ]
    config = {"repos_excluidos": [], "topic_exclusion": []}
    res = filtrar_repos(repos, config)
    assert len(res) == 1
    assert res[0]["name"] == "active"


def test_quita_proyecto_base():
    repos = [
        {"name": "proyecto-base", "private": False, "fork": False, "archived": False, "topics": [], "pushed_at": "2023-01-01T00:00:00Z"},
        {"name": "app", "private": False, "fork": False, "archived": False, "topics": [], "pushed_at": "2023-01-02T00:00:00Z"}
    ]
    config = {"repos_excluidos": ["proyecto-base"], "topic_exclusion": []}
    res = filtrar_repos(repos, config)
    assert len(res) == 1
    assert res[0]["name"] == "app"


def test_quita_repos_con_topic_no_perfil():
    repos = [
        {"name": "excluded", "private": False, "fork": False, "archived": False, "topics": ["no-perfil"], "pushed_at": "2023-01-01T00:00:00Z"},
        {"name": "included", "private": False, "fork": False, "archived": False, "topics": [], "pushed_at": "2023-01-02T00:00:00Z"}
    ]
    config = {"repos_excluidos": [], "topic_exclusion": ["no-perfil"]}
    res = filtrar_repos(repos, config)
    assert len(res) == 1
    assert res[0]["name"] == "included"


def test_ordena_por_pushed_at_descendente():
    repos = [
        {"name": "old", "private": False, "fork": False, "archived": False, "topics": [], "pushed_at": "2022-01-01T00:00:00Z"},
        {"name": "new", "private": False, "fork": False, "archived": False, "topics": [], "pushed_at": "2023-01-01T00:00:00Z"}
    ]
    config = {"repos_excluidos": [], "topic_exclusion": []}
    res = filtrar_repos(repos, config)
    assert res[0]["name"] == "new"
    assert res[1]["name"] == "old"


def test_lista_vacia_devuelve_lista_vacia():
    config = {"repos_excluidos": [], "topic_exclusion": []}
    res = filtrar_repos([], config)
    assert res == []


def test_obtener_repos_llama_al_cliente_correctamente():
    # Usamos un mock para simular el cliente de GitHub
    mock_client = MagicMock()
    mock_client.rest.return_value = [{"name": "test-repo"}]
    
    res = obtener_repos(mock_client, "test_user")
    
    # Verificamos que se llame a la ruta y parámetros correctos
    mock_client.rest.assert_called_once_with('/users/test_user/repos', {'type': 'owner', 'per_page': 100})
    assert res == [{"name": "test-repo"}]
    