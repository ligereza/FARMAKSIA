# Carpeta de tratamiento audiovisual - version corregida

> **Current successor of:** [`11_revision_delta.md`](11_revision_delta.md). This is a local draft for adaptation, not a submitted attachment. See [`README.md`](README.md).

## 1. Identificacion y propuesta

**Titulo:** Dimensiones del Orden

**Linea sugerida:** Produccion de obras experimentales, Fondo Audiovisual 2027.

**Tipo de resultado:** obra audiovisual generativa en vivo acompañada de un documento de proceso.

La obra investiga la traduccion de una regla matematica de luz entre distintas arquitecturas de software, hardware y espacio. En la primera capa, una escena procedural de Blender distribuye haces sobre una estructura arquitectonica y los anima mediante angulo, fase, tiempo, oscilacion y pulso. En la segunda, un estado audiovisual comun se proyecta sobre superficies LED y luminarias controladas por distintos protocolos. La instalacion real se observa, se verifica y se convierte en un grafo espacial antes de la ejecucion. La obra no parte de la promesa de que las capas seran identicas: hace visible la diferencia entre una regla continua y sus salidas discretas, limitadas por capacidades, patch, actualizacion, latencia y respuesta del hardware.

## 2. Punto de vista artistico

La iluminacion escenica suele aparecer como resultado de una consola, un preset o una secuencia de decisiones manuales. Ademas, cada cambio de plataforma obliga al operador a reaprender nombres, menus y convenciones aunque la intencion audiovisual sea la misma. En esta obra la regla que organiza la luz ocupa el centro de la puesta en escena y se expresa mediante una capa comun de fase, ritmo, energia, densidad, direccion y topologia. El espacio no ilustra una historia externa: muestra como una serie de relaciones matematicas puede convertirse en arquitectura visual y como esa serie cambia al pasar por distintas interfaces, protocolos y dispositivos.

El titulo no alude a un orden unico. Alude a las dimensiones que permiten construir distintos ordenes defendibles: posicion angular, velocidad, fase, densidad, pulso, capacidad, distancia y respuesta temporal. Cambiar un parametro no es aplicar un filtro decorativo; es cambiar la forma en que el sistema organiza el espacio y el tiempo. Una consola no desaparece: se vuelve un destino posible de una regla mas general.

## 3. Materializacion de la obra

La capa simulada se construye en Blender 4.5.4 mediante Geometry Nodes y Cycles. El archivo de trabajo contiene trece arboles de Geometry Nodes. `Curve to Tube` tiene 617 nodos y convierte trayectorias en geometria tubular. El grupo de haces inspeccionado distribuye puntos sobre una malla, calcula un angulo con `atan2`, suma una oscilacion senoidal dependiente del tiempo y usa una fase modular para decidir intensidad y longitud del haz.

La serie de camara tiene un loop verificable: en Blender 4.5.4, `Camera.002` posee una unica curva animada, `rotation_euler[2]`, con keyframes en los frames 300 y 790. Los valores de esos keyframes difieren en `-2*pi`: la camara completa una rotacion de 360 grados y vuelve a la orientacion inicial. Por eso el rango completo son 491 frames a 30 FPS, equivalente a 16,366667 segundos, igual que el material audiovisual complementario entregado. El rango de render 620-790 que aparece guardado en una version del archivo es solo un segmento de ese loop y no se presenta como duracion total de la obra.

La capa fisica parte de un dispositivo BLE controlado por codigo local. `miracles_star_web.py` contiene 743 lineas en su estado actual y define comunicacion GATT, lectura de nivel de audio y control de color/pulso. Esa evidencia demuestra un antecedente de control de una luminaria; no demuestra todavia que cuatro o seis unidades esten sincronizadas ni que un patch desconocido pueda reconstruirse. La ampliacion a varias unidades, el mapping geometrico y la traduccion semantica constituyen el experimento financiado.

Las superficies LED no funcionan solamente como pantallas donde se reproduce una imagen. Reciben el mismo estado abstracto que las luminarias y lo interpretan como luminancia, color, densidad, desplazamiento y ritmo. Asi, una superficie LED, un haz y un pulso de audio pertenecen al mismo sistema aunque tengan resoluciones y capacidades distintas.

## 4. Layout, mapping y patch

Cada luminaria se representa como un nodo con posicion, identidad, perfil, capacidad y relacion con sus vecinas. El montaje puede usar una linea, un anillo, una malla, una espiral o una irregularidad controlada. La geometria no es un adorno posterior: determina como se propagan los efectos y como se construyen las secuencias.

El sistema distingue dos operaciones. `Mapping` relaciona una posicion observada con un nodo logico. `Patching` relaciona ese nodo y su perfil de fixture con un universo, direccion y conjunto de canales. La camara ayuda a resolver la primera; RDM puede ayudar con la identidad y configuracion de la segunda. Si RDM no esta disponible, una secuencia de prueba cambia una salida por vez, observa la respuesta y produce una propuesta de patch con evidencia y nivel de confianza.

