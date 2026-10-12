"""Genera la línea de cifras del perfil (bloque auto:cifras)."""

from urllib.parse import quote

COLOR = 'blue'

TEXTOS = {
    'es': {
        'proyectos': 'Proyectos',
        'estrellas': 'Estrellas',
        'forks': 'Forks',
        'colaboradores': 'Colaboradores',
        'aportes': 'Aportes',
    },
    'en': {
        'proyectos': 'Projects',
        'estrellas': 'Stars',
        'forks': 'Forks',
        'colaboradores': 'Contributors',
        'aportes': 'Contributions',
    },
}

CLAVES = ('proyectos', 'estrellas', 'forks', 'colaboradores', 'aportes')


def calcular_cifras(repos, aportes):
    """Calcula las cifras del perfil.

    repos es la lista de repos de la API REST (usa stargazers_count y
    forks_count) y aportes la lista de dicts con la clave 'aportes'.
    Devuelve un dict con 'proyectos', 'estrellas', 'forks',
    'colaboradores' (len de aportes) y 'aportes' (suma de aportes).
    """
    return {
        'proyectos': len(repos),
        'estrellas': sum(repo['stargazers_count'] for repo in repos),
        'forks': sum(repo['forks_count'] for repo in repos),
        'colaboradores': len(aportes),
        'aportes': sum(aporte['aportes'] for aporte in aportes),
    }


def _escapar(texto):
    """Escapa un texto para la ruta de img.shields.io/badge."""
    return quote(str(texto).replace('-', '--').replace('_', '__'))


def generar(cifras, idioma):
    """Devuelve una línea centrada con 5 insignias de img.shields.io/badge.

    cifras es el dict de calcular_cifras e idioma es 'es' o 'en'; el texto
    de cada insignia sale de TEXTOS según el idioma.
    """
    textos = TEXTOS[idioma]
    insignias = []
    for clave in CLAVES:
        etiqueta = textos[clave]
        valor = cifras[clave]
        url = (
            f'https://img.shields.io/badge/'
            f'{_escapar(etiqueta)}-{_escapar(valor)}-{COLOR}'
        )
        insignias.append(f'<img src="{url}" alt="{etiqueta}: {valor}">')
    return '<p align="center">' + ' '.join(insignias) + '</p>'
