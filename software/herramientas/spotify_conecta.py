#!/usr/bin/env python3
"""Prisma — conecta tu cuenta de Spotify (una sola vez).

Antes, en https://developer.spotify.com/dashboard (con tu cuenta Premium):
  Create app → nombre «Prisma», descripción cualquiera,
  Redirect URI:  https://pepventura.github.io/Prisma/spotify/   (exactamente así)
  API: marca «Web API» → Save. Copia el «Client ID».

Después, en la Pi:
  python3 ~/prisma/software/herramientas/spotify_conecta.py
Pega el Client ID, abre el enlace en el navegador del portátil, acepta, y pega aquí el código
que te enseña la página de vuelta.
"""
import os, sys, urllib.parse
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from nucleo.fuentes import musica

print(__doc__)
client_id = (sys.argv[1] if len(sys.argv) > 1 else input("Client ID: ")).strip()
url, verificador = musica.empieza_conexion(client_id)
print("\n1) Abre este enlace en el navegador (en el portátil vale) y pulsa «Aceptar»:\n")
print("   " + url + "\n")
print("2) Te llevará a una página de Prisma con un código.")
vuelta = input("   Cópialo y pégalo aquí: ").strip()
q = urllib.parse.parse_qs(urllib.parse.urlparse(vuelta).query) if "://" in vuelta else {"code": [vuelta]}
if "error" in q:
    sys.exit("Spotify respondió: " + q["error"][0])
if "code" not in q:
    sys.exit("No veo «code=» en esa dirección. Vuelve a ejecutar el programa.")
musica.termina_conexion(client_id, q["code"][0], verificador)
print("\nConectado. Comprobando…")
try:
    e = musica.estado()
    print("   Suena:", e.get("nombre") or "nada ahora mismo")
    d = musica._prisma()
    print("   Altavoz «Prisma»:", "visible" if d else "no aparece todavía: elígelo una vez en la app de Spotify")
except Exception as ex:
    print("   Aviso:", ex)
print("Listo. Reinicia la pantalla:  systemctl --user restart prisma")
