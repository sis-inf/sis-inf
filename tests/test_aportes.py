import pytest

# Importamos la función desde el contrato indicado en el Issue
from scripts.perfil.aportes import contar_aportes


def test_pr_aceptado_cuenta_1_aporte():
    prs = [{"user": {"login": "user1"}}]
    commits = []
    config = {"cuentas_excluidas": []}
    res = contar_aportes(prs, commits, config)
    
    assert len(res) == 1
    assert res[0]["login"] == "user1"
    assert res[0]["prs"] == 1
    assert res[0]["commits"] == 0
    assert res[0]["aportes"] == 1


def test_commit_directo_cuenta_1_aporte():
    prs = []
    commits = [{"author": {"login": "user2"}}]
    config = {"cuentas_excluidas": []}
    res = contar_aportes(prs, commits, config)
    
    assert len(res) == 1
    assert res[0]["login"] == "user2"
    assert res[0]["prs"] == 0
    assert res[0]["commits"] == 1
    assert res[0]["aportes"] == 1


def test_aportes_igual_prs_mas_commits():
    prs = [{"user": {"login": "user1"}}, {"user": {"login": "user1"}}]
    commits = [{"author": {"login": "user1"}}, {"author": {"login": "user1"}}]
    config = {"cuentas_excluidas": []}
    res = contar_aportes(prs, commits, config)
    
    assert res[0]["prs"] == 2
    assert res[0]["commits"] == 2
    assert res[0]["aportes"] == 4


def test_suma_misma_persona_en_varios_repos():
    prs = [{"user": {"login": "user1"}}]
    commits = [{"author": {"login": "user1"}}, {"author": {"login": "user1"}}]
    config = {"cuentas_excluidas": []}
    res = contar_aportes(prs, commits, config)
    
    assert res[0]["prs"] == 1
    assert res[0]["commits"] == 2
    assert res[0]["aportes"] == 3


def test_cuenta_excluida_no_aparece():
    prs = [{"user": {"login": "excluded_user"}}, {"user": {"login": "user1"}}]
    commits = []
    config = {"cuentas_excluidas": ["excluded_user"]}
    res = contar_aportes(prs, commits, config)
    
    assert len(res) == 1
    assert res[0]["login"] == "user1"


def test_bots_y_ghost_no_aparecen():
    prs = [
        {"user": {"login": "actions[bot]"}}, 
        {"user": {"login": "ghost"}}, 
        {"user": {"login": "user1"}}
    ]
    commits = [{"author": {"login": "dependabot[bot]"}}]
    config = {"cuentas_excluidas": []}
    res = contar_aportes(prs, commits, config)
    
    assert len(res) == 1
    assert res[0]["login"] == "user1"


def test_desempata_por_prs_y_luego_login():
    # user1: 2 aportes (2 prs, 0 commits)
    # user2: 2 aportes (1 prs, 1 commits)
    # user3: 2 aportes (2 prs, 0 commits)
    prs = [
        {"user": {"login": "user1"}},
        {"user": {"login": "user1"}},
        {"user": {"login": "user2"}},
        {"user": {"login": "user3"}},
        {"user": {"login": "user3"}}
    ]
    commits = [{"author": {"login": "user2"}}]
    config = {"cuentas_excluidas": []}
    res = contar_aportes(prs, commits, config)
    
    # Todos tienen 2 aportes.
    # user1 y user3 tienen 2 PRs (user2 tiene 1 PR). user2 queda último.
    # Entre user1 y user3, desempata por login alfabético: user1, user3
    assert res[0]["login"] == "user1"
    assert res[1]["login"] == "user3"
    assert res[2]["login"] == "user2"


def test_listas_vacias_devuelven_lista_vacia():
    prs = []
    commits = []
    config = {"cuentas_excluidas": []}
    res = contar_aportes(prs, commits, config)
    
    assert res == []
    