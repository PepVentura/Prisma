#!/usr/bin/env python3
"""Prisma — prueba de la IA local en la Raspberry Pi 5.

Mide lo que importa para la voz: cuánto tarda en salir la primera frase completa
(es cuando Piper podría empezar a hablar) y la velocidad de generación.

  python3 prueba_ia.py --comparar              compara los modelos instalados con preguntas fijas
  python3 prueba_ia.py --modelo qwen3.5:2b     charla por texto con un modelo (escribe 'salir' para terminar)
  python3 prueba_ia.py --modelo qwen3.5:2b --buscar "¿quién ganó el último Tour de Francia?"

Solo usa la biblioteca estándar de Python.
"""
import argparse, json, re, sys, time, urllib.parse, urllib.request

OLLAMA = "http://127.0.0.1:11434"
SEARXNG = "http://127.0.0.1:8888"
SISTEMA = ("Eres Prisma, un asistente de sobremesa que habla en español de España. "
           "Respondes de forma natural y breve: una a tres frases, sin listas ni formato, "
           "porque tu respuesta se leerá en voz alta.")
PREGUNTAS = [
    "Hola, ¿qué tal estás?",
    "Cuéntame un chiste corto.",
    "Explícame en pocas palabras qué es un radiador pasivo en un altavoz.",
    "¿Qué me recomiendas cenar hoy algo ligero?",
]
FIN_FRASE = re.compile(r"[.!?…]\s")


def modelos_instalados():
    with urllib.request.urlopen(OLLAMA + "/api/tags") as r:
        return [m["name"] for m in json.load(r)["models"]]


def preguntar(modelo, mensajes, mostrar=True):
    """Envía la conversación en streaming y devuelve (texto, métricas)."""
    datos = json.dumps({"model": modelo, "messages": mensajes, "stream": True, "think": False,
                        "options": {"num_predict": 160, "temperature": 0.6}}).encode()
    req = urllib.request.Request(OLLAMA + "/api/chat", data=datos, headers={"Content-Type": "application/json"})
    t0 = time.perf_counter(); t_primer = t_frase = None; texto = ""; final = {}
    with urllib.request.urlopen(req) as r:
        for linea in r:
            trozo = json.loads(linea)
            c = trozo.get("message", {}).get("content", "")
            if c:
                if t_primer is None: t_primer = time.perf_counter() - t0
                texto += c
                if mostrar: print(c, end="", flush=True)
                if t_frase is None and FIN_FRASE.search(texto + " "): t_frase = time.perf_counter() - t0
            if trozo.get("done"): final = trozo
    total = time.perf_counter() - t0
    if mostrar: print()
    n = final.get("eval_count", 0); d = final.get("eval_duration", 1) / 1e9
    pn = final.get("prompt_eval_count", 0); pd = final.get("prompt_eval_duration", 1) / 1e9
    return texto, {"primer_token": t_primer or total, "primera_frase": t_frase or total, "total": total,
                   "tok_s": n / d if d else 0, "lectura_tok_s": pn / pd if pd else 0, "tokens_pregunta": pn}


def buscar(pregunta, n=3, recorte=220):
    url = SEARXNG + "/search?" + urllib.parse.urlencode({"q": pregunta, "format": "json", "language": "es-ES"})
    t0 = time.perf_counter()
    with urllib.request.urlopen(url, timeout=8) as r:
        res = json.load(r)
    t = time.perf_counter() - t0
    directa = (res.get("answers") or [None])[0]
    if isinstance(directa, dict): directa = directa.get("answer")
    trozos = [f"- {x.get('title', '')}: {(x.get('content') or '')[:recorte]}" for x in res.get("results", [])[:n]]
    return directa, "\n".join(trozos), t


def comparar(modelos):
    print(f"Modelos: {', '.join(modelos)}\n")
    filas = []
    for m in modelos:
        print(f"== {m} (cargando…)")
        preguntar(m, [{"role": "user", "content": "Hola"}], mostrar=False)   # carga en memoria
        medidas = []
        for p in PREGUNTAS:
            print(f"> {p}\n  ", end="")
            _, k = preguntar(m, [{"role": "system", "content": SISTEMA}, {"role": "user", "content": p}])
            medidas.append(k)
            print(f"  [primera frase {k['primera_frase']:.1f} s · {k['tok_s']:.1f} tok/s]\n")
        media = lambda c: sum(x[c] for x in medidas) / len(medidas)
        filas.append((m, media("primer_token"), media("primera_frase"), media("total"), media("tok_s"), media("lectura_tok_s")))
    print("\nResumen (medias)")
    print(f"{'modelo':<16}{'1.er token':>11}{'1.ª frase':>11}{'total':>8}{'gen tok/s':>11}{'lect. tok/s':>13}")
    for f in filas:
        print(f"{f[0]:<16}{f[1]:>10.1f}s{f[2]:>10.1f}s{f[3]:>7.1f}s{f[4]:>11.1f}{f[5]:>13.0f}")
    print("\nA la voz le importa la columna '1.ª frase': es cuando Prisma empezaría a hablar.")


def con_busqueda(modelo, pregunta):
    directa, contexto, t = buscar(pregunta)
    print(f"[SearXNG: {t:.1f} s]")
    if directa:
        print(f"Respuesta directa del buscador: {directa}")
    mensajes = [{"role": "system", "content": SISTEMA + " Usa solo estos resultados de búsqueda; si no "
                 "contienen la respuesta, dilo.\n" + contexto},
                {"role": "user", "content": pregunta}]
    _, k = preguntar(modelo, mensajes)
    print(f"[{k['tokens_pregunta']} tokens leídos a {k['lectura_tok_s']:.0f} tok/s · primera frase a los "
          f"{t + k['primera_frase']:.1f} s contando la búsqueda]")


def charla(modelo):
    historial = [{"role": "system", "content": SISTEMA}]
    print(f"Charla con {modelo}. Escribe 'salir' para terminar.")
    while True:
        try: p = input("\nTú: ").strip()
        except EOFError: break
        if p.lower() in ("salir", "exit", "q"): break
        historial.append({"role": "user", "content": p})
        print("Prisma: ", end="")
        texto, k = preguntar(modelo, historial[-7:])
        historial.append({"role": "assistant", "content": texto})
        print(f"[primera frase {k['primera_frase']:.1f} s · {k['tok_s']:.1f} tok/s]")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--comparar", action="store_true")
    ap.add_argument("--modelo")
    ap.add_argument("--buscar")
    a = ap.parse_args()
    try:
        if a.comparar: comparar([a.modelo] if a.modelo else modelos_instalados())
        elif a.modelo and a.buscar: con_busqueda(a.modelo, a.buscar)
        elif a.modelo: charla(a.modelo)
        else: ap.print_help()
    except urllib.error.URLError as e:
        sys.exit(f"No hay conexión con Ollama o SearXNG ({e}). ¿Has ejecutado 02_ia.sh?")