Esta separacion responde a un problema concreto de los shows: un showfile o patchfile puede parecer correcto y aun asi controlar otra cosa, usar otro modo de fixture o ignorar una parte de la instalacion. La obra no oculta ese problema. Lo incorpora al preshow y lo convierte en una condicion de la composicion.

## 5. Preshow, soundcheck y liveshow

En el **preshow**, el sistema observa el montaje, compara las posiciones visibles con el patron geometrico esperado y genera un perfil de layout. El resultado puede incluir discrepancias, fuentes no identificadas o capacidades desconocidas.

En el **soundcheck**, ejecuta pruebas controladas de identidad, intensidad, color, movimiento, direccion y latencia. Tambien verifica la relacion entre el perfil de fixture, el canal y la respuesta visible. Las pruebas pueden terminar en `correspondent`, `degraded` o `divergent`.

En el **liveshow**, el layout validado se congela como una partitura espacial. El operador trabaja con relaciones de ritmo, energia, fase y distancia. El adaptador traduce esas relaciones a la consola o protocolo disponible, y registra cualquier capacidad que no pueda expresarse. No se pretende que todas las consolas sean iguales; se pretende que una misma intencion pueda ser traducida sin esconder la perdida.

## 6. Pregunta y metodo

La pregunta es: ¿puede una representacion matematica comun conservar la intencion espacial y temporal de una obra cuando pasa entre distintas consolas, protocolos, luminarias y superficies LED con capacidades y latencias diferentes?

La respuesta se buscara mediante comparacion controlada. Primero se congela un archivo de parametros y se renderiza la referencia. Luego se reconstruye el layout con una plantilla geometrica y una secuencia de identificacion. Despues se verifica un dispositivo, se prueba el conjunto de unidades y se ejecuta el mismo estado sobre los backends disponibles. Finalmente se introducen perturbaciones conocidas de frecuencia, retraso, capacidad, patch incorrecto y perdida de actualizacion.

Se comparara una tarea audiovisual expresada por el flujo nativo y por la capa comun. El objetivo no es declarar que una interfaz es universalmente mejor, sino observar si se conserva la intencion espacial, cuanto cuesta recuperar un error y que partes de la expresion se pierden en cada backend.

## 7. Imagen, sonido y montaje

La imagen trabaja con una arquitectura oscura y envolvente: cupula, malla, tubos luminosos, superficies LED utilizadas como campos de luz, haces direccionales, vapor y cambios de color. La camara virtual recorre el espacio mediante el loop de rotacion ya verificado; su movimiento sirve para revelar la estructura, no para reemplazarla con cortes rapidos.

El sonido se trata como una entrada del sistema. Se utilizara una pista electronica o ambiental controlada, con segmentos de nivel sostenido, transitorios y silencio. El audio modifica fase, energia, densidad, transicion y velocidad, pero no queda reducido a un detector de golpes. La relacion sonido-luz se registrara como dato del experimento y como experiencia de montaje.

El montaje puede alternar referencia simulada, superficie LED, luminarias y registros de verificacion. La edicion no ocultara las pruebas fallidas ni transformara un resultado tecnico en una afirmacion causal sobre la percepcion humana.

## 8. Plan de trabajo

Durante la primera etapa se consolidara la regla, la escena de referencia, el inventario de dispositivos y el contrato semantico comun. Durante la segunda se probara una unidad, se reconstruira un layout geometrico y se estimaran frecuencia de actualizacion, latencia, estabilidad y capacidad. Durante la tercera se ampliara el conjunto fisico, se verificara el patch y se ejecutaran repeticiones con parametros fijos y perturbaciones controladas. Durante la cuarta se comparara una tarea audiovisual expresada por el flujo nativo y por la capa comun. Durante la quinta se producira la obra audiovisual en vivo, su registro y el documento de proceso. Un render de referencia puede integrarse como material de apoyo, pero no reemplaza el resultado vivo. La ultima etapa corresponde a montaje, exhibicion, archivo de versiones y cierre.

## 9. Riesgos asumidos

El protocolo BLE puede introducir retrasos o perdida de comandos. RDM puede no estar disponible. Un patchfile puede describir una configuracion distinta de la instalacion real. Las unidades pueden no compartir un reloj suficientemente estable. Un numero pequeño de fuentes puede no sostener la misma lectura espacial que una distribucion densa. Una consola puede no tener la capacidad necesaria para expresar un estado. La pista sonora puede dominar la lectura visual o producir una sincronizacion aparente que no coincide con los tiempos registrados. Estos riesgos no se esconden: se convierten en variables, criterios de medicion y decisiones de montaje.

## 10. Entregables

- Obra audiovisual generativa presentada en vivo.
- Registro de la ejecucion fisica y de su contraparte procedural.
- Documento de proceso experimental con hipotesis, versiones, parametros, mediciones, resultados y fallas.
- Archivo tecnico reproducible con escena, formulas, configuracion y logs seleccionados.
- Perfil de layout y mapping con posiciones, identidades, capacidades, correspondencias y estado de verificacion.
- Prototipo de traduccion semantica documentado para los backends efectivamente disponibles durante la ejecucion.
