# OpenSCAD v0.3
Abrir `prisma_volumetrica_v0_3.scad`. Todas las cotas están en `parametros.scad`.

Es un modelo de distribución. No es todavía la carcasa final.

## Interruptores útiles (en `parametros.scad` o con `-D`)
| Variable | Efecto |
|---|---|
| `section_x = true` | Corte por el plano medio: vista lateral interior |
| `show_chamber_air = true` | Muestra el aire neto de la cámara acústica |
| `show_shell`, `show_screen`, `show_audio`, `show_electronics` | Mostrar u ocultar grupos |

## Comprobación
```bash
pip install trimesh numpy
python3 tools/comprobar_volumetrico.py
```
Da el volumen neto de la cámara y avisa de cualquier interferencia, o de un componente que se salga de la envolvente. Conviene lanzarlo después de cambiar cualquier cota.

## Próxima revisión
- geometría real de la pantalla (medir la unidad);
- cotas reales de DMA105-4 / DMA105-PR (recorte, marco, fondo);
- paredes, refuerzos y junta de la cámara acústica;
- división en piezas imprimibles y fijaciones;
- rejillas de ventilación reales.

`archivo/` contiene la v0.2 tal cual estaba, como referencia.
