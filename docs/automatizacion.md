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

Por defecto, el perfil solo muestra repositorios **públicos**. Un proyecto privado aparece en el perfil recién cuando se hace público. Antes de publicarlo, sigue estos pasos en orden.

### 1. Revisar que el historial no tenga contraseñas ni claves

Al hacer público un repositorio se expone todo su historial, no solo los archivos actuales. Un secreto que se borró en un commit antiguo sigue siendo visible. Busca contraseñas, tokens, llaves de API, archivos `.env`, claves privadas y cadenas de conexión a bases de datos.

Una revisión rápida desde la terminal, en todas las ramas y commits:

```powershell
git --no-pager log --all -i -p -G "password|secret|token|api_key|PRIVATE KEY"
```

Para una revisión más completa se puede usar una herramienta como gitleaks o trufflehog.

Si encuentras un secreto:

1. Revócalo o cámbialo de inmediato en el servicio que lo emitió. Se debe dar por comprometido aunque se elimine del historial.
2. Limpia el historial (por ejemplo con `git filter-repo`) o crea un repositorio nuevo sin el historial anterior.
3. No hagas público el repositorio hasta que la revisión salga limpia.

### 2. Confirmar que tenga una licencia MIT

Un repositorio sin licencia no es software libre aunque sea público: por defecto todos los derechos quedan reservados. Verifica que exista un archivo `LICENSE` en la raíz con el texto de la licencia MIT, con el año y el nombre correctos. Si no existe, en GitHub pulsa **Add file > Create new file**, escribe `LICENSE` como nombre y elige la plantilla **MIT License**.

### 3. Hacerlo público

1. Abre **Settings** del repositorio.
2. En la sección **Danger Zone**, pulsa **Change repository visibility**.
3. Elige **Make public** y confirma.

Requiere permisos de administración. También se puede hacer con GitHub CLI:

```powershell
gh repo edit sis-inf/nombre-del-repo --visibility public --accept-visibility-change-consequences
```

Comprueba además que el repositorio no tenga el topic `no-perfil` ni esté en `repos_excluidos`; de lo contrario no aparecerá aunque sea público (ver «Cómo excluir un repositorio»).

### 4. Ejecutar el workflow a mano

Si no lo ejecutas, el proyecto aparece en la siguiente ejecución diaria, a las 06:00 UTC.

1. Abre la pestaña **Actions** del repositorio del perfil.
2. Selecciona el workflow `actualizar-perfil.yml` en la barra lateral.
3. Pulsa **Run workflow**.

Con GitHub CLI:

```powershell
gh workflow run actualizar-perfil.yml --repo sis-inf/sis-inf
```

### 5. Verificar que aparezca

1. Espera a que la ejecución termine con la marca verde en **Actions**.
2. Abre el perfil de la organización y confirma que el proyecto aparece en el bloque «Proyectos» y que los números de `cifras` subieron.
3. Si no aparece, revisa que la ejecución no haya fallado, que el repositorio sea público y que no esté excluido. Si el contenido generado no cambió, la Action no crea ningún commit.


## Limitaciones

### Los workflows programados se desactivan tras 60 días sin actividad

GitHub desactiva automáticamente los workflows con `schedule` en un repositorio público cuando pasan 60 días sin actividad en él. Si ocurre, el workflow `actualizar-perfil.yml` deja de ejecutarse cada día y el perfil queda desactualizado, aunque el cron siga escrito en el archivo.

Para reactivarlo:

1. Abre la pestaña **Actions** del repositorio.
2. Selecciona el workflow `actualizar-perfil.yml` en la barra lateral. Aparece marcado como desactivado.
3. Pulsa **Enable workflow**.
4. Si quieres actualizar el perfil de inmediato, pulsa **Run workflow**.

También se puede hacer con GitHub CLI: `gh workflow enable actualizar-perfil.yml --repo sis-inf/sis-inf`.

Para que no vuelva a pasar, el repositorio debe recibir actividad (por ejemplo, un commit o un Pull Request) al menos una vez cada 60 días.

### Límites de la API con `GITHUB_TOKEN`

La cantidad de consultas que el script puede hacer a la API de GitHub depende del token con el que se ejecute:

- **Sin token:** 60 consultas por hora.
- **Con un token personal:** 5000 consultas por hora.
- **Con el `GITHUB_TOKEN` que GitHub entrega a la Action:** 1000 consultas por hora por repositorio.

Cuantos más proyectos y colaboradores tiene la organización, más consultas hace el script en cada ejecución. Si se supera el límite, la API responde con errores `403` o `429` y la ejecución falla o deja datos incompletos. En ese caso hay que esperar a que se reinicie el límite (el encabezado `X-RateLimit-Reset` indica cuándo) y volver a ejecutar el workflow desde **Run workflow**.

Además, el `GITHUB_TOKEN` de la Action solo da acceso a los datos públicos de la organización. Por eso los repositorios privados nunca aparecen en el perfil.

### Los aportes cuentan desde que existe cada repositorio

El conteo de aportes se calcula con el historial que tiene cada repositorio. Todo lo que ocurrió antes de que el repositorio existiera, por ejemplo trabajo hecho en otro repositorio, en otra organización o en una cuenta personal, no se cuenta. Un repositorio recién creado empieza desde cero, y un proyecto trasladado a la organización sin su historial original tampoco suma los aportes anteriores.

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
