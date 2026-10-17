#!/usr/bin/env bash
# Prisma — paso 2: IA local (Ollama + modelos candidatos) y buscador SearXNG.
# Uso (en la Pi):  bash ~/prisma/software/instalacion/02_ia.sh [--gemma]
#   --gemma  descarga también gemma4:e2b (≈5 GB más; necesita tarjeta de 64 GB)
set -euo pipefail

MODELOS=(qwen3.5:2b qwen3:1.7b qwen2.5:3b)
[[ "${1:-}" == "--gemma" ]] && MODELOS+=(gemma4:e2b)
CONF="$HOME/.config/prisma"
mkdir -p "$CONF/searxng"

echo "== 1/4 Ollama =="
# Se reinstala si falta el programa o el servicio (p. ej. si se cortó la conexión a mitad)
if ! command -v ollama > /dev/null || ! systemctl cat ollama.service > /dev/null 2>&1; then
    curl -fsSL https://ollama.com/install.sh | sh
fi
# Modelo siempre cargado en memoria y solo accesible desde la propia Pi
sudo mkdir -p /etc/systemd/system/ollama.service.d
sudo tee /etc/systemd/system/ollama.service.d/prisma.conf > /dev/null <<'CFG'
[Service]
Environment="OLLAMA_KEEP_ALIVE=-1"
Environment="OLLAMA_HOST=127.0.0.1:11434"
Environment="OLLAMA_MAX_LOADED_MODELS=1"
CFG
sudo systemctl daemon-reload
sudo systemctl restart ollama
sleep 3

echo "== 2/4 Modelos candidatos: ${MODELOS[*]} =="
for m in "${MODELOS[@]}"; do ollama pull "$m"; done

echo "== 3/4 Docker =="
if ! command -v docker > /dev/null || ! systemctl cat docker.service > /dev/null 2>&1; then
    curl -fsSL https://get.docker.com | sh
    sudo usermod -aG docker "$USER"
fi

echo "== 4/4 SearXNG (solo accesible desde la Pi, puerto 8888) =="
if [ ! -f "$CONF/searxng/settings.yml" ]; then
    CLAVE=$(openssl rand -hex 32)
    sed "s/CAMBIAR_CLAVE/$CLAVE/" "$HOME/prisma/software/config/searxng_settings.yml" > "$CONF/searxng/settings.yml"
fi
sudo docker rm -f searxng > /dev/null 2>&1 || true
sudo docker run -d --name searxng --restart unless-stopped \
    -p 127.0.0.1:8888:8080 \
    -v "$CONF/searxng:/etc/searxng" \
    docker.io/searxng/searxng:latest
sleep 8
if curl -fs "http://127.0.0.1:8888/search?q=Donostia&format=json" > /dev/null; then
    echo "   SearXNG responde"
else
    echo "   SearXNG aún arrancando; prueba en un minuto: curl 'http://127.0.0.1:8888/search?q=test&format=json'"
fi

echo
echo "Hecho. Prueba los modelos con:"
echo "   python3 ~/prisma/software/herramientas/prueba_ia.py --comparar"
