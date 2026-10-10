# Automatización del perfil

## Cómo ejecutarlo localmente

Requisitos: Python 3.12 y una copia local del repositorio. Todos los comandos se ejecutan desde la carpeta raíz del repositorio.

Primero instala pytest:

```bash
python -m pip install pytest
```

### Sin `GITHUB_TOKEN`

Sirve para una prueba rápida. Sin autenticación, la API de GitHub solo permite 60 consultas por hora, y el script muestra una advertencia de que no hay token.

```bash
python scripts/actualizar_perfil.py
pytest -q
```

### Con `GITHUB_TOKEN`

Es la forma recomendada, porque el límite de consultas a la API es mucho mayor. Crea un token personal en **GitHub > Settings > Developer settings > Personal access tokens**. Para leer repositorios públicos basta con acceso de solo lectura.

Linux o macOS:

```bash
export GITHUB_TOKEN=tu_token
python scripts/actualizar_perfil.py
pytest -q
```

Windows (cmd):

```bat
set GITHUB_TOKEN=tu_token
python scripts\actualizar_perfil.py
pytest -q
```

Windows (PowerShell):

```powershell
$env:GITHUB_TOKEN = "tu_token"
python scripts/actualizar_perfil.py
pytest -q
```

> No escribas el token dentro de ningún archivo del repositorio ni lo incluyas en un commit.

### Qué revisar después

- El script puede modificar `README.md` y `README.en.md`. Revisa los cambios con `git diff` y no los incluyas en tu Pull Request si no forman parte de tu issue.
- pytest busca las pruebas en la carpeta `tests/` y toma los módulos de `scripts/`, según la configuración de `pyproject.toml`. Al final debe indicar que todas las pruebas pasaron (`passed`).
- Si la carpeta `tests/` todavía no existe o no tiene pruebas, pytest no ejecuta ninguna y muestra un aviso como `No files were found in testpaths` o `no tests ran`. No es un error del script: solo indica que aún no hay pruebas que ejecutar.
