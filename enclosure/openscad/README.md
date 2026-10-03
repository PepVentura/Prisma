# OpenSCAD v0.5
Abrir `prisma_volumetrica_v0_5.scad`. Todas las cotas están en `parametros.scad`.

Es un modelo de distribución. No es todavía la carcasa final.

## Interruptores útiles (en `parametros.scad` o con `-D`)
| Variable | Efecto |
|---|---|
| `section_x = true` | Corte por el plano medio: vista lateral interior |
| `show_chamber_air = true` | Muestra el aire neto de la cámara acústica |
| `show_shell`, `show_screen`, `show_audio`, `show_electronics` | Mostrar u ocultar grupos |

## Comprobación
```bash
pip install trimesh numpy manifold3d
python3 tools/comprobar_volumetrico.py
```
Da el volumen neto de la cámara y avisa de cualquier interferencia, o de un componente que se salga de la envolvente. Conviene lanzarlo después de cambiar cualquier cota.

## Próxima revisión
- geometría real de la pantalla (medir la unidad);
- cotas reales de DMA105-4 / DMA105-PR (recorte, marco, fondo);
- paredes, refuerzos y junta de la cámara acústica;
- división en piezas imprimibles y fijaciones;
- rejillas de ventilación reales.

`capucha.scad` es la capucha imprimible (ver `docs/14_capucha.md`); `tools/comprobar_capucha.py` la comprueba.

`marco_pantalla_prueba.scad` es el marco de prueba de la pantalla (ver `docs/06_pantalla.md`).

`archivo/` contiene versiones anteriores: v0.2 y `v0_4/` (diseño con estrías y frontal partido).
