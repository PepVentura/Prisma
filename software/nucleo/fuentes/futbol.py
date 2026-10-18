"""Fútbol con football-data.org (gratis con clave): resultados, próximos partidos y clasificación.
La clave se guarda en ~/.config/prisma/nucleo.json como "futbol_clave"."""
import datetime, re, time
from ..config import CONFIG
from ..texto import normaliza, pide_json, fecha_hablada

API = "https://api.football-data.org/v4"
_PIDE = re.compile(r"\b(la real|real sociedad|futbol|liga|laliga|partido|clasificacion|"
                   r"ha ganado|gano|empato|perdio|marcador|resultado|como quedo|cuando juega|contra quien juega|"
                   r"en que puesto|que puesto|lider|gol(?:es)?)\b")
_ULTIMO = re.compile(r"\b(ultim|resultado|como quedo|ha ganado|gano|empato|perdio|marcador|ayer|anoche)")
_PROXIMO = re.compile(r"\b(proxim|cuando juega|contra quien juega|siguiente partido|juega hoy|juega manana)")
_TABLA = re.compile(r"\b(clasificacion|que puesto|en que puesto|lider|como va la liga|tabla)\b")
_equipos = {"t": 0, "lista": []}


def entiende(texto):
    """('ultimo' | 'proximo' | 'clasificacion', texto) si es una pregunta de fútbol; si no, None."""
    n = normaliza(texto)
    if not _PIDE.search(n):
        return None
    deportivo = re.search(r"\b(la real|real sociedad|futbol|liga|laliga|partido|clasificacion|lider|gol)", n) \
        or _nombre_equipo(n, sin_red=True)
    if not deportivo:
        return None
    if _TABLA.search(n):
        return "clasificacion", texto
    if _PROXIMO.search(n):
        return "proximo", texto
    return "ultimo", texto


def _cab():
    return {"X-Auth-Token": CONFIG.get("futbol_clave") or ""}


def _lista_equipos():
    if time.time() - _equipos["t"] > 86400:
        d = pide_json(f"{API}/competitions/{CONFIG['futbol_liga']}/teams", _cab(), 6)
        _equipos.update(t=time.time(), lista=d["teams"])
    return _equipos["lista"]


def _nombre_equipo(n, sin_red=False):
    """Busca en el texto (normalizado) el nombre de un equipo de la liga."""
    lista = _equipos["lista"] if sin_red else _lista_equipos()
    for e in lista:
        for nombre in {e.get("shortName", ""), e.get("name", ""), e.get("tla", "")}:
            nn = normaliza(nombre)
            if len(nn) > 3 and re.search(rf"\b{re.escape(nn)}\b", n):
                return e
    return None


def _equipo(texto):
    n = normaliza(texto)
    e = _nombre_equipo(n)
    if e:
        return e
    objetivo = normaliza(CONFIG["equipo"])
    for e in _lista_equipos():
        if objetivo in normaliza(e.get("name", "")) or objetivo in normaliza(e.get("shortName", "")):
            return e
    raise LookupError(CONFIG["equipo"])


def responde(tipo, texto):
    if not CONFIG.get("futbol_clave"):
        return ("Para el fútbol necesito la clave gratuita de football-data.org. Está explicado en la guía de "
                "instalación, paso 4.")
    if tipo == "clasificacion":
        d = pide_json(f"{API}/competitions/{CONFIG['futbol_liga']}/standings", _cab(), 6)
        return redacta_tabla(d, _equipo(texto))
    e = _equipo(texto)
    estado = "FINISHED" if tipo == "ultimo" else "SCHEDULED,TIMED"
    d = pide_json(f"{API}/teams/{e['id']}/matches?status={estado}&limit=40", _cab(), 6)
    return redacta_partido(d.get("matches", []), e, tipo)


def _cuando(d):
    """«hoy», «mañana», «ayer» o «el domingo 18 de octubre»."""
    dif = (d - datetime.date.today()).days
    return {0: "hoy", 1: "mañana", -1: "ayer"}.get(dif, f"el {fecha_hablada(d)}")


def _corto(equipo):
    return equipo.get("shortName") or equipo.get("name")


def redacta_partido(partidos, e, tipo):
    if not partidos:
        return f"No encuentro {'el último' if tipo == 'ultimo' else 'el próximo'} partido de {_corto(e)}."
    p = max(partidos, key=lambda x: x["utcDate"]) if tipo == "ultimo" else min(partidos, key=lambda x: x["utcDate"])
    cuando = datetime.datetime.fromisoformat(p["utcDate"].replace("Z", "+00:00")).astimezone()
    local, visit = _corto(p["homeTeam"]), _corto(p["awayTeam"])
    if tipo == "proximo":
        return f"{_corto(e)} juega {_cuando(cuando.date())} a las {cuando:%H:%M}: {local} contra {visit}."
    gl, gv = p["score"]["fullTime"]["home"], p["score"]["fullTime"]["away"]
    propio = gl if p["homeTeam"]["id"] == e["id"] else gv
    ajeno = gv if p["homeTeam"]["id"] == e["id"] else gl
    veredicto = "ganó" if propio > ajeno else "perdió" if propio < ajeno else "empató"
    cuando_txt = _cuando(cuando.date())
    return f"{cuando_txt[0].upper() + cuando_txt[1:]}, {local} {gl}, {visit} {gv}. {_corto(e)} {veredicto}."


def redacta_tabla(d, e):
    tabla = next((s["table"] for s in d.get("standings", []) if s.get("type") == "TOTAL"), [])
    if not tabla:
        return "No tengo la clasificación ahora mismo."
    lider = tabla[0]
    fila = next((f for f in tabla if f["team"]["id"] == e["id"]), None)
    texto = f"Líder: {_corto(lider['team'])} con {lider['points']} puntos."
    if fila and fila is not lider:
        texto += f" {_corto(e)} va {fila['position']}.º con {fila['points']} puntos tras {fila['playedGames']} partidos."
    return texto
