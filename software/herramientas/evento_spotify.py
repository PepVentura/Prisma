#!/usr/bin/env python3
"""Prisma — aviso de Spotify Connect. raspotify (librespot) lo ejecuta en cada evento
(LIBRESPOT_ONEVENT) con los datos en variables de entorno, y lo pasa al servidor de la pantalla."""
import json, os, urllib.request

CLAVES = ["PLAYER_EVENT", "NAME", "ARTISTS", "ALBUM", "COVERS", "DURATION_MS", "POSITION_MS", "USER_NAME", "TRACK_ID"]
datos = {k.lower(): os.environ[k] for k in CLAVES if k in os.environ}
try:
    urllib.request.urlopen(urllib.request.Request("http://127.0.0.1:8080/api/musica", json.dumps(datos).encode(),
                                                  {"Content-Type": "application/json"}), timeout=2)
except Exception:
    pass            # la pantalla puede no estar en marcha: la música sigue igual
