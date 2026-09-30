# Prisma
Asistente inteligente de sobremesa con Raspberry Pi 5, pantalla táctil de 7", avatar 3D y audio integrado.

**Estado actual: hardware y volumétrico v0.2.** Las cotas provisionales deben verificarse antes de fabricar piezas definitivas.

## Hardware
- Raspberry Pi 5 8 GB — confirmado
- Waveshare 7inch HDMI LCD (C), 1024×600 — recibido
- Dayton DMA105-4 — propuesto
- Dayton DMA105-PR — propuesto
- Dayton KABD-250 — propuesto
- DAC I²S→analógico — pendiente
- Matriz de 2–4 micrófonos — pendiente
- WS2812B, 8–12 LEDs — propuesto
- Cámara — opcional
- Fuente externa 24 V — pendiente
- Buck 24→5 V — pendiente

## Arquitectura
```text
Pantalla → Raspberry Pi 5 → DAC → KABD-250 → DMA105-4
                 │
                 ├── micrófonos
                 ├── LEDs
                 └── cámara opcional
```

La electrónica queda separada de la cámara acústica. La fuente AC/DC será externa.

## CAD
`enclosure/openscad/` contiene el volumétrico v0.2. Es una maqueta de distribución, no la carcasa final.

Consulta `docs/DECISIONS.md` y `docs/BOM.md`.
