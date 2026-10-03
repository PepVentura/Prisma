# 09 — Carcasa
Orden de desarrollo:
1. volumétrico — **v0.3 hecho** (perfil, zonas, cámara en L, comprobación de interferencias);
2. marco de pantalla — siguiente paso: medir la Waveshare real (espesor, pestañas, conectores);
3. cámara acústica — paredes, refuerzos, junta y pasamuros;
4. estructura interna;
5. piel exterior;
6. fijaciones;
7. ventilación;
8. detalles estéticos;
9. STL de producción.

## Requisitos del frontal definitivo
- Guía en cola de milano y tapa deslizante de la cámara (D026), según `tapa_camara_prueba.scad`.

## División en piezas
Ver `docs/14_capucha.md` (D027). La capucha v0.1 ya está diseñada; faltan la cubeta, la bandeja y la caja superior.

## Notas para la división en piezas (impresión)
- La altura de 262 mm y el frontal inclinado hacen pensar en varias piezas: cámara acústica (pieza estanca propia), bahía superior con tapa desmontable y marco frontal de la pantalla.
- La tapa de la bahía da acceso de servicio a la Pi y al resto de la electrónica sin abrir la cámara.
