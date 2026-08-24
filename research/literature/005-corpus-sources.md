# Literatura 005 — fuentes abiertas para corpus creativo

Fecha: 2026-08-23

Este registro separa licencia del software, licencia de la obra y permiso de
los assets. “Open source” del programa no convierte automáticamente en libre
el contenido producido o distribuido con él.

## Fuentes candidatas

### Blender Open Movies

La página oficial de *Spring* indica que la película y los datos publicados del
proyecto se liberan bajo CC BY 4.0, con exclusiones para logos, marcas y
material de terceros: <https://studio.blender.org/projects/spring/pages/about/>.
La página de películas confirma que Blender Studio mantiene archivos de
producción y assets de Open Movies, pero la bóveda completa se ofrece mediante
suscripción: <https://studio.blender.org/films/> y
<https://studio.blender.org/vault/>.

**Decisión:** candidato de alta relevancia para escenas, `.blend`, renders y
secuencias, pero no se descarga ni se incorpora hasta verificar el acceso
concreto y la licencia del asset individual. La suscripción no se trata como
permiso universal de redistribución.

### Wikimedia Commons

Commons exige que los archivos sean de dominio público o estén bajo una
licencia libre; la licencia se debe comprobar en la página individual y pueden
existir restricciones no copyright:
<https://commons.wikimedia.org/wiki/Commons:Licensing> y
<https://commons.wikimedia.org/wiki/Commons:Reusing_content_outside_Wikimedia/licenses/en>.

**Decisión:** candidato para entradas raster, audio y video seleccionadas una
por una. Cada archivo debe conservar URL, autoría, licencia, fecha de consulta,
hash y notas sobre personas, marcas o restricciones adicionales. No se acepta
“Wikimedia Commons” como licencia suficiente del corpus completo.

### OpenUSD example assets

La documentación oficial enumera Kitchen Set, City Set, UsdSkel y otros
assets: <https://openusd.org/release/dl_downloads.html>. Sin embargo, el EULA
de los ejemplos UsdSkel limita su uso a pruebas personales no comerciales y
revocables: <https://openusd.org/dev/dl_usdskel_examples.html>.

**Decisión:** útiles para probar el software OpenUSD y la composición de escenas,
pero no se adoptan como corpus redistribuible ni como evidencia de licencia
abierta de contenido. Requieren una pista de uso separada.

## Herramientas relacionadas

La licencia del software Blender permite usar las obras creadas por la persona
usuaria, pero esto no sustituye la revisión de la licencia de una obra de
terceros: <https://www.blender.org/about/license/>. Por ahora se mantienen
Python estándar, Git y los formatos mínimos; Blender, OpenUSD, FFmpeg y
OpenImageIO quedan como herramientas candidatas condicionadas a una entrada
autorizada y una consulta medible.

## Decisión de corpus

No se incorpora ningún archivo externo en este ciclo. La investigación de
fuentes reduce el riesgo de confundir software abierto, datos accesibles y
permiso de transformación. El próximo ingreso debe ser una selección concreta
con autoridad y manifiesto, no un scrape general.
