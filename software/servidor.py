#!/usr/bin/env python3
"""Prisma en la pantalla: servidor local de la interfaz.

  python3 ~/prisma/software/servidor.py            sirve http://127.0.0.1:8080 (solo para la propia Pi)

La interfaz (interfaz/index.html) se abre en Chromium a pantalla completa al arrancar
(ver instalacion/04_interfaz.sh). Las preguntas llegan por POST /api/preguntar y la respuesta
vuelve en streaming (Server-Sent Events): estado, trozos de texto y fin.
"""
import argparse, html, json, mimetypes, os, re, sys, threading, time, urllib.error, urllib.parse, urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from nucleo.config import CONFIG
from nucleo.asistente import Asistente
from nucleo import memoria
from nucleo.fuentes import tiempo
from nucleo.fuentes import musica as spotify
from nucleo.fuentes import video
from nucleo.fuentes import local

RAIZ = os.path.join(os.path.dirname(os.path.abspath(__file__)), "interfaz")
asistente = Asistente()
RETRATO_PROPIO = os.path.expanduser("~/.config/prisma/retrato")
RETRATO_MUESTRA = os.path.join(RAIZ, "retrato_muestra")


# Lo que suena en Spotify Connect (lo cuenta librespot en cada evento)
musica = {"estado": None, "cuando": 0.0}


def musica_evento(ev):
    tipo = ev.get("player_event", "")
    if tipo == "track_changed":
        musica.update(nombre=ev.get("name"), artistas=(ev.get("artists") or "").replace("\n", ", "),
                      album=ev.get("album"), portada=(ev.get("covers") or "").split("\n")[0] or None,
                      duracion_ms=int(ev.get("duration_ms") or 0), posicion_ms=0, cuando=time.time())
    elif tipo in ("playing", "paused", "seeked", "position_correction"):
        musica.update(estado="sonando" if tipo != "paused" else "pausa",
                      posicion_ms=int(ev.get("position_ms") or 0), cuando=time.time())
        if tipo in ("seeked", "position_correction"):
            musica["estado"] = musica.get("estado_previo", "sonando")
    elif tipo in ("stopped", "session_disconnected"):
        musica.update(estado="parada" if tipo == "stopped" else None, cuando=time.time())
    elif tipo == "session_connected":
        musica.update(estado="conectado", usuario=ev.get("user_name"), cuando=time.time())
    if musica.get("estado") in ("sonando", "pausa"):
        musica["estado_previo"] = musica["estado"]


_cache_musica = {"t": 0.0, "datos": None}
_pendiente_spotify = {}


def musica_pantalla():
    """Con la API de Spotify conectada: lo que suena en la cuenta (y se puede controlar).
    Sin ella: lo que cuenta raspotify cuando suena en Prisma."""
    if spotify.configurado():
        if time.time() - _cache_musica["t"] > 1.5:
            try:
                _cache_musica.update(t=time.time(), datos=spotify.estado())
            except Exception as e:
                _cache_musica.update(t=time.time(), datos={**musica_actual(), "api": True, "error": str(e)[:120]})
        return _cache_musica["datos"]
    return musica_actual()


def musica_actual():
    m = dict(musica)
    if m.get("estado") == "sonando":           # posición estimada desde el último aviso
        m["posicion_ms"] = m.get("posicion_ms", 0) + int((time.time() - m["cuando"]) * 1000)
    return m


def comprueba_casa():
    """¿Responde Home Assistant y deja mostrarse dentro de la pantalla de Prisma?"""
    url = CONFIG.get("home_assistant")
    if not url:
        return {"ok": False, "motivo": "sin_url"}
    try:
        with urllib.request.urlopen(url, timeout=3) as r:
            xfo = (r.headers.get("X-Frame-Options") or "").upper()
            return {"ok": not xfo, "motivo": "marcos" if xfo else None, "url": url}
    except Exception as e:
        return {"ok": False, "motivo": "no_responde", "url": url, "detalle": str(e)[:120]}


def tipo_avatar():
    """Retrato animado propio > personaje 3D propio > retrato de muestra."""
    if os.path.isfile(os.path.join(RETRATO_PROPIO, "retrato.json")):
        return "retrato"
    if os.path.isfile(os.path.expanduser("~/.config/prisma/avatar.vrm")):
        return "vrm"
    return "retrato"
estado = {"listo": False, "error": None}


def calienta():
    while not estado["listo"]:
        try:
            asistente.calienta()
            estado.update(listo=True, error=None)
        except urllib.error.URLError as e:          # Ollama aún arrancando tras encender la Pi
            estado["error"] = str(e)
            time.sleep(3)


