"""Música y vídeos guardados en la Pi o en un USB.

Carpetas: las de Música y Vídeos del usuario (~/Música, ~/Vídeos…) y cualquier USB o disco conectado
(/media/<usuario>/…). Se pueden añadir otras en ~/.config/prisma/nucleo.json:
    "carpetas_musica": ["/ruta"], "carpetas_video": ["/ruta"]
La biblioteca se indexa al pedirla y se guarda en ~/.config/prisma/biblioteca.json; se vuelve a
indexar sola si cambia algo en las carpetas (o con «actualiza la biblioteca»).
Los datos de cada canción salen de sus etiquetas (mutagen) o, si no tiene, de las carpetas:
Artista/Álbum/01 - Título.mp3.
"""
import difflib, glob, hashlib, json, os, random, re, subprocess, threading, time
from ..config import CONFIG
from ..texto import normaliza

try:
    import mutagen
except ImportError:                       # sin mutagen: datos sacados de las carpetas
    mutagen = None

AUDIO = {".mp3", ".flac", ".ogg", ".oga", ".opus", ".m4a", ".aac", ".wav"}
VIDEO = {".mp4", ".mkv", ".webm", ".mov", ".m4v", ".avi"}
PORTADAS = ["cover.jpg", "cover.png", "folder.jpg", "folder.png", "front.jpg", "albumart.jpg"]
FICHERO = os.path.expanduser("~/.config/prisma/biblioteca.json")
CACHE = os.path.expanduser("~/.cache/prisma")
_bib = {"canciones": [], "videos": [], "firma": None, "cuando": 0}
_cerrojo = threading.Lock()


# ------------------------------------------------------------------ carpetas e índice
def _xdg(nombre):
    try:
        r = subprocess.run(["xdg-user-dir", nombre], capture_output=True, text=True, timeout=3).stdout.strip()
        return [r] if r and r != os.path.expanduser("~") else []
    except Exception:
        return []


def carpetas():
    """(carpetas de música, carpetas de vídeo, unidades externas) que existen."""
    casa = os.path.expanduser("~")
    musica = CONFIG.get("carpetas_musica") or (_xdg("MUSIC") + [casa + "/Música", casa + "/Music"])
    videos = CONFIG.get("carpetas_video") or (_xdg("VIDEOS") + [casa + "/Vídeos", casa + "/Videos"])
    externas = glob.glob("/media/*/*") + glob.glob("/mnt/*")
    unico = lambda l: sorted({os.path.realpath(os.path.expanduser(c)) for c in l if os.path.isdir(os.path.expanduser(c))})
    return unico(musica), unico(videos), unico(externas)


def _firma():
    """Cambia si se añade o quita algo (fecha de modificación de las carpetas, dos niveles)."""
    m, v, e = carpetas()
    h = hashlib.sha1()
    for raiz in m + v + e:
        for base, dirs, _ in os.walk(raiz):
            h.update(f"{base}{os.stat(base).st_mtime}".encode())
            if base.count(os.sep) - raiz.count(os.sep) >= 2:
                dirs[:] = []
    return h.hexdigest()


def _id(ruta):
    return hashlib.sha1(ruta.encode()).hexdigest()[:12]


def _etiquetas(ruta):
    """titulo, artista, album, pista, duracion (desde las etiquetas; vacío si no hay)."""
    if not mutagen:
        return {}
    try:
        f = mutagen.File(ruta, easy=True)
        if not f:
            return {}
        g = lambda k: (f.tags.get(k) or [""])[0] if f.tags else ""
        pista = re.match(r"\d+", g("tracknumber") or "")
        return {"titulo": g("title"), "artista": g("albumartist") or g("artist"), "album": g("album"),
                "pista": int(pista.group()) if pista else 0,
                "duracion": round(getattr(f.info, "length", 0) or 0)}
    except Exception:
        return {}


def _de_ruta(ruta, raiz):
    """Artista/Álbum/01 - Título.mp3 → datos, cuando no hay etiquetas."""
    partes = os.path.relpath(ruta, raiz).split(os.sep)
    nombre = os.path.splitext(partes[-1])[0]
    m = re.match(r"^\s*(\d{1,3})[\s._-]+(.*)$", nombre)
    pista, titulo = (int(m.group(1)), m.group(2)) if m else (0, nombre)
    titulo = titulo.replace("_", " ").strip()
    artista = partes[-3] if len(partes) >= 3 else ""
    album = partes[-2] if len(partes) >= 2 else ""
    if not artista and " - " in titulo:              # suelta: «Artista - Título.mp3»
        artista, titulo = (x.strip() for x in titulo.split(" - ", 1))
        album = ""
    return {"titulo": titulo, "pista": pista, "album": album, "artista": artista}


