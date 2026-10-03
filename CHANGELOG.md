# Changelog
## v0.5.1
- Franjas de luz en los dos cantos del frontal (D033): insertos impresos en filamento transparente y tiras WS2812B de 5 mm detrás, en un canal cerrado separado de la cámara acústica. El color depende del estado del asistente (tabla en `docs/11_software.md`).
- Difusor de la barra LED en transparente.
- Capucha v0.3 y cubeta v0.3 con las ranuras y los canales; nuevos insertos `franja_inf_v0_1.stl` y `franja_sup_v0_1.stl`.
- Pasadores capucha ↔ bandeja 19 mm por detrás del frontal para dejar sitio al canal; la bandeja lleva una muesca que cierra el canal.
- Consumo de los LEDs limitado por software a 0,6 A. Cámara: ≈3,11 L netos.

## v0.5
- Vuelta al boceto original (D031): frontal inclinado 11° continuo, aristas redondeadas, banda de lamas a todo lo ancho bajo la pantalla, laterales lisos y acabado negro mate. Envolvente 205 × 262 × 150 mm.
- Nuevo volumétrico `prisma_volumetrica_v0_5.scad`: altavoz en el frontal inclinado; parte alta de la cámara acústica tras un tabique paralelo al frontal; ≈3,13 L netos.
- Capucha v0.2: perforado trasero, botones en el techo (capuchones de 8 mm y silencio deslizante), botón de encendido trasero (D032).
- Cubeta v0.2: banda de lamas (pasante solo delante del cono), anillo de montaje inclinado.
- Las comprobaciones de capucha y cubeta usan manifold3d (mucho más rápidas).
- v0.4 (capucha y cubeta con estrías) archivada en `enclosure/openscad/archivo/v0_4/`.

## v0.4.1
- Cubeta acústica v0.1 imprimible (`stl/cubeta_v0_1.stl`): rejilla de ranuras integrada delante y detrás, altavoz y radiador montados por dentro sobre anillos, rebordes para la bandeja y la caja superior, refuerzos y patas de TPU (D030).
- Parte alta de la cámara más grande (techo 176 mm, pared delantera en 60 mm) para compensar los anillos: ≈3,1 L netos finales.
- Nuevo `tools/comprobar_cubeta.py`; altavoz y radiador del volumétrico en su posición real.

## v0.4
- Capucha v0.1 imprimible (`stl/capucha_v0_1.stl`): estrías de 4 mm, rejillas integradas, ventana y resaltes de la pantalla, cámara con guía de tapa, ranura y difusor LED, micrófonos con raíles, conector DC, ventilador opcional y uniones.
- División de la carcasa en 4 piezas (D027), estrías (D028) y uniones (D029).
- Cámara: OV5647 (la que hay); el soporte admite también la Camera Module 3.
- Nuevo `tools/comprobar_capucha.py`.

## v0.3.3
- Cámara Raspberry Pi Camera Module 3 centrada sobre la pantalla, en el frontal inclinado (D025).
- Carcasa 16 mm más alta (250 → 266 mm) para alojarla; la cámara acústica no cambia.
- Tapa deslizante de privacidad (D026) con pieza de prueba: `stl/tapa_camara_prueba_v0_1.stl`.

## v0.3.2
- Electrónica propuesta: DAC GY-PCM5102, ReSpeaker Lite USB, Pololu D36V50F5 y Mean Well GST60A24 (D011–D014), con presupuesto de consumo y cableado en `docs/10_electronica.md`.
- LEDs por SPI con adaptador de nivel (D023); cancelación de eco (D024); filtro paso alto en la Pi (D022).
- Simulación de graves (`tools/simulacion_audio.py`): radiador pasivo con ≈10 g, sintonía ≈43 Hz.
- Modelo: DAC, conversor y micrófonos con sus medidas reales; ventilación trasera y lateral; cámara opcional sin posición.

## v0.3.1
- Pantalla con las cotas del plano oficial de Waveshare: 124,27 mm de alto con pestañas, taladros a 156,90 × 114,96 mm y posición exacta de HDMI, micro-USB e interruptor.
- PCB modelado con pestañas y hueco central.
- Medidas de calibre: taladros de 3,0 mm (→ M2.5) y grosor de 9,5 mm + 7 mm del HDMI.
- Marco de pantalla de prueba imprimible: `enclosure/openscad/marco_pantalla_prueba.scad` y `stl/marco_pantalla_prueba_v0_1.stl`.

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
