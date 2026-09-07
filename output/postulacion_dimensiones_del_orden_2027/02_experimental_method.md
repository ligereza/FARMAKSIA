# Metodo experimental

## 1. Regla de referencia y estado semantico

Para el indice `i` de un dispositivo o haz, con posicion angular `theta_i`, la fase de referencia es:

`phase_i(t) = frac((theta_i * sequence_spread + t * sequence_speed + wing_amount * sin(theta_i + t * wing_speed)) / (2 * pi))`

El estado de pulso es:

`pulse_i(t) = 1 when phase_i(t) < pulse_width, otherwise 0`

La longitud y la intensidad del haz se derivan del estado de pulso. En la capa fisica, el controlador no transmite una senal continua ideal. Envia comandos a intervalos finitos y recibe respuestas del dispositivo con un retraso variable:

`phase_real_i(t) = sample(phase_i(t - delay_i), update_interval, packet_state_i)`

El experimento compara la regla de referencia con su realizacion muestreada. Las formulas describen de forma compacta la logica existente en Geometry Nodes; no afirman que el hardware ya implemente todo el sistema.

La regla se expone mediante un estado intermedio pequeno, en vez de un vocabulario especifico de consola:

`S(t) = {phase, tempo, energy, density, direction, topology, palette, transition}`

Un adaptador traduce este estado a los canales y capacidades disponibles en cada sistema objetivo. Toda capacidad ausente debe registrarse como `unsupported` o `degraded`; no debe representarse silenciosamente como si fuera equivalente.

## 2. Layout espacial y mapping activo

Cada fuente se representa como un nodo `v_i = (x_i, y_i, z_i, fixture_type_i, capability_i)`. Las aristas describen adyacencia o distancia fisica. La instalacion esperada es una plantilla geometrica; la instalacion observada es un conjunto de detecciones de imagen y respuestas de dispositivos.

La etapa de mapping estima la transformacion entre la geometria esperada y la observada, y luego resuelve la asignacion entre nodos mediante posicion, distancia y consistencia vecinal. Un layout plano puede usar una homografia; un layout no plano requiere profundidad conocida o un modelo 3D calibrado. La camara por si sola no revela una direccion DMX.

Cuando RDM esta disponible, el sistema puede leer identidad y configuracion del dispositivo mediante una ruta bidireccional de gestion DMX. Cuando no esta disponible, ejecuta una prueba activa: cambia una salida por vez, la camara observa la respuesta visible y el resultado se convierte en una propuesta de patch con confianza y evidencia.

`mapping` significa relacionar posicion fisica con nodo logico. `patching` significa relacionar nodo logico y perfil de fixture con direccion de protocolo y layout de canales. Mantenerlos separados evita confundir una posicion visualmente correcta con una configuracion DMX verificada.

## 3. Variables independientes

- `sequence_speed`: velocidad de progresion de la fase.
- `sequence_spread`: separacion angular del campo de fase.
- `wing_speed` y `wing_amount`: oscilacion de la direccion del haz.
- `pulse_width`: duracion del pulso visible dentro de un ciclo.
- `device_count`: un dispositivo frente al rig multi-dispositivo planificado.
- `update_interval`: periodo de actualizacion del controlador.
- `network_condition`: comunicacion BLE estable, retrasada o interrumpida.
- `audio_input`: pista controlada, silencio, nivel sostenido y nivel transitorio.
- `layout_pattern`: layout uniforme, geometrico o intencionalmente irregular.
- `target_backend`: BLE, DMX, Art-Net, OSC o adaptador simulado.
- `fixture_capability`: dimmer, color, pan, tilt, strobe y capacidades no soportadas.
- `mapping_condition`: patch conocido, patch incorrecto o remapeo activo.

## 4. Mediciones

Cada corrida recibe un `run_id` estable, una captura de parametros, una version de software, una lista de hardware, una marca temporal monotonicamente creciente y una referencia de video o log. Se mide por separado lo siguiente:

- `command_latency_ms`: tiempo entre el comando del controlador y el reconocimiento del dispositivo cuando el protocolo lo expone.
- `visual_onset_ms`: inicio de un pulso medido por frames en el video fisico registrado.
- `order_accuracy`: proporcion de eventos anotados en que el orden fisico coincide con el esperado.
- `phase_error`: diferencia circular entre la fase esperada y la fase medida del evento.
- `drop_rate`: comandos que no fueron reconocidos o no resultaron visibles en el registro.
- `repeatability`: diferencia entre corridas repetidas con los mismos parametros.
- `mapping_accuracy`: proporcion de fuentes observadas asignadas al nodo logico correcto.
- `patch_recovery_time_ms`: tiempo necesario para identificar y corregir un error de patch controlado.
- `semantic_translation_loss`: dimensiones del estado solicitado que el backend objetivo no puede expresar.
- `operator_task_time_ms`: tiempo necesario para reproducir una intencion espacial definida con el flujo nativo y con la capa semantica.
- `safe_state_rate`: proporcion de corridas fallidas o incompletas que terminan en un estado de salida no destructivo.

## 5. Secuencia de prueba

