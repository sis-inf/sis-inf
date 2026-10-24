# Integración continua (CI)

## Qué revisa cada workflow

| Workflow | Cuándo corre | Qué revisa |
|---|---|---|
| `markdown-lint` | En cada Pull Request y en cada push a `main`. | Que todos los archivos `.md` del repositorio cumplan las reglas de `.markdownlint.jsonc`. |
| `Enlaces rotos` | En cada Pull Request y todos los lunes a las 06:00 UTC. | Que los enlaces de todos los archivos `.md` respondan; falla si alguno no lo hace. La configuración está en `lychee.toml`. |
| `Pruebas Python` | En los Pull Requests que cambian archivos de `scripts/`, `tests/`, `config/` o `pyproject.toml`. | Que `pytest -q` pase con Python 3.12. |
| `actualizar-perfil` | Todos los días a las 06:00 UTC y a mano desde **Actions > Run workflow**. | No revisa nada: ejecuta `scripts/actualizar_perfil.py` para regenerar los bloques automáticos de `README.md` y `README.en.md`. Si hubo cambios, hace commit y push a `main`. |
## Qué hacer si falla

### Cómo leer el log de un check fallido

1. Abre tu Pull Request y baja hasta la sección **Checks**.
2. Junto al check que falló, pulsa **Details**.
3. En la columna izquierda, selecciona el job marcado con una X roja.
4. Expande el paso que falló. Los pasos anteriores que salieron bien aparecen colapsados.
5. Lee las últimas líneas del paso: el error real casi siempre está al final e indica el archivo y la línea.

También se puede leer desde la terminal con GitHub CLI:

- `gh pr checks` muestra el estado de cada check del Pull Request.
- `gh run list --branch nombre-de-tu-rama --limit 5` lista las últimas ejecuciones.
- `gh run view ID_DE_LA_EJECUCION --log-failed` muestra solo el log de los pasos que fallaron.

### Las 3 causas más comunes

#### 1. Falla el check «markdown-lint»

**Cómo se reconoce:** en el log aparece una línea con el formato `archivo.md:número` seguida de un código de regla que empieza con `MD`. El workflow revisa todos los archivos `.md` del repositorio con las reglas de `.markdownlint.jsonc`.

**Solución:** abre el archivo en esa línea y corrige lo que indica la regla. Los casos típicos son falta de línea en blanco alrededor de un encabezado o de una lista, o encabezados que saltan de nivel. Para comprobarlo antes de subir el cambio (requiere Node.js):

```bash
npx --yes markdownlint-cli2 "**/*.md"
```

Guarda, haz commit y push: el check se vuelve a ejecutar solo.

#### 2. Falla el check «Enlaces rotos»

**Cómo se reconoce:** el log de lychee lista las direcciones que no respondieron, con un código de estado como `404`, `403` o `timeout`. Revisa todos los `.md` del repositorio, y también se ejecuta cada lunes a las 06:00 UTC, por lo que puede fallar sin que nadie haya abierto un Pull Request.

**Solución:** abre cada dirección del log en el navegador.

- Si el enlace está mal escrito, corrígelo.
- Si la página ya no existe, reemplázalo por otro enlace o quítalo.
- Si en el navegador sí funciona, puede ser un fallo temporal del sitio: vuelve a ejecutar el check con **Re-run jobs** antes de cambiar nada.
- Si un enlace es válido pero lychee no puede revisarlo, la configuración está en `lychee.toml`.

#### 3. Falla el check «Pruebas Python»

**Cómo se reconoce:** el log del paso **Ejecutar pruebas** muestra líneas que empiezan con `FAILED tests/` y un resumen final como `1 failed, 20 passed`. Este check solo se ejecuta si el Pull Request cambia archivos de `scripts/`, `tests/`, `config/` o `pyproject.toml`.

**Solución:** reproduce el error en tu computadora con Python 3.12:

```bash
python -m pip install pytest
pytest -q
```

Corrige lo que falla y sube el cambio. Si ejecutaste `scripts/actualizar_perfil.py` antes de hacer commit, es posible que `README.md` o `README.en.md` hayan cambiado: descarta esos cambios con `git restore README.md README.en.md`.

Si después de esto el check sigue fallando y no entiendes el error, deja un comentario en tu Pull Request con el enlace al log y pide ayuda.
