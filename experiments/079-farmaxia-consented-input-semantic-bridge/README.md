# Experimento 079 — input consentido como motor semántico

Este experimento conecta input local real con el kernel de transiciones sin
pretender adivinar la intención del usuario.

Observa, sólo con autorización explícita:

- actividad de teclado como conteo, sin teclas ni texto;
- cambio de aplicación en primer plano;
- tipo de control UIA de la ventana activa;
- movimiento del puntero sólo si se activa `--pointer`.

No hace clicks, no escribe, no captura cámara, pantalla ni títulos de ventana,
y no guarda una intención. El evento es una observación que después debe
relacionarse con un delta nativo de estado.

## Reproducir

```powershell
python experiments/079-farmaxia-consented-input-semantic-bridge/run_experiment.py --duration 10 --sample-hz 8 --pointer
python experiments/079-farmaxia-consented-input-semantic-bridge/run_contract_test.py
python experiments/079-farmaxia-consented-input-semantic-bridge/run_kill_test.py
```

La ejecución de diez segundos permite trabajar normalmente mientras se registra
la actividad categorizada. `keyboard_activity` no significa “editar”: sólo dice
que hubo teclas. La intención queda UNKNOWN hasta que un adaptador nativo
observe el cambio correspondiente.
