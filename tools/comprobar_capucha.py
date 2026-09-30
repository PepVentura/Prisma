#!/usr/bin/env python3
"""Comprueba la capucha: interferencias con los componentes del volumétrico, pieza cerrada
(watertight) y tamaño de impresión. Uso: python3 tools/comprobar_capucha.py"""
import os, subprocess, sys, tempfile, warnings
import trimesh
warnings.filterwarnings("ignore", category=RuntimeWarning)
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "enclosure", "openscad")
BED = (260, 260, 260)
COMPONENTS = ["screen", "screen_conn", "pi_port_clear", "pi5", "kabd", "buck", "dac", "bracket",
              "led_bar", "mics", "camera", "speaker", "pr", "chamber_walls"]
# contactos buscados: los resaltes tocan el PCB de la pantalla y la placa de la cámara
TOLERANCE_MM3 = {"screen": 5, "camera": 5,
                 "chamber_walls": 60}   # los tabiques del volumétrico se solapan 0,01 mm con la pared exterior

def stl(expr, out):
    with tempfile.NamedTemporaryFile("w", suffix=".scad", delete=False, dir=D) as f:
        f.write('use <capucha.scad>;\nuse <prisma_volumetrica_v0_3.scad>;\ninclude <parametros.scad>;\n' + expr + "\n")
        src = f.name
    try:
        r = subprocess.run(["openscad", "-o", out, src], capture_output=True, text=True)
        return os.path.exists(out) and "empty" not in (r.stdout + r.stderr).lower()
    finally:
        os.remove(src)

tmp = tempfile.mkdtemp(); problems = []
out = os.path.join(tmp, "c.stl")
stl("capucha();", out)
m = trimesh.load(out)
print(f"Capucha: {m.volume/1000:.0f} cm³ (≈{m.volume/1000*1.24:.0f} g de PLA al 100 %), cerrada: {m.is_watertight}")
ext = sorted(m.extents)
print(f"Medidas: {m.extents[0]:.0f} × {m.extents[1]:.0f} × {m.extents[2]:.0f} mm")
if not m.is_watertight: problems.append("la malla no está cerrada")
if any(e > b for e, b in zip(sorted(m.extents), sorted(BED))): problems.append("no cabe en la cama")
for c in COMPONENTS:
    o = os.path.join(tmp, c + ".stl")
    if stl(f'intersection() {{ capucha(); component("{c}"); }}', o):
        v = trimesh.load(o).volume
        if v > TOLERANCE_MM3.get(c, 0.5):
            problems.append(f"capucha ↔ {c}: {v:.0f} mm³")
if problems:
    print("PROBLEMAS:"); [print("  -", p) for p in problems]; sys.exit(1)
print(f"OK: sin interferencias con {len(COMPONENTS)} componentes.")
