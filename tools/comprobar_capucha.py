#!/usr/bin/env python3
"""Comprueba la capucha: malla cerrada, tamaño de impresión e interferencias con los
componentes del volumétrico. Exporta cada pieza una vez con OpenSCAD y hace las
intersecciones con manifold3d (rápido).

Requisitos: OpenSCAD, `pip install trimesh numpy manifold3d`.
Uso: python3 tools/comprobar_capucha.py
"""
import os, subprocess, sys, tempfile, warnings
import trimesh
warnings.filterwarnings("ignore", category=RuntimeWarning)
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "enclosure", "openscad")
MODEL = "prisma_volumetrica_v0_5.scad"
BED = (260, 260, 260)
COMPONENTS = ["screen", "screen_conn", "pi_port_clear", "pi5", "kabd", "buck", "dac", "bracket",
              "led_bar", "edge_leds", "edge_inserts", "mics", "camera", "speaker", "pr", "chamber_walls",
              "ssd", "hdmi_tv"]
# contactos buscados: los resaltes tocan el PCB de la pantalla y la placa de la cámara;
# los tabiques del volumétrico se solapan 0,01 mm con la pared exterior
TOLERANCE_MM3 = {"screen": 5, "camera": 5, "chamber_walls": 60}


def export(expr, out, use="capucha.scad"):
    with tempfile.NamedTemporaryFile("w", suffix=".scad", delete=False, dir=D) as f:
        f.write(f"use <{use}>;\nuse <{MODEL}>;\ninclude <parametros.scad>;\n{expr}\n")
        src = f.name
    try:
        subprocess.run(["openscad", "-o", out, src], capture_output=True, text=True)
        return trimesh.load(out) if os.path.exists(out) else None
    finally:
        os.remove(src)


def main():
    """Comprueba la capucha de una pieza y sus dos mitades (frente y cuerpo, D044), y que entre
    las dos no se solapen."""
    tmp = tempfile.mkdtemp(); problems = []
    piezas = {}
    for nombre in ["capucha", "frente", "cuerpo"]:
        m = export(f"{nombre}();", os.path.join(tmp, nombre + ".stl"))
        piezas[nombre] = m
        print(f"{nombre.capitalize()}: {m.volume/1000:.0f} cm³ (≈{m.volume/1000*1.24:.0f} g de PLA al 100 %), "
              f"cerrada: {m.is_watertight}, medidas {m.extents[0]:.0f} × {m.extents[1]:.0f} × {m.extents[2]:.0f} mm")
        if not m.is_watertight: problems.append(f"{nombre}: la malla no está cerrada")
        if any(e > b for e, b in zip(sorted(m.extents), sorted(BED))): problems.append(f"{nombre}: no cabe en la cama")
    v = trimesh.boolean.intersection([piezas["frente"], piezas["cuerpo"]], engine="manifold").volume
    if v > 0.5: problems.append(f"frente ↔ cuerpo se solapan: {v:.0f} mm³")
    for c in COMPONENTS:
        comp = export(f'component("{c}");', os.path.join(tmp, c + ".stl"))
        if comp is None or comp.volume == 0: continue
        for nombre in ["capucha", "frente", "cuerpo"]:
            v = trimesh.boolean.intersection([piezas[nombre], comp], engine="manifold").volume
            if v > TOLERANCE_MM3.get(c, 0.5):
                problems.append(f"{nombre} ↔ {c}: {v:.0f} mm³")
    if problems:
        print("PROBLEMAS:"); [print("  -", p) for p in problems]; sys.exit(1)
    print(f"OK: sin interferencias con {len(COMPONENTS)} componentes, y frente y cuerpo no se solapan.")


if __name__ == "__main__":
    main()
