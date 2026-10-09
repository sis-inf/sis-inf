# Guía de contribución

## Cómo previsualizar el README

Antes de enviar cambios al archivo `README.md`, es importante comprobar que su contenido se visualice correctamente en GitHub.

### Previsualización desde la rama propia

1. Subir los cambios a la rama de trabajo del repositorio personal.
2. Abrir el repositorio en GitHub y seleccionar la rama correspondiente.
3. Entrar al archivo `README.md`.
4. Seleccionar la vista **Preview**, si está disponible, para comprobar cómo se muestra el contenido Markdown.
5. Revisar que los títulos, enlaces, listas e imágenes se visualicen correctamente.

### Previsualización desde el Pull Request

1. Abrir el Pull Request que contiene los cambios del README.
2. Seleccionar la pestaña **Files changed**.
3. Buscar el archivo `README.md` entre los archivos modificados.
4. Abrir el menú del archivo y seleccionar **View file**, cuando esté disponible, para revisar su contenido renderizado.
5. Comprobar que el formato, los enlaces y las imágenes se muestren correctamente antes de solicitar la revisión.

### Comprobación del modo oscuro

1. Abrir GitHub e ingresar a **Settings**.
2. Seleccionar **Appearance**.
3. Cambiar el tema a **Dark**.
4. Regresar al README y comprobar que el texto, los enlaces y las imágenes sean legibles.
5. Repetir la comprobación con el tema **Light** para verificar que el contenido se visualice correctamente en ambos modos.

## Ramas y commits

### Ramas del proyecto

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

### Mensajes de commit

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

### Configuración de Git

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