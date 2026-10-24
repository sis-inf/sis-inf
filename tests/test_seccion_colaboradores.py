
"""Pruebas de la sección de colaboradores (sin llamadas de red)."""

import socket
import sys
from pathlib import Path

import pytest

RUTA_SECCIONES = (
    Path(__file__).resolve().parents[1]
    / "scripts"
    / "perfil"
    / "secciones"
)
sys.path.insert(0, str(RUTA_SECCIONES))

import colaboradores  # noqa: E402


@pytest.fixture(autouse=True)
def sin_red(monkeypatch):
    """Falla si alguna prueba intenta abrir una conexión de red."""

    def bloqueado(*args, **kwargs):
        raise AssertionError("Las pruebas no deben hacer llamadas de red")

    monkeypatch.setattr(socket.socket, "connect", bloqueado)


@pytest.fixture
def aportes():
    """Colaboradores falsos para las pruebas."""
    return [
        {"login": "ana", "prs": 3, "commits": 2, "aportes": 5},
        {"login": "luis", "prs": 1, "commits": 4, "aportes": 5},
        {"login": "maria", "prs": 2, "commits": 1, "aportes": 3},
    ]


def test_cuadricula_muestra_solo_top(aportes):
    salida = colaboradores.generar(aportes, 2, "es")
    cuadricula = salida.split("<details>", 1)[0]

    assert "ana" in cuadricula
    assert "luis" in cuadricula
    assert "maria" not in cuadricula


def test_detalles_incluyen_a_todos(aportes):
    salida = colaboradores.generar(aportes, 1, "es")

    assert "ana" in salida
    assert "luis" in salida
    assert "maria" in salida


def test_resumen_muestra_total(aportes):
    salida = colaboradores.generar(aportes, 2, "es")

    assert "Ver todos (3)" in salida


def test_textos_en_ingles(aportes):
    salida = colaboradores.generar(aportes, 2, "en")

    assert "See all (3)" in salida


def test_lista_vacia_en_espanol():
    salida = colaboradores.generar([], 3, "es")

    assert salida.strip()


def test_lista_vacia_en_ingles():
    salida_es = colaboradores.generar([], 3, "es")
    salida_en = colaboradores.generar([], 3, "en")

    assert salida_en.strip()
    assert salida_es != salida_en


def test_avatar_y_enlace_al_perfil(aportes):
    salida = colaboradores.generar(aportes, 1, "es")

    assert "https://github.com/ana.png?size=80" in salida
    assert 'width="60"' in salida
    assert 'alt="ana"' in salida
    assert "https://github.com/ana" in salida


def test_nota_explicativa(aportes):
    salida = colaboradores.generar(aportes, 2, "es")

    assert "main" in salida
    assert "PR" in salida
    assert "commit" in salida.lower()
  
def test_tabla_tiene_todas_las_columnas(aportes):
    salida = colaboradores.generar(aportes, 1, "es")

    assert "| # | Colaborador | PRs aceptados | Commits directos | Aportes de todos |" in salida


def test_tabla_tiene_encabezados_en_ingles(aportes):
    salida = colaboradores.generar(aportes, 1, "en")

    assert "Contributor" in salida
    assert "Accepted PRs" in salida
    assert "Direct commits" in salida
    assert "Total contributions" in salida
