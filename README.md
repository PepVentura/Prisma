# Prisma
Asistente inteligente de sobremesa con Raspberry Pi 5, pantalla táctil de 7", avatar 3D y audio integrado.

**Estado actual: volumétrico v0.3.** Las cotas provisionales deben verificarse antes de fabricar piezas definitivas.

![Prisma v0.4](docs/img/prisma_v0_4_frontal.png)

## Hardware
- Raspberry Pi 5 8 GB — confirmado
- Waveshare 7inch HDMI LCD (C), 1024×600 — recibido
- Dayton DMA105-4 — propuesto
- Dayton DMA105-PR — propuesto
- Dayton KABD-250 — propuesto
- DAC GY-PCM5102 (PCM5102A, I²S) — propuesto
- ReSpeaker Lite USB (2 micrófonos con AEC) — propuesto
- WS2812B, 8–12 LEDs — propuesto
- Cámara OV5647 5 MP, sobre la pantalla — disponible
- Fuente Mean Well GST60A24-P1J (24 V, 60 W) — propuesta
- Conversor Pololu D36V50F5 (24→5 V, 5,5 A) — propuesto

## Arquitectura
```text
Pantalla → Raspberry Pi 5 → DAC → KABD-250 → DMA105-4
                 │
                 ├── micrófonos
                 ├── LEDs
                 └── cámara opcional
```

## Distribución (v0.3)
```text
              techo: micrófonos (ReSpeaker Lite)
           ┌───────────────────────────┐
          ╱   bahía: Pi 5 · KABD · DAC │ ← rejilla + DC 24 V
 pantalla╱      ┌──────────────────────┤
   18°  ╱ canal │ cámara (parte alta)  │
       ╱ cables │                      │
 LEDs ├─────────┘                      │
      │                                │
 DMA105-4 ◄  cámara acústica ≈3,3 L  ►  DMA105-PR
      └────────────────────────────────┘
   frente                            trasera
```

- La electrónica queda separada de la cámara acústica, que es estanca.
- La fuente AC/DC es externa: dentro solo entra 24 V.

## CAD
`enclosure/openscad/prisma_volumetrica_v0_3.scad` es una maqueta de distribución, no la carcasa final.

`tools/comprobar_volumetrico.py` mide el volumen neto de la cámara y comprueba interferencias entre componentes.

Piezas imprimibles: la capucha (`enclosure/openscad/capucha.scad`, ver `docs/14_capucha.md`) y la cubeta acústica (`enclosure/openscad/cubeta.scad`, ver `docs/15_cubeta.md`).

`tools/simulacion_audio.py` simula la respuesta en graves del altavoz y el radiador en la cámara (ver `docs/05_audio.md`).

Consulta `docs/DECISIONS.md`, `docs/08_distribucion.md` y `docs/BOM.md`.
