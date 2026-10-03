#!/usr/bin/env python3
"""Comprueba la cubeta acústica: malla cerrada, tamaño de impresión, interferencias con
altavoz, radiador y tabiques, y volumen neto real de la cámara descontando la propia pieza
(anillos, rebordes, refuerzos) y el aire que queda delante de los conos.

Requisitos: OpenSCAD, `pip install trimesh numpy manifold3d`.
Uso: python3 tools/comprobar_cubeta.py
"""
import os, subprocess, sys, tempfile, warnings
import trimesh
warnings.filterwarnings("ignore", category=RuntimeWarning)
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "enclosure", "openscad")
MODEL = "prisma_volumetrica_v0_5.scad"
BED = (260, 260, 260)
TOL = {"speaker": 5, "pr": 5, "chamber_walls": 60}
BOX_2B_L = 0.05     # paredes propias de la caja superior (pieza 2b), aún sin modelar


def export(expr, out):
    with tempfile.NamedTemporaryFile("w", suffix=".scad", delete=False, dir=D) as f:
        f.write(f"use <cubeta.scad>;\nuse <{MODEL}>;\ninclude <parametros.scad>;\n{expr}\n")
        src = f.name
    try:
        subprocess.run(["openscad", "-o", out, src], capture_output=True, text=True)
        return trimesh.load(out) if os.path.exists(out) else None
    finally:
        os.remove(src)


def inter(a, b):
    return trimesh.boolean.intersection([a, b], engine="manifold").volume


def main():
    tmp = tempfile.mkdtemp(); problems = []
    m = export("cubeta();", os.path.join(tmp, "c.stl"))
    print(f"Cubeta: {m.volume/1000:.0f} cm³, cerrada: {m.is_watertight}, "
          f"{m.extents[0]:.0f} × {m.extents[1]:.0f} × {m.extents[2]:.0f} mm")
    if not m.is_watertight: problems.append("la malla no está cerrada")
    if any(e > b for e, b in zip(sorted(m.extents), sorted(BED))): problems.append("no cabe en la cama")
    for c in ["speaker", "pr", "chamber_walls"]:
        comp = export(f'component("{c}");', os.path.join(tmp, c + ".stl"))
        v = inter(m, comp)
        if v > TOL[c]: problems.append(f"cubeta ↔ {c}: {v:.0f} mm³")

    air = export('component("chamber_air");', os.path.join(tmp, "air.stl"))
    front = export('''union() {
        translate([outer_w/2, 0, 0]) rotate([-front_angle, 0, 0]) translate([0, 0, drv_s]) rotate([-90, 0, 0]) cylinder(d = drv_cut, h = drv_n);
        translate([outer_w/2, pr_flange_y, audio_center_z]) rotate([-90, 0, 0]) cylinder(d = pr_cut, h = outer_d - pr_flange_y); }''',
        os.path.join(tmp, "front.stl"))
    taken = inter(air, m); fr = inter(air, front)
    net = (air.volume - taken - fr) / 1e6 - 0.10 - BOX_2B_L
    print(f"Cámara: {air.volume/1e6:.2f} L del volumétrico − {taken/1e6:.2f} L de la cubeta − {fr/1e6:.2f} L delante de los conos"
          f" − 0,10 L de reserva − {BOX_2B_L:.2f} L de la caja superior = {net:.2f} L netos")
    if not 3.0 <= net <= 4.0: problems.append(f"volumen neto {net:.2f} L fuera de 3–4 L")
    if problems:
        print("PROBLEMAS:"); [print("  -", p) for p in problems]; sys.exit(1)
    print("OK")


if __name__ == "__main__":
    main()
