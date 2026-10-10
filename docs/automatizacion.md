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
