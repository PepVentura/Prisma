#!/usr/bin/env python3
"""Prisma por texto: el núcleo del asistente sin voz, para probarlo y medir tiempos.

  python3 ~/prisma/software/prisma_texto.py            charla (escribe 'salir' para terminar)
  python3 ~/prisma/software/prisma_texto.py --tiempos  muestra el desglose de tiempos en cada respuesta
  python3 ~/prisma/software/prisma_texto.py --configurar-noticias   busca los RSS de los periódicos (una vez)

Memoria: «me llamo…», «recuerda que…», «olvida…» (se guarda en ~/.config/prisma/memoria.json).
Sin modelo (no inventan): hora y fecha, el tiempo (Open-Meteo), fútbol (football-data.org),
noticias (RSS) y búsquedas (lee el fragmento más relevante citando la fuente).
El modelo solo se usa para charlar.

Cada trozo de la respuesta aparece cuando Piper ya podría empezar a leerlo.
"""
import argparse, sys, time, urllib.error
from nucleo.config import CONFIG
from nucleo import enrutador, memoria
from nucleo.fuentes import web, noticias
from nucleo.cerebro import Cerebro

GRIS, AZUL, FIN = "\033[90m", "\033[96m", "\033[0m"


def turno(cerebro, texto, tiempos):
    t0 = time.perf_counter()
    r = memoria.intenta(texto)                  # «me llamo…», «¿cómo me llamo?», «recuerda que…»: sin modelo
    if r:
        respuesta, cambio = r
        if cambio:
            cerebro.actualiza_sistema()
            cerebro.historial.clear()            # que no repita respuestas anteriores ya superadas
        print(f"{AZUL}Prisma:{FIN} {respuesta}")
        if tiempos:
            print(f"{GRIS}[memoria · {time.perf_counter() - t0:.2f} s]{FIN}")
        return
    accion, datos = enrutador.decide(texto)
    if accion != "charla":
        if accion == "web":
            print(f"{AZUL}Prisma:{FIN} Lo busco…", flush=True)
        detalle = ""
        try:
            if accion == "reloj":
                respuesta = datos
            elif accion == "web":
                respuesta, tb, detalle = web.responde(datos)
                detalle = f" · búsqueda {tb:.1f} s · {detalle}"
            else:
                respuesta = enrutador.responde_fuente(accion, datos)
        except Exception as e:                    # sin red, clave errónea, servicio caído…
            respuesta = "No he podido consultarlo ahora mismo."
            detalle = f" · error: {e}"
        print(f"{AZUL}Prisma:{FIN} {respuesta}")
        if tiempos:
            print(f"{GRIS}[{accion}{detalle} · {time.perf_counter() - t0:.1f} s]{FIN}")
        return
    contexto = None
    detalle = []
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
    ap.add_argument("--configurar-noticias", action="store_true", help="busca los RSS de los periódicos y sale")
    a = ap.parse_args()
    if a.configurar_noticias:
        print("Buscando los RSS de los periódicos…")
        noticias.configura()
        return
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
