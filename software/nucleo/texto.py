"""Utilidades de texto y red compartidas."""
import datetime, json, unicodedata, urllib.request

MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre",
         "octubre", "noviembre", "diciembre"]
DIAS = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
_UA = {"User-Agent": "Prisma/0.1 (asistente de sobremesa; https://github.com/PepVentura/Prisma)"}


def normaliza(t):
    """Minúsculas y sin tildes, para comparar."""
    t = unicodedata.normalize("NFD", t.lower())
    return "".join(c for c in t if unicodedata.category(c) != "Mn")


def fecha_hablada(d):
    return f"{DIAS[d.weekday()]} {d.day} de {MESES[d.month - 1]}"


def pide(url, cabeceras=None, espera=4):
    req = urllib.request.Request(url, headers={**_UA, **(cabeceras or {})})
    with urllib.request.urlopen(req, timeout=espera) as r:
        return r.read()


def pide_json(url, cabeceras=None, espera=4):
    return json.loads(pide(url, cabeceras, espera))


def hoy():
    return datetime.date.today()