def indexa(forzar=False):
    """Recorre las carpetas y rehace la biblioteca si ha cambiado algo."""
    with _cerrojo:
        if not _bib["firma"] and os.path.isfile(FICHERO) and not forzar:
            try:
                with open(FICHERO) as f:
                    _bib.update(json.load(f))
            except Exception:
                pass
        firma = _firma()
        if firma == _bib["firma"] and not forzar:
            return _bib
        m, v, e = carpetas()
        canciones, videos = [], []
        for raiz in m + v + e:
            for base, dirs, ficheros in os.walk(raiz):
                dirs[:] = [d for d in dirs if not d.startswith(".")]
                for nombre in ficheros:
                    ruta = os.path.join(base, nombre)
                    ext = os.path.splitext(nombre)[1].lower()
                    if ext in AUDIO and raiz not in v:
                        d = {**_de_ruta(ruta, raiz), **{k: x for k, x in _etiquetas(ruta).items() if x}}
                        canciones.append({"id": _id(ruta), "ruta": ruta, **d})
                    elif ext in VIDEO and raiz not in m:
                        titulo = os.path.splitext(nombre)[0].replace("_", " ").replace(".", " ").strip()
                        videos.append({"id": _id(ruta), "ruta": ruta, "titulo": titulo,
                                       "carpeta": os.path.basename(base)})
        canciones.sort(key=lambda c: (normaliza(c["artista"]), normaliza(c["album"]), c["pista"], normaliza(c["titulo"])))
        videos.sort(key=lambda x: normaliza(x["titulo"]))
        _bib.update(canciones=canciones, videos=videos, firma=firma, cuando=time.time())
        os.makedirs(os.path.dirname(FICHERO), exist_ok=True)
        with open(FICHERO, "w") as f:
            json.dump(_bib, f, ensure_ascii=False)
        return _bib


def elemento(id_):
    b = indexa()
    for x in b["canciones"] + b["videos"]:
        if x["id"] == id_:
            return x
    return None


def albumes():
    """[{album, artista, id_portada, canciones: [ids]}] para la pantalla."""
    grupos = {}
    for c in indexa()["canciones"]:
        clave = (c["album"] or "Sin álbum", c["artista"])
        grupos.setdefault(clave, []).append(c["id"])
    return [{"album": a, "artista": ar, "portada": ids[0], "canciones": ids} for (a, ar), ids in grupos.items()]


def publico(x):
    """Lo que ve la pantalla (sin la ruta en disco)."""
    return {k: v for k, v in x.items() if k != "ruta"}


# ------------------------------------------------------------------ portadas y miniaturas
def portada(id_):
    """Imagen (bytes, tipo) de la portada de la canción: fichero cover.jpg… o la incrustada."""
    c = elemento(id_)
    if not c:
        return None
    carpeta = os.path.dirname(c["ruta"])
    for n in os.listdir(carpeta):
        if n.lower() in PORTADAS:
            with open(os.path.join(carpeta, n), "rb") as f:
                return f.read(), "image/png" if n.lower().endswith("png") else "image/jpeg"
    if mutagen:
        try:
            f = mutagen.File(c["ruta"])
            for k in (f.tags or {}).keys():
                if k.startswith("APIC") or k == "covr":
                    t = f.tags[k]
                    dato = t.data if hasattr(t, "data") else bytes(t[0])
                    return dato, getattr(t, "mime", "image/jpeg")
            if hasattr(f, "pictures") and f.pictures:
                return f.pictures[0].data, f.pictures[0].mime
        except Exception:
            pass
    return None


def miniatura(id_):
    """JPEG de un fotograma del vídeo (al 10 %), guardado en ~/.cache/prisma/miniaturas."""
    v = elemento(id_)
    if not v:
        return None
    destino = os.path.join(CACHE, "miniaturas", id_ + ".jpg")
    if not os.path.isfile(destino):
        os.makedirs(os.path.dirname(destino), exist_ok=True)
        try:
            dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                                        v["ruta"]], capture_output=True, text=True, timeout=10).stdout or 0)
            subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-ss", f"{max(1, dur * 0.1):.1f}", "-i", v["ruta"],
                            "-frames:v", "1", "-vf", "scale=320:-2", destino], timeout=20)
        except Exception:
            return None
    if not os.path.isfile(destino):
        return None
    with open(destino, "rb") as f:
        return f.read()


def remux(id_, desde=0.0):
    """Para vídeos que el navegador no abre tal cual (avi, mkv con AC3/DTS…): ffmpeg copia el vídeo
    y pasa el sonido a AAC, en MP4 fragmentado que se reproduce mientras llega."""
    v = elemento(id_)
    cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-nostdin"]
    if desde > 0:
        cmd += ["-ss", f"{desde:.1f}"]
    cmd += ["-i", v["ruta"], "-map", "0:v:0", "-map", "0:a:0?", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
            "-avoid_negative_ts", "make_zero", "-f", "mp4", "-movflags", "frag_keyframe+empty_moov+default_base_moof",
            "pipe:1"]
    return subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)


def duracion(id_):
    v = elemento(id_)
    try:
        return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                                     v["ruta"]], capture_output=True, text=True, timeout=10).stdout or 0)
    except Exception:
        return 0


