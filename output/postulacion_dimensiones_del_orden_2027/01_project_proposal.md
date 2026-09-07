# Dimensiones del Orden

## Resumen del proyecto

`Dimensiones del Orden` es una obra audiovisual experimental en vivo que investiga si una misma logica matematica puede atravesar distintas arquitecturas de iluminacion, video y control sin depender de una marca, consola o showfile particular.

La obra no trata la luz como una coleccion de presets. Construye un campo de estados basado en fase, ritmo, energia, densidad, direccion, distancia y relaciones espaciales. Ese campo puede expresarse en una escena procedural de Blender, en superficies LED y en luminarias controladas por DMX, Art-Net, OSC o protocolos equivalentes.

El sistema incorpora una capa intermedia: no obliga al operador a aprender nuevamente cada interfaz para expresar una misma decision. El operador trabaja con relaciones audiovisuales comunes y un adaptador traduce esas relaciones al sistema disponible. La instalacion fisica, sus posiciones, sus capacidades y sus errores se convierten en parte del modelo espacial de la obra.

## Problema artistico y tecnico

La iluminacion y el video en vivo suelen esconder su logica dentro de interfaces especializadas. Cambiar de Avolites a grandMA, Resolume, TouchDesigner o una consola generica implica reaprender nombres, menus, canales, modos y convenciones, incluso cuando la intencion del operador es la misma: aumentar la tension, abrir el espacio, propagar un pulso, concentrar la atencion o desplazar una secuencia.

Esta obra pregunta que ocurre cuando esas intenciones se expresan primero como relaciones matematicas y luego se traducen al hardware disponible. El problema no se resuelve fingiendo que todas las consolas son iguales. Se construye una representacion comun, se declara que capacidades conserva cada sistema y se hace visible lo que se pierde durante la traduccion.

## Motor de la obra

El motor mantiene un estado audiovisual abstracto. Una formulacion inicial es:

`S(t) = {phase, tempo, energy, density, direction, topology, palette, transition}`

La posicion de cada fuente se representa como un nodo de un grafo espacial. Las relaciones entre nodos permiten generar recorridos, diagonales, ondas, abanicos, simetrias rotas y propagaciones por distancia. El audio modifica el estado temporal; no se limita a activar un efecto prefabricado.

La misma representacion se proyecta en varias superficies:

- Geometry Nodes y Cycles para la referencia procedural.
- TouchDesigner para la ejecucion audiovisual en tiempo real.
- Superficies LED como campos luminosos y no solamente como pantallas narrativas.
- Luminarias y moving heads mediante DMX, Art-Net, OSC u otros adaptadores.

La obra no afirma que estas salidas sean identicas. Hace visible como una regla continua se vuelve discreta, limitada y situada cuando entra en un sistema concreto.

## Instalacion como variable

El layout no es una decoracion posterior. Cada luminaria tiene una posicion, una identidad, una capacidad y una relacion con sus vecinas. El sistema puede partir de una linea, un anillo, una malla, una espiral o un patron irregular controlado. La geometria elegida determina como se propaga el estado audiovisual.

Durante el preshow, una camara y una secuencia de identificacion permiten reconstruir las posiciones visibles. Cuando existe RDM, el sistema puede aprovechar la identificacion bidireccional del dispositivo. Cuando no existe, XIO realiza una prueba activa: cambia una salida temporalmente, observa la respuesta y propone la correspondencia entre posicion, fixture y canal. El resultado es una propuesta de mapping y patch, no una suposicion silenciosa.

## Tres momentos de la obra

En el **preshow**, el espacio se observa y se convierte en un grafo: se detectan las fuentes, se comparan con el patron geometrico y se registran sus capacidades.

En el **soundcheck**, el sistema comprueba identidad, intensidad, color, movimiento, direccion, latencia y respuesta. Las diferencias entre el showfile y la instalacion se vuelven parte visible del proceso.

En el **liveshow**, el layout validado se congela como una partitura espacial. El operador no necesita repetir la configuracion especifica de cada consola para producir una secuencia; trabaja con relaciones de ritmo, energia, fase y distancia, mientras el adaptador traduce al sistema disponible.

## Pregunta experimental

¿Puede una representacion matematica comun conservar la intencion espacial y temporal de una obra cuando se traduce entre distintas consolas, protocolos, luminarias y superficies LED, y puede el proceso de reconocimiento y verificacion del montaje convertirse en parte de la experiencia audiovisual?

## Hipotesis de trabajo

Una representacion comun conservara mejor la estructura de una secuencia cuando el sistema conoce el layout, las capacidades reales de cada dispositivo y las limitaciones del protocolo. Cuando falten capacidades o aparezcan errores de patch, la traduccion producira una desviacion medible. Esa desviacion no se eliminara automaticamente: puede convertirse en una nueva forma visual o exigir una decision del operador.

## Resultados

- Una obra audiovisual generativa presentada en vivo.
- Una instalacion de luminarias y superficies LED organizada por un modelo espacial explicito.
- Un prototipo de mapping, verificacion y traduccion semantica para una configuracion controlada.
- Un documento de proceso con reglas, layout, pruebas, errores, capacidades y decisiones.
- Un registro audiovisual que muestre la relacion entre sonido, superficie LED, luminarias y espacio.
- Un archivo tecnico reproducible con parametros, perfiles de fixture, logs y adaptadores seleccionados.

## Alcance y limites

El proyecto no promete reemplazar grandMA, Avolites ni otra consola profesional, ni soportar de inmediato cualquier showfile o fixture. El resultado financiado sera una demostracion controlada de la capa comun y sus adaptadores, no un producto universal terminado.

La evidencia actual incluye una escena procedural de Blender, una implementacion de control de una luminaria BLE y el protocolo para comparar referencia y ejecucion fisica. La instalacion multi-dispositivo, la reconstruccion de layout, la traduccion entre protocolos y las pruebas de recuperacion de errores constituyen el desarrollo experimental financiado.
