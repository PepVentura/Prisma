#!/usr/bin/env bash
# Prisma — paso 3: ajusta SearXNG para respuestas rápidas y deja listo el núcleo por texto.
# Uso (en la Pi):  bash ~/prisma/software/instalacion/03_nucleo.sh
set -euo pipefail
AJ="$HOME/.config/prisma/searxng/settings.yml"
[ -f "$AJ" ] || { echo "No encuentro $AJ: ejecuta antes 02_ia.sh"; exit 1; }

echo "== Tiempos de espera de SearXNG =="
if ! grep -q "^outgoing:" "$AJ"; then
    cat >> "$AJ" <<'CFG'
outgoing:
  request_timeout: 1.5
  max_request_timeout: 3.0
CFG
    echo "   Añadidos (1,5 s por buscador)"
else
    echo "   Ya estaban"
fi
sudo docker restart searxng > /dev/null
sleep 6
curl -fs "http://127.0.0.1:8888/search?q=Donostia&format=json" > /dev/null && echo "   SearXNG responde" \
    || echo "   SearXNG aún arrancando; espera un minuto"

echo "== Modelo siempre cargado =="
curl -fs http://127.0.0.1:11434/api/generate -d '{"model":"qwen3:1.7b","keep_alive":-1}' > /dev/null && echo "   qwen3:1.7b cargado"

echo
echo "Hecho. Prueba Prisma por texto con:"
echo "   python3 ~/prisma/software/prisma_texto.py --tiempos"