# ------------------------------------------------------------------ qué se está reproduciendo
# La pantalla avisa (POST /api/local/estado) de lo que suena; así «pausa» o «siguiente» van al
# reproductor de la pantalla en vez de a Spotify mientras suena algo de aquí.
_reproductor = {"medio": None, "sonando": False, "cuando": 0}


def informa(medio, sonando):
    _reproductor.update(medio=medio, sonando=bool(sonando), cuando=time.time())


def activo():
    """'audio' / 'video' si la pantalla está reproduciendo algo propio (o lo pausó hace poco)."""
    r = _reproductor
    if not r["medio"]:
        return None
    if r["sonando"] or time.time() - r["cuando"] < 30 * 60:
        return r["medio"]
    return None


# ------------------------------------------------------------------ órdenes
_MIA = r"(?:de |en )?(?:mi musica|mis canciones|mi biblioteca|la pi|local|el disco duro|el usb|el pen(?:drive)?)"
_PON_MIA = re.compile(r"^(?:pon(?:me)?|reproduce|toca|quiero (?:escuchar|oir))\s+(?:mi musica|mis canciones|musica de la pi|mi biblioteca|musica local)(?:\s+(?:aleatoria|al azar|mezclada))?$")
_PON_ALGO_MIO = re.compile(r"^(?:pon(?:me)?|reproduce|toca|quiero (?:escuchar|oir))\s+(?:el disco |el album |la cancion |musica de |canciones de |a )?(.+?)\s+" + _MIA + "$")
_PON_PELI = re.compile(r"^(?:pon(?:me)?|reproduce|quiero ver)\s+(?:la pelicula|la peli|el capitulo|la serie|mi video)\s+(.+?)(?:\s+" + _MIA + r"|\s+de mis videos)?$")
_PON_DE_MIS_VIDEOS = re.compile(r"^(?:pon(?:me)?|reproduce|quiero ver)\s+(?:el video |la pelicula )?(.+?)\s+(?:de mis videos|de la pi|del usb|del disco duro)$")
_ACTUALIZA = re.compile(r"^(?:actualiza|vuelve a mirar|reindexa)\s+(?:la |mi )?(?:biblioteca|musica|carpeta)")
_CONTROL = {"pause", "play", "next", "prev", "vol", "vol_abs"}


def entiende(texto, orden_musica=None):
    """('pon_todo',None) · ('pon_musica', consulta) · ('pon_video', consulta) · ('actualiza',None) ·
    ('control', (orden, valor)) si «pausa/siguiente…» deben ir al reproductor de la pantalla."""
    n = normaliza(texto).strip(" ?¿!¡.,")
    n = re.sub(r"^(?:oye[, ]+)?(?:prisma|ordenador)[, ]+", "", n)
    if _ACTUALIZA.match(n):
        return "actualiza", None
    if _PON_MIA.match(n):
        return "pon_todo", None
    m = _PON_PELI.match(n) or _PON_DE_MIS_VIDEOS.match(n)
    if m:
        return "pon_video", m.group(1)
    m = _PON_ALGO_MIO.match(n)
    if m:
        return "pon_musica", m.group(1)
    if orden_musica and orden_musica[0] in _CONTROL and activo():
        return "control", orden_musica
    return None


def _puntua(consulta, *campos):
    q = normaliza(consulta)
    mejor = 0.0
    for c in campos:
        c = normaliza(c or "")
        if not c:
            continue
        if q == c:
            return 1.0
        if q in c:
            mejor = max(mejor, 0.85 + 0.1 * len(q) / len(c))
        mejor = max(mejor, difflib.SequenceMatcher(None, q, c).ratio())
    return mejor


def busca_musica(consulta):
    """Canciones para la consulta: un artista o un álbum enteros, o la canción. Lista vacía si nada encaja."""
    cs = indexa()["canciones"]
    por_artista = max(((_puntua(consulta, c["artista"]), c["artista"]) for c in cs), default=(0, ""))
    por_album = max(((_puntua(consulta, c["album"]), c["album"]) for c in cs), default=(0, ""))
    por_cancion = max(((_puntua(consulta, c["titulo"]), c["id"]) for c in cs), default=(0, ""))
    mejor = max(por_artista[0], por_album[0], por_cancion[0])
    if mejor < 0.72:
        return [], ""
    if por_album[0] == mejor:
        return [c for c in cs if c["album"] == por_album[1]], f"el disco {por_album[1]}"
    if por_artista[0] == mejor:
        return [c for c in cs if c["artista"] == por_artista[1]], f"música de {por_artista[1]}"
    c = next(c for c in cs if c["id"] == por_cancion[1])
    return [c], f"{c['titulo']}" + (f", de {c['artista']}" if c["artista"] else "")


def busca_video(consulta):
    vs = indexa()["videos"]
    puntos = sorted(((_puntua(consulta, v["titulo"], v["carpeta"]), i) for i, v in enumerate(vs)), reverse=True)
    if not puntos or puntos[0][0] < 0.6:
        return None
    return vs[puntos[0][1]]


def todo_mezclado():
    cs = list(indexa()["canciones"])
    random.shuffle(cs)
    return cs
