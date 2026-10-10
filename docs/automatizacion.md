# Automatización del perfil

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
