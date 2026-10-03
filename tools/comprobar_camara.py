#!/usr/bin/env python3
"""Comprueba la bandeja (2a), la caja superior (2b) y la balda del KABD: mallas cerradas,
tamaño de impresión, choques entre piezas de la carcasa y con los componentes, y el volumen
neto real de la cámara acústica con todas las piezas modeladas.

Requisitos: OpenSCAD, `pip install trimesh numpy manifold3d`.
Uso: python3 tools/comprobar_camara.py
"""
import os, subprocess, sys, tempfile, warnings
import trimesh
warnings.filterwarnings("ignore", category=RuntimeWarning)
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "enclosure", "openscad")
MODEL = "prisma_volumetrica_v0_5.scad"
BED = (260, 260, 260)
COMPONENTS = ["screen", "screen_conn", "pi_port_clear", "pi5", "kabd", "buck", "dac", "dc_jack",
              "power_button", "top_buttons", "led_bar", "edge_leds", "mics", "camera", "speaker", "pr"]
CONTACT = 30        # mm³: apoyos planos y uniones a 0,01 mm
TOUCHES = {("balda", "kabd")}    # el KABD apoya en la balda


def export(expr, out):
    with tempfile.NamedTemporaryFile("w", suffix=".scad", delete=False, dir=D) as f:
        f.write("use <bandeja.scad>;\nuse <caja_superior.scad>;\nuse <cubeta.scad>;\nuse <capucha.scad>;\n"
                f"use <{MODEL}>;\ninclude <parametros.scad>;\n{expr}\n")
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
    parts = {n: export(e, os.path.join(tmp, n + ".stl")) for n, e in
             [("bandeja", "bandeja();"), ("caja", "caja();"), ("balda", "balda_en_sitio();"),
              ("cubeta", "cubeta();"), ("capucha", "capucha();")]}
    for n in ["bandeja", "caja", "balda"]:
        m = parts[n]
        print(f"{n}: {m.volume/1000:.0f} cm³, {m.extents[0]:.0f} × {m.extents[1]:.0f} × {m.extents[2]:.0f} mm, cerrada: {m.is_watertight}")
        if not m.is_watertight: problems.append(f"{n}: la malla no está cerrada")
        if any(e > b for e, b in zip(sorted(m.extents), sorted(BED))): problems.append(f"{n}: no cabe en la cama")
    for a, b in [("bandeja", "cubeta"), ("bandeja", "capucha"), ("caja", "cubeta"), ("caja", "capucha"),
                 ("caja", "bandeja"), ("balda", "capucha"), ("balda", "caja")]:
        v = inter(parts[a], parts[b])
        if v > CONTACT: problems.append(f"{a} ↔ {b}: {v:.0f} mm³")
    for c in COMPONENTS:
        comp = export(f'component("{c}");', os.path.join(tmp, c + ".stl"))
        if comp is None or comp.volume == 0: continue
        for n in ["bandeja", "caja", "balda"]:
            v = inter(parts[n], comp)
            if v > (CONTACT if (n, c) in TOUCHES else 0.5): problems.append(f"{n} ↔ {c}: {v:.0f} mm³")

    air = export('component("chamber_air");', os.path.join(tmp, "air.stl"))
    front = export('''union() {
        translate([outer_w/2, 0, 0]) rotate([-front_angle, 0, 0]) translate([0, 0, drv_s]) rotate([-90, 0, 0]) cylinder(d = drv_cut, h = drv_n);
        translate([outer_w/2, pr_flange_y, audio_center_z]) rotate([-90, 0, 0]) cylinder(d = pr_cut, h = outer_d - pr_flange_y); }''',
        os.path.join(tmp, "front.stl"))
    t = {n: inter(air, parts[n]) / 1e6 for n in ["cubeta", "bandeja", "caja"]}
    fr = inter(air, front) / 1e6
    net = air.volume / 1e6 - sum(t.values()) - fr - 0.10
    print(f"Cámara: {air.volume/1e6:.2f} L − cubeta {t['cubeta']:.2f} − bandeja {t['bandeja']:.2f} − caja {t['caja']:.2f}"
          f" − delante de los conos {fr:.2f} − reserva 0,10 = {net:.2f} L netos")
    if not 3.0 <= net <= 4.0: problems.append(f"volumen neto {net:.2f} L fuera de 3–4 L")
    if problems:
        print("PROBLEMAS:"); [print("  -", p) for p in problems]; sys.exit(1)
    print("OK")


if __name__ == "__main__":
    main()
