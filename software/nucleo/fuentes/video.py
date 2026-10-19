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


# YouTube ya casi no da vídeo y sonido juntos: se piden por separado (H.264 + AAC, hasta 720p, lo que la
# Pi decodifica con soltura) y ffmpeg los une al vuelo para la pantalla (ver junta()).
_FORMATO = ("bv*[height<=720][vcodec^=avc1]+ba[acodec^=mp4a]/bv*[height<=720][vcodec^=avc1]+ba/"
            "bv*[height<=720]+ba/b[height<=720]/bv*+ba/b")
_info = {}                   # id → (datos, cuándo); las direcciones de YouTube duran unas horas
_buscando = {}               # id → Event mientras yt-dlp trabaja
_cerrojo = threading.Lock()
ultimo_error = ""


def info(id_):
    """{'entradas': [(url, cabeceras)…], 'duracion'} del vídeo, o None. El navegador no lo pide a
    YouTube: el servidor de la Pi lo une con ffmpeg y se lo sirve (junta())."""
    if not re.fullmatch(r"[A-Za-z0-9_-]{11}", id_ or ""):
        return None
    with _cerrojo:
        hecho = _info.get(id_)
        en_marcha = _buscando.get(id_)
        vale = hecho and time.time() - hecho[1] < 3 * 3600
        if not en_marcha and not vale:
            _buscando[id_] = threading.Event()
    if vale:
        return hecho[0]
    if en_marcha:                          # ya lo está obteniendo prepara(): esperar a ese
        en_marcha.wait(60)
        return (_info.get(id_) or (None,))[0]
    try:
        d = _obtiene(id_)
    finally:
        with _cerrojo:
            _buscando.pop(id_).set()
    return d


def _obtiene(id_):
    global ultimo_error
    cmd = _ytdlp_cmd()
    if not cmd:
        ultimo_error = "yt-dlp no está instalado (instalacion/06_video.sh)"
        return None
    try:
        p = subprocess.run(cmd + ["-j", "-f", _FORMATO, "--no-playlist", "--no-warnings",
                                  "https://www.youtube.com/watch?v=" + id_],
                           capture_output=True, text=True, timeout=60)
        j = json.loads(p.stdout) if p.stdout.strip() else {}
    except Exception as e:
        j, p = {}, None
        ultimo_error = str(e)[:200]
    partes = j.get("requested_formats") or ([j] if j.get("url") else [])
    if not partes:
        if p is not None:
            ultimo_error = (p.stderr.strip().splitlines() or ["sin respuesta de yt-dlp"])[-1][:200]
        return None
    d = {"entradas": [(f["url"], f.get("http_headers") or j.get("http_headers") or {}) for f in partes],
         "duracion": j.get("duration") or 0}
    with _cerrojo:
        _info[id_] = (d, time.time())
    return d


def junta(d, desde=0):
    """ffmpeg une vídeo y sonido en un MP4 fragmentado que el navegador reproduce mientras llega.
    desde: segundo por el que empezar (para adelantar se vuelve a pedir desde otro punto)."""
    cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-nostdin"]
    for url, cab in d["entradas"]:
        texto = "".join(f"{k}: {v}\r\n" for k, v in cab.items() if k.lower() != "user-agent")
        cmd += ["-reconnect", "1", "-reconnect_streamed", "1", "-reconnect_delay_max", "4"]
        if cab.get("User-Agent"):
            cmd += ["-user_agent", cab["User-Agent"]]
        if texto:
            cmd += ["-headers", texto]
        if desde > 0:
            cmd += ["-ss", f"{desde:.1f}"]
        cmd += ["-i", url]
    if len(d["entradas"]) > 1:
        cmd += ["-map", "0:v:0", "-map", "1:a:0"]
    cmd += ["-c", "copy", "-avoid_negative_ts", "make_zero", "-f", "mp4",
            "-movflags", "frag_keyframe+empty_moov+default_base_moof", "pipe:1"]
    return subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)


def prepara(id_):
    """Empieza a obtener el vídeo en segundo plano (mientras Prisma contesta)."""
    threading.Thread(target=info, args=(id_,), daemon=True).start()


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
