# Checklist de Revisión

| Función | Resultado | Revisor | Fecha | Observaciones |
| :--- | :--- | :--- | :--- | :--- |
| Texto alternativo | OK | Crackgol | 2026-10-11 | Perfil github.com/sis-inf (Overview): las 8 imágenes (avatares e insignias) tienen alt. El README solo contiene un emoji, sin imágenes propias. |
| Modo claro | OK | Crackgol | 2026-10-11 | Perfil github.com/sis-inf en tema claro: secciones legibles.|
| Ítem / Característica | Resultado | Revisor | Fecha | Observaciones |
| :--- | :--- | :--- | :--- | :--- |
| Modo oscuro | OK | Crackgol | 2026-10-11 | Verificación de banner y legibilidad en Settings -> Appearance. |

# Checklist de revisión del perfil

Antes de difundir el perfil, revisa cada ítem y registra el resultado, la persona responsable y la fecha de revisión.

| Ítem | Cómo se revisa | Resultado | Revisado por | Fecha | Observaciones / Evidencia |
|---|---|---|---|---|---|
| Datos oficiales | Comparar historia, carreras y contacto con `docs/investigacion-carrera.md` y sus fuentes | Problemas encontrados | Marushan-code | 2026-10-11 | **Historia:** los principales datos coinciden.<br>**Carreras:** la sección «Nuestras carreras» del README está incompleta.<br>**Contacto:** faltan datos en el README y en la investigación.<br>**Issues relacionados:** #32, #104 |
| Ambos idiomas | Comparar `README.md` y `README.en.md`: mismas secciones, selector de idioma en ambos sentidos, sin frases sin traducir | Problemas encontrados | Crackgol | 2026-10-15 | **Secciones (EN):** `README.en.md` tiene secciones duplicadas y textos bajo el título equivocado: «About us» y «Contact» salen dos veces, el texto de «Projects» está bajo «Languages» y el de «Contributors» bajo «Contact» (#228).<br>**Secciones (ES):** `README.md` conserva después del pie un bloque «Sobre la carrera» duplicado (#229).<br>**Contenido:** la historia de la carrera no coincide entre idiomas: el español menciona 1987 y el inglés no (#230).<br>**Traducción:** no se encontraron frases sin traducir.<br>**Issues relacionados:** #228, #229, #230 |
| Licencias | Revisar en la tabla de proyectos que todos tengan licencia de software libre | OK | PXNDX-coder | 2026-10-17 | Al 2026-10-17 el README del perfil aún no tiene tabla de proyectos (solo «Hi there»), por lo que se verificó en la lista de repositorios de la organización: 7/7 con licencia MIT (ChuspaPulse, ChuspaSocial, sis-inf, ChuspaNumeric, ChuspaCalc, ChuspaDB y proyecto-base). Volver a revisar cuando se agregue la tabla. |
