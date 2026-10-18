#!/usr/bin/env python3
"""Prisma en la pantalla: servidor local de la interfaz.

  python3 ~/prisma/software/servidor.py            sirve http://127.0.0.1:8080 (solo para la propia Pi)

La interfaz (interfaz/index.html) se abre en Chromium a pantalla completa al arrancar
(ver instalacion/04_interfaz.sh). Las preguntas llegan por POST /api/preguntar y la respuesta
vuelve en streaming (Server-Sent Events): estado, trozos de texto y fin.
"""
import argparse, json, mimetypes, os, sys, threading, time, urllib.error
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from nucleo.config import CONFIG
from nucleo.asistente import Asistente
from nucleo import memoria
from nucleo.fuentes import tiempo

RAIZ = os.path.join(os.path.dirname(os.path.abspath(__file__)), "interfaz")
asistente = Asistente()
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

    def do_GET(self):
        if self.path == "/api/estado":
            m = memoria.carga()
            return self._json({"listo": estado["listo"], "error": estado["error"], "modelo": CONFIG["modelo"],
                               "nombre": m.get("nombre"), "ciudad": CONFIG["ciudad"]})
        if self.path == "/api/tiempo":
            try:
                return self._json({"texto": tiempo.responde(0, CONFIG["ciudad"])})
            except Exception as e:
                return self._json({"texto": None, "error": str(e)})
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

    def do_POST(self):
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
    print(f"Prisma en http://127.0.0.1:{a.puerto}")
    ThreadingHTTPServer(("127.0.0.1", a.puerto), Manejador).serve_forever()


if __name__ == "__main__":
    main()
