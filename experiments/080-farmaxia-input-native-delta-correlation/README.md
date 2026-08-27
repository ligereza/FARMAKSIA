# Experimento 080 — correlación input/delta nativo

Este experimento conecta el observer de input con el estado interno de una
aplicación real. No intenta leer la mente del usuario: busca si existe un delta
nativo de Excel cerca de una observación de teclado y lo marca como asociación
candidata, ambigua o no asociada.

## Modos

`scratch` crea un libro efímero real, escribe una fórmula, la limpia y cierra
sin guardar. Sirve para verificar el detector de transiciones sin fabricar un
fixture de aplicación.

```powershell
python experiments/080-farmaxia-input-native-delta-correlation/run_experiment.py --mode scratch
```

`live-excel` se conecta sólo a una instancia de Excel ya abierta y observa
durante el tiempo indicado. No modifica el libro, no guarda contenido y sólo
persiste conteos/estados categóricos.

```powershell
python experiments/080-farmaxia-input-native-delta-correlation/run_experiment.py --mode live-excel --duration 60 --sample-hz 8
```

## Regla matemática

Para un delta en `t_d`, se consideran inputs de la misma aplicación en
`[t_d - window, t_d]`. Una coincidencia única produce `candidate_association`;
varias producen `ambiguous_association`; ninguna produce
`unassociated_native_delta`. Ninguna de las tres categorías afirma intención.

## Privacidad y límites

Las firmas de valores, fórmulas y direcciones se calculan con sal aleatoria en
memoria y no se emiten. No se guardan teclas, texto, títulos ni píxeles. El modo
scratch muta sólo procesos efímeros; el modo live es read-only. Todavía no
demuestra causalidad: el orden temporal no prueba que el input causó el delta.
