# Automatización del perfil

## Qué hace

Una GitHub Action ejecuta el script `scripts/actualizar_perfil.py`, que consulta la API de GitHub y regenera automáticamente algunas secciones del README del perfil de SIS-INF.

**Bloques que actualiza:**

| Bloque | Contenido |
|---|---|
| `cifras` | Línea de insignias con la cantidad de proyectos, estrellas, forks, colaboradores y aportes. |
| `proyectos` | Listado de los proyectos de la organización. |
| `lenguajes` | Lenguajes de programación usados en los proyectos. |
| `colaboradores` | Personas que contribuyen en los proyectos. |
| `participar` | Cómo contribuir a los proyectos de la comunidad. |

**Archivos que modifica:** `README.md` (español) y `README.en.md` (inglés).

**Cada cuánto se ejecuta:** una vez al día, a las 06:00 UTC (02:00 en Bolivia), mediante el workflow `.github/workflows/actualizar-perfil.yml`. También puede ejecutarse manualmente desde la pestaña **Actions** con el botón **Run workflow**. Si el contenido generado no cambió, no se crea ningún commit.

**Qué repositorios considera:** solo los repositorios **públicos** de la organización. Los repositorios privados nunca aparecen en el perfil.

**No se editan a mano:** cada bloque automático está delimitado por un par de marcadores:

```markdown
<!-- auto:proyectos -->
(contenido generado)
<!-- /auto:proyectos -->
```

Todo lo que está entre `<!-- auto:nombre -->` y `<!-- /auto:nombre -->` se reemplaza en cada ejecución, por lo que cualquier cambio manual en esa zona se pierde. Para cambiar ese contenido hay que modificar el script, no el README. El texto que está fuera de los marcadores sí se edita a mano con normalidad.

## Cómo se cuentan los aportes

Cada **Pull Request aceptado** cuenta como 1 aporte, y cada **commit directo a la rama principal** que no haya llegado por un Pull Request también cuenta como 1 aporte. No hay puntajes ni pesos: todos los aportes valen lo mismo, sin importar el tamaño del cambio.

**Qué no cuenta:**

- Los issues abiertos o cerrados.
- Las revisiones de Pull Requests ajenos.
- Los commits de fusión.
- Los commits de bots y los que genera la propia Action.
- Las cuentas listadas en `cuentas_excluidas` dentro de `config/perfil.json`.
- Los commits cuyo correo no esté vinculado a una cuenta de GitHub, porque la API no puede atribuirlos a ninguna persona.

**Cómo se resuelven los empates:** cuando dos personas tienen el mismo total de aportes, se ordenan alfabéticamente por su nombre de usuario, sin distinguir mayúsculas de minúsculas. El criterio está implementado en `scripts/perfil/secciones/colaboradores.py`.

## Cómo ejecutarlo localmente

## Cómo excluir un repositorio

## Al publicar un proyecto privado

## Limitaciones
## Cómo excluir un repositorio

Por defecto, todos los repositorios públicos de la organización aparecen en el perfil. Hay dos formas de excluir uno.

### Opción 1: agregar el topic `no-perfil` en GitHub

1. Abre el repositorio en GitHub.
2. En la columna derecha, junto a **About**, pulsa el ícono de engranaje.
3. En el campo **Topics**, escribe `no-perfil` y pulsa Enter.
4. Pulsa **Save changes**.

Es la opción recomendada cuando tienes permisos de administración sobre ese repositorio, porque no requiere cambios en este repositorio.

### Opción 2: agregarlo a `repos_excluidos` en `config/perfil.json`

Agrega el nombre del repositorio, sin el nombre de la organización, a la lista `repos_excluidos`:

```json
{
  "repos_excluidos": [
    "repositorio-de-prueba",
    "otro-repositorio"
  ]
}
```

Este cambio se propone con un Pull Request a este repositorio. Úsala cuando no tengas permisos de administración sobre el repositorio que quieres excluir.

En ambos casos, el repositorio deja de aparecer en el perfil a partir de la siguiente ejecución de la Action. Para que vuelva a aparecer, quita el topic o elimina su nombre de la lista.
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
- Si la carpeta `tests/` todavía no existe o no tiene pruebas, pytest no ejecuta ninguna, muestra un aviso como `No files were found in testpaths` o `no tests ran` y **finaliza con el código de salida 5** en lugar de 0. No es un error del script: solo indica que aún no hay pruebas que ejecutar.
- Para ver el código de salida del último comando: `echo $?` en Linux o macOS, `echo %ERRORLEVEL%` en cmd y `$LASTEXITCODE` en PowerShell. El código 0 significa que todas las pruebas pasaron.
