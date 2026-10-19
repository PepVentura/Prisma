#!/usr/bin/env python3
"""Prisma — diagnóstico de los vídeos de YouTube. Uso:  python3 ~/prisma/software/herramientas/prueba_video.py [ID]"""
import os, shutil, subprocess, sys, time
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from nucleo.fuentes import video

vid = sys.argv[1] if len(sys.argv) > 1 else "aqz-KE-bpKQ"
cmd = video._ytdlp_cmd()
print("yt-dlp:", cmd)
if cmd:
    print("versión:", subprocess.run([cmd[0], "--version"], capture_output=True, text=True).stdout.strip())
deno = os.path.expanduser("~/.deno/bin/deno")
print("ffmpeg:", shutil.which("ffmpeg") or "NO (sudo apt install ffmpeg)")
print("deno:", subprocess.run([deno, "--version"], capture_output=True, text=True).stdout.split("\n")[0] if os.path.isfile(deno) else "NO")
print("\nBúsqueda «gatos»:", [v["titulo"][:40] for v in video.busca("gatos", 3)] or "nada")
t = time.time()
d = video.info(vid)
print(f"\nyt-dlp con el vídeo {vid}: {'bien' if d else 'FALLA'} ({time.time() - t:.1f} s)")
if not d:
    print("   error:", video.ultimo_error)
    sys.exit(1)
print("   partes:", len(d["entradas"]), "· duración:", d["duracion"], "s")
t = time.time()
proc = video.junta(d)
datos = proc.stdout.read(512 * 1024)
proc.kill()
print(f"ffmpeg uniendo vídeo y sonido: {'bien' if len(datos) > 100_000 else 'FALLA'} "
      f"({len(datos) // 1024} KB en {time.time() - t:.1f} s)")
print("\nSi todo pone «bien», el vídeo debería verse en la pantalla.")
