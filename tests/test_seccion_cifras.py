from scripts.perfil.secciones.cifras import calcular_cifras, generar


def test_calcular_cifras_suma_estrellas_y_forks():
    repos = [
        {"stargazers_count": 10, "forks_count": 3},
        {"stargazers_count": 5, "forks_count": 2},
    ]

    cifras = calcular_cifras(repos, [])

    assert cifras["proyectos"] == 2
    assert cifras["estrellas"] == 15
    assert cifras["forks"] == 5


def test_calcular_cifras_cuenta_colaboradores_y_suma_aportes():
    aportes = [
        {"aportes": 10},
        {"aportes": 20},
        {"aportes": 30},
    ]

    cifras = calcular_cifras([], aportes)

    assert cifras["colaboradores"] == 3
    assert cifras["aportes"] == 60


def test_generar_texto_en_espanol():
    cifras = {
        "proyectos": 2,
        "estrellas": 15,
        "forks": 5,
        "colaboradores": 3,
        "aportes": 60,
    }

    resultado = generar(cifras, "es")

    assert resultado.startswith('<p align="center">')
    assert resultado.endswith("</p>")
    assert "Proyectos" in resultado
    assert "Estrellas" in resultado
    assert "Colaboradores" in resultado


def test_generar_texto_en_ingles():
    cifras = {
        "proyectos": 2,
        "estrellas": 15,
        "forks": 5,
        "colaboradores": 3,
        "aportes": 60,
    }

    resultado = generar(cifras, "en")

    assert "Projects" in resultado
    assert "Stars" in resultado
    assert "Contributors" in resultado


def test_generar_cinco_insignias_con_los_numeros():
    cifras = {
        "proyectos": 2,
        "estrellas": 15,
        "forks": 5,
        "colaboradores": 3,
        "aportes": 60,
    }

    resultado = generar(cifras, "es")

    assert resultado.count("img.shields.io/badge/") == 5

    for numero in ("2", "15", "5", "3", "60"):
        assert numero in resultado