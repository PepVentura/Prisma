"""Decide qué hacer con cada petición, de la más rápida y fiable a la más lenta:

  1. reloj     hora y fecha                                 (instantáneo)
  2. tiempo    Open-Meteo                                   (≈0,5 s, datos reales)
  3. fútbol    football-data.org                            (≈1 s, datos reales)
  4. noticias  titulares RSS de los periódicos elegidos     (≈0,5 s, tal cual)
  5. web       SearXNG: lee el fragmento más relevante      (≈1 s, tal cual, citando la fuente)
  6. charla    qwen3:1.7b                                   (≈1–3 s hasta la primera frase)

Las fuentes 1–5 no pasan por el modelo de lenguaje: no pueden inventar.
Además:
  - corrige erratas en las palabras clave («titukares» → «titulares»);
  - entiende preguntas de seguimiento («¿y mañana?», «¿y en Bilbao?», «¿y de TV3?»).
(La memoria —«me llamo…», «¿cómo me llamo?»— se resuelve antes, en memoria.py.)
"""
import difflib, re
from .config import CONFIG
from .texto import normaliza
from .fuentes import reloj, tiempo, futbol, noticias

# Pide buscar explícitamente
_PIDE_BUSCAR = re.compile(r"^(?:oye[, ]+)?(?:prisma[, ]+)?(?:busca(?:me)?|buscar|mira|consulta|averigua)\b"
                          r"(?:\s+(?:en\s+)?(?:internet|la\s+red|google))?\s*(?:si\s+|que\s+|qué\s+)?")
# Preguntas que dependen de datos actuales o de hechos concretos
_ACTUALIDAD = re.compile(
    r"\b(hoy|ayer|esta semana|este mes|este ano|ultim[oa]s?|actual(?:mente)?|ahora mismo|"
    r"resultado|marcador|quien gano|ha ganado|clasificacion|precio|cuanto cuesta|cotizacion|"
    r"estreno|cuando (?:es|sera|juega|abre|cierra)|horario|20[2-3]\d)\b")
_DATO = re.compile(r"^(quien (?:es|era|fue|invento|escribio|dirigio|descubrio)|cuantos? (?:habitantes|anos tiene)|"
                   r"donde (?:esta|nacio)|en que ano)\b")
_SEGUIMIENTO = re.compile(r"^(?:y|e|vale y|bueno y|tambien)\b")

# Palabras clave que se corrigen si llegan con una errata (solo palabras de 5 letras o más)
_CLAVES = ["noticias", "titulares", "portada", "tiempo", "llover", "llovera", "lloviendo", "temperatura",
           "pronostico", "clasificacion", "partido", "resultado", "busca", "buscame", "manana", "pasado",
           "sabado", "domingo", "viernes", "jueves", "miercoles", "martes", "vanguardia", "periodico"]

_ultimo = {"accion": None, "datos": None}


def corrige(texto):
    """Sustituye palabras casi iguales a una palabra clave («titukares» → «titulares»)."""
    salida = []
    for w in texto.split():
        base = normaliza(w).strip("¿?¡!.,;:«»\"")
        if len(base) >= 5 and base not in _CLAVES:
            parecida = difflib.get_close_matches(base, _CLAVES, n=1, cutoff=0.8)
            if parecida:
                w = parecida[0]
        salida.append(w)
    return " ".join(salida)


def _seguimiento(texto):
    """«¿y mañana?», «¿y en Bilbao?», «¿y de TV3?», «¿y el Athletic?»: repite lo anterior cambiando el dato."""
    n = normaliza(texto).strip(" ?¿!¡.")
    corta = len(n.split()) <= 5
    if not (_SEGUIMIENTO.match(n) or corta) or not _ultimo["accion"]:
        return None
    if _ultimo["accion"] == "tiempo":
        dia, ciudad = tiempo.dia_de(n), tiempo.ciudad_de(texto)
        if dia is not None or ciudad:
            viejo_dia, vieja_ciudad = _ultimo["datos"]
            return "tiempo", (viejo_dia if dia is None else dia, ciudad or vieja_ciudad)
    if _ultimo["accion"] == "noticias":
        p = noticias.periodico_en(n)
        if p:
            return "noticias", p
    if _ultimo["accion"] == "futbol" and _SEGUIMIENTO.match(n):
        return "futbol", (_ultimo["datos"][0], texto)
    return None


def decide(texto):
    """Devuelve (accion, datos):
    ('reloj', respuesta) · ('tiempo', (dia, ciudad)) · ('futbol', (tipo, texto)) ·
    ('noticias', periodico) · ('web', consulta) · ('charla', texto)."""
    texto = corrige(texto)
    accion, datos = _decide(texto)
    if accion in ("tiempo", "futbol", "noticias"):
        _ultimo.update(accion=accion, datos=datos)
    elif accion != "reloj":
        _ultimo.update(accion=None, datos=None)
    return accion, datos


def _decide(texto):
    r = reloj.intenta(texto)
    if r:
        return "reloj", r
    s = _seguimiento(texto)
    if s:
        return s
    t = tiempo.entiende(texto)
    if t:
        return "tiempo", t
    f = futbol.entiende(texto)
    if f:
        return "futbol", f
    p = noticias.entiende(texto)
    if p:
        return "noticias", p
    limpio = texto.strip().strip("?¿!¡. ")
    n = normaliza(limpio)
    m = _PIDE_BUSCAR.match(n)
    if m:
        return "web", limpio[m.end():].strip(" ,:") or limpio
    if _ACTUALIDAD.search(n) or _DATO.match(n):
        return "web", limpio
    return "charla", texto.strip()


def responde_fuente(accion, datos):
    """Resuelve las acciones 2–4. Devuelve el texto hablado."""
    if accion == "tiempo":
        return tiempo.responde(*datos)
    if accion == "futbol":
        return futbol.responde(*datos)
    if accion == "noticias":
        return noticias.responde(datos)
    raise ValueError(accion)
