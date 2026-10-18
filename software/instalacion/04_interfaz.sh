#!/usr/bin/env bash
# Prisma — paso 5: la interfaz en la pantalla al encender la Pi.
#   - servicio «prisma» (servidor.py) que arranca solo con la sesión
#   - Chromium a pantalla completa (modo quiosco) con la interfaz
# Uso (en la Pi):  bash ~/prisma/software/instalacion/04_interfaz.sh
#                  bash ~/prisma/software/instalacion/04_interfaz.sh --quitar   (vuelve al escritorio normal)
set -euo pipefail
SERV="$HOME/.config/systemd/user/prisma.service"
AUTO="$HOME/.config/labwc/autostart"

if [[ "${1:-}" == "--quitar" ]]; then
    systemctl --user disable --now prisma.service 2>/dev/null || true
    if [ -f "$AUTO.antes_de_prisma" ]; then mv "$AUTO.antes_de_prisma" "$AUTO"; else rm -f "$AUTO"; fi
    echo "Quitado. Al reiniciar volverá el escritorio normal."
    exit 0
fi

echo "== 0/3 Avatar =="
# El retrato animado de muestra va en el repositorio. Para preparar el tuyo hacen falta numpy y Pillow
# (herramientas/prepara_retrato.py). Un personaje 3D propio (VRM) se usa si está en ~/.config/prisma/avatar.vrm
sudo apt-get -y install python3-numpy python3-pil >/dev/null && echo "   Listo"

echo "== 1/3 Servicio de Prisma =="
mkdir -p "$(dirname "$SERV")"
cat > "$SERV" <<CFG
[Unit]
Description=Prisma (servidor de la interfaz)
After=network-online.target

[Service]
ExecStart=/usr/bin/python3 $HOME/prisma/software/servidor.py
Restart=on-failure
RestartSec=3

[Install]
WantedBy=default.target
CFG
systemctl --user daemon-reload
systemctl --user enable --now prisma.service
sleep 2
systemctl --user is-active --quiet prisma.service && echo "   En marcha" || echo "   No arranca: journalctl --user -u prisma -n 30"

echo "== 2/3 Chromium en modo quiosco al iniciar la sesión =="
NAV=$(command -v chromium || command -v chromium-browser)
mkdir -p "$(dirname "$AUTO")"
if [ -f "$AUTO" ] && ! grep -q "Prisma" "$AUTO"; then cp "$AUTO" "$AUTO.antes_de_prisma"; fi
cat > "$AUTO" <<CFG
# Prisma: solo la interfaz a pantalla completa (sin barra de tareas ni escritorio).
# Para volver al escritorio normal: bash ~/prisma/software/instalacion/04_interfaz.sh --quitar
$NAV --kiosk --noerrdialogs --disable-infobars --no-first-run --password-store=basic \\
  --disable-session-crashed-bubble --check-for-update-interval=31536000 \\
  --user-data-dir=$HOME/.config/prisma/chromium http://127.0.0.1:8080 &
CFG

echo "== 3/3 Comprobación =="
curl -fs http://127.0.0.1:8080/api/estado && echo || echo "   El servidor aún arranca; espera unos segundos"
echo
echo "Hecho. Reinicia para verlo:  sudo reboot"
echo "Salir del modo quiosco: Alt+F4 con un teclado, o por SSH: pkill chromium"
