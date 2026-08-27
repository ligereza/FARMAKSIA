# Experimento 081 — sandbox de ventana proxy reversible

## Pregunta

¿Existe una base técnica real para reinterpretar la gráfica de una ventana sin
modificar el código ni el contenido de la aplicación original?

## Hipótesis falsable

En un sandbox controlado, una ventana fuente puede capturarse mediante
`Windows.Graphics.Capture`, sus cuatro regiones visuales pueden permutarse en
una ventana proxy y un clic sobre una región reubicada puede regresar a la
coordenada de origen correcta.

La transformación se acepta sólo si cumple las tres condiciones:

```text
captura de píxeles actualizados tras un evento
        +
permutación visual verificable
        +
T⁻¹(T(p)) = p para las coordenadas interactivas
```

No captura una aplicación del usuario: el binario crea una fuente de 320 × 320
px con cuatro regiones de color y una proxy temporal. Tras verificar un clic
sintético dirigido a su propia fuente, ambas ventanas se cierran solas.

## Base adoptada

El camino de captura se deriva del ejemplo oficial MIT
`microsoft/Windows.UI.Composition-Win32-Samples`, commit
`ee50e2ea137dcef7b82ba504eff7435e5ebf5294`. Se adoptó después de compilarlo
localmente con Windows SDK 10.0.26100.0, Visual Studio 2022 y
`Microsoft.Windows.CppWinRT` 2.0.221121.5. Este experimento no incorpora su
binario ni sus paquetes: el script recupera la dependencia oficial bajo la
carpeta ignorada `native/packages/` cuando hace falta.

## Ejecutar la validación nativa

Desde la raíz del repositorio:

```powershell
powershell -ExecutionPolicy Bypass -File experiments/081-farmaxia-window-proxy-sandbox/run_native_validation.ps1
```

La ventana fuente y la proxy aparecen sin tomar foco durante menos de ocho
segundos. El resultado aceptado contiene:

```text
FARMAXIA_081_NATIVE={"status":"WINDOW_PROXY_SANDBOX_VERIFIED", ...}
```

## Qué queda deliberadamente fuera

- No se captura pantalla completa, cámaras, texto, títulos ni ventanas ajenas.
- No se inyecta input del sistema: el clic de prueba es un mensaje dirigido sólo
  a la ventana fuente creada por el mismo proceso.
- No mide latencia, comodidad, aprendizaje ni precisión perceptual humana.
- El reordenamiento sólo admite una biyección de regiones. Una transformación
  que duplique, oculte o fusione áreas no tiene inversa única y debe bloquearse.

La ruta GPU/DirectComposition de 058 queda como candidato de rendimiento. 081
comprueba primero la corrección espacial y la sincronía real de captura.

## Kill tests

1. Permutaciones no biyectivas se rechazan.
2. El round-trip de cada punto de prueba debe recuperar su coordenada original.
3. Un cambio de la fuente debe aparecer en su región proxy correspondiente.
4. Ningún HWND externo puede ser objetivo de captura o de input en este test.
5. Sin frame actualizado, el proceso expira como fallo en vez de declarar éxito.
