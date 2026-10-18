"""Memoria de Prisma: datos que el usuario le pide recordar (su nombre, gustos…).
Se guarda en ~/.config/prisma/memoria.json y se añade a las instrucciones del modelo."""
import json, os, re

RUTA = os.path.expanduser("~/.config/prisma/memoria.json")
_NOMBRE = re.compile(r"^(?:oye[, ]+)?(?:prisma[, ]+)?(?:me llamo|mi nombre es|llamame|llámame)\s+([a-záéíóúñü][\w áéíóúñü'-]{0,30})$", re.I)
_RECUERDA = re.compile(r"^(?:oye[, ]+)?(?:prisma[, ]+)?(?:recuerda|apunta|memoriza|no olvides)(?:\s+que)?\s+(.+)$", re.I)
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


def intenta(texto):
    """Si el texto es una orden de memoria, la ejecuta y devuelve la respuesta hablada; si no, None."""
    t = texto.strip().strip("?¿!¡. ")
    m = carga()
    if g := _NOMBRE.match(t):
        nombre = g.group(1).strip().title()
        m["nombre"] = nombre
        guarda(m)
        return f"Encantado, {nombre}. Lo recordaré."
    if g := _RECUERDA.match(t):
        dato = g.group(1).strip()
        if dato.lower().startswith(("me llamo ", "mi nombre es ")):
            return intenta(dato)
        m["datos"] = [d for d in m["datos"] if d.lower() != dato.lower()] + [dato]
        guarda(m)
        return "Hecho, lo recordaré."
    if g := _OLVIDA.match(t):
        dato = g.group(1).strip().lower()
        if dato in ("mi nombre", "como me llamo", "cómo me llamo"):
            m["nombre"] = None
        elif dato in ("todo", "todo lo que sabes"):
            m = {"nombre": None, "datos": []}
        else:
            m["datos"] = [d for d in m["datos"] if dato not in d.lower()]
        guarda(m)
        return "De acuerdo, lo he olvidado."
    return None
