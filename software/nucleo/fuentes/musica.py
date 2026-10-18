"""Música: control de Spotify con su API web (Premium).

La música suena en la propia Pi (raspotify, altavoz «Prisma» de Spotify Connect); esta parte la
controla: poner un artista, una canción, un disco o una lista, pausar, seguir, saltar, volumen y
«¿qué suena?». Hace falta conectar la cuenta una vez con herramientas/spotify_conecta.py, que guarda
los permisos en ~/.config/prisma/spotify.json.
"""
import base64, hashlib, json, os, re, secrets, time, urllib.error, urllib.parse, urllib.request
from ..config import CONFIG
from ..texto import normaliza

FICHERO = os.path.expanduser("~/.config/prisma/spotify.json")
API = "https://api.spotify.com/v1"
CUENTAS = "https://accounts.spotify.com"
# Página de vuelta en GitHub Pages (HTTPS): solo enseña el código para copiarlo. Antes se usaba
# http://127.0.0.1:8080/spotify, pero algunos navegadores se quedan colgados al volver a una dirección local.
REDIRECCION = CONFIG.get("spotify_vuelta", "https://pepventura.github.io/Prisma/spotify/")
PERMISOS = "user-read-playback-state user-modify-playback-state user-read-currently-playing"
NO_CONECTADO = ("Spotify todavía no está conectado. Ejecuta en la Pi "
                "python3 ~/prisma/software/herramientas/spotify_conecta.py y sigue los pasos.")


class SinConectar(Exception):
    pass


# ---------------------------------------------------------------- permisos (OAuth con PKCE)
def configurado():
    return os.path.isfile(FICHERO)


def _carga():
    with open(FICHERO) as f:
        return json.load(f)


def _guarda(d):
    os.makedirs(os.path.dirname(FICHERO), exist_ok=True)
    with open(FICHERO, "w") as f:
        json.dump(d, f, indent=1)
    os.chmod(FICHERO, 0o600)


def _cuentas(datos):
    req = urllib.request.Request(CUENTAS + "/api/token", urllib.parse.urlencode(datos).encode(),
                                 {"Content-Type": "application/x-www-form-urlencoded"})
    with urllib.request.urlopen(req, timeout=8) as r:
        return json.loads(r.read())


def empieza_conexion(client_id):
    """Devuelve (url para autorizar, verificador PKCE)."""
    verificador = secrets.token_urlsafe(64)[:96]
    reto = base64.urlsafe_b64encode(hashlib.sha256(verificador.encode()).digest()).rstrip(b"=").decode()
    q = {"client_id": client_id, "response_type": "code", "redirect_uri": REDIRECCION, "scope": PERMISOS,
         "code_challenge_method": "S256", "code_challenge": reto}
    return CUENTAS + "/authorize?" + urllib.parse.urlencode(q), verificador


def termina_conexion(client_id, codigo, verificador):
    t = _cuentas({"grant_type": "authorization_code", "code": codigo, "redirect_uri": REDIRECCION,
                  "client_id": client_id, "code_verifier": verificador})
    _guarda({"client_id": client_id, "refresh_token": t["refresh_token"], "access_token": t["access_token"],
             "expira": time.time() + t.get("expires_in", 3600) - 60})


def _token(forzar=False):
    if not configurado():
        raise SinConectar()
    d = _carga()
    if forzar or time.time() > d.get("expira", 0):
        t = _cuentas({"grant_type": "refresh_token", "refresh_token": d["refresh_token"], "client_id": d["client_id"]})
        d.update(access_token=t["access_token"], expira=time.time() + t.get("expires_in", 3600) - 60)
        if t.get("refresh_token"):
            d["refresh_token"] = t["refresh_token"]
        _guarda(d)
    return d["access_token"]


def _api(metodo, ruta, cuerpo=None, params=None, _reintento=True):
    url = API + ruta + ("?" + urllib.parse.urlencode(params) if params else "")
    datos = json.dumps(cuerpo).encode() if cuerpo is not None else (b"" if metodo in ("PUT", "POST") else None)
    req = urllib.request.Request(url, datos, {"Authorization": "Bearer " + _token(),
                                              "Content-Type": "application/json"}, method=metodo)
    try:
        with urllib.request.urlopen(req, timeout=6) as r:
            texto = r.read()
            return json.loads(texto) if texto else None
    except urllib.error.HTTPError as e:
        if e.code == 401 and _reintento:
            _token(forzar=True)
            return _api(metodo, ruta, cuerpo, params, False)
        raise


