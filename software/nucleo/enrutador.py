"""Decide qué hacer con cada petición. De momento: buscar en Internet o charlar.

Las órdenes directas (hora, temporizadores, tiempo, música…) se añadirán aquí, delante,
para que se resuelvan sin pasar por el modelo.
"""
import re
import unicodedata


def _normaliza(t):
    t = unicodedata.normalize("NFD", t.lower())
    return "".join(c for c in t if unicodedata.category(c) != "Mn")


# Pide buscar explícitamente
_PIDE_BUSCAR = re.compile(r"^(?:oye[, ]+)?(?:prisma[, ]+)?(?:busca(?:me)?|buscar|mira|consulta|averigua)\b"
                          r"(?:\s+(?:en\s+)?(?:internet|la\s+red|google))?\s*(?:si\s+|que\s+|qué\s+)?")
# Preguntas que dependen de datos actuales o de hechos concretos
_ACTUALIDAD = re.compile(
    r"\b(hoy|ayer|esta semana|este mes|este ano|ultim[oa]s?|actual(?:mente)?|ahora mismo|noticias?|"
    r"resultado|marcador|quien gano|ha ganado|clasificacion|precio|cuanto cuesta|cotizacion|"
    r"estreno|cuando (?:es|sera|juega|abre|cierra)|horario|20[2-3]\d)\b")
_DATO = re.compile(r"^(quien (?:es|era|fue|invento|escribio|dirigio|descubrio)|cuantos? (?:habitantes|anos tiene)|"
                   r"donde (?:esta|nacio)|en que ano)\b")


def decide(texto):
    """Devuelve (accion, consulta): ('buscar', consulta) o ('charla', texto)."""
    limpio = texto.strip().strip("?¿!¡. ")
    n = _normaliza(limpio)
    m = _PIDE_BUSCAR.match(n)
    if m:
        return "buscar", limpio[m.end():].strip(" ,:") or limpio
    if _ACTUALIDAD.search(n) or _DATO.match(n):
        return "buscar", limpio
    return "charla", texto.strip()
