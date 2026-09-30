# Guía completa: monta y pon en marcha tu SteamMachine UM790

Esta guía te lleva de cero a tener el proyecto funcionando, aunque no
hayas tocado nunca una impresora 3D, un ESP32 o una terminal. No hace
falta ningún conocimiento previo — cada paso explica qué estás haciendo
y por qué. Si en algún momento algo no funciona, ve directo a la
sección [10. Solución de problemas](#10-solución-de-problemas).

Los documentos técnicos detallados (`docs/01` a `docs/14`) siguen ahí
para quien quiera profundizar; esta guía es el camino corto para llegar
a tenerlo funcionando.

## Índice

1. [Qué vas a construir](#1-qué-vas-a-construir)
2. [Antes de empezar: lista de materiales](#2-antes-de-empezar-lista-de-materiales)
3. [Paso 1 — Imprimir y montar la carcasa](#3-paso-1--imprimir-y-montar-la-carcasa)
4. [Paso 2 — Cablear la electrónica](#4-paso-2--cablear-la-electrónica)
5. [Paso 3 — Preparar el mini PC (Bazzite)](#5-paso-3--preparar-el-mini-pc-bazzite)
6. [Paso 4 — Programar el ESP32 (firmware)](#6-paso-4--programar-el-esp32-firmware)
7. [Paso 5 — Instalar el software del PC (el "Core")](#7-paso-5--instalar-el-software-del-pc-el-core)
8. [Paso 6 — Primera prueba completa](#8-paso-6--primera-prueba-completa)
9. [Paso 7 — Que arranque solo](#9-paso-7--que-arranque-solo)
10. [Solución de problemas](#10-solución-de-problemas)
11. [Mapa del repositorio](#11-mapa-del-repositorio)

---

## 1. Qué vas a construir

Un mini PC (Minisforum UM790 Pro) metido dentro de una carcasa impresa
en 3D con forma de consola. Tiene paneles frontales intercambiables:
cada panel lleva una etiqueta NFC escondida, y al acercarlo a un lector
y pulsar un botón, el PC lanza automáticamente Steam, tu colección
retro (RetroDECK / RetroArch) o el panel de disparos/zombies (THE
HOUSE OF THE DEAD: Remake y THE HOUSE OF THE DEAD 2: Remake, ambos
nativos de Steam vía Proton). Hay también un panel **Apagar** que
apaga el equipo de forma ordenada. Una pantalla OLED y una barra de
LEDs te muestran qué panel has puesto.

Tres piezas hacen que esto funcione:

- **La carcasa** (impresión 3D, diseño en OpenSCAD).
- **El firmware** (`firmware/`): un programa en C++ que vive dentro de
  un ESP32 — una placa pequeña y barata que lee el NFC, controla la
  pantalla y los LEDs, y detecta el botón.
- **El Core** (`software/`): un programa en Python que corre en el
  propio mini PC, habla con el ESP32 por USB, y decide qué aplicación
  lanzar según el panel que hayas puesto.

No hace falta que hagas los tres pasos en orden estricto, pero esta
guía sí lo hace, porque cada uno se apoya en el anterior para poder
probarse.

---

## 2. Antes de empezar: lista de materiales

### Hardware

| Componente | Notas |
|---|---|
| Mini PC Minisforum UM790 Pro | El "cerebro" del sistema |
| Ventilador Noctua NF-A12x15 PWM (120×120×15mm) | Refrigeración |
| Placa ESP32-WROOM-32D DevKit (modelo HW-394) | El "controlador" del frontal |
| Lector NFC MFRC522 | Lee los paneles |
| Pantalla OLED I²C 0.96" (128×64) | Muestra el estado |
| Barra LED WS2812B (RGB direccionable) | Feedback visual — se conecta directa al ESP32, sin nivelador |
| Pulsador metálico antivandálico Ø16mm, iluminado | Confirma el lanzamiento |
| HUB USB CJMCU-204 (4 puertos) | Reparte el USB del mini PC entre frontal y ESP32 |
| Fuente de alimentación externa | Menos calor y más espacio dentro de la carcasa |
| Tags NFC (uno por panel) | Los que vayas a esconder en cada panel intercambiable |
| Tornillería M2, M2.5, M3, M4, M5, M6, M8 e insertos roscados | Según pieza — ver `docs/07_Hardware_Specification.md` |
| Imanes de neodimio 3×2mm y 6×2mm | Fijan los paneles intercambiables |
| Filamento **PETG** (todas las piezas; el PLA se deforma con el calor del equipo) | Impresión 3D. PLA solo para pruebas de encaje, nunca montado |
| Loctite (cianoacrilato tipo 401/454) | Pegar los anagramas sueltos de `STL/Anagramas/` sobre el panel NFC en blanco |

### Herramientas

- Impresora 3D FDM (el proyecto se ha probado con una Anycubic Kobra X).
- Destornilladores pequeños (Phillips/Allen, tornillería M2-M4).
- Un cable USB para flashear el ESP32.
- Un ordenador (puede ser el mismo mini PC, o cualquier otro) para
  compilar el firmware y descargar el proyecto.
- Un pendrive (para instalar el sistema operativo del mini PC).

### Conocimientos previos

Ninguno es obligatorio. Si nunca has abierto una terminal, cada comando
de esta guía está pensado para copiar y pegar tal cual. Lo único que
ayuda (pero no es necesario) es haber usado antes un ordenador con
Linux.

---

## 3. Paso 1 — Imprimir y montar la carcasa

1. Descarga el repositorio completo (botón **Code → Download ZIP** en
   GitHub, o `git clone` si ya sabes usarlo).
2. Los ficheros listos para imprimir están en `STL/`. Si tu impresora
   los admite directamente, no necesitas tocar nada más.

   Para los **paneles NFC con anagrama** (Steam, RetroBat, etc.),
   `STL/Anagramas/` trae el panel en blanco (`nfc_panel_blank.stl`) y
   cada anagrama por separado (`Steam.stl`, `Retrobat.stl`,
   `Parrot.stl`, `engranaje.stl`, `Gung.stl` — este último es el
   anagrama del panel Zombies —, y `Apagar.stl`, el del panel Apagar)
   para imprimirlos como piezas independientes en vez de la pieza única con el emblema
   integrado. Imprime el panel en blanco y el anagrama que quieras por
   separado, y pégalos con **Loctite** (un cianoacrilato tipo Loctite
   401/454). Sobre PETG el cianoacrilato agarra algo peor que sobre PLA:
   lija ligeramente las dos caras y desengrasa con alcohol isopropílico
   antes de pegar; si se despega, usa epoxi de 5 minutos. Este método baja el tiempo de
   impresión de ~6 horas (pieza única con el emblema en relieve) a
   ~1 hora, porque el anagrama es una pieza pequeña y plana que no
   necesita soportes ni tantas capas del panel completo debajo.
   Los STL de un único bloque (con el emblema ya integrado, sin pegar)
   siguen disponibles directamente en `STL/` y en
   `openscad/parts/03_panels/` si prefieres esa vía.
   **Caja para guardar los paneles**: `STL/caja_nfc_panel_caja.stl` y
   `STL/caja_nfc_panel_tapa.stl` (o `caja_nfc_panel_caja_y_tapa.stl`,
   las dos piezas en una sola placa). Guarda hasta 6 paneles de canto;
   ver `docs/14_Caja_Paneles_NFC.md`.
3. Si quieres ajustar medidas (por ejemplo, si tu mini PC no es
   exactamente un UM790 Pro), el diseño paramétrico está en
   `openscad/` y `00_parametros.scad`, hecho con
   [OpenSCAD](https://openscad.org/) (gratuito).
4. **Material: PETG para todas las piezas.** El PLA (y el PLA+) se
   deforma con la temperatura del mini PC, así que no lo dejes montado
   dentro del equipo; úsalo solo para probar encajes. Si una pieza lleva
   dos filamentos (el panel inferior, con el difusor LED translúcido),
   los dos deben ser PETG. Parámetros orientativos: altura de capa
   0.20mm, 3-4 perímetros, relleno 15-30%; PETG con boquilla a
   230-250 °C, cama a 70-85 °C y ventilador de capa bajo (30-50%) —
   parte del perfil PETG de tu marca de filamento. Más detalle en el
   [README](README.md#material-petg).
   Las holguras del diseño se ajustaron con PLA+: con PETG revisa los
   encajes antes de montar.
5. El montaje mecánico paso a paso (con checklist) está en
   `docs/11_Assembly_Manual.md`. Termina el montaje físico completo
   (carcasa, mini PC, ventilador, soportes) antes de pasar al cableado.

---

## 4. Paso 2 — Cablear la electrónica

Con la carcasa montada, toca conectar el ESP32 a sus periféricos.
**Antes de dar corriente a nada, revisa dos veces que cada cable va al
pin correcto** — un fallo aquí es la causa más común de que algo "no
funcione" más adelante.

### Pinout

| Función | Pin del ESP32 |
|---|---|
| RC522 SDA/SS | GPIO5 |
| RC522 SCK | GPIO18 |
| RC522 MISO | GPIO19 |
| RC522 MOSI | GPIO23 |
| RC522 RST | GPIO27 |
| OLED SDA | GPIO21 |
| OLED SCL | GPIO22 |
| Barra LED WS2812B (directa, sin nivelador) | GPIO25 |
| Pulsador | GPIO13 |

### Alimentación

| Riel | Alimenta |
|---|---|
| 3V3 (del ESP32) | RC522 + OLED |
| VIN, ~4.68V | WS2812B |
| GND | Masa común a todo |

El dato de la barra LED sale del ESP32 a 3.3V por el GPIO25 y va
**directo** a la tira, sin ningún chip intermedio. El diseño original
llevaba un nivelador lógico (74AHCT125) para elevar la señal a los
~5V que en teoría espera la WS2812B, pero se retiró: probado con 8
LEDs, funciona bien recibiendo la señal directamente a 3.3V, y con el
nivelador en el circuito no encendía nada — lo más probable es que
tuviera un pin de habilitación (/OE) sin conectar a GND, un fallo muy
típico con ese chip. Si en el futuro con la tira completa (más larga)
notas parpadeos o colores erráticos, puede ser señal de que sí hace
falta un nivelador bien cableado — pero de entrada, directo funciona.

### Cable y colores

Cable 22 AWG / 0,32 mm², cobre estañado, aislamiento de silicona. Usa
siempre el mismo color para lo mismo en todo el montaje — te ahorra
sustos al revisar el cableado más adelante:

| Color | Para |
|---|---|
| 🔴 Rojo | +5V |
| ⚫ Negro | GND |
| 🟡 Amarillo | Datos / señales |
| 🔵 Azul | SPI (RC522) |
| 🟢 Verde | I²C (OLED) |

No conectes todavía el ESP32 al mini PC por USB — eso lo harás en el
[Paso 4](#6-paso-4--programar-el-esp32-firmware), después de
flashearlo.

---

## 5. Paso 3 — Preparar el mini PC (Bazzite)

1. Descarga [Bazzite](https://bazzite.gg/) (el sistema operativo, un
   Linux orientado a gaming) y grábalo en un pendrive con una
   herramienta como [Balena Etcher](https://etcher.balena.io/) o
   [Rufus](https://rufus.ie/).
2. Arranca el mini PC desde el pendrive e instala Bazzite siguiendo el
   asistente (formatea el disco del UM790, así que asegúrate de que no
   tiene nada que quieras conservar).
3. Una vez dentro del escritorio, instala RetroDECK (pack todo-en-uno
   de emulación retro) desde la Discover Store o con:
   ```bash
   flatpak install flathub net.retrodeck.retrodeck
   ```
4. Instala también **RetroArch** (Flatpak, directo, sin pasar por
   RetroDECK — útil para paneles dedicados a un sistema/core concreto):
   ```bash
   flatpak install flathub org.libretro.RetroArch
   ```
   Ábrelo una vez para que genere su configuración en
   `~/.var/app/org.libretro.RetroArch/config/retroarch/`. Luego, desde
   dentro de RetroArch: **Menú principal → Actualizador en línea →
   Actualizar información de núcleos** (imprescindible, o el
   Descargador de núcleos mostrará "No hay elementos disponibles") y a
   continuación **Descargador de núcleos**, donde instalas los que
   necesites — por ejemplo:
   - **Flycast** (Dreamcast/Naomi)
   - **Beetle Saturn** / Mednafen Saturn
   - **PCSX-ReARMed** (PS1)
   - **MAME2003-Plus** (arcade)

   Los BIOS (obligatorios para PS1 y Saturn; recomendables para
   Dreamcast) van en
   `~/.var/app/org.libretro.RetroArch/config/retroarch/system/` —
   tienes que dumpearlos tú mismo de hardware que poseas, RetroArch no
   los distribuye. Las ROMs las importas luego desde **Importar
   contenido → Escanear directorio**.
5. Comprueba que Steam ya está instalado (Bazzite lo trae de fábrica).
   Para el panel de zombies, instala desde Steam **THE HOUSE OF THE
   DEAD: Remake** (AppID `1694600`) y **THE HOUSE OF THE DEAD 2:
   Remake** (AppID `3376690`) — son juegos nativos de Steam vía
   Proton, no necesitan emulador. Si al primero le fallan los vídeos
   de introducción, fuerza **Proton GE** en vez del Proton estándar
   (Propiedades del juego → Compatibilidad).

---

## 6. Paso 4 — Programar el ESP32 (firmware)

Esto se puede hacer desde el propio mini PC o desde otro ordenador —
lo único que necesitas es el ESP32 conectado por USB a la máquina desde
la que flasheas.

1. Instala [Visual Studio Code](https://code.visualstudio.com/) y,
   dentro, la extensión **PlatformIO IDE** (búscala en el panel de
   extensiones). PlatformIO es la herramienta que compila el código C++
   y lo sube al ESP32.
2. Abre la carpeta `firmware/` del proyecto en VS Code (**Archivo →
   Abrir carpeta**).
3. Conecta el ESP32 al ordenador por USB.
4. En VS Code, con `firmware/` abierta y el ESP32 conectado por USB,
   usa los **botones de PlatformIO** en vez de escribir comandos —
   son más fiables porque no dependen de que tu terminal tenga nada
   configurado. Al instalar la extensión aparece una franja azul en la
   parte inferior de VS Code con varios iconos; los que necesitas son:
   - ✔️ (**Build**) — compila.
   - ➡️ (**Upload**) — flashea el ESP32.
   - 🔌 (**Serial Monitor**) — abre el monitor serie.

   Pulsa los tres en ese orden. Si no ves esa franja azul, abre el
   icono de PlatformIO (una cabeza de hormiga) en la barra lateral
   izquierda → **PROJECT TASKS → esp32doit-devkit-v1 → General**, y
   ahí tienes Build/Upload/Monitor como una lista.

   > **¿Por qué no usar una terminal normal?** En Windows es habitual
   > que el comando `pio` dé el error *"no se reconoce como nombre de
   > un cmdlet..."* aunque la extensión funcione perfectamente — el
   > `pio` de PlatformIO no se añade solo al PATH de PowerShell. Si
   > prefieres la terminal de todos modos, abre **PlatformIO Core
   > CLI** desde el icono de PlatformIO (no "Terminal → Nueva
   > terminal" de VS Code): esa sí tiene `pio` disponible, con los
   > mismos comandos que abajo.
   ```bash
   cd firmware
   pio run                                            # compila
   pio run --target upload -e esp32doit-devkit-v1     # flashea el ESP32
   pio device monitor -b 115200                        # abre el monitor serie
   ```
   El monitor serie (por botón o por `pio device monitor`) es clave:
   abre una ventana de texto en directo con todo lo que el ESP32 envía
   por el cable USB — es la única forma de "ver" lo que está haciendo,
   ya que no tiene pantalla propia. Todo lo que describen los pasos 5
   y 6 aparece ahí.
5. Al arrancar verás primero unas líneas de texto sueltas del propio
   arranque del ESP32 (algo como `ets Jul 29 2019...`, `rst:0x1...`,
   `load:0x3fff0030...`) — son normales, ignóralas. Justo después debe
   aparecer la línea que de verdad importa:
   ```
   {"event":"boot","firmware":"1.0.0"}
   ```
   Si el ESP32 llevaba un rato encendido antes de abrir el monitor, te
   la habrás perdido — pulsa el botón RESET/EN de la placa, o
   desconecta y vuelve a conectar el USB, para que arranque de nuevo
   con el monitor ya abierto.

   Si justo después ves también `{"event":"error","code":1}`, es que
   el RC522 (lector NFC) no responde — normal si todavía no lo has
   cableado. Ver [Solución de problemas](#10-solución-de-problemas).

   Si no aparece ninguna línea en absoluto, ve a
   [Solución de problemas](#10-solución-de-problemas).
6. Con el monitor todavía abierto, haz estas comprobaciones antes de
   seguir:
   - Acerca un tag NFC al lector → debe aparecer
     `{"event":"tag","uid":"..."}` con un código de 8 caracteres.
     **Apunta ese UID**, lo necesitarás en el paso siguiente.
   - Retíralo → `{"event":"tag_removed"}`.
   - Pulsa el botón → `{"event":"button"}`.
   - Escribe a mano en el monitor y pulsa Enter para probar la
     pantalla y los LEDs:
     `{"cmd":"oled","text":"Hola"}` (debe aparecer en pantalla) y
     `{"cmd":"led","color":"#00FF00"}` (la barra debe ponerse verde).

Solo sigas al siguiente paso cuando estas seis comprobaciones
funcionen. Es la única forma de saber si un problema viene del
cableado/firmware o del software del PC.

---

## 7. Paso 5 — Instalar el software del PC (el "Core")

Este paso sí es en el propio mini PC (necesita hablar con el ESP32 por
USB).

1. Descarga el proyecto en el mini PC (mismo repositorio del Paso 1).
2. Abre una terminal y ejecuta:
   ```bash
   cd software
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
3. Conecta el ESP32 (ya flasheado) al mini PC por USB, a través del
   HUB del frontal.
4. Añade los UID reales de tus tags NFC (los que apuntaste en el paso
   anterior) en `config/panel_database.json`. Ya trae varios de ejemplo:
   ```json
   {
     "04A1C8B2": { "name": "Steam", "launcher": "steam", "led": "#0055FF", "icon": "steam.png" },
     "04B2D9C3": { "name": "RetroDECK", "launcher": "retrodeck", "led": "#8800FF", "icon": "retrodeck.png" },
     "04C3EAD4": { "name": "Zombies - HOTD Remake", "launcher": "hotd_remake", "led": "#FF3300", "icon": "hotd_remake.png" },
     "0AAABBCC": { "name": "Zombies - HOTD 2 Remake", "launcher": "hotd2_remake", "led": "#CC0000", "icon": "hotd2_remake.png" },
     "04E5A0F6": { "name": "Apagar", "profile": "APAGAR", "launcher": null, "led": "#FF0000", "icon": "apagar.png" }
   }
   ```
   Sustituye esas claves (`04A1C8B2`, etc.) por los UID de tus tags
   reales — la clave es el UID, el resto de campos puedes dejarlos o
   personalizarlos. El de HOTD 2 Remake (`0AAABBCC`) es un placeholder
   hasta que tengas un segundo tag/panel físico dedicado a ese juego;
   mientras tanto, un solo panel puede apuntar a `hotd_remake` y
   cambiar de juego se hace a mano desde Steam.

   **Panel Apagar**: el fichero real trae su entrada con la clave
   `UID_APAGAR_PENDIENTE`. Sustitúyela por el UID del tag que metas en
   ese panel (el mismo procedimiento que con los demás). Es importante
   que la entrada conserve `"profile": "APAGAR"`: es el perfil
   (`config/profiles/apagar.json`) el que le dice al Core que ese panel
   apaga el equipo; sin él, el botón no hace nada. En el modo simulado
   del Core el apagado nunca se ejecuta de verdad, solo se registra en
   el log.
5. Arranca el Core:
   ```bash
   python main.py
   ```
   Por defecto busca el ESP32 automáticamente. Si no lo encuentra:
   ```bash
   ls /dev/serial/by-id/     # busca algo como usb-1a86_USB_Serial-if00-port0
   ```
   y pon esa ruta a mano en `config/config.json`:
   ```json
   "serial": { "port": "/dev/ttyUSB0", "simulate": false }
   ```

---

## 8. Paso 6 — Primera prueba completa

Con el Core corriendo (`python main.py`), acerca un panel al lector:

1. La pantalla OLED debería mostrar el nombre del panel.
2. La barra LED debería cambiar suavemente al color de ese panel.
3. Pulsa el botón → la barra hace una animación de "lanzamiento" y, si
   todo va bien, se abre Steam/RetroDECK/RetroArch o el juego de
   zombies correspondiente según el panel.
4. Retira el panel → la pantalla se apaga y el LED vuelve al azul de
   reposo.

**Prueba del panel Apagar** (hazla con el equipo ya en su sitio y sin
nada importante abierto: apaga el mini PC de verdad). Antes, comprueba
en una terminal que tu usuario puede apagar sin contraseña — el panel
usa exactamente el mismo comando:

```bash
systemctl poweroff
```

Si eso apaga el equipo sin pedir nada, el panel también podrá.
Arranca de nuevo y prueba con el panel: al colocarlo, la OLED debe
mostrar `APAGAR EQUIPO` (todavía sin apagar); al pulsar el botón, pasa a
`Apagando...`, los LEDs se funden a negro y el equipo se apaga.

Si algo de esto no pasa, revisa primero que el [Paso 4](#6-paso-4--programar-el-esp32-firmware)
funcionó por sí solo (con el monitor serie) — si el firmware ya
funcionaba a solas y ahora falla con el Core, el problema suele estar
en `config/panel_database.json` (UID mal copiado) o en el puerto serie.

---

## 9. Paso 7 — Que arranque solo

Para no tener que abrir una terminal cada vez que enciendas el mini PC:

```bash
mkdir -p ~/.config/systemd/user
cp steammachine.service ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable --now steammachine.service
```

Si instalaste el proyecto en una ruta distinta de
`~/SteamMachine-UM790/software`, edita `ExecStart` y `WorkingDirectory`
dentro de `steammachine.service` antes del `cp`.

Para comprobar que está corriendo, o ver qué está pasando si algo
falla:

```bash
systemctl --user status steammachine.service
journalctl --user -u steammachine.service -f
```

---

## 10. Solución de problemas

**`pio` no se reconoce como comando (Windows, PowerShell)**
La extensión de PlatformIO no añade `pio` al PATH de una terminal
normal. Usa los botones ✔️/➡️/🔌 de la franja azul inferior de VS
Code, o abre **PlatformIO Core CLI** desde el icono de PlatformIO en
la barra lateral (no "Terminal → Nueva terminal") — ver el
[Paso 4](#6-paso-4--programar-el-esp32-firmware).

**El ESP32 no aparece al conectarlo (ni en PlatformIO ni en `/dev/serial/by-id/`)**
Prueba otro cable USB (muchos cables baratos son solo de carga, sin
datos) y otro puerto USB. En Linux, puede que necesites permisos:
`sudo usermod -aG dialout $USER` y reiniciar sesión.

**`pio run` falla al compilar**
Revisa el mensaje de error concreto — suele ser una librería que no se
descargó bien. Prueba `pio pkg update` dentro de `firmware/` y vuelve a
intentarlo. Si el error es de red, comprueba tu conexión a internet
(PlatformIO descarga el compilador y las librerías la primera vez). Si
el error menciona `FastLED` y `rbtree.h` (`mTree`, `const_iterator`,
`RedBlackTree`...), es un fallo conocido de las versiones más recientes
de FastLED con este compilador — este proyecto ya fija la versión
`3.7.8` en `firmware/platformio.ini`, que lo evita. Si aun así te
aparece, borra la carpeta `.pio` dentro de `firmware/` por completo
(PlatformIO puede haber dejado en caché una versión rota descargada
antes de que se fijara) y vuelve a compilar.

**El monitor serie no muestra nada al arrancar**
Confirma que elegiste la velocidad correcta (115200) y que ningún otro
programa tiene el puerto abierto (cierra PlatformIO's monitor antes de
abrir el Core, y viceversa — solo uno puede usar el puerto a la vez).

**Aparece `{"event":"error","code":1}` justo después de arrancar**
El firmware no encuentra el lector RC522. Normal si todavía no lo has
cableado. Si ya lo tienes conectado, revisa los 5 cables (SDA/SS, SCK,
MISO, MOSI, RST) contra la tabla del
[Paso 2](#4-paso-2--cablear-la-electrónica), que esté alimentado a
3.3V (no 5V — puede dañarlo) y reinicia el ESP32 tras corregir algo.

**El panel NFC no se detecta**
Acércalo más (unos 2-3cm) y prueba distintas orientaciones — el
alcance del RC522 es corto. Si nunca detecta nada, revisa el cableado
SPI (SCK/MISO/MOSI/SS/RST) contra la tabla del [Paso 2](#4-paso-2--cablear-la-electrónica).

**El Core no encuentra el ESP32**
Comprueba con `ls /dev/serial/by-id/` que el sistema lo ve. Si no
aparece nada ahí, el problema es de cableado/USB, no del software —
vuelve al Paso 4. Si aparece pero el Core no conecta, ponlo a mano en
`config/config.json` como se explica en el Paso 5.

**Steam/RetroDECK/RetroArch/Zombies no arrancan al pulsar el botón**
Prueba a lanzarlos a mano desde el escritorio de Bazzite primero — si
tampoco arrancan así, el problema es de esa instalación, no del
proyecto. Si arrancan a mano pero no desde el botón, revisa que el
`launcher` de ese panel en `panel_database.json` coincide con las
claves `steam` / `retrodeck` / `retroarch` / `hotd_remake` /
`hotd2_remake` de `config/config.json`.

**El Descargador de núcleos de RetroArch muestra "No hay elementos disponibles"**
Falta actualizar el índice antes de poder listar núcleos: entra en
**Actualizador en línea → Actualizar información de núcleos**, espera
a que termine, y vuelve a **Descargador de núcleos** — ya debería
aparecer la lista completa.

**La pantalla OLED no enciende**
Revisa la dirección I2C — por defecto se asume `0x3C`. Si tu módulo usa
`0x3D`, cámbialo en `firmware/src/config.h` (`OLED_I2C_ADDRESS`) y
vuelve a flashear.

**Los LEDs no encienden, o encienden en colores raros**
La tira va directa al GPIO25 (sin nivelador, ver Paso 2) — comprueba
que está bien alimentada por VIN (no por 3V3) y que el GND de la tira
está unido al GND del ESP32. Si el color sale invertido, revisa que el
orden de color de tu tira coincide con `GRB` (el que usa el firmware
por defecto) — si tu tira es `RGB`, avisa para ajustar
`firmware/src/hardware/leds.cpp`.

Si nada de esto lo resuelve, el firmware tiene un canal de depuración
más detallado por Serial2 — ver "Depuración" en `firmware/README.md`.

**El mini PC se queda en un prompt `grub>` en vez de arrancar Bazzite**
*Prevención: apaga siempre con el panel Apagar (o desde el menú de
Bazzite) en vez de cortar la corriente de golpe.*

Es la consola de rescate de GRUB — aparece cuando el firmware UEFI
pierde la referencia al fichero de arranque, normalmente por un corte
de corriente justo durante un arranque anterior (no es un fallo del
proyecto, ni algo que se pueda producir cableando el pulsador de
encendido trasero — solo coincidencia si pasa justo después). El
sistema en sí no suele estar dañado, solo esa referencia. Para
recuperarlo sin perder nada:

1. En el prompt `grub>`, comprueba que el disco se ve bien:
   ```
   ls
   ```
   Deberías ver algo como `(hd0) (hd0,gpt1) (hd0,gpt2) (hd0,gpt3)`.
2. Localiza la partición EFI (comprueba una a una si hace falta):
   ```
   ls (hd0,gpt1)/
   ```
   Busca una carpeta `efi/` — si no está en `gpt1`, prueba con `gpt2`, etc.
3. Dentro debería haber `efi/fedora/grub.cfg`. Cárgalo directamente:
   ```
   configfile (hd0,gpt1)/efi/fedora/grub.cfg
   ```
   (ajusta el número de partición al que hayas encontrado en el paso 2).
4. Debería aparecer el menú normal de arranque de Bazzite — arranca
   con Enter.
5. Una vez dentro, **reinicia una vez de forma normal** (menú de
   Steam/Bazzite, no cortando corriente) para confirmar que el
   arranque automático ya funciona solo, sin repetir estos pasos. Si
   vuelve a fallar, hay un comando (`sudo bootupctl`) para reescribir
   la entrada de arranque de forma permanente.

**El panel Apagar muestra `Error al apagar` (o el botón no hace nada)**
- `Error al apagar`: el sistema ha rechazado la orden y el equipo sigue
  encendido. Mira el motivo en `journalctl --user -u steammachine.service -n 30`.
  Lo más habitual es un bloqueo de apagado (p. ej. una actualización de
  Bazzite en curso). Comprueba qué lo bloquea con
  `systemd-inhibit --list`, y prueba `systemctl poweroff` a mano para
  ver el mensaje completo.
- El botón no hace nada con el panel puesto: la entrada del panel en
  `panel_database.json` no lleva `"profile": "APAGAR"` (o falta
  `config/profiles/apagar.json`). Sin perfil, el Core lo trata como un
  panel informativo y no hace nada.
- La OLED dice `Panel no reconocido`: el UID del tag no está en
  `panel_database.json`; sustituye `UID_APAGAR_PENDIENTE` por el real.

**Las piezas impresas se han deformado con el calor**
Están en PLA. Reimprímelas en PETG (ver [Paso 1](#3-paso-1--imprimir-y-montar-la-carcasa)).

---

## 11. Mapa del repositorio

```
GUIA_INICIO.md        Esta guía
README.md              Presentación general del proyecto
docs/                  Documentación técnica detallada (01 a 14)
openscad/, STL/         Diseño e impresión 3D de la carcasa
firmware/               Código C++ del ESP32 (ver firmware/README.md)
software/               Código Python del Core, corre en el mini PC (ver software/README.md)
```

Para profundizar en cualquier pieza, los documentos técnicos son la
referencia completa: `docs/04_Communication_Protocol.md` (cómo hablan
el ESP32 y el PC entre sí), `docs/05_Firmware_Architecture.md` y
`docs/08_Software_API.md` (arquitectura interna de cada lado),
`docs/07_Hardware_Specification.md` (lista de materiales completa),
`docs/11_Assembly_Manual.md` (montaje mecánico paso a paso) y
`docs/14_Caja_Paneles_NFC.md` (caja para guardar los paneles).

---

## Licencia

Proyecto bajo licencia MIT — ver `LICENSE`. Puedes usarlo, modificarlo
y compartirlo libremente.