# ---------------------------------------------------------------- reproductor
def _prisma():
    """El altavoz «Prisma» (raspotify) en la lista de dispositivos de la cuenta, si está."""
    nombre = normaliza(CONFIG.get("spotify_dispositivo", "Prisma"))
    for d in (_api("GET", "/me/player/devices") or {}).get("devices", []):
        if normaliza(d.get("name", "")) == nombre:
            return d
    return None


def _destino():
    """device_id donde sonar: Prisma si está; si no, el que esté activo (None = el activo)."""
    p = _prisma()
    return p["id"] if p else None


def estado():
    """Lo que suena ahora en la cuenta (en Prisma o en otro dispositivo), para la pantalla."""
    j = _api("GET", "/me/player", params={"additional_types": "episode"})
    if not j or not j.get("item"):
        return {"api": True, "estado": None}
    it = j["item"]
    imgs = it.get("album", {}).get("images") or it.get("images") or []
    return {"api": True, "estado": "sonando" if j.get("is_playing") else "pausa",
            "nombre": it.get("name"),
            "artistas": ", ".join(a["name"] for a in it.get("artists", [])) or it.get("show", {}).get("name"),
            "album": it.get("album", {}).get("name"),
            "portada": (imgs[1] if len(imgs) > 1 else imgs[0])["url"] if imgs else None,
            "duracion_ms": it.get("duration_ms", 0), "posicion_ms": j.get("progress_ms") or 0,
            "dispositivo": (j.get("device") or {}).get("name"),
            "volumen": (j.get("device") or {}).get("volume_percent")}


def accion(a, valor=None):
    """play · pause · next · prev · vol (relativo: +10 / −10) · vol_abs (0–100)."""
    if a == "play":
        dev = _destino()
        _api("PUT", "/me/player/play", params={"device_id": dev} if dev else None)
    elif a == "pause":
        _api("PUT", "/me/player/pause")
    elif a == "next":
        _api("POST", "/me/player/next")
    elif a == "prev":
        _api("POST", "/me/player/previous")
    elif a in ("vol", "vol_abs"):
        if a == "vol_abs":
            nuevo = int(valor)
        else:
            actual = (_api("GET", "/me/player") or {}).get("device", {}).get("volume_percent", 50)
            nuevo = actual + int(valor or 0)
        _api("PUT", "/me/player/volume", params={"volume_percent": max(0, min(100, nuevo))})
        return max(0, min(100, nuevo))


def reproduce(consulta, tipo=None):
    """Busca y pone. tipo: artist · track · album · playlist · None (lo que mejor encaje).
    Devuelve el texto hablado."""
    tipos = tipo or "artist,track,playlist,album"
    r = _api("GET", "/search", params={"q": consulta, "type": tipos, "limit": 5, "market": "from_token"})
    c = normaliza(consulta)
    elegido = None
    # Sin tipo dicho: un artista que se llame exactamente así gana; si no, la canción más popular
    if not tipo:
        for a in (r.get("artists") or {}).get("items", []):
            if a and normaliza(a["name"]) == c:
                elegido = ("artist", a)
                break
    for t in ([tipo] if tipo else ["track", "artist", "playlist", "album"]):
        if elegido:
            break
        items = [i for i in (r.get(t + "s") or {}).get("items", []) if i]
        if items:
            elegido = (t, items[0])
    if not elegido:
        return f"No encuentro «{consulta}» en Spotify."
    t, i = elegido
    dev = _destino()
    cuerpo = {"uris": [i["uri"]]} if t == "track" else {"context_uri": i["uri"]}
    _api("PUT", "/me/player/play", cuerpo, params={"device_id": dev} if dev else None)
    if t == "track":
        return f"Pongo {i['name']}, de {i['artists'][0]['name']}."
    if t == "artist":
        return f"Pongo música de {i['name']}."
    if t == "album":
        return f"Pongo el disco {i['name']}, de {i['artists'][0]['name']}."
    return f"Pongo la lista {i['name']}."


