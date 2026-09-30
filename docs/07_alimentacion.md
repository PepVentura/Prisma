# 07 — Alimentación
Fuente AC/DC externa de 24 V (D003). **No hay fuente de red dentro de Prisma.**

Dentro de Prisma:
- conector DC 24 V de panel en la trasera, a la altura de la bahía de electrónica (D019);
- KABD-250 alimentado a 24 V;
- buck 24→5 V sobre el soporte encima del KABD-250;
- distribución de 5 V a Pi, pantalla y periféricos.

La potencia/corriente definitiva se calculará antes de comprar fuente y buck. Recordatorio: la Pi 5 pide 5 V / 5 A para dar corriente completa a los USB, así que el buck debe ir sobrado.
