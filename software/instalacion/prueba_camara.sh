#!/usr/bin/env bash
# Prisma — comprueba la cámara OV5647: la lista, enseña 5 s de imagen y guarda una foto.
set -euo pipefail
echo "== Cámaras detectadas =="
rpicam-hello --list-cameras
echo
echo "== Vista previa de 5 segundos en la pantalla =="
rpicam-hello -t 5000
echo
FOTO="$HOME/prueba_camara.jpg"
rpicam-still -t 2000 -o "$FOTO"
echo "Foto guardada en $FOTO"
