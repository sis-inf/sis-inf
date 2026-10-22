import pytest

# Importamos las funciones desde el contrato indicado en el Issue
from scripts.perfil.lenguajes import sumar_lenguajes, porcentajes


def test_suma_el_mismo_lenguaje_de_2_repos():
    por_repo = {
        "repo1": {"Python": 100, "JavaScript": 50},
        "repo2": {"Python": 200, "HTML": 20}
    }
    totales = sumar_lenguajes(por_repo)
    
    assert totales["Python"] == 300
    assert totales["JavaScript"] == 50
    assert totales["HTML"] == 20


def test_ordena_de_mayor_a_menor():
    totales = {"Python": 300, "JavaScript": 100, "HTML": 50}
    resultado = porcentajes(totales)
    
    assert resultado[0][0] == "Python"
    assert resultado[1][0] == "JavaScript"
    assert resultado[2][0] == "HTML"


def test_agrupa_en_otros_los_menores_a_1_porciento():
    # Total = 1000 bytes. 1% = 10 bytes. 
    # HTML tiene 5 bytes (0.5%), así que debe ir a "Otros"
    totales = {"Python": 995, "HTML": 5}
    resultado = porcentajes(totales)
    
    lenguajes = [lang for lang, pct in resultado]
    assert "Otros" in lenguajes
    assert "HTML" not in lenguajes
    
    # Otros debe tener el 0.5%
    otros_pct = [pct for lang, pct in resultado if lang == "Otros"][0]
    assert otros_pct == 0.5


def test_la_suma_da_100_mas_menos_0_1():
    totales = {"Python": 300, "JavaScript": 100, "HTML": 50}
    resultado = porcentajes(totales)
    
    suma_total = sum(pct for lang, pct in resultado)
    assert abs(suma_total - 100.0) <= 0.1


def test_sin_datos_devuelve_lista_vacia():
    totales = {}
    resultado = porcentajes(totales)
    
    assert resultado == []
    