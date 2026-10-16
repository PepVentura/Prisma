#!/usr/bin/env bash
# Prisma — paso 1: configuración base de la Raspberry Pi 5 (Raspberry Pi OS 64 bits, Trixie).
# Uso (en la Pi):  bash ~/prisma/software/instalacion/01_base.sh
# Se puede ejecutar varias veces: solo cambia lo que falte.
set -euo pipefail

CONFIG=/boot/firmware/config.txt
MARCA_INI="# --- Prisma: inicio ---"
MARCA_FIN="# --- Prisma: fin ---"

echo "== 1/5 Actualizando el sistema (puede tardar) =="
sudo apt-get update
sudo apt-get -y full-upgrade

echo "== 2/5 Paquetes =="
sudo apt-get -y install git python3-venv python3-pip python3-picamera2 rpicam-apps \
    python3-gpiozero python3-lgpio python3-spidev alsa-utils

echo "== 3/5 Interfaces: SPI (LEDs) =="
sudo raspi-config nonint do_spi 0      # 0 = activar

echo "== 4/5 config.txt =="
if ! grep -q "$MARCA_INI" "$CONFIG"; then
    sudo cp "$CONFIG" "$CONFIG.antes_de_prisma"
    sudo tee -a "$CONFIG" > /dev/null <<'CFG'

# --- Prisma: inicio ---
[all]
# Cámara OV5647: la detección automática suele bastar. Si rpicam-hello no la encuentra,
# pon camera_auto_detect=0 arriba y quita el # de la línea que corresponda al conector usado:
#dtoverlay=ov5647,cam0
#dtoverlay=ov5647,cam1

# DAC GY-PCM5102 (I2S): quitar el # cuando esté conectado
#dtoverlay=hifiberry-dac

# Alimentación desde el Pololu (sin USB-PD): quitar el # cuando se alimente así
#usb_max_current_enable=1
# --- Prisma: fin ---
CFG
    echo "   Bloque de Prisma añadido (copia en $CONFIG.antes_de_prisma)"
else
    echo "   El bloque de Prisma ya estaba"
fi

echo "== 5/5 Repositorio =="
if [ ! -d "$HOME/prisma/.git" ]; then
    git clone https://github.com/PepVentura/Prisma.git "$HOME/prisma"
else
    git -C "$HOME/prisma" pull --ff-only || true
fi

echo
echo "Hecho. Reinicia con:  sudo reboot"
echo "Después comprueba la cámara con:  bash ~/prisma/software/instalacion/prueba_camara.sh"
