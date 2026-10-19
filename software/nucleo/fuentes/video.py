"""Vídeos de YouTube en la pantalla.

Busca con SearXNG (buscador «youtube», ya instalado) y, si no da nada, con yt-dlp. La pantalla los
reproduce con el reproductor de YouTube incrustado: con el dedo se pausa, se adelanta y se cierra.
Si un vídeo no deja verse fuera de YouTube, la pantalla salta solo al siguiente resultado.
"""
import json, re, shutil, subprocess, urllib.parse, urllib.request
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


def _ytdlp(consulta, n):
    if not shutil.which("yt-dlp"):
        return []
    try:
        p = subprocess.run(["yt-dlp", "--flat-playlist", "-J", f"ytsearch{n}:{consulta}"],
                           capture_output=True, text=True, timeout=15)
        datos = json.loads(p.stdout)
    except Exception:
        return []
    return [{"id": e["id"], "titulo": e.get("title", ""), "canal": e.get("channel") or e.get("uploader", ""),
             "duracion": ""} for e in datos.get("entries", []) if e.get("id")]
