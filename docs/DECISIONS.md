# Decisiones
| ID | Decisión | Estado |
|---|---|---|
| D001 | Raspberry Pi 5 8 GB | Cerrada |
| D002 | Waveshare 7", montada en horizontal (apaisada) para vídeo | Cerrada |
| D003 | Fuente AC/DC externa (nada de red 230 V dentro de Prisma) | Cerrada |
| D004 | Bus interno 24 V + buck 5 V | En desarrollo |
| D005 | DMA105-4 | Propuesta |
| D006 | DMA105-PR con ≈10 g de masa añadida (sintonía ≈43 Hz, validado por simulación) | Propuesta |
| D007 | KABD-250 | Propuesta |
| D008 | Cámara acústica independiente y estanca | Cerrada |
| D009 | Envolvente 205×262×150 mm con frontal inclinado continuo (v0.5). Cámara acústica ≈3,1 L netos | Provisional |
| D010 | OpenSCAD | Cerrada |
| D011 | DAC GY-PCM5102 (PCM5102A) por I²S → AUX del KABD-250 | Propuesta |
| D012 | Micrófonos ReSpeaker Lite USB (2 micrófonos, AEC por hardware) bajo el techo | Propuesta |
| D013 | Fuente Mean Well GST60A24-P1J (24 V, 60 W) | Propuesta |
| D014 | Conversor Pololu D36V50F5 (5 V, 5,5 A) | Propuesta |
| D015 | ~~Frontal inferior vertical + superior inclinado 18°~~ Sustituida por D031 | Sustituida |
| D016 | Cámara acústica en L: bloque inferior de ancho y fondo completos + bloque superior-trasero detrás de la pantalla | Propuesta (v0.3) |
| D017 | Electrónica en bahía superior sobre la tapa de la cámara: Pi 5, buck y DAC en el suelo; KABD-250 en una balda encima (lado derecho). Ventilación pasiva solo en la bahía (rejillas trasera superior y laterales). Ningún ventilador ni rejilla en la zona de la cámara | Propuesta (v0.3) |
| D018 | DMA105-PR en la trasera inferior, coaxial con el DMA105-4 | Propuesta (v0.3) |
| D019 | Trasera: entrada DC 24 V de panel en la bahía superior. Los puertos de la Pi no salen al exterior; si hace falta USB/HDMI externo, alargador de panel | Propuesta (v0.3) |
| D020 | Micrófonos en el techo, en la zona trasera (lo más lejos posible del DMA105-4). Cámara opcional: posición pendiente | Propuesta (v0.3) |
| D021 | Conexión de la pantalla con clavijas acodadas: HDMI (cable plano o adaptador a 90° → micro-HDMI de la Pi) y micro-USB táctil acodado. Hueco lateral reservado de 15 mm | Propuesta (v0.3) |
| D022 | Filtro paso alto a ≈40 Hz en la Pi (CamillaDSP/PipeWire) para proteger el altavoz por debajo de la sintonía | Propuesta |
| D023 | LEDs WS2812B por SPI (GPIO10) con adaptador de nivel SN74AHCT125 | Propuesta |
| D024 | Cancelación de eco por hardware en el ReSpeaker Lite; alternativa por software en PipeWire | Propuesta |
| D025 | Cámara OV5647 5 MP (compatible v1.3; la Camera Module 3 también encaja) centrada sobre la pantalla, en el frontal inclinado (mira al usuario con la inclinación de la pantalla). La carcasa crece 16 mm de alto para alojarla | Propuesta |
| D026 | Tapa deslizante de privacidad sobre la cámara, integrada en el frontal (guía en cola de milano), más LED de aviso cuando la cámara está activa | Cerrada |
| D027 | Carcasa en 4 piezas: cubeta acústica (PLA), bandeja (PLA), caja superior de la cámara (PETG) y capucha desmontable (PLA). La Kobra X imprime 260 mm y la carcasa mide 266 | Propuesta |
| D028 | ~~Estrías horizontales en laterales y trasera~~ Sin efecto con el acabado negro mate de D031 | Sustituida |
| D029 | Uniones de la capucha: 2 pasadores delanteros en la bandeja y 2 tornillos M3 avellanados traseros a insertos de la caja superior | Propuesta |
| D030 | Rejillas integradas en la cubeta (banda de lamas delante, circular detrás); altavoz y radiador montados por dentro sobre anillos de 7 y 14 mm con insertos M3 | Cerrada |
| D031 | Vuelta al boceto original: frontal inclinado 11° continuo de arriba abajo, aristas redondeadas, banda de lamas a todo lo ancho bajo la pantalla, laterales lisos, negro mate. 205 × 262 × 150 mm. La parte alta de la cámara acústica queda tras un tabique paralelo al frontal | Cerrada |
| D034 | Bandeja y caja superior: bandeja de 5 mm sobre un reborde delantero nuevo de la cubeta, con 2 tornillos; caja superior abierta por abajo, fijada con 4 tornillos M3 × 80 por tubos desde el suelo de la bahía; burlete de espuma en todos los apoyos; tapa lisa con insertos ciegos para la Pi y la balda del KABD | Propuesta |
| D033 | Luz de acento: franjas de 4 mm en los dos cantos del frontal y difusor de la barra, impresos en filamento transparente; el color lo dan tiras WS2812B de 5 mm (160 LED/m) según el estado del asistente (escucha, pensando, hablando, silencio, avisos). El marco de color alrededor de la pantalla lo dibuja el software | Cerrada |
| D032 | Botones: volumen − y + con capuchones de 8 mm enrasados en el techo, interruptor deslizante que corta la alimentación USB del ReSpeaker (silencio real) y botón de encendido trasero al conector de la Pi 5 | Cerrada |
