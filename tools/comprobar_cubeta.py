#!/usr/bin/env python3
"""Comprueba la cubeta acústica: malla cerrada, tamaño de impresión, interferencias con
altavoz, radiador y tabiques, y volumen neto real de la cámara descontando la propia pieza
(anillos, rebordes, refuerzos). Uso: python3 tools/comprobar_cubeta.py"""
import os, subprocess, sys, tempfile, warnings
import trimesh
warnings.filterwarnings("ignore", category=RuntimeWarning)
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "enclosure", "openscad")
BED = (260, 260, 260)
TOL = {"speaker": 5, "pr": 5, "chamber_walls": 60}   # contactos de apoyo y solapes de 0,01 mm del volumétrico

def stl(expr, out):
    with tempfile.NamedTemporaryFile("w", suffix=".scad", delete=False, dir=D) as f:
        f.write('use <cubeta.scad>;\nuse <prisma_volumetrica_v0_3.scad>;\ninclude <parametros.scad>;\n' + expr + "\n")
        src = f.name
    try:
        r = subprocess.run(["openscad", "-o", out, src], capture_output=True, text=True)
        return os.path.exists(out) and "empty" not in (r.stdout + r.stderr).lower()
    finally:
        os.remove(src)

def vol(expr, tmp, name):
    o = os.path.join(tmp, name + ".stl")
    return trimesh.load(o).volume if stl(expr, o) else 0.0

tmp = tempfile.mkdtemp(); problems = []
o = os.path.join(tmp, "c.stl"); stl("cubeta();", o); m = trimesh.load(o)
print(f"Cubeta: {m.volume/1000:.0f} cm³, cerrada: {m.is_watertight}, "
      f"{m.extents[0]:.0f} × {m.extents[1]:.0f} × {m.extents[2]:.0f} mm")
if not m.is_watertight: problems.append("la malla no está cerrada")
if any(e > b for e, b in zip(sorted(m.extents), sorted(BED))): problems.append("no cabe en la cama")
for c in ["speaker", "pr", "chamber_walls"]:
    v = vol(f'intersection() {{ cubeta(); component("{c}"); }}', tmp, c)
    if v > TOL[c]: problems.append(f"cubeta ↔ {c}: {v:.0f} mm³")

# Volumen neto: aire del volumétrico menos lo que ocupa la cubeta dentro de la cámara y menos el aire
# que queda delante de los conos (entre rejilla y cono, fuera de la caja)
air = vol('component("chamber_air");', tmp, "air")
taken = vol('intersection() { component("chamber_air"); cubeta(); }', tmp, "taken")
front = vol('''intersection() { component("chamber_air"); union() {
    translate([outer_w/2, 0, audio_center_z]) rotate([-90,0,0]) cylinder(d = drv_cut, h = drv_flange_y);
    translate([outer_w/2, pr_flange_y, audio_center_z]) rotate([-90,0,0]) cylinder(d = pr_cut, h = outer_d - pr_flange_y); } }''', tmp, "front")
net = (air - taken - front) / 1e6 - 0.10
print(f"Cámara: {air/1e6:.2f} L del volumétrico − {taken/1e6:.2f} L de la cubeta − {front/1e6:.2f} L delante de los conos"
      f" − 0,10 L de reserva = {net:.2f} L netos (la caja superior 2b restará ≈0,05 L más)")
if not 3.0 <= net <= 4.0: problems.append(f"volumen neto {net:.2f} L fuera de 3–4 L")
if problems:
    print("PROBLEMAS:"); [print("  -", p) for p in problems]; sys.exit(1)
print("OK")
