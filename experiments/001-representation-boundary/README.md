# Experimento 001 — frontera X-ANA-X / KETAMINE

## Pregunta

¿Puede distinguirse una transformación que conserva una consulta declarada de
una transformación que modifica el espacio del problema?

## Objeto

`input.svg` contiene una cancha rectangular, una línea central y dos regiones
cerradas. La consulta inicial es:

> ¿Qué regiones cerradas intersectan la línea central?

## Condiciones

### KETAMINE candidato

- SVG estructurado → lista de paths.
- SVG estructurado → tabla geométrica.
- SVG → PNG, solo si la consulta se redefine explícitamente como consulta de
  píxeles.

La transformación debe declarar qué preserva y qué deja de poder consultarse.

### X-ANA-X candidato

- Incorporar el registro externo `events.json` como dimensión temporal de cada
  región.
- Cambiar el observable de intersección geométrica a secuencia de eventos.
- Repartir las regiones por una partición distinta de la cancha.

Estas operaciones no solo codifican el objeto: cambian la pregunta o el espacio
de estados disponibles.

El tiempo no debe inventarse dentro del transformador. `events.json` se trata
como una entrada adicional con procedencia explícita. La condición de control
temporal constante permite comprobar que añadir una columna sin variación no
constituye X-ANA-X.

## Medidas

- información conservada y perdida;
- consulta original respondible o no;
- nuevas consultas habilitadas;
- coordenadas y dimensiones;
- costo de preparación;
- costo de consulta;
- reversibilidad;
- residuo;
- decisión de clasificación: X-ANA-X, KETAMINE o ninguno.

## Kill condition

Si añadir una dimensión temporal puede describirse completamente como una
serialización alternativa sin cambiar variables, observables ni consulta,
X-ANA-X queda absorbido por KETAMINE. Si la lista de paths no conserva una
consulta declarada, la transformación no cuenta como KETAMINE: es solo una
conversión incompleta.

## Estado

Primera ejecución completada. La comparación cuantitativa y la primera
falsación están registradas en `results.md`. El kill test sobre la dimensión
temporal queda pendiente.
