
from scripts.perfil.secciones.colaboradores import generar


def datos_colaboradores():
    return [
        {"login": "ana", "prs": 5, "commits": 3},
        {"login": "bruno", "prs": 2, "commits": 2},
        {"login": "carlos", "prs": 4, "commits": 1},
        {"login": "daniela", "prs": 1, "commits": 1},
        {"login": "eduardo", "prs": 3, "commits": 2},
        {"login": "fernanda", "prs": 2, "commits": 1},
    ]


def test_cuadricula_muestra_solo_los_primeros_top():
    resultado = generar(datos_colaboradores(), top=3, idioma="es")
    cuadricula = resultado.split("<details>")[0]

    assert "ana" in cuadricula
    assert "carlos" in cuadricula
    assert "eduardo" in cuadricula
    assert "bruno" not in cuadricula
    assert "daniela" not in cuadricula
    assert "fernanda" not in cuadricula



def test_detalles_incluyen_todos_los_colaboradores():
    aportes = datos_colaboradores()

    resultado = generar(aportes, top=2, idioma="es")
    detalles = resultado.split("<details>")[1]

    for colaborador in aportes:
        assert colaborador["login"] in detalles


def test_resumen_muestra_total_de_aportes():
    resultado = generar(datos_colaboradores(), top=3, idioma="es")

    assert "<summary>Ver todos (6)</summary>" in resultado


def test_textos_se_traducen_al_ingles():
    resultado = generar(datos_colaboradores(), top=3, idioma="en")

    assert "<summary>See all (6)</summary>" in resultado
    assert "Contributor" in resultado
    assert "Accepted PRs" in resultado
    assert "Direct commits" in resultado
    assert "Total contributions" in resultado
    assert "Each accepted PR and each direct commit to main counts as 1 contribution." in resultado


def test_lista_vacia_muestra_textos_traducidos():
    resultado = generar([], top=5, idioma="en")

    assert "<summary>See all (0)</summary>" in resultado
    assert "Total contributions" in resultado
    assert "Each accepted PR and each direct commit to main counts as 1 contribution." in resultado
    assert "|---|---|---|---|---|" in resultado
