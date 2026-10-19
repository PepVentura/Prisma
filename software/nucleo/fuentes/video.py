"""Vídeos de YouTube en la pantalla.

Busca con SearXNG (buscador «youtube», ya instalado) y, si no da nada, con yt-dlp. El vídeo no usa el
reproductor de YouTube (fallaba con «Vídeo no disponible» y sus enlaces sacaban de Prisma): yt-dlp
obtiene la dirección directa del vídeo y la pantalla lo reproduce con un reproductor propio.
yt-dlp necesita Deno para YouTube; los instala instalacion/06_video.sh.
"""
import json, os, re, shutil, subprocess, threading, time, urllib.parse, urllib.request
from ..config import CONFIG
from ..texto import normaliza

_ID = re.compile(r"(?:v=|youtu\.be/|/shorts/|/embed/)([A-Za-z0-9_-]{11})")
_PIDE = [
    re.compile(r"^(?:pon(?:me)?|reproduce|ensename|muestrame|quiero ver|busca(?:me)?)\s+(?:un |el )?(?:video|videos)\s+(?:de |del |sobre |con )?(.+)$"),
    re.compile(r"^(?:pon(?:me)?|reproduce|busca(?:me)?|quiero ver)\s+(.+?)\s+(?:en|de) youtube$"),
    re.compile(r"^(?:pon(?:me)?|busca(?:me)?|abre)\s+(?:en )?youtube\s+(.+)$"),
    re.compile(r"^youtube\s+(.+)$"),
]
_CIERRA = re.compile(r"^(?:cierra|quita|para|deten|apaga)\s+(?:el |los )?(?:video|youtube)s?$")


def entiende(texto):
    """('buscar', consulta) · ('cerrar', None) · None."""
    n = normaliza(texto).strip(" ?¿!¡.,")
    n = re.sub(r"^(?:oye[, ]+)?(?:prisma|ordenador)[, ]+", "", n)
    if _CIERRA.match(n):
        return "cerrar", None
    for p in _PIDE:
        m = p.match(n)
        if m:
            return "buscar", _original(texto, m.group(1))
    return None


def _original(texto, trozo):
    """El trozo con sus tildes y mayúsculas, sacado del texto tal como se escribió."""
    t = normaliza(texto)
    i = t.find(trozo)
    return texto[i:i + len(trozo)] if i >= 0 else trozo


def busca(consulta, n=6):
    """Lista de {'id', 'titulo', 'canal', 'duracion'}."""
    vistos, salida = set(), []
    for r in _searxng(consulta) or _ytdlp(consulta, n):
        if r["id"] not in vistos:
            vistos.add(r["id"])
            salida.append(r)
    return salida[:n]


def _searxng(consulta):
    q = {"q": consulta, "format": "json", "engines": "youtube", "language": "es-ES"}
    try:
        with urllib.request.urlopen(CONFIG["searxng"] + "/search?" + urllib.parse.urlencode(q), timeout=5) as r:
            res = json.load(r).get("results", [])
    except Exception:
        return []
    salida = []
    for x in res:
        m = _ID.search(x.get("url", ""))
        if m:
            salida.append({"id": m.group(1), "titulo": x.get("title", ""), "canal": x.get("author", ""),
                           "duracion": x.get("length", "")})
    return salida


def _ytdlp_cmd():
    """yt-dlp oficial (~/.local/bin, se actualiza solo) con Deno; si no, el del sistema."""
    exe = os.path.expanduser("~/.local/bin/yt-dlp")
    exe = exe if os.path.isfile(exe) else shutil.which("yt-dlp")
    if not exe:
        return None
    deno = os.path.expanduser("~/.deno/bin/deno")
    return [exe] + (["--js-runtimes", "deno:" + deno] if os.path.isfile(deno) else [])


# Calidad: vídeo con sonido en un solo fichero (lo que reproduce el navegador sin más), hasta 720p
_FORMATO = "best[ext=mp4][vcodec!=none][acodec!=none][height<=720]/18/best[vcodec!=none][acodec!=none][height<=720]"
_flujos = {}                 # id → (url, cuándo); las direcciones de YouTube duran unas horas
_buscando = {}               # id → Event mientras yt-dlp trabaja
_cerrojo = threading.Lock()


def flujo(id_):
    """Dirección directa del vídeo para la pantalla, o None si no se puede."""
    if not re.fullmatch(r"[A-Za-z0-9_-]{11}", id_ or ""):
        return None
    with _cerrojo:
        hecho = _flujos.get(id_)
        en_marcha = _buscando.get(id_)
        if not en_marcha and not (hecho and time.time() - hecho[1] < 3 * 3600):
            _buscando[id_] = threading.Event()
    if hecho and time.time() - hecho[1] < 3 * 3600:
        return hecho[0]
    if en_marcha:                          # ya lo está obteniendo prepara(): esperar a ese
        en_marcha.wait(45)
        return (_flujos.get(id_) or (None,))[0]
    try:
        url = _obtiene(id_)
    finally:
        with _cerrojo:
            _buscando.pop(id_).set()
    return url


def _obtiene(id_):
    cmd = _ytdlp_cmd()
    if not cmd:
        return None
    try:
        p = subprocess.run(cmd + ["-g", "-f", _FORMATO, "--no-playlist", "--no-warnings",
                                  "https://www.youtube.com/watch?v=" + id_],
                           capture_output=True, text=True, timeout=40)
        url = next((l for l in p.stdout.splitlines() if l.startswith("http")), None)
    except Exception:
        url = None
    if url:
        with _cerrojo:
            _flujos[id_] = (url, time.time())
    return url


def prepara(id_):
    """Empieza a obtener el vídeo en segundo plano (mientras Prisma contesta)."""
    threading.Thread(target=flujo, args=(id_,), daemon=True).start()


def _ytdlp(consulta, n):
    cmd = _ytdlp_cmd()
    if not cmd:
        return []
    try:
        p = subprocess.run(cmd + ["--flat-playlist", "-J", f"ytsearch{n}:{consulta}"],
                           capture_output=True, text=True, timeout=15)
        datos = json.loads(p.stdout)
    except Exception:
        return []
    return [{"id": e["id"], "titulo": e.get("title", ""), "canal": e.get("channel") or e.get("uploader", ""),
             "duracion": ""} for e in datos.get("entries", []) if e.get("id")]
