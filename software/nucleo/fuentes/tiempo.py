"""El tiempo con Open-Meteo (gratis, sin clave): https://open-meteo.com"""
import datetime, re, urllib.parse
from ..config import CONFIG
from ..texto import normaliza, pide_json, fecha_hablada, DIAS

_PIDE = re.compile(r"\b(tiempo (?:hace|hara|va a hacer|tendremos|para)|que tiempo|el tiempo|pronostico|"
                   r"llover|llovera|llueve|lluvia|va a llover|nieve|nevara|temperatura|cuantos grados|"
                   r"hace (?:frio|calor)|hara (?:frio|calor)|paraguas)\b")
_CIUDAD = re.compile(r"\ben ([A-Za-zÁÉÍÓÚÑÜáéíóúñü][\wÁÉÍÓÚÑÜáéíóúñü' -]{1,40})$")

# Códigos WMO → descripción hablada
_CIELO = {0: "despejado", 1: "casi despejado", 2: "nubes y claros", 3: "cubierto", 45: "niebla", 48: "niebla",
          51: "llovizna débil", 53: "llovizna", 55: "llovizna intensa", 56: "llovizna helada", 57: "llovizna helada",
          61: "lluvia débil", 63: "lluvia", 65: "lluvia fuerte", 66: "lluvia helada", 67: "lluvia helada",
          71: "nieve débil", 73: "nieve", 75: "nevadas fuertes", 77: "granizo fino", 80: "chubascos débiles",
          81: "chubascos", 82: "chubascos fuertes", 85: "chubascos de nieve", 86: "chubascos de nieve fuertes",
          95: "tormenta", 96: "tormenta con granizo", 99: "tormenta con granizo"}
_cache_geo = {}


def entiende(texto):
    """Devuelve (dias_desde_hoy, ciudad) si es una pregunta del tiempo; si no, None."""
    n = normaliza(texto).strip(" ?¿!¡.")
    if not _PIDE.search(n):
        return None
    dia = 0
    if "pasado manana" in n:
        dia = 2
    elif re.search(r"\bmanana\b", n):
        dia = 1
    else:
        for i, d in enumerate(DIAS):
            if re.search(rf"\b{normaliza(d)}\b", n):
                dia = (i - datetime.date.today().weekday()) % 7 or 7
                break
        if "fin de semana" in n:
            dia = (5 - datetime.date.today().weekday()) % 7
    limpio = texto.strip(" ?¿!¡.")
    for palabra in ("pasado mañana", "mañana", "hoy", "este fin de semana", "el fin de semana") + tuple(DIAS):
        limpio = re.sub(rf"\s+(?:el\s+|este\s+)?{palabra}$", "", limpio, flags=re.I)
    m = _CIUDAD.search(limpio)
    ciudad = m.group(1).strip() if m else CONFIG["ciudad"]
    return dia, ciudad


def _geo(ciudad):
    if ciudad not in _cache_geo:
        q = urllib.parse.urlencode({"name": ciudad, "count": 1, "language": "es", "format": "json"})
        r = pide_json("https://geocoding-api.open-meteo.com/v1/search?" + q).get("results")
        _cache_geo[ciudad] = r[0] if r else None
    return _cache_geo[ciudad]


def responde(dia, ciudad):
    lugar = _geo(ciudad)
    if not lugar:
        return f"No encuentro dónde está {ciudad}."
    q = urllib.parse.urlencode({
        "latitude": lugar["latitude"], "longitude": lugar["longitude"], "timezone": "Europe/Madrid",
        "current": "temperature_2m,weather_code",
        "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max",
        "forecast_days": 8})
    d = pide_json("https://api.open-meteo.com/v1/forecast?" + q)
    return redacta(d, dia, lugar["name"])


def redacta(d, dia, nombre):
    """Texto hablado a partir de la respuesta de Open-Meteo (separado para poder probarlo)."""
    dd = d["daily"]
    if dia >= len(dd["time"]):
        return "Solo tengo el pronóstico de la próxima semana."
    cielo = _CIELO.get(dd["weather_code"][dia], "tiempo variable")
    tmin, tmax = round(dd["temperature_2m_min"][dia]), round(dd["temperature_2m_max"][dia])
    lluvia = dd["precipitation_probability_max"][dia]
    if dia == 0:
        cuando = "Hoy"
        actual = d.get("current", {}).get("temperature_2m")
        ahora = f" Ahora hace {round(actual)} grados." if actual is not None else ""
    else:
        f = datetime.date.fromisoformat(dd["time"][dia])
        cuando = "Mañana" if dia == 1 else "Pasado mañana" if dia == 2 else f"El {fecha_hablada(f)}"
        ahora = ""
    texto = f"{cuando} en {nombre}: {cielo}, entre {tmin} y {tmax} grados"
    if lluvia is not None:
        texto += f", con un {lluvia} % de probabilidad de lluvia" if lluvia >= 20 else ", sin lluvia prevista"
    return texto + "." + ahora
