# Experimento 088 — replay temporal del estado de VIZZ

## Objetivo

Probar la frontera entre el host de VIZZ y el renderer sin abrir una cámara,
una ventana, TouchDesigner ni un socket. El replay consume una secuencia
JSONL de estados ya declarados, aplica el contrato 087 y devuelve, para cada
registro, el estado normalizado, los canales y el plan visual.

Esto responde una pregunta concreta antes de la integración: ¿un estado válido
produce una adaptación acotada y un estado viejo, repetido o de baja confianza
vuelve a neutral sin arrastrar el estado anterior?

## Regla temporal

El replay mantiene un cursor de secuencia. Sólo una secuencia estrictamente
creciente puede actualizar el renderer. Un duplicado o un paquete atrasado se
marca `UNKNOWN` aunque su timestamp todavía parezca reciente. Así se evita que
un evento retrasado reanime una adaptación visual antigua.

La regla no pretende ordenar relojes de fuentes distintas: el host debe
asignar `seq` antes de transportar el estado. Sin secuencia válida no hay
certeza de orden.

## Ejecución pura

Desde la raíz del repositorio:

```powershell
.\.venv\Scripts\python.exe experiments\088-vizz-state-replay-preflight\run_replay.py `
  --input experiments\088-vizz-state-replay-preflight\fixtures\sequence.jsonl `
  --now-ms 1100
```

El resultado es JSONL en stdout. No contiene frames, texto escrito, títulos de
ventana ni comandos de input.

## Límites

El replay prueba orden y contrato, no demuestra que una webcam estime mirada,
que TouchDesigner ejecute el bootstrap, ni que una adaptación sea cómoda o
reduzca fatiga. La prueba manual dentro de TouchDesigner sigue siendo el
siguiente paso, cuando el usuario la autorice.
