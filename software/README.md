# Software de Prisma

- `instalacion/01_base.sh`: configuración base de la Raspberry Pi 5 (sistema, paquetes, SPI, bloque de `config.txt`, repositorio).
- `instalacion/prueba_camara.sh`: comprueba la cámara OV5647.
- `instalacion/02_ia.sh`: Ollama con los modelos candidatos y SearXNG en Docker.
- `herramientas/prueba_ia.py`: compara modelos (tiempo hasta la primera frase), charla por texto y prueba búsquedas.
- `config/searxng_settings.yml`: configuración de SearXNG.
- `instalacion/03_nucleo.sh`: ajusta los tiempos de espera de SearXNG y carga el modelo.
- `prisma_texto.py`: Prisma por texto en la terminal, con desglose de tiempos.
- `servidor.py` + `interfaz/index.html`: Prisma en la pantalla (servidor local en el puerto 8080 y página a pantalla completa).
- `instalacion/04_interfaz.sh`: arranque automático en modo quiosco.
- `nucleo/`: el núcleo del asistente.
  - `enrutador.py`: decide entre buscar y charlar; aquí irán las órdenes directas.
  - `buscador.py`: SearXNG recortado a 2 resultados cortos.
  - `cerebro.py`: Ollama en streaming, troceado para la voz.
  - `asistente.py`: une memoria, enrutador, fuentes y modelo; emite eventos (estado, trozos, fin).
  - `fuentes/`: respuestas sin modelo (reloj, tiempo, fútbol, noticias, web).
  - `config.py`: modelo, límites e instrucciones. Se puede cambiar sin tocar el código con `~/.config/prisma/nucleo.json`.

Guía paso a paso: `docs/17_raspberry.md`.
