#!/usr/bin/env python3
"""Prisma por texto: el asistente en la terminal, para probarlo y medir tiempos.

  python3 ~/prisma/software/prisma_texto.py            charla (escribe 'salir' para terminar)
  python3 ~/prisma/software/prisma_texto.py --tiempos  muestra el desglose de tiempos en cada respuesta
  python3 ~/prisma/software/prisma_texto.py --configurar-noticias   busca los RSS de los periódicos (una vez)

Memoria: «me llamo…», «recuerda que…», «olvida…» (se guarda en ~/.config/prisma/memoria.json).
Sin modelo (no inventan): hora y fecha, el tiempo (Open-Meteo), fútbol (football-data.org),
noticias (RSS) y búsquedas (lee el fragmento más relevante citando la fuente).
El modelo solo se usa para charlar.
"""
import argparse, sys, urllib.error
from nucleo.config import CONFIG
from nucleo.asistente import Asistente
from nucleo.fuentes import noticias

GRIS, AZUL, FIN = "\033[90m", "\033[96m", "\033[0m"


def turno(asistente, texto, tiempos):
    empezado = False
    for ev in asistente.procesa(texto):
        if ev["tipo"] == "trozo":
            if not empezado:
                print(f"{AZUL}Prisma:{FIN} ", end="")
                empezado = True
            if ev["texto"] == "Lo busco…":
                print(ev["texto"])
                empezado = False
            else:
                print(ev["texto"], end=" ", flush=True)
        elif ev["tipo"] == "fin":
            print()
            if tiempos:
                d = f" · {ev['detalle']}" if ev["detalle"] else ""
                print(f"{GRIS}[{ev['accion']}{d} · primera respuesta a los {ev['primera']:.1f} s · "
                      f"total {ev['total']:.1f} s]{FIN}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--tiempos", action="store_true")
    ap.add_argument("--configurar-noticias", action="store_true", help="busca los RSS de los periódicos y sale")
    a = ap.parse_args()
    if a.configurar_noticias:
        print("Buscando los RSS de los periódicos…")
        noticias.configura()
        return
    asistente = Asistente()
    try:
        print(f"{GRIS}Cargando {CONFIG['modelo']}…{FIN}", end="", flush=True)
        print(f"{GRIS} listo en {asistente.calienta():.1f} s{FIN}")
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
        turno(asistente, texto, a.tiempos)


if __name__ == "__main__":
    main()
