"""Memoria de Prisma: datos que el usuario le pide recordar (su nombre, gustos…).
Se guarda en ~/.config/prisma/memoria.json y se añade a las instrucciones del modelo."""
import json, os, re

RUTA = os.path.expanduser("~/.config/prisma/memoria.json")
_NOMBRE = re.compile(r"^(?:oye[, ]+)?(?:prisma[, ]+)?(?:me llamo|mi nombre es|llamame|llámame)\s+([a-záéíóúñü][\w áéíóúñü'-]{0,30})$", re.I)
_RECUERDA = re.compile(r"^(?:oye[, ]+)?(?:prisma[, ]+)?(?:recuerda|apunta|memoriza|no olvides)(?:\s+que)?\s+(.+)$", re.I)
_PREGUNTA_NOMBRE = re.compile(r"^(?:oye[, ]+)?(?:prisma[, ]+)?(?:sabes |te acuerdas de )?(?:como me llamo|cual es mi nombre|quien soy(?: yo)?|mi nombre)$")
_PREGUNTA_DATOS = re.compile(r"^(?:oye[, ]+)?(?:prisma[, ]+)?(?:que sabes de mi|que recuerdas de mi|que te he pedido que recuerdes)$")
_OLVIDA = re.compile(r"^(?:oye[, ]+)?(?:prisma[, ]+)?(?:olvida|borra)(?:\s+que)?\s+(.+)$", re.I)


def carga():
    try:
        with open(RUTA, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {"nombre": None, "datos": []}


def guarda(m):
    os.makedirs(os.path.dirname(RUTA), exist_ok=True)
    with open(RUTA, "w", encoding="utf-8") as f:
        json.dump(m, f, ensure_ascii=False, indent=1)


def resumen(m):
    """Texto para las instrucciones del modelo."""
    partes = []
    if m.get("nombre"):
        partes.append(f"La persona con la que hablas se llama {m['nombre']}.")
    if m.get("datos"):
        partes.append("Cosas que te ha pedido recordar: " + "; ".join(m["datos"]) + ".")
    return " ".join(partes)


def _sin_tildes(t):
    import unicodedata
    t = unicodedata.normalize("NFD", t.lower())
    return "".join(c for c in t if unicodedata.category(c) != "Mn")


def intenta(texto):
    """Si el texto es una orden o pregunta de memoria, la resuelve y devuelve (respuesta, cambio);
    si no, None. «cambio» indica si se ha modificado la memoria."""
    t = texto.strip().strip("?¿!¡. ")
    n = _sin_tildes(t)
    m = carga()
    # preguntas: se contestan sin el modelo, que con 1,7B no siempre hace caso a sus instrucciones
    if _PREGUNTA_NOMBRE.match(n):
        if m.get("nombre"):
            return f"Te llamas {m['nombre']}.", False
        return "Todavía no me lo has dicho. Dime «me llamo…» y lo recordaré.", False
    if _PREGUNTA_DATOS.match(n):
        partes = ([f"te llamas {m['nombre']}"] if m.get("nombre") else []) + m.get("datos", [])
        if not partes:
            return "Todavía no me has pedido que recuerde nada.", False
        return "Sé que " + "; ".join(partes) + ".", False
    if g := _NOMBRE.match(t):
        nombre = g.group(1).strip().title()
        m["nombre"] = nombre
        guarda(m)
        return f"Encantado, {nombre}. Lo recordaré.", True
    if g := _RECUERDA.match(t):
        dato = g.group(1).strip()
        if dato.lower().startswith(("me llamo ", "mi nombre es ")):
            return intenta(dato)
        m["datos"] = [d for d in m["datos"] if d.lower() != dato.lower()] + [dato]
        guarda(m)
        return "Hecho, lo recordaré.", True
    if g := _OLVIDA.match(t):
        dato = g.group(1).strip().lower()
        if dato in ("mi nombre", "como me llamo", "cómo me llamo"):
            m["nombre"] = None
        elif dato in ("todo", "todo lo que sabes"):
            m = {"nombre": None, "datos": []}
        else:
            m["datos"] = [d for d in m["datos"] if dato not in d.lower()]
        guarda(m)
        return "De acuerdo, lo he olvidado.", True
    return None
