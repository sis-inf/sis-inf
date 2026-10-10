import os
import json
import logging
import sys

# Asegurar que la raiz este en sys.path
DIR_RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if DIR_RAIZ not in sys.path:
    sys.path.insert(0, DIR_RAIZ)

from perfil.github_api import ClienteGitHub
from perfil.repos import obtener_y_filtrar_repos

def main():
    token = os.getenv("GITHUB_TOKEN")
    cliente = ClienteGitHub(token)
    
    # Ejemplo de configuracion
    config = {
        'readmes': {
            'README.md': 'es'
        }
    }
    
    # Iteracion corregida sobre items()
    readmes = config.get('readmes', {})
    for ruta_relativa_readme, idioma in readmes.items():
        print(f"Procesando {ruta_relativa_readme} para el idioma {idioma}...")

if __name__ == "__main__":
    main()
