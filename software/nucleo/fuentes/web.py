"""Búsqueda general: lee tal cual el fragmento más relevante, citando la fuente. Sin modelo."""
import re
from urllib.parse import urlparse
from ..texto import normaliza
from .. import buscador

_VACIAS = set("el la los las un una unos unas de del al a en y o que quien quienes cual cuales como cuando "
              "donde por para con sin es son fue ser se su sus lo le les me mi tu te ha han hay mas muy "
              "este esta estos estas ese esa eso hoy busca buscar mira dime".split())
_RELLENO = re.compile(r"^(?:consulta|entra|descubre|conoce|lee|sigue|todas? las|todos los)\b", re.I)


def _palabras(t):
    return {w for w in re.findall(r"\w+", normaliza(t)) if w not in _VACIAS and len(w) > 2}


def _fuente(r):
    titulo = r.get("title", "")
    if " - " in titulo:
        return titulo.rsplit(" - ", 1)[-1].strip()
    if " | " in titulo:
        return titulo.rsplit(" | ", 1)[-1].strip()
    dominio = urlparse(r.get("url", "")).netloc.replace("www.", "")
    return dominio or "Internet"


def _primeras_frases(t, maximo=220):
    t = " ".join(t.split())
    frases = re.split(r"(?<=[.!?])\s+", t)
    salida = ""
    for i, f in enumerate(frases):
        if i == 2 or (len(salida) + len(f) > maximo and salida):     # como mucho dos frases
            break
        salida = f"{salida} {f}".strip()
    return salida if len(salida) <= maximo + 40 else salida[:maximo].rsplit(" ", 1)[0] + "…"


def elige(consulta, res):
    """Elige el fragmento con más palabras de la pregunta. Devuelve (fuente, texto) o None."""
    q = _palabras(consulta)
    mejor, puntos = None, 0
    for r in res.get("results", [])[:8]:
        contenido = r.get("content") or ""
        if len(contenido) < 40 or _RELLENO.search(contenido.strip()):
            continue                                  # «Consulta los resultados…» no responde a nada
        p = len(q & _palabras(contenido)) + 0.5 * len(q & _palabras(r.get("title", "")))
        if p > puntos:
            mejor, puntos = r, p
    if not mejor or puntos < 1:
        return None
    return _fuente(mejor), _primeras_frases(mejor["content"])


def responde(consulta):
    """Devuelve (texto_hablado, segundos, detalle)."""
    directa, res, t = buscador.consulta_cruda(consulta)
    if directa:
        return directa, t, "respuesta directa"
    elegido = elige(consulta, res)
    if not elegido:
        return "No he encontrado una respuesta clara en Internet.", t, "sin fragmento útil"
    fuente, texto = elegido
    return f"Según {fuente}: {texto}", t, f"fragmento de {fuente}"
