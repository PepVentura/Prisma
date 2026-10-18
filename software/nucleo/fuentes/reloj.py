"""Hora y fecha."""
import datetime, re
from ..texto import normaliza, fecha_hablada

_HORA = re.compile(r"\b(que hora es|que hora tienes|dime la hora|la hora)\b")
_FECHA = re.compile(r"\b(que dia es (?:hoy)?|a que dia estamos|que fecha es|la fecha de hoy|en que dia estamos)\b")


def intenta(texto):
    n = normaliza(texto)
    ahora = datetime.datetime.now()
    if _HORA.search(n):
        h, m = ahora.hour, ahora.minute
        hh = h % 12 or 12
        art = "Es la" if hh == 1 else "Son las"
        franja = "de la mañana" if 6 <= h < 13 else "de la tarde" if 13 <= h < 21 else "de la noche"
        return f"{art} {hh}:{m:02d} {franja}."
    if _FECHA.search(n):
        return f"Hoy es {fecha_hablada(ahora.date())} de {ahora.year}."
    return None
