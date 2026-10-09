# Ramas y commits

## Ramas del proyecto

Las ramas deben utilizarse para organizar el trabajo y facilitar la revisión de los cambios antes de integrarlos en la rama principal.

| Rama | Propósito |
|---|---|
| `main` | Rama principal del proyecto. Contiene la versión estable. |
| `feat/*` | Desarrollo de nuevas funcionalidades. |
| `fix/*` | Corrección de errores. |
| `docs/*` | Cambios en la documentación. |
| `test/*` | Incorporación o modificación de pruebas. |
| `chore/*` | Tareas de mantenimiento y configuración. |

Los nombres de las ramas deben seguir el formato `tipo/descripcion`. La descripción debe ser breve, clara y utilizar guiones para separar las palabras.

## Mensajes de commit

Los mensajes de commit deben seguir el formato `tipo: descripción`. El tipo identifica la naturaleza del cambio y la descripción resume brevemente el trabajo realizado.

| Tipo | Propósito |
|---|---|
| `docs` | Cambios en la documentación. |
| `feat` | Incorporación de funcionalidades. |
| `chore` | Tareas de mantenimiento y configuración. |
| `test` | Cambios relacionados con pruebas. |
| `fix` | Corrección de errores. |

Ejemplos de mensajes de commit:

```text
docs: documentar las normas de contribución
feat: agregar registro de estudiantes
fix: corregir error de validación
```

## Configuración de Git

Para que los commits puedan atribuirse correctamente a tu cuenta de GitHub, configura `user.name` y `user.email`. Utiliza una dirección de correo vinculada y verificada en tu cuenta de GitHub.

```bash
git config --global user.name "Tu nombre"
git config --global user.email "tu-correo-vinculado@ejemplo.com"
```

Sustituye los valores de ejemplo por tus datos. Puedes comprobar la configuración con:

```bash
git config --global user.name
git config --global user.email
```