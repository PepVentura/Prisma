#!/usr/bin/env python3
"""
Comprobaciones del volumétrico de Prisma.

1. Volumen neto de aire de la cámara acústica (litros), medido sobre el modelo.
2. Interferencias entre componentes, y entre componentes y cámara/paredes.
3. Componentes que se salen de la envolvente interior.

Requisitos: OpenSCAD en el PATH y `pip install trimesh numpy`.
Uso:  python3 tools/comprobar_volumetrico.py [ruta/al/modelo.scad]
"""
import itertools
import warnings
import os
import subprocess
import sys
import tempfile

import trimesh

warnings.filterwarnings("ignore", category=RuntimeWarning)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
    ROOT, "enclosure", "openscad", "prisma_volumetrica_v0_5.scad")
MODEL = os.path.abspath(MODEL)

TARGET_L = 3.5
BRACING_L = 0.10

# Componentes sólidos que no deben tocarse entre sí
COMPONENTS = ["screen", "screen_conn", "pi_port_clear", "speaker", "pr", "pi5",
              "kabd", "buck", "dac", "bracket", "dc_jack", "led_bar", "mics", "camera", "power_button", "top_buttons", "edge_channel"]
# Componentes que atraviesan la pared o la cámara a propósito
MAY_CROSS_SHELL = {"speaker", "pr", "dc_jack", "camera", "edge_channel"}
MAY_ENTER_CHAMBER = {"speaker", "pr"}
# Pares que se solapan a propósito
ALLOWED_PAIRS = set()


def openscad_stl(expr, out):
    """Renderiza una expresión OpenSCAD a STL. Devuelve False si el resultado es vacío."""
    with tempfile.NamedTemporaryFile("w", suffix=".scad", delete=False,
                                     dir=os.path.dirname(MODEL)) as f:
        f.write(f'use <{os.path.basename(MODEL)}>;\ninclude <parametros.scad>;\n{expr}\n')
        src = f.name
    try:
        r = subprocess.run(["openscad", "-o", out, src], capture_output=True, text=True)
        empty = "empty" in (r.stdout + r.stderr).lower() or not os.path.exists(out)
        return not empty
    finally:
        os.remove(src)


def volume_l(expr, tmp):
    out = os.path.join(tmp, "v.stl")
    if not openscad_stl(expr, out):
        return 0.0
    return trimesh.load(out).volume / 1e6


def main():
    tmp = tempfile.mkdtemp()
    problems = []

    # 1. Volumen de la cámara
    air = volume_l('component("chamber_air");', tmp)
    net = air - BRACING_L
    print(f"Cámara acústica: {air:.2f} L de aire (descontados altavoz y radiador)")
    print(f"                 {net:.2f} L netos tras reservar {BRACING_L:.2f} L para refuerzos/espuma")
    print(f"                 objetivo {TARGET_L:.1f} L (rango 3–4 L)")
    if not 3.0 <= net <= 4.0:
        problems.append(f"volumen neto {net:.2f} L fuera del rango 3–4 L")

    # 2. Interferencias entre componentes
    for a, b in itertools.combinations(COMPONENTS, 2):
        if (a, b) in ALLOWED_PAIRS:
            continue
        v = volume_l(f'intersection() {{ component("{a}"); component("{b}"); }}', tmp)
        if v > 1e-6:
            problems.append(f"interferencia {a} ↔ {b}: {v*1e6:.0f} mm³")

    # 3. Componentes frente a tabiques y aire de la cámara
    for c in COMPONENTS:
        v = volume_l(f'intersection() {{ component("{c}"); component("chamber_walls"); }}', tmp)
        if v > 1e-6:
            problems.append(f"interferencia {c} ↔ tabiques de la cámara: {v*1e6:.0f} mm³")
        if c not in MAY_ENTER_CHAMBER:
            v = volume_l(f'intersection() {{ component("{c}"); component("chamber_air"); }}', tmp)
            if v > 1e-6:
                problems.append(f"{c} invade la cámara acústica: {v*1e6:.0f} mm³")
        if c not in MAY_CROSS_SHELL:
            v = volume_l(f'difference() {{ component("{c}"); component("body_inner"); }}', tmp)
            if v > 1e-6:
                problems.append(f"{c} se sale de la envolvente interior: {v*1e6:.0f} mm³")

    print()
    if problems:
        print("PROBLEMAS:")
        for p in problems:
            print("  -", p)
        sys.exit(1)
    print(f"OK: {len(COMPONENTS)} componentes sin interferencias ni salidas de la envolvente.")


if __name__ == "__main__":
    main()
