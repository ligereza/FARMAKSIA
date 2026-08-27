# Resultados — experimento 081

## Ejecución nativa local

El binario se compiló y ejecutó en Windows usando:

- Windows SDK 10.0.26100.0;
- Visual Studio 2022 Community, MSVC v143;
- `Microsoft.Windows.CppWinRT` 2.0.221121.5;
- captura `Windows.Graphics.Capture` de Microsoft;
- dispositivo D3D11 hardware, con fallback WARP sólo si el hardware no está
  disponible.

Salida observada:

```text
FARMAXIA_081_NATIVE={"status":"WINDOW_PROXY_SANDBOX_VERIFIED","reason":"capture_transform_inverse_mapping","source_frames":2,"post_route_frames":1,"external_window_capture":false,"system_input_injected":false,"screen_capture":false}
```

La evidencia es más específica que una compilación: llegó un primer frame de la
ventana fuente; después un clic dirigido a la ventana proxy fue traducido al
cuadrante original; la fuente cambió; llegó un segundo frame; y los cuatro
cuadrantes del proxy coincidieron con la permutación declarada.

## Qué queda demostrado

La hipótesis es válida en su forma acotada:

```text
ventana propia → captura real → reordenamiento de regiones → input inverso
```

Esto justifica un renderer proxy como base técnica. No justifica todavía un
reordenador semántico universal. La prueba no sabe qué significa un botón,
texto, video o canvas; sólo sabe conservar una transformación espacial
declarada.

## Falsaciones y límites

- La captura estática no produce frames continuamente; el test tuvo que esperar
  un cambio real. Esto reduce trabajo y GPU, y debe formar parte del runtime.
- El click fue un mensaje interno al sandbox, no input inyectado en otra
  aplicación. La ruta entre procesos sigue pendiente.
- Una permutación no biyectiva no tiene inversa única y el contrato la rechaza.
- No se usaron ventanas del usuario, pantalla completa, cámara, texto ni red.
- No hay evidencia humana de comodidad, aprendizaje o utilidad sensorial.

## Decisión

La arquitectura pasa de ser una hipótesis abstracta a una base experimental
real. El siguiente trabajo no será conectar dos aplicaciones directamente:
será reemplazar el transformador de cuatro regiones por una escena visual
declarativa, usando UI Automation/OCR sólo como fuentes opcionales de regiones
y manteniendo un modo preview sin interceptar input.
