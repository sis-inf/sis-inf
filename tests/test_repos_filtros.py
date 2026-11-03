import pytest
from perfil.repos import filtrar_repos


@pytest.mark.parametrize(
    "privado, fork, archivado, conservar",
    [
        (False, False, False, True),
        (True, False, False, False),
        (False, True, False, False),
        (False, False, True, False),
        (True, True, False, False),
        (True, False, True, False),
        (False, True, True, False),
        (True, True, True, False),
    ],
    ids=[
        "publico-original-activo",
        "privado",
        "fork",
        "archivado",
        "privado-y-fork",
        "privado-y-archivado",
        "fork-y-archivado",
        "privado-fork-y-archivado",
    ],
)
def test_filtrar_repos_segun_combinacion_de_banderas(
    privado, fork, archivado, conservar
):
    repositorio = {
        "name": "evaluado",
        "private": privado,
        "fork": fork,
        "archived": archivado,
    }

    resultado = filtrar_repos([repositorio], {})

    if conservar:
        assert resultado == [repositorio]
    else:
        assert resultado == []


def test_lista_mixta_conserva_solo_los_publicos_originales_y_activos():
    repositorios = [
        {"name": "publico-a", "private": False, "fork": False, "archived": False},
        {"name": "privado", "private": True, "fork": False, "archived": False},
        {"name": "fork", "private": False, "fork": True, "archived": False},
        {"name": "archivado", "private": False, "fork": False, "archived": True},
        {"name": "publico-b", "private": False, "fork": False, "archived": False},
    ]

    resultado = filtrar_repos(repositorios, {})

    assert len(resultado) == 2
    assert {repositorio["name"] for repositorio in resultado} == {
        "publico-a",
        "publico-b",
    }
