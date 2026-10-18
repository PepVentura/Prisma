#!/usr/bin/env bash
# Prisma — paso 6: música con Spotify Connect (raspotify / librespot).
# Prisma aparece como altavoz «Prisma» en la app de Spotify (hace falta Premium) y la pantalla
# enseña lo que suena (botón «Música»).
# Uso (en la Pi):  bash ~/prisma/software/instalacion/05_musica.sh
set -euo pipefail
CONF=/etc/raspotify/conf
GANCHO=/usr/local/bin/prisma-evento-spotify

echo "== 1/3 raspotify =="
if ! command -v librespot >/dev/null; then
    curl -sL https://dtcooper.github.io/raspotify/install.sh | sh
else
    echo "   Ya instalado"
fi

echo "== 2/3 Configuración =="
# El aviso de eventos va fuera de /home: el servicio de raspotify no puede leer las carpetas personales
sudo install -m 755 "$HOME/prisma/software/herramientas/evento_spotify.py" "$GANCHO"
pon() {   # pon CLAVE valor → descomenta o añade la línea en la configuración de raspotify
    if sudo grep -qE "^#?\s*$1=" "$CONF"; then sudo sed -i -E "s|^#?\s*$1=.*|$1=$2|" "$CONF"
    else echo "$1=$2" | sudo tee -a "$CONF" >/dev/null; fi
}
pon LIBRESPOT_NAME '"Prisma"'
pon LIBRESPOT_BITRATE 320
pon LIBRESPOT_DEVICE_TYPE speaker
pon LIBRESPOT_INITIAL_VOLUME 60
pon LIBRESPOT_ONEVENT "$GANCHO"
# Salida de audio: por ahora la predeterminada. Con el DAC PCM5102A (D011) será: LIBRESPOT_DEVICE=hw:CARD=sndrpihifiberry

echo "== 3/3 Arranque =="
sudo systemctl restart raspotify
sleep 2
systemctl is-active --quiet raspotify && echo "   En marcha" || echo "   No arranca: journalctl -u raspotify -n 30"
echo
echo "Hecho. En el móvil: Spotify → icono de altavoz → «Prisma»."
