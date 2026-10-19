#!/usr/bin/env bash
# Prisma — paso 7: vídeos de YouTube.
# yt-dlp oficial (el de los repositorios se queda viejo y YouTube cambia a menudo) y Deno, que yt-dlp
# necesita para YouTube desde finales de 2025. Ambos en tu carpeta personal; no tocan el sistema.
# Uso (en la Pi):  bash ~/prisma/software/instalacion/06_video.sh     (vuelve a ejecutarlo para actualizar)
set -euo pipefail
mkdir -p "$HOME/.local/bin"

echo "== 1/3 yt-dlp =="
curl -fL --retry 3 -o "$HOME/.local/bin/yt-dlp" \
  https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp_linux_aarch64
chmod +x "$HOME/.local/bin/yt-dlp"
"$HOME/.local/bin/yt-dlp" --version

echo "== 2/3 Deno =="
if [ -x "$HOME/.deno/bin/deno" ]; then "$HOME/.deno/bin/deno" upgrade -q || true
else curl -fsSL https://deno.land/install.sh | sh -s -- -y --no-modify-path; fi
"$HOME/.deno/bin/deno" --version | head -1

echo "== 3/3 Prueba =="
if "$HOME/.local/bin/yt-dlp" --js-runtimes "deno:$HOME/.deno/bin/deno" -g -f "18/best" --no-warnings \
     "https://www.youtube.com/watch?v=aqz-KE-bpKQ" >/dev/null; then
    echo "   YouTube responde"
else
    echo "   No consigo un vídeo de prueba: mira el mensaje de arriba"
fi
systemctl --user restart prisma 2>/dev/null || true
echo "Hecho. Prueba: «pon un vídeo de recetas de bacalao»."
