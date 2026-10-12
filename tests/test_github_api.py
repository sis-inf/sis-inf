import pytest
from unittest.mock import MagicMock, patch

# Importamos la clase desde el contrato indicado en el Issue
from scripts.perfil.github_api import ClienteGitHub


def create_mock_response(status_code, json_data, headers=None):
    mock_resp = MagicMock()
    mock_resp.status_code = status_code
    mock_resp.json.return_value = json_data
    mock_resp.headers = headers or {}
    return mock_resp


def test_sin_token_no_envia_authorization(monkeypatch):
    mock_get = MagicMock(return_value=create_mock_response(200, []))
    monkeypatch.setattr("scripts.perfil.github_api.requests.get", mock_get)
    
    cliente = ClienteGitHub()
    cliente.rest("/users/test/repos")
    
    _, kwargs = mock_get.call_args
    assert "Authorization" not in kwargs.get("headers", {})


def test_con_token_envia_authorization(monkeypatch):
    mock_get = MagicMock(return_value=create_mock_response(200, []))
    monkeypatch.setattr("scripts.perfil.github_api.requests.get", mock_get)
    
    cliente = ClienteGitHub(token="mi_token_secreto")
    cliente.rest("/users/test/repos")
    
    _, kwargs = mock_get.call_args
    assert kwargs["headers"]["Authorization"] == "token mi_token_secreto"


def test_junta_2_paginas_siguiendo_link(monkeypatch):
    page1 = create_mock_response(200, [{"id": 1}], {"Link": '<https://api.github.com/page2>; rel="next"'})
    page2 = create_mock_response(200, [{"id": 2}])
    mock_get = MagicMock(side_effect=[page1, page2])
    monkeypatch.setattr("scripts.perfil.github_api.requests.get", mock_get)
    
    cliente = ClienteGitHub()
    resultado = cliente.rest("/users/test/repos")
    
    assert len(resultado) == 2
    assert resultado[0]["id"] == 1
    assert resultado[1]["id"] == 2


def test_reintenta_ante_502_y_luego_exito(monkeypatch):
    err_resp = create_mock_response(502, {})
    ok_resp = create_mock_response(200, [{"id": 1}])
    mock_get = MagicMock(side_effect=[err_resp, ok_resp])
    monkeypatch.setattr("scripts.perfil.github_api.requests.get", mock_get)
    monkeypatch.setattr("scripts.perfil.github_api.time.sleep", MagicMock()) # Evitar que el test se pause
    
    cliente = ClienteGitHub()
    resultado = cliente.rest("/users/test/repos")
    
    assert mock_get.call_count == 2
    assert len(resultado) == 1


def test_lanza_runtime_error_ante_404(monkeypatch):
    mock_get = MagicMock(return_value=create_mock_response(404, {"message": "Not Found"}))
    monkeypatch.setattr("scripts.perfil.github_api.requests.get", mock_get)
    
    cliente = ClienteGitHub()
    with pytest.raises(RuntimeError, match="Not Found"):
        cliente.rest("/users/test/repos")


def test_graphql_lanza_runtime_error_si_hay_errors(monkeypatch):
    mock_post = MagicMock(return_value=create_mock_response(200, {"errors": [{"message": "Invalid query"}]}))
    monkeypatch.setattr("scripts.perfil.github_api.requests.post", mock_post)
    
    cliente = ClienteGitHub()
    with pytest.raises(RuntimeError, match="Invalid query"):
        cliente.graphql("query { viewer { login } }", {})
        