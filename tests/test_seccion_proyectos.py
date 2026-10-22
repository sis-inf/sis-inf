"""Pruebas de scripts/perfil/secciones/proyectos.py (sin llamadas de red)."""

import socket
import sys
from pathlib import Path

import pytest

RUTA_SECCIONES = Path(__file__).resolve().parents[1] / "scripts" / "perfil" / "secciones"
sys.path.insert(0, str(RUTA_SECCIONES))

import proyectos  # noqa: E402


@pytest.fixture(autouse=True)
def sin_red(monkeypatch):
    """Falla si alguna prueba intenta abrir una conexión de red."""

    def _bloqueado(*args, **kwargs):
        raise AssertionError("Las pruebas no deben hacer llamadas de red")

    monkeypatch.setattr(socket.socket, "connect", _bloqueado)


def hacer_repo(**cambios):
    """Devuelve un repo falso con el formato de la API REST de GitHub."""
    repo = {
        "name": "demo",
        "description": "Un proyecto de prueba",
        "language": "Python",
        "license": {"spdx_id": "MIT"},
        "stargazers_count": 3,
        "forks_count": 1,
        "pushed_at": "2026-10-01T12:00:00Z",
        "html_url": "https://github.com/sis-inf/demo",
        "topics": [],
        "fork": False,
        "archived": False,
        "private": False,
    }
    repo.update(cambios)
    return repo


def celdas_de_fila(salida, nombre="demo"):
    """Devuelve las celdas de la fila de tabla que contiene el repo dado."""
    fila = next(linea for linea in salida.splitlines() if f"[{nombre}]" in linea)
    return [celda.strip() for celda in fila.strip().strip("|").split("|")]


def test_encabezados_en_espanol():
    salida = proyectos.generar([hacer_repo()], "es")
    for texto in ("Proyecto", "Descripción", "Lenguaje", "Licencia", "⭐", "🍴", "Actualizado"):
        assert texto in salida


def test_encabezados_en_ingles():
    salida = proyectos.generar([hacer_repo()], "en")
    for texto in ("Project", "Description", "Language", "License", "⭐", "🍴", "Updated"):
        assert texto in salida
    assert "Descripción" not in salida
    assert "Licencia" not in salida


def test_enlace_al_repo():
    salida = proyectos.generar([hacer_repo()], "es")
    assert "[demo](https://github.com/sis-inf/demo)" in salida


def test_fecha_con_formato_aaaa_mm_dd():
    salida = proyectos.generar([hacer_repo()], "es")
    assert "2026-10-01" in salida
    assert "T12:00:00Z" not in salida


def test_descripcion_nula_muestra_raya():
    salida = proyectos.generar([hacer_repo(description=None)], "es")
    assert celdas_de_fila(salida)[1] == "—"


def test_muestra_la_licencia_mit():
    salida = proyectos.generar([hacer_repo()], "es")
    assert celdas_de_fila(salida)[3] == "MIT"


def test_repo_sin_licencia_muestra_raya():
    salida = proyectos.generar([hacer_repo(license=None)], "es")
    assert celdas_de_fila(salida)[3] == "—"


def test_escapa_la_barra_vertical():
    salida = proyectos.generar([hacer_repo(description="uno | dos")], "es")
    assert r"uno \| dos" in salida
    assert "uno | dos" not in salida


def test_sin_repos_muestra_la_frase():
    salida = proyectos.generar([], "es")
    assert "Pronto habrá proyectos aquí" in salida
