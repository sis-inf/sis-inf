"""Pruebas de la sección de primeras issues del perfil."""

import pytest

from scripts.perfil.secciones.primeras_issues import generar


URL_BUSQUEDA = (
    "https://github.com/search?"
    "q=user%3Asis-inf+label%3A%22good+first+issue%22+state%3Aopen"
    "&type=issues"
)


@pytest.fixture
def datos_ejemplo():
    """Devuelve datos ficticios para las pruebas."""
    return {
        "total": 3,
        "items": [
            {
                "titulo": "Corregir documentación",
                "url": "https://github.com/sis-inf/proyecto1/issues/1",
                "repo": "proyecto1",
            },
            {
                "titulo": "Agregar pruebas",
                "url": "https://github.com/sis-inf/proyecto2/issues/2",
                "repo": "proyecto2",
            },
            {
                "titulo": "Mejorar README",
                "url": "https://github.com/sis-inf/proyecto3/issues/3",
                "repo": "proyecto3",
            },
        ],
    }


def test_respeta_max_items(datos_ejemplo):
    """Comprueba que no se muestren más issues que las permitidas."""
    resultado = generar(datos_ejemplo, 2, "es")

    assert "Corregir documentación" in resultado
    assert "Agregar pruebas" in resultado
    assert "Mejorar README" not in resultado


def test_issues_enlazadas_con_repositorio(datos_ejemplo):
    """Comprueba que las issues incluyan sus enlaces y repositorios."""
    resultado = generar(datos_ejemplo, 2, "es")

    assert datos_ejemplo["items"][0]["url"] in resultado
    assert datos_ejemplo["items"][1]["url"] in resultado
    assert "proyecto1" in resultado
    assert "proyecto2" in resultado


def test_escapa_corchetes_en_titulos():
    """Comprueba que los corchetes se escapen en Markdown."""
    datos = {
        "total": 1,
        "items": [
            {
                "titulo": "Corregir [README]",
                "url": "https://github.com/sis-inf/proyecto/issues/1",
                "repo": "proyecto",
            }
        ],
    }

    resultado = generar(datos, 5, "es")

    assert r"\[README\]" in resultado


def test_total_cero_espanol():
    """Comprueba el mensaje en español cuando no hay issues."""
    datos = {"total": 0, "items": []}

    resultado = generar(datos, 5, "es")

    assert isinstance(resultado, str)
    assert resultado.strip()
    assert "0" in resultado


def test_total_cero_ingles():
    """Comprueba el mensaje en inglés cuando no hay issues."""
    datos = {"total": 0, "items": []}

    resultado = generar(datos, 5, "en")

    assert isinstance(resultado, str)
    assert resultado.strip()
    assert "0" in resultado


def test_textos_en_ingles(datos_ejemplo):
    """Comprueba que el resultado incluya textos en inglés."""
    resultado = generar(datos_ejemplo, 2, "en")

    assert isinstance(resultado, str)
    assert "3" in resultado
    assert "proyecto1" in resultado


def test_enlace_busqueda_general(datos_ejemplo):
    """Comprueba que se incluya el enlace general de búsqueda."""
    resultado = generar(datos_ejemplo, 2, "es")

    assert URL_BUSQUEDA in resultado


def test_no_hace_llamadas_de_red(monkeypatch, datos_ejemplo):
    """Comprueba que la generación no necesite conexiones de red."""
    import socket

    def bloquear_conexion(*args, **kwargs):
        raise AssertionError("No se permiten llamadas de red")

    monkeypatch.setattr(socket, "create_connection", bloquear_conexion)
    monkeypatch.setattr(socket.socket, "connect", bloquear_conexion)

    resultado = generar(datos_ejemplo, 2, "es")

    assert isinstance(resultado, str)
