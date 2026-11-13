import io
import json
import urllib.error
import urllib.request
from unittest.mock import MagicMock
import pytest

# Importamos la clase desde el contrato indicado en el Issue
from scripts.perfil.github_api import ClienteGitHub


def create_mock_response(status_code, json_data, headers=None):
    mock_resp = MagicMock()
    mock_resp.status = status_code
    cuerpo = json.dumps(json_data).encode("utf-8") if json_data is not None else b""
    mock_resp.read.return_value = cuerpo
    mock_resp.headers = headers or {}
    mock_resp.__enter__.return_value = mock_resp
    mock_resp.__exit__.return_value = None
    return mock_resp


def create_http_error(url, status_code, json_data):
    cuerpo = json.dumps(json_data).encode("utf-8") if json_data is not None else b""
    fp = io.BytesIO(cuerpo)
    return urllib.error.HTTPError(url, status_code, "HTTP Error", {}, fp)


def test_sin_token_no_envia_authorization(monkeypatch):
    mock_open = MagicMock(return_value=create_mock_response(200, []))
    monkeypatch.setattr("urllib.request.urlopen", mock_open)

    cliente = ClienteGitHub()
    cliente.rest("/users/test/repos")

    req = mock_open.call_args[0][0]
    assert not req.has_header("Authorization")


def test_con_token_envia_authorization(monkeypatch):
    mock_open = MagicMock(return_value=create_mock_response(200, []))
    monkeypatch.setattr("urllib.request.urlopen", mock_open)

    cliente = ClienteGitHub(token="mi_token_secreto")
    cliente.rest("/users/test/repos")

    req = mock_open.call_args[0][0]
    assert req.get_header("Authorization") == "Bearer mi_token_secreto"


def test_junta_2_paginas_siguiendo_link(monkeypatch):
    page1 = create_mock_response(200, [{"id": 1}], {"Link": '<https://api.github.com/page2>; rel="next"'})
    page2 = create_mock_response(200, [{"id": 2}])
    mock_open = MagicMock(side_effect=[page1, page2])
    monkeypatch.setattr("urllib.request.urlopen", mock_open)

    cliente = ClienteGitHub()
    resultado = cliente.rest("/users/test/repos")

    assert len(resultado) == 2
    assert resultado[0]["id"] == 1
    assert resultado[1]["id"] == 2


def test_reintenta_ante_502_y_luego_exito(monkeypatch):
    err_resp = create_http_error("https://api.github.com/users/test/repos", 502, {})
    ok_resp = create_mock_response(200, [{"id": 1}])
    mock_open = MagicMock(side_effect=[err_resp, ok_resp])
    monkeypatch.setattr("urllib.request.urlopen", mock_open)
    monkeypatch.setattr("scripts.perfil.github_api.time.sleep", MagicMock())  # Evitar que el test se pause

    cliente = ClienteGitHub()
    resultado = cliente.rest("/users/test/repos")

    assert mock_open.call_count == 2
    assert len(resultado) == 1


def test_lanza_runtime_error_ante_404(monkeypatch):
    err_resp = create_http_error("https://api.github.com/users/test/repos", 404, {"message": "Not Found"})
    mock_open = MagicMock(side_effect=err_resp)
    monkeypatch.setattr("urllib.request.urlopen", mock_open)

    cliente = ClienteGitHub()
    with pytest.raises(RuntimeError, match="Not Found"):
        cliente.rest("/users/test/repos")


def test_graphql_lanza_runtime_error_si_hay_errors(monkeypatch):
    mock_open = MagicMock(return_value=create_mock_response(200, {"errors": [{"message": "Invalid query"}]}))
    monkeypatch.setattr("urllib.request.urlopen", mock_open)

    cliente = ClienteGitHub()
    with pytest.raises(RuntimeError, match="Invalid query"):
        cliente.graphql("query { viewer { login } }", {})
