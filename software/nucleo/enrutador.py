"""Decide qué hacer con cada petición, de la más rápida y fiable a la más lenta:

  1. reloj     hora y fecha                                 (instantáneo)
  2. tiempo    Open-Meteo                                   (≈1,5 s, datos reales)
  3. fútbol    football-data.org                            (≈1,5 s, datos reales)
  4. noticias  titulares RSS de los periódicos elegidos     (≈1,5 s, tal cual)
  5. web       SearXNG: lee el fragmento más relevante      (≈1,5–2 s, tal cual, citando la fuente)
  6. charla    qwen3:1.7b                                   (≈1–3 s hasta la primera frase)

Las fuentes 1–5 no pasan por el modelo de lenguaje: no pueden inventar.
(La memoria —«me llamo…», «¿cómo me llamo?»— se resuelve antes, en memoria.py.)
"""
import re
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


def decide(texto):
    """Devuelve (accion, datos):
    ('reloj', respuesta) · ('tiempo', (dia, ciudad)) · ('futbol', (tipo, texto)) ·
    ('noticias', periodico) · ('web', consulta) · ('charla', texto)."""
    r = reloj.intenta(texto)
    if r:
        return "reloj", r
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
    """Resuelve las acciones 2–5. Devuelve el texto hablado."""
    if accion == "tiempo":
        return tiempo.responde(*datos)
    if accion == "futbol":
        return futbol.responde(*datos)
    if accion == "noticias":
        return noticias.responde(datos)
    raise ValueError(accion)
