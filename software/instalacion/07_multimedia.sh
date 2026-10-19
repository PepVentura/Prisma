#!/usr/bin/env bash
# Prisma — paso 8: música y vídeos guardados en la Pi o en un USB.
#   - carpetas Música y Vídeos, etiquetas de las canciones (mutagen) y ffmpeg (miniaturas y formatos raros)
#   - los USB se montan solos al enchufarlos (udiskie), también en modo quiosco
#   - carpetas compartidas en la red (Samba) para copiar desde el ordenador: \\prisma\Música y \\prisma\Vídeos
# Uso (en la Pi):  bash ~/prisma/software/instalacion/07_multimedia.sh
set -euo pipefail
AUTO="$HOME/.config/labwc/autostart"

echo "== 1/4 Paquetes =="
sudo apt-get -y install python3-mutagen ffmpeg udiskie samba >/dev/null && echo "   Listo"

echo "== 2/4 Carpetas =="
MUS=$(xdg-user-dir MUSIC 2>/dev/null || true); VID=$(xdg-user-dir VIDEOS 2>/dev/null || true)
[ -z "$MUS" ] || [ "$MUS" = "$HOME" ] && MUS="$HOME/Música"
[ -z "$VID" ] || [ "$VID" = "$HOME" ] && VID="$HOME/Vídeos"
mkdir -p "$MUS" "$VID"
echo "   Música: $MUS"
echo "   Vídeos: $VID"

echo "== 3/4 USB automático =="
if [ -f "$AUTO" ] && ! grep -q udiskie "$AUTO"; then
    sed -i '1a udiskie --no-notify --no-tray &' "$AUTO"
fi
pgrep -x udiskie >/dev/null || (nohup udiskie --no-notify --no-tray >/dev/null 2>&1 &)
echo "   Los USB aparecerán en /media/$USER/"

echo "== 4/4 Carpetas compartidas en la red =="
if ! grep -q "^\[Música\]" /etc/samba/smb.conf; then
    sudo tee -a /etc/samba/smb.conf >/dev/null <<CFG

[Música]
   path = $MUS
   valid users = $USER
   read only = no
   force user = $USER

[Vídeos]
   path = $VID
   valid users = $USER
   read only = no
   force user = $USER
CFG
fi
echo "   Contraseña para entrar desde el ordenador (puede ser la misma de la Pi):"
sudo smbpasswd -a "$USER"
sudo systemctl restart smbd
systemctl --user restart prisma 2>/dev/null || true
echo
echo "Hecho. Desde Windows: Explorador → \\\\$(hostname)\\Música  (usuario $USER)."
echo "Copia música (mejor en carpetas Artista/Álbum) y vídeos; Prisma los encuentra solos."
