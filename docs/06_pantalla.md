# 06 — Pantalla
Modelo: Waveshare 7inch HDMI LCD (C) Rev4.1, 1024×600, IPS, táctil capacitivo (USB).

**Orientación: horizontal (apaisada)**, para ver vídeo (YouTube, etc.) a pantalla completa. Es la orientación nativa del panel, así que no hace falta rotar nada en el sistema.

1024×600 es un formato ≈ 17:10. Un vídeo 16:9 ocupa todo el ancho y deja dos franjas negras finas, de unos 12 píxeles, arriba y abajo.

![Frontal v0.3](img/v0_3_frontal_pantalla.png)

## Medidas (sacadas de fotos de la unidad real, ±1–2 mm)
Pendientes de confirmar con calibre antes de diseñar el marco.

| Cota | Valor | Nota |
|---|---:|---|
| Ancho del cristal | 164,9 mm | es el elemento más ancho |
| Alto del cristal | ≈ 98,6 mm | |
| Alto total con pestañas | ≈ 119 mm | la hoja de datos da 124,27: medir |
| Área visible | 154,2 × 85,9 mm | |
| Margen cristal → área visible | izq. ≈ 3,6 · der. ≈ 7,1 · sup. ≈ 4,5 · inf. ≈ 8,2 mm | el área visible no está centrada |
| Cristal → cara trasera del PCB | ≈ 9,5 mm | |
| Conectores detrás del PCB | ≈ 7 mm (HDMI) | |
| Taladros de fijación | 4, en pestañas, ≈ 151 × 113 mm entre centros | medir |

## Conectores
Mirando la pantalla de frente, con el flex del LCD abajo:
- todos en el **canto derecho**, en la mitad superior;
- de arriba abajo: HDMI (≈ 13–30 mm desde el borde superior de las pestañas), micro-USB del táctil (≈ 37–43 mm) e interruptor de retroiluminación (≈ 49–58 mm);
- las clavijas entran de lado (en horizontal), no por detrás.

Por eso hacen falta **clavijas acodadas** (D021):
- HDMI: cable plano HDMI-A → micro-HDMI con cabezales a 90°, o un adaptador HDMI a 90° + cable;
- táctil: cable micro-USB acodado → USB-A.

El modelo reserva 15 mm libres a la derecha del cristal. Por eso los laterales de la carcasa ya no se estrechan.

El interruptor de retroiluminación queda accesible solo con la carcasa abierta. Déjalo en ON.
