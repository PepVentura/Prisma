# 05 — Audio
## DMA105-4
4", 4 Ω, 35 W RMS. Transductor principal propuesto. Montado en el frontal inferior vertical (bafle), centrado a z ≈ 57 mm.

## DMA105-PR
4", radiador pasivo propuesto. Montado en la trasera inferior, coaxial con el DMA105-4 (D018). La trasera inferior queda libre: sin puertos, rejillas ni ventilador delante del radiador.

## Cámara acústica (D008, D016)
Forma en L:
- bloque inferior: ancho y fondo completos, de z = 3 a z = 111 mm;
- bloque superior-trasero: desde y = 64 mm hasta la trasera, de z = 111 a z = 170 mm, detrás de la pantalla.

Volumen medido sobre el modelo v0.3 (`tools/comprobar_volumetrico.py`):

| Concepto | Litros |
|---|---:|
| Aire interior descontando DMA105-4 y DMA105-PR | 3,40 |
| Reserva para refuerzos, espuma y cableado | −0,10 |
| **Volumen neto estimado** | **≈ 3,30** |

Dentro del objetivo de 3–4 L. El desplazamiento de los transductores se modela como troncos de cono conservadores; conviene sustituirlo por las cotas reales de Dayton cuando se confirmen.

Solo con un bloque inferior (como en v0.2) la cámara se quedaba en ≈ 2,5 L netos. El bloque superior-trasero es lo que permite llegar al objetivo sin cambiar la envolvente.

## Pendiente
- Simular DMA105-4 + DMA105-PR en ≈ 3,3 L (WinISD o similar) y decidir si el PR necesita masa añadida.
- Refuerzos internos y posición de la espuma.
- Paso estanco de cables del altavoz (pasamuros sellado en la tapa de la cámara).

La cámara acústica debe quedar aislada del compartimento electrónico.
