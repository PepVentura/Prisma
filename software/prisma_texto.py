#!/usr/bin/env python3
"""Prisma por texto: el núcleo del asistente sin voz, para probarlo y medir tiempos.

  python3 ~/prisma/software/prisma_texto.py            charla (escribe 'salir' para terminar)
  python3 ~/prisma/software/prisma_texto.py --tiempos  muestra el desglose de tiempos en cada respuesta

Cada trozo de la respuesta aparece cuando Piper ya podría empezar a leerlo.
"""
import argparse, sys, time, urllib.error
from nucleo.config import CONFIG
from nucleo import enrutador, buscador
from nucleo.cerebro import Cerebro

GRIS, AZUL, FIN = "\033[90m", "\033[96m", "\033[0m"


def turno(cerebro, texto, tiempos):
    t0 = time.perf_counter()
    accion, consulta = enrutador.decide(texto)
    contexto = None
    detalle = []
    if accion == "buscar":
        print(f"{AZUL}Prisma:{FIN} Lo busco…", flush=True)
        try:
            directa, contexto, tb = buscador.buscar(consulta)
            detalle.append(f"búsqueda {tb:.1f} s")
            if directa:
                contexto = f"- Respuesta directa: {directa}\n{contexto}"
            if not contexto:
                contexto = "- (la búsqueda no ha devuelto resultados)"
        except (urllib.error.URLError, TimeoutError) as e:
            detalle.append(f"búsqueda fallida: {e}")
            contexto = "- (no se ha podido buscar en Internet)"
    print(f"{AZUL}Prisma:{FIN} ", end="", flush=True)
    primera = None
    for trozo in cerebro.responde(texto, contexto):
        if primera is None:
            primera = time.perf_counter() - t0
        print(trozo, end=" ", flush=True)
    print()
    if tiempos:
        u = cerebro.ultimo
        if u.get("tokens_leidos"):
            detalle.append(f"lectura {u['tokens_leidos']} tokens en {u.get('lectura_s', 0):.1f} s")
        detalle.append(f"generación {u.get('tok_s', 0):.1f} tok/s")
        print(f"{GRIS}[{accion} · {' · '.join(detalle)} · empezaría a hablar a los {primera or 0:.1f} s · "
              f"total {time.perf_counter() - t0:.1f} s]{FIN}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--tiempos", action="store_true")
    a = ap.parse_args()
    cerebro = Cerebro()
    try:
        print(f"{GRIS}Cargando {CONFIG['modelo']}…{FIN}", end="", flush=True)
        print(f"{GRIS} listo en {cerebro.calienta():.1f} s{FIN}")
    except urllib.error.URLError as e:
        sys.exit(f"\nNo hay conexión con Ollama ({e}). ¿Está instalado? bash ~/prisma/software/instalacion/02_ia.sh")
    print("Escribe tu pregunta. 'salir' para terminar.")
    while True:
        try:
            texto = input("\nTú: ").strip()
        except (EOFError, KeyboardInterrupt):
            print(); break
        if not texto:
            continue
        if texto.lower() in ("salir", "adiós", "adios", "exit"):
            break
        turno(cerebro, texto, a.tiempos)


if __name__ == "__main__":
    main()
