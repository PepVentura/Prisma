# Changelog
## v0.3
- Nuevo perfil lateral: frontal inferior vertical + frontal superior inclinado 18° para la pantalla (D015).
- Cámara acústica en L: ≈3,3 L netos medidos sobre el modelo. Con el esquema de v0.2 se quedaba en ≈2,5 L (D016).
- Electrónica en bahía superior. Ventilación pasiva solo en esa zona, sin ventilador junto a la cámara (D017).
- DMA105-PR en la trasera inferior, sin puertos ni rejillas delante (D018).
- Sin fuente interna: entrada DC 24 V de panel (D003, D019).
- Micrófonos y cámara opcional en el techo, zona delantera (D020).
- Pantalla modelada con medidas de la unidad real: cristal, pestañas, taladros, área visible descentrada y conectores en el canto derecho.
- Laterales rectos y 15 mm libres para las clavijas acodadas de la pantalla (D021).
- Bahía reorganizada: Pi 5 en orientación normal con huecos de 20 mm para clavijas; KABD-250 en una balda superior.
- Script `tools/comprobar_volumetrico.py`: volumen de la cámara + interferencias.
- Vistas en `docs/img/`.
- Corregido: en v0.2 el altavoz y el radiador se rotaban dos veces y quedaban fuera de la caja.
- Limpieza: quitados archivos del proyecto Steam Machine que se colaron (`00_parametros.scad`, `GUIA_INICIO.md`); `.gitignore` y `VERSION.md` reescritos para Prisma; LICENSE con titular; `hardware/BOM.csv` convertido a CSV real.
- v0.2 archivada en `enclosure/openscad/archivo/`.

## v0.2
- Raspberry Pi 5 8 GB.
- Waveshare 7" como referencia física principal.
- Envolvente inicial 205×250×145 mm.
- Cámara acústica separada de electrónica.
- Alimentación externa 24 V.
- DMA105-4 + DMA105-PR como arquitectura acústica propuesta.
- KABD-250 como amplificador propuesto.
- Estructura inicial de GitHub.

## v0.1
- Primera maqueta volumétrica.