# ---------------------------------------------------------------- órdenes habladas
_PON = re.compile(r"^(?:pon(?:me)?|reproduce|quiero (?:escuchar|oir)|toca|ponte)\s+(?:algo de\s+|un poco de\s+)?(.+)$")
_TIPO = [(re.compile(r"^(?:la )?(?:lista|playlist)\s+(?:de\s+)?(.+)$"), "playlist"),
         (re.compile(r"^(?:el )?(?:disco|album)\s+(?:de\s+)?(.+)$"), "album"),
         (re.compile(r"^(?:la )?cancion\s+(.+)$"), "track"),
         (re.compile(r"^(?:musica|canciones) de\s+(.+)$"), "artist")]
_PAUSA = re.compile(r"^(?:pausa|pausa la musica|para(?: la musica)?|deten(?: la musica)?|stop|quita la musica|calla la musica)$")
_SIGUE = re.compile(r"^(?:continua|sigue|reanuda|play|dale|pon (?:la )?musica|quita la pausa)(?: la musica)?$")
_SIGUIENTE = re.compile(r"^(?:siguiente|salta|pasa|otra)(?: (?:cancion|tema))?$|^(?:la )?siguiente cancion$|^(?:pon )?otra cancion$")
_ANTERIOR = re.compile(r"^(?:anterior|la (?:cancion )?anterior|la de antes|vuelve atras|(?:pon )?la cancion anterior)$")
_VOLUMEN = re.compile(r"^(sube|baja)(?: el)? volumen|^(?:mas alto|mas bajo)$|^(?:pon el )?volumen (?:al |a )?(\d{1,3})")
_QUE_SUENA = re.compile(r"(?:que (?:cancion|tema) (?:es|suena)(?: esta)?|que suena|quien canta|como se llama esta cancion)")


def entiende(texto):
    """('orden', valor) si es una orden de música; None si no."""
    n = normaliza(texto).strip(" ?¿!¡.,")
    n = re.sub(r"^(?:oye[, ]+)?(?:prisma|ordenador)[, ]+", "", n)
    if _PAUSA.match(n):
        return "pause", None
    if _SIGUE.match(n):
        return "play", None
    if _SIGUIENTE.match(n):
        return "next", None
    if _ANTERIOR.match(n):
        return "prev", None
    m = _VOLUMEN.match(n)
    if m:
        if m.group(2):
            return "vol_abs", int(m.group(2))
        return "vol", 10 if (m.group(1) == "sube" or n == "mas alto") else -10
    if _QUE_SUENA.search(n):
        return "que", None
    m = _PON.match(n)
    if m:
        resto = m.group(1).strip()
        if re.match(r"^(?:las )?noticias|^(?:el )?tiempo|^(?:un )?temporizador|^(?:una )?alarma", resto):
            return None
        for patron, tipo in _TIPO:
            t = patron.match(resto)
            if t:
                return "pon", (_original(texto, t.group(1)), tipo)
        return "pon", (_original(texto, resto), None)
    return None


def _original(texto, normalizado):
    """Recupera el trozo con sus tildes y mayúsculas («Pon Rosalía» → «Rosalía»)."""
    palabras = texto.strip(" ?¿!¡.,").split()
    n = len(normalizado.split())
    return " ".join(palabras[-n:]) if n <= len(palabras) else normalizado


def responde(orden, valor):
    if not configurado():
        return NO_CONECTADO
    try:
        if orden == "pon":
            return reproduce(*valor)
        if orden == "que":
            e = estado()
            if not e.get("nombre"):
                return "Ahora mismo no suena nada."
            return f"Suena {e['nombre']}, de {e['artistas']}." if e.get("artistas") else f"Suena {e['nombre']}."
        if orden in ("vol", "vol_abs"):
            v = accion(orden, valor)
            return f"Volumen al {v} por ciento."
        accion(orden)
        return {"pause": "Pausado.", "play": "Sigo.", "next": "Siguiente.", "prev": "Anterior."}[orden]
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return ("No encuentro dónde sonar. Elige «Prisma» una vez en la app de Spotify "
                    "y desde entonces podré ponerla yo.")
        if e.code == 403:
            return "Spotify no me deja hacerlo. Hace falta una cuenta Premium."
        raise
