# Mantenimiento del perfil

## Cuándo actualizar

El perfil no se revisa en una fecha fija, sino cada vez que ocurre alguno de estos eventos:

- **Se publica o se archiva un proyecto.** Un repositorio nuevo debe aparecer en la tabla de proyectos; uno archivado debe retirarse o marcarse como inactivo, para no mostrar trabajo abandonado.
- **Cambia el contacto.** Si se modifica el correo institucional, el sitio web o alguna red social, hay que corregirlo de inmediato: un dato de contacto muerto es peor que no tener ninguno.
- **Empieza un semestre nuevo.** Al inicio de cada período se revisan las cifras, la lista de colaboradores y los enlaces, porque cambian los equipos y las materias activas.
- **Cambia el plan de estudios.** Cualquier modificación en las carreras o en la malla curricular debe reflejarse en la descripción del perfil.

## Textos manuales

## Responsables
# Mantenimiento del proyecto

## Responsables

La gestión y el mantenimiento de la documentación e infraestructura del repositorio se organizan por roles funcionales:

- **Equipo Mantenedor (Auxiliares / Docentes):** Tiene la responsabilidad de revisar, aprobar y hacer merge de los Pull Requests (PRs), asegurando que las contribuciones cumplan con los estándares de calidad y las directrices del proyecto.
- **Administración de Configuración e Infraestructura:** Los mantenedores principales son los únicos encargados de gestionar los archivos de configuración (`config/`) y los flujos de trabajo de automatización (`.github/workflows/`), garantizando la integridad de las pruebas y despliegues automáticos.
- **Traspaso de Responsabilidad entre Semestres:** Al finalizar cada período académico, no se transfieren credenciales; se deben revocar los accesos del equipo saliente y asignar permisos individuales al nuevo equipo designado para garantizar la seguridad y continuidad del proyecto.

<!-- seccion:textos-manuales -->
## Textos manuales

Para actualizar la información histórica, las carreras o los datos de contacto del proyecto, se debe seguir el siguiente procedimiento:

1. **Documento principal de origen:** Realizar primero las modificaciones en `docs/investigacion-carrera.md`, incluyendo siempre la fuente de información correspondiente. Si el archivo o el encabezado no existen todavía, deben crearse.
2. **Sincronización:** Una vez actualizada la fuente en la documentación general, replicar y actualizar los cambios correspondientes en los archivos `README.md` (español) y `README.en.md` (inglés).
<!-- /seccion:textos-manuales -->
