"""Búsqueda en Internet con SearXNG, recortada para que el modelo lea poco."""
import json, time, urllib.parse, urllib.request
from .config import CONFIG


def buscar(consulta):
    """Devuelve (respuesta_directa, contexto, segundos)."""
    params = {"q": consulta, "format": "json", "language": "es-ES",
              "timeout_limit": CONFIG["busqueda_espera"]}
    if CONFIG["buscadores"]:
        params["engines"] = CONFIG["buscadores"]
    t0 = time.perf_counter()
    res = _pide(params)
    if not res.get("results") and CONFIG["buscadores"]:      # si los elegidos fallan, todos
        params.pop("engines")
        res = _pide(params)
    t = time.perf_counter() - t0

    directa = None
    for a in res.get("answers") or []:
        directa = a.get("answer") if isinstance(a, dict) else a
        if directa: break
    if not directa:
        for box in res.get("infoboxes") or []:
            if box.get("content"):
                directa = _recorta(box["content"], CONFIG["busqueda_caracteres"]); break

    trozos = []
    n = CONFIG["busqueda_resultados"] - (1 if directa else 0)     # con respuesta directa, un resultado menos
    for r in res.get("results", [])[:max(n, 1)]:
        texto = _recorta(r.get("content") or "", CONFIG["busqueda_caracteres"])
        if texto:
            trozos.append(f"- {r.get('title', '').strip()}: {texto}")
    return directa, "\n".join(trozos), t


def _pide(params):
    url = CONFIG["searxng"] + "/search?" + urllib.parse.urlencode(params)
    with urllib.request.urlopen(url, timeout=CONFIG["busqueda_espera"] + 3) as r:
        return json.load(r)


def _recorta(texto, n):
    texto = " ".join(texto.split())
    if len(texto) <= n:
        return texto
    corte = texto[:n].rsplit(" ", 1)[0]
    return corte + "…"