class Manejador(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _json(self, datos, codigo=200):
        cuerpo = json.dumps(datos, ensure_ascii=False).encode()
        self.send_response(codigo)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(cuerpo)))
        self.end_headers()
        self.wfile.write(cuerpo)

    def _html(self, cuerpo, codigo=200):
        pagina = ('<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width">'
                  '<title>Prisma · Spotify</title><body style="font:18px system-ui;max-width:640px;margin:60px auto;'
                  'padding:0 20px;background:#07090d;color:#e9eff4;line-height:1.5">' + cuerpo).encode()
        self.send_response(codigo)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(pagina)))
        self.end_headers()
        self.wfile.write(pagina)

    def _spotify(self):
        """Conectar Spotify desde el navegador (en el portátil, con un túnel SSH al puerto 8080 de la Pi):
        /spotify/conectar → Spotify pide permiso → vuelve a /spotify?code=… y se guarda solo."""
        u = urllib.parse.urlparse(self.path)
        q = urllib.parse.parse_qs(u.query)
        if u.path == "/spotify/conectar":
            cid = (q.get("client_id") or [""])[0].strip()
            codigo = (q.get("codigo") or [""])[0].strip()
            if codigo:                                   # paso 3: el código copiado de la página de vuelta
                if not _pendiente_spotify:
                    return self._html('<h2>Empieza de nuevo</h2><p><a style="color:#22d3ee" href="/spotify/conectar">Conectar Spotify</a></p>')
                codigo = urllib.parse.parse_qs(urllib.parse.urlparse(codigo).query).get("code", [codigo])[0]
                try:
                    spotify.termina_conexion(_pendiente_spotify["client_id"], codigo, _pendiente_spotify["verificador"])
                    _pendiente_spotify.clear()
                    _cache_musica["t"] = 0
                    return self._html("<h2>✓ Spotify conectado</h2><p>Ya puedes cerrar esta página. En Prisma, pulsa "
                                      "«Música» o escribe «pon …». Si dice que no encuentra el altavoz, elige «Prisma» "
                                      "una vez en la app de Spotify.</p>")
                except Exception as e:
                    return self._html(f"<h2>No se pudo conectar</h2><p>{html.escape(str(e))}</p>"
                                      '<p><a style="color:#22d3ee" href="/spotify/conectar">Volver a intentarlo</a></p>')
            if not cid:                                  # paso 1: Client ID
                return self._html('<h2>Conectar Spotify</h2><form><p>Client ID de tu app de Spotify:</p>'
                                  '<input name="client_id" size="36" autofocus style="font:18px monospace;padding:8px">'
                                  ' <button style="font:18px system-ui;padding:8px 16px">Siguiente</button></form>')
            url, verificador = spotify.empieza_conexion(cid)     # paso 2: permiso en Spotify (otra pestaña)
            _pendiente_spotify.update(client_id=cid, verificador=verificador)
            return self._html('<h2>Conectar Spotify</h2>'
                              f'<p>1. <a style="color:#22d3ee" target="_blank" href="{html.escape(url)}">Abre Spotify y pulsa «Aceptar»</a> '
                              '(se abre en otra pestaña).</p><p>2. Te llevará a una página de Prisma con un código. '
                              'Cópialo y pégalo aquí:</p><form><input name="codigo" size="40" autofocus '
                              'style="font:18px monospace;padding:8px"> <button style="font:18px system-ui;padding:8px 16px">'
                              'Conectar</button></form>')
        return self._html('<h2>Conectar Spotify</h2><p><a style="color:#22d3ee" href="/spotify/conectar">Empezar</a></p>')

    def do_GET(self):
        if self.path.startswith("/spotify"):
            return self._spotify()
        if self.path == "/api/estado":
            m = memoria.carga()
            return self._json({"listo": estado["listo"], "error": estado["error"], "modelo": CONFIG["modelo"],
                               "nombre": m.get("nombre"), "ciudad": CONFIG["ciudad"],
                               "home_assistant": CONFIG.get("home_assistant")})
        if self.path == "/api/musica":
            return self._json(musica_pantalla())
        if self.path.startswith("/api/video?"):
            vid = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query).get("id", [""])[0]
            d = video.info(vid)
            return self._json({"ok": bool(d), "url": "/api/video/flujo?id=" + vid if d else None,
                               "duracion": d["duracion"] if d else 0, "error": None if d else video.ultimo_error})
        if self.path.startswith("/api/video/flujo?"):
            q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            try:
                desde = max(0.0, float(q.get("t", ["0"])[0]))
            except ValueError:
                desde = 0.0
            return self._flujo_video(q.get("id", [""])[0], desde)
        if self.path.startswith("/api/local/"):
            return self._local()
        if self.path == "/api/casa":
            return self._json(comprueba_casa())
        if self.path == "/api/tiempo":
            try:
                return self._json({"texto": tiempo.responde(0, CONFIG["ciudad"])})
            except Exception as e:
                return self._json({"texto": None, "error": str(e)})
        if self.path == "/avatar.vrm":
            return self._avatar()
        if self.path == "/api/avatar":
            return self._json({"tipo": tipo_avatar()})
        if self.path.startswith("/retrato/"):
            return self._retrato(self.path[len("/retrato/"):].split("?")[0])
        ruta = "index.html" if self.path in ("/", "") else self.path.lstrip("/").split("?")[0]
        fichero = os.path.realpath(os.path.join(RAIZ, ruta))
        if not fichero.startswith(os.path.realpath(RAIZ)) or not os.path.isfile(fichero):
            self.send_error(404)
            return
        with open(fichero, "rb") as f:
            cuerpo = f.read()
        self.send_response(200)
        self.send_header("Content-Type", (mimetypes.guess_type(fichero)[0] or "text/plain") + "; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(cuerpo)

    def _retrato(self, nombre):
        carpeta = RETRATO_PROPIO if os.path.isfile(os.path.join(RETRATO_PROPIO, "retrato.json")) else RETRATO_MUESTRA
        f = os.path.realpath(os.path.join(carpeta, nombre))
        if not f.startswith(os.path.realpath(carpeta) + os.sep) or not os.path.isfile(f):
            return self.send_error(404)
        with open(f, "rb") as fh:
            cuerpo = fh.read()
        self.send_response(200)
        self.send_header("Content-Type", mimetypes.guess_type(f)[0] or "application/octet-stream")
        self.send_header("Content-Length", str(len(cuerpo)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(cuerpo)

    def _flujo_video(self, vid, desde=0.0):
        """Vídeo de YouTube para la pantalla: ffmpeg une vídeo y sonido (con las cabeceras de yt-dlp)
        en un MP4 fragmentado que se envía según llega. Para adelantar, la pantalla lo pide desde otro segundo."""
        d = video.info(vid)
        if not d:
            return self.send_error(404)
        proc = video.junta(d, desde)
        self.send_response(200)
        self.send_header("Content-Type", "video/mp4")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        try:
            while True:
                trozo = proc.stdout.read(64 * 1024)
                if not trozo:
                    break
                self.wfile.write(trozo)
        except (BrokenPipeError, ConnectionResetError):
            pass                                  # la pantalla cerró el vídeo o saltó a otro punto
        finally:
            proc.kill()
            proc.wait()

    def _local(self):
        """Música y vídeos de la Pi: biblioteca, ficheros (con rangos, para adelantar), portadas y miniaturas."""
        u = urllib.parse.urlparse(self.path)
        q = urllib.parse.parse_qs(u.query)
        id_ = (q.get("id") or [""])[0]
        if u.path == "/api/local/biblioteca":
            b = local.indexa()
            return self._json({"albumes": local.albumes(), "canciones": {c["id"]: local.publico(c) for c in b["canciones"]},
                               "videos": [local.publico(v) for v in b["videos"]]})
        if u.path == "/api/local/portada":
            img = local.portada(id_)
            return self._binario(*img) if img else self.send_error(404)
        if u.path == "/api/local/miniatura":
            img = local.miniatura(id_)
            return self._binario(img, "image/jpeg") if img else self.send_error(404)
        if u.path == "/api/local/info":
            return self._json({"duracion": local.duracion(id_)})
        x = local.elemento(id_)
        if not x:
            return self.send_error(404)
        if u.path == "/api/local/archivo":
            return self._fichero_rangos(x["ruta"])
        if u.path == "/api/local/remux":
            try:
                desde = max(0.0, float((q.get("t") or ["0"])[0]))
            except ValueError:
                desde = 0.0
            proc = local.remux(id_, desde)
            self.send_response(200)
            self.send_header("Content-Type", "video/mp4")
            self.end_headers()
            try:
                while True:
                    trozo = proc.stdout.read(64 * 1024)
                    if not trozo:
                        break
                    self.wfile.write(trozo)
            except (BrokenPipeError, ConnectionResetError):
                pass
            finally:
                proc.kill()
                proc.wait()
            return
        self.send_error(404)

    def _binario(self, datos, tipo):
        self.send_response(200)
        self.send_header("Content-Type", tipo)
        self.send_header("Content-Length", str(len(datos)))
        self.send_header("Cache-Control", "max-age=86400")
        self.end_headers()
        self.wfile.write(datos)

    def _fichero_rangos(self, ruta):
        """Sirve un fichero respetando «Range» (el navegador lo usa para adelantar y para empezar rápido)."""
        total = os.path.getsize(ruta)
        tipo = mimetypes.guess_type(ruta)[0] or "application/octet-stream"
        if ruta.lower().endswith((".mkv", ".webm")):
            tipo = "video/webm"
        ini, fin = 0, total - 1
        m = re.match(r"bytes=(\d*)-(\d*)", self.headers.get("Range") or "")
        if m and (m.group(1) or m.group(2)):
            if m.group(1):
                ini = int(m.group(1))
                fin = int(m.group(2)) if m.group(2) else total - 1
            else:
                ini = max(0, total - int(m.group(2)))
            fin = min(fin, total - 1)
            if ini > fin:
                self.send_response(416)
                self.send_header("Content-Range", f"bytes */{total}")
                self.end_headers()
                return
            self.send_response(206)
            self.send_header("Content-Range", f"bytes {ini}-{fin}/{total}")
        else:
            self.send_response(200)
        self.send_header("Content-Type", tipo)
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Content-Length", str(fin - ini + 1))
        self.end_headers()
        try:
            with open(ruta, "rb") as f:
                f.seek(ini)
                quedan = fin - ini + 1
                while quedan > 0:
                    trozo = f.read(min(256 * 1024, quedan))
                    if not trozo:
                        break
                    self.wfile.write(trozo)
                    quedan -= len(trozo)
        except (BrokenPipeError, ConnectionResetError):
            pass

    def _avatar(self):
        """Tu personaje en ~/.config/prisma/avatar.vrm; si no, el de muestra que descarga 04_interfaz.sh."""
        for f in (os.path.expanduser("~/.config/prisma/avatar.vrm"), os.path.join(RAIZ, "modelos", "muestra.vrm")):
            if os.path.isfile(f):
                self.send_response(200)
                self.send_header("Content-Type", "model/gltf-binary")
                self.send_header("Content-Length", str(os.path.getsize(f)))
                self.send_header("Cache-Control", "max-age=3600")
                self.end_headers()
                with open(f, "rb") as fh:
                    self.wfile.write(fh.read())
                return
        self.send_error(404)

    def do_POST(self):
        if self.path == "/api/local/estado":
            d = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
            local.informa(d.get("medio"), d.get("sonando"))
            return self._json({"ok": True})
        if self.path == "/api/musica/accion":
            # Botones del panel de música (API de Spotify)
            d = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
            try:
                v = spotify.accion(d.get("accion"), d.get("valor"))
                _cache_musica["t"] = 0
                return self._json({"ok": True, "valor": v})
            except Exception as e:
                return self._json({"ok": False, "error": str(e)[:200]})
        if self.path == "/api/musica":
            # Avisos de Spotify Connect (raspotify → herramientas/evento_spotify.py), solo desde la propia Pi
            if self.client_address[0] != "127.0.0.1":
                return self.send_error(403)
            ev = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
            musica_evento(ev)
            return self._json({"ok": True})
        if self.path != "/api/preguntar":
            self.send_error(404)
            return
        datos = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
        texto = (datos.get("texto") or "").strip()[:500]
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        try:
            for ev in asistente.procesa(texto):
                self.wfile.write(f"data: {json.dumps(ev, ensure_ascii=False)}\n\n".encode())
                self.wfile.flush()
        except (BrokenPipeError, ConnectionResetError):
            pass
        except Exception as e:
            fallo = {"tipo": "fin", "accion": "error", "detalle": str(e), "primera": 0, "total": 0,
                     "texto": "Algo ha fallado. Inténtalo otra vez."}
            self.wfile.write(f"data: {json.dumps(fallo, ensure_ascii=False)}\n\n".encode())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--puerto", type=int, default=8080)
    a = ap.parse_args()
    threading.Thread(target=calienta, daemon=True).start()
    threading.Thread(target=local.indexa, daemon=True).start()     # la biblioteca, lista antes de pedirla
    print(f"Prisma en http://127.0.0.1:{a.puerto}")
    ThreadingHTTPServer(("127.0.0.1", a.puerto), Manejador).serve_forever()


if __name__ == "__main__":
    main()