Primero, la escena de Blender se renderiza con un archivo de parametros congelado. En Blender 4.5.4, `Camera.002` tiene una curva animada `rotation_euler[2]` cuyos keyframes de los frames 300 y 790 difieren en `-2*pi`; esto corresponde a una rotacion completa de camara de 360 grados. El loop completo es, por tanto, de los frames 300-790 a 30 FPS, coincidente con el MP4 complementario de 491 frames y 16.366667 segundos. El rango guardado de render 620-790 se trata solo como un segmento parcial.

Segundo, un dispositivo fisico recibe una version reducida de la misma regla de fase. Esto aisla el protocolo y el tiempo antes de agregar complejidad espacial.

Tercero, la instalacion se dispone segun una plantilla geometrica conocida. La camara estima las posiciones visibles y el sistema registra una propuesta de layout. Se usa descubrimiento RDM cuando es compatible; de lo contrario, una prueba optica activa asocia cada respuesta de salida con una fuente visible. La evidencia de mapping y la evidencia de patch se almacenan por separado.

Cuarto, la configuracion multi-dispositivo se prueba con parametros identicos e identidades explicitas. Cada corrida se repite con la misma semilla y luego con un cambio controlado de velocidad, ancho de pulso, layout o capacidad del backend.

Quinto, el controlador introduce una perturbacion temporal conocida: un retraso fijo, un jitter acotado, una direccion incorrecta, un atributo no soportado o una actualizacion perdida. El objetivo no es ocultar la falla, sino observar la transicion desde la correspondencia hacia la degradacion o la divergencia.

Sexto, una intencion espacial se expresa mediante el flujo de control nativo y mediante el estado semantico comun. La comparacion registra tiempo, errores de mapping, dimensiones no soportadas y la desviacion visual resultante. Una interaccion mas corta no se considera automaticamente mejor; conservar la relacion espacial intencionada es la condicion principal.

Septimo, la instalacion fisica se registra con el mismo conjunto de parametros usado para el render de referencia. La obra final puede presentar la correspondencia, la desviacion o ambas, segun lo que produzca el experimento.

## 6. Reglas de decision fijadas antes de la prueba

La corrida se clasifica como `correspondent` cuando el orden esperado se conserva en los eventos anotados, el mapping queda dentro de la tolerancia geometrica declarada y el retraso medido permanece bajo la mitad del intervalo de pulso activo. Se clasifica como `degraded` cuando el estado semantico es expresable solo en parte, el patch es recuperable o el orden se conserva con una perdida medible. Se clasifica como `divergent` cuando cambia el orden, desaparecen eventos de pulso, el mapping se vuelve ambiguo o el tiempo cruza el limite declarado.

La tolerancia numerica exacta se almacena con cada corrida porque depende del ancho de pulso seleccionado, la tasa de actualizacion y la escala del layout. No se importa un unico umbral de percepcion humana como si fuera un limite universal de ingenieria.

## 7. Plan de analisis

Para cada corrida, el analisis mantiene separados el tiempo tecnico, el mapping y la interpretacion visual. Si `t_ref_i` es el tiempo esperado del evento y `t_real_i` es el primer evento visible en el registro fisico, la desviacion de onset es `delta_t_i = t_real_i - t_ref_i`. Para la fase circular, el error se calcula como `angle(exp(1j * (phase_real_i - phase_ref_i)))`, de modo que una fase cercana al limite del ciclo no se trate como un error lineal grande.

El informe de cada condicion contiene la mediana y el percentil 95 de la desviacion absoluta de onset, la mediana y el percentil 95 del error de fase circular, exactitud de orden, exactitud de mapping, tiempo de recuperacion del patch, perdida de traduccion semantica, tasa de perdida y repetibilidad. El orden espacial se resume por separado del tiempo mediante la proporcion de eventos anotados que conservan el orden esperado de los dispositivos. Cuando hay corridas repetidas, la incertidumbre se estima remuestreando corridas completas y no frames de video correlacionados.

La comparacion es pareada: se usa el mismo conjunto congelado de parametros para la referencia simulada y la condicion fisica. La comparacion principal no afirma superioridad perceptual humana; pregunta si el sistema muestreado conserva el orden de eventos de la regla dentro de la tolerancia predeclarada. Una segunda comparacion pregunta si la capa semantica reduce el costo de reconfiguracion sin aumentar salidas inseguras o no soportadas. Las observaciones secundarias describen cuando la divergencia se vuelve visualmente legible en el material registrado.

## 8. Base cientifica

La investigacion sobre sincronia audiovisual muestra que la simultaneidad se juzga dentro de una ventana temporal y que los resultados dependen fuertemente del metodo experimental y del muestreo temporal. Esto respalda medir el tiempo en vez de asumir que un comando sincronizado produce una percepcion sincronizada. La investigacion sobre multiples elementos visuales tambien muestra que agregar elementos simultaneos puede cambiar el rendimiento de discriminacion. Estos hallazgos motivan el diseno pareado referencia/fisico y las condiciones explicitas de cantidad de dispositivos y tiempo.

La afirmacion cientifica es deliberadamente acotada: este proyecto prueba la reproducibilidad y traduccion de una regla computacional bajo un sistema material controlado. No generaliza desde una instalacion pequena hacia la vision humana en su conjunto.
