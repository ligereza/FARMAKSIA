# Experimento 076 — adapter real pywinauto/UIA

Este es el primer paso de adopción de una herramienta externa en vez de
reimplementar la superficie de Windows. Usa `pywinauto 0.6.9`, descargado del
repositorio oficial y fijado al commit `f6219c0`, con backend Microsoft UI
Automation (`uia`).

La prueba inspecciona ventanas y, opcionalmente, el árbol de controles. Lee
roles y estructura, pero no emite títulos, texto de usuario, capturas ni
coordenadas sensibles. No hace click, no escribe, no usa cámara y no envía
datos fuera del equipo.

## Resultado observado

En una ejecución del escritorio local se observaron 6 ventanas de primer nivel
y 1.623 controles descendientes, incluyendo 156 `Button`, 4 `Document`, 1
`Edit` y 24 `Pane`. Las cantidades dependen del escritorio activo; se registran
como observación de la máquina, no como benchmark universal.

Esto aporta algo que los fixtures anteriores no aportaban: FARMAKSIA ya puede
recibir una primera representación estructural de una aplicación Windows real
sin depender de visión por computador ni de un modelo generativo.

## Instalar desde el checkout verificado

```powershell
python -m pip install -r experiments/076-farmaxia-pywinauto-uia-adapter/requirements.txt
python -m pip install --no-deps C:/IA/vendor/pywinauto
```

El checkout de código se conserva fuera del repositorio en
`C:/IA/vendor/pywinauto`, fijado al tag `0.6.9`. La dependencia `six` se fija
explícitamente porque el checkout probado la importa aunque no la declare.

## Reproducir

```powershell
python experiments/076-farmaxia-pywinauto-uia-adapter/run_experiment.py --inspect-controls
python experiments/076-farmaxia-pywinauto-uia-adapter/run_contract_test.py
python experiments/076-farmaxia-pywinauto-uia-adapter/run_kill_test.py
```

`--title-regex` permite filtrar localmente una ventana, pero el texto del título
nunca se imprime. El adapter queda limitado a lectura hasta que exista una
acción con autorización, precondición, postcondición y verificador.
