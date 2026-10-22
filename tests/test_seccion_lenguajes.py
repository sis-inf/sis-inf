"""Pruebas de la sección de lenguajes del perfil."""

import socket

import pytest

from scripts.perfil.secciones.lenguajes import generar


def test_una_insignia_por_lenguaje():
    """Comprueba que cada lenguaje tenga su propia insignia."""
    porcentajes = [
        ("Python", 60.0),
        ("JavaScript", 30.0),
        ("HTML", 10.0),
    ]

    resultado = generar(porcentajes, "es")

    assert resultado.count("https://img.shields.io/badge/") == 3
    assert "| Python | 60.0 |" in resultado
    assert "| JavaScript | 30.0 |" in resultado
    assert "| HTML | 10.0 |" in resultado


@pytest.mark.parametrize(
    ("lenguaje", "fragmento"),
    [
        ("Jupyter Notebook", "Jupyter%20Notebook"),
        ("C++", "C%2B%2B"),
        ("C#", "C%23"),
    ],
)
def test_codificacion_url(lenguaje, fragmento):
    """Comprueba la codificación de espacios, + y #."""
    resultado = generar([(lenguaje, 50.0)], "es")

    assert f"https://img.shields.io/badge/{fragmento}-" in resultado


@pytest.mark.parametrize(
    ("idioma", "encabezado"),
    [
        ("es", "| Lenguaje | % |"),
        ("en", "| Language | % |"),
    ],
)
def test_encabezados_traducidos(idioma, encabezado):
    """Comprueba los encabezados en español e inglés."""
    resultado = generar([("Python", 100.0)], idioma)

    assert encabezado in resultado


@pytest.mark.parametrize(
    ("idioma", "mensaje"),
    [
        ("es", "Aún no hay datos de lenguajes."),
        ("en", "No language data yet."),
    ],
)
def test_lista_vacia(idioma, mensaje):
    """Comprueba el mensaje traducido para una lista vacía."""
    assert generar([], idioma) == mensaje


def test_sin_llamadas_de_red(monkeypatch):
    """Impide conexiones de red durante la generación."""
    def bloquear(*args, **kwargs):
        raise AssertionError("No se permiten llamadas de red")

    monkeypatch.setattr(socket, "create_connection", bloquear)
    monkeypatch.setattr(socket.socket, "connect", bloquear)

    resultado = generar([("Python", 100.0)], "es")

    assert "https://img.shields.io/badge/" in resultado
    
