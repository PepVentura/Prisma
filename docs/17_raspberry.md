# 17 — Puesta en marcha de la Raspberry Pi 5

Primera fase con lo que ya hay: **Pi 5 + pantalla Waveshare 7" (C) + cámara OV5647**. Los micrófonos, el DAC, los LEDs y los botones se añadirán en pasos siguientes.

## 1. Grabar el sistema (en tu ordenador)
1. Instala **Raspberry Pi Imager** (raspberrypi.com/software) y mete la tarjeta microSD (32 GB o más, A2).
2. Dispositivo: **Raspberry Pi 5**. Sistema: **Raspberry Pi OS (64-bit)**, el normal, con escritorio: la interfaz de Prisma irá en un navegador a pantalla completa.
3. En «Personalización» (el engranaje o «Editar ajustes»):
   - Nombre de equipo: `prisma`.
   - Usuario y contraseña: los que quieras (los scripts no dependen del nombre).
   - Wi-Fi: tu red, país `ES`.
   - Zona horaria `Europe/Madrid`, teclado `es`.
   - Servicios: **activar SSH** con contraseña.
4. Graba la tarjeta.

## 2. Conexiones
| Qué | Dónde |
|---|---|
| Pantalla, vídeo | Cable micro-HDMI → HDMI al puerto **HDMI0** de la Pi (el que está junto al USB-C de alimentación) |
| Pantalla, táctil y alimentación | Cable micro-USB del conector *Touch* de la pantalla a un USB de la Pi |
| Cámara | Cable de 22 → 15 pines: el extremo estrecho al conector **CAM/DISP 0** de la Pi y el ancho a la cámara. Con la Pi apagada; contactos dorados según el dibujo del conector |
| Alimentación | De momento, la fuente oficial de 27 W (5 V, 5 A) de la Pi 5 |

El interruptor *Backlight* de la pantalla, en ON.

## 3. Primer arranque y configuración
1. Enciende. La primera vez tarda un par de minutos.
2. Abre una terminal en la propia Pi o entra por SSH desde tu ordenador: `ssh tu_usuario@prisma.local`.
3. Descarga el repositorio y lanza la configuración base:
   ```bash
   git clone https://github.com/PepVentura/Prisma.git ~/prisma
   bash ~/prisma/software/instalacion/01_base.sh
   sudo reboot
   ```
   El script actualiza el sistema, instala lo necesario, activa el SPI (para los LEDs) y añade a `/boot/firmware/config.txt` un bloque de Prisma, con las líneas de la cámara, el DAC y la alimentación comentadas hasta que hagan falta.

## 4. Comprobaciones
**Pantalla:** debe verse a 1024 × 600 y el táctil debe mover el puntero. Las líneas `hdmi_cvt` de la wiki de Waveshare son del sistema antiguo y la Pi 5 las ignora. Si la imagen sale mal, añade al final de la única línea de `/boot/firmware/cmdline.txt` (separado por un espacio):
```
video=HDMI-A-1:1024x600M@60
```

**Cámara:**
```bash
bash ~/prisma/software/instalacion/prueba_camara.sh
```
Lista la cámara, enseña 5 s de imagen y guarda `~/prueba_camara.jpg`. Si dice *No cameras available*:
1. Revisa el cable: que esté bien metido en los dos extremos y con los contactos del lado correcto.
2. Si sigue sin verla, en `config.txt` pon `camera_auto_detect=0` y quita el `#` de `dtoverlay=ov5647,cam0`.

## 5. El cerebro
Todo en local, en la propia Pi, con consultas a Internet a través de SearXNG. La arquitectura y los tiempos de respuesta están en `11_software.md` (D036).

## 6. Paso 2: IA local y buscador
```bash
bash ~/prisma/software/instalacion/02_ia.sh
```
- Instala **Ollama**, que deja el modelo siempre cargado y solo accesible desde la propia Pi.
- Descarga tres modelos candidatos para compararlos: `qwen3.5:2b`, `qwen3:1.7b` y `qwen2.5:3b`, unos 7 GB en total. Con `--gemma` añade `gemma4:e2b`, unos 5 GB más; para eso conviene una tarjeta de 64 GB.
- Instala **Docker** y **SearXNG**, en el puerto 8888, solo para la Pi, con respuestas en JSON y en español.

**Prueba de velocidad:**
```bash
python3 ~/prisma/software/herramientas/prueba_ia.py --comparar
```
Hace las mismas preguntas a cada modelo y mide cuándo sale la **primera frase completa**, que es cuando Prisma empezaría a hablar, y la velocidad de generación. Al final saca una tabla resumen.

**Charlar por texto con un modelo y probar una búsqueda:**
```bash
python3 ~/prisma/software/herramientas/prueba_ia.py --modelo qwen3.5:2b
python3 ~/prisma/software/herramientas/prueba_ia.py --modelo qwen3.5:2b --buscar "¿quién ganó el último Tour de Francia?"
```
Con los resultados (velocidad y calidad de las respuestas en español) elegiremos el modelo definitivo.
