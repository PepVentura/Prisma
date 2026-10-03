// Prisma — BANDEJA v0.1 (pieza 2a de la carcasa) — D027, D034
//
// Techo del bloque inferior de la cámara acústica, delante del tabique inclinado.
// Placa de 5 mm (z 108–113) que se apoya en el reborde delantero, los rebordes laterales y
// el anillo del altavoz de la cubeta, con burlete de espuma debajo.
//  - 2 tornillos M3 × 10 avellanados delante, a insertos de la cubeta.
//  - Detrás la pisa el tabique de la caja superior (2b), que lleva sus propios tornillos.
//  - 2 agujeros para los pasadores de la capucha (D029).
//  - Muescas para el canal de las franjas de luz (D033): la bandeja hace de pared del canal.
//  - Borde delantero 1 mm retrasado: al bajar la capucha en vertical, su frontal inclinado
//    avanza ≈1 mm en los últimos 5 mm.
//
// Material: PLA negro. Impresión: plana, cara inferior en la cama, sin soportes.

use <prisma_volumetrica_v0_5.scad>;
include <parametros.scad>;
$fn = 40;

pieza = "bandeja";   // "bandeja" | "montaje"

H = chamber_low_top;
fa = front_angle;
tray_screw_y = H * tan(fa) + tray_screw_n / cos(fa);
pin_y = (H + wall_int) * tan(fa) + pin_n;

module bandeja_envelope() intersection() {
    translate([-1, -1, H]) cube([outer_w + 2, outer_d + 2, wall_int]);
    difference() { translate([-1, -1, H - 1]) cube([outer_w + 2, outer_d + 2, wall_int + 2]); behind(part_n + wall_int); }
    body(wall + box_gap);
    translate([0, tray_front_gap, 0]) body(wall);
}

module bandeja() difference() {
    bandeja_envelope();
    component("edge_void");
    for (x = [wall + pin_block / 2, outer_w - wall - pin_block / 2])
        translate([x, pin_y, H + wall_int - pin_len - 0.5]) cylinder(d = pin_hole_d, h = pin_len + 1);
    for (x = [tray_screw_x, outer_w - tray_screw_x]) translate([x, tray_screw_y, H - 0.01]) {
        cylinder(d = 3.4, h = wall_int + 1);
        translate([0, 0, wall_int - 1.8]) cylinder(d1 = 3.4, d2 = 6.6, h = 1.82);
    }
}

if (pieza == "bandeja") bandeja();
if (pieza == "montaje") { bandeja(); color([0.3, 0.3, 0.3, 0.3]) component("shell"); }
