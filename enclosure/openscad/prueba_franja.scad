// Prisma — PIEZA DE PRUEBA DE LAS FRANJAS (D033)
//
// Un tramo de 50 mm de la pared del frontal con la ranura de 4 mm y el canal de la tira
// de LEDs detrás, igual que en la cubeta y la capucha, y 3 insertos con distinta holgura.
// Sirve para elegir la holgura (edge_ins_clear en parametros.scad) y ver cómo difunde la luz
// tu filamento transparente antes de imprimir las piezas grandes.
//
// Impresión: pared en PLA negro mate, de pie (como la cubeta); insertos en PETG o PLA
// transparente, tumbados con la cara vista sobre la cama.
// Los insertos entran deslizando por arriba. Marcas en la pestaña: 1 muesca = 0,10 mm por lado,
// 2 = 0,15 mm (la del diseño), 3 = 0,20 mm.

use <prisma_volumetrica_v0_5.scad>;
include <parametros.scad>;
$fn = 32;

pieza = "todo";   // "pared" | "insertos" | "todo"

L = 50;            // largo del tramo
W = 30;            // ancho del trozo de pared
slot_z0 = 5;       // la ranura llega hasta arriba (abierta), como en la unión de las piezas
cx = W / 2;
clears = [0.10, 0.15, 0.20];

module pared() difference() {
    union() {
        cube([W, wall, L]);                                                         // pared frontal
        translate([cx - edge_ch_w / 2 - edge_ch_t, wall - 0.01, 0])
            cube([edge_ch_w + 2 * edge_ch_t, edge_ch_n + edge_ch_t - wall + 0.01, L]); // canal
        translate([0, 0, 0]) cube([W, 25, 2]);                                      // pie de apoyo
    }
    translate([cx - edge_strip_w / 2, -1, slot_z0]) cube([edge_strip_w, wall + 1.02, L]);          // ranura
    translate([cx - edge_ch_w / 2, wall - 0.01, 2]) cube([edge_ch_w, edge_ch_n - wall + 0.01, L]);   // hueco del canal
    translate([cx - 2, edge_ch_n - 0.01, 8]) cube([4, edge_ch_t + 1, 6]);                          // salida de cables
}

// Insertos tumbados: cara vista abajo (z = 0), a lo largo de X
module insertos() for (i = [0 : 2]) translate([0, i * 10, 0]) difference() {
    multmatrix([[0, 0, 1, 0], [1, 0, 0, 0], [0, 1, 0, 0]])
        linear_extrude(L - slot_z0 - 0.3) edge_insert_profile(clears[i]);
    for (k = [0 : i]) translate([L - slot_z0 - 2 - k * 2.5, -4, wall + 0.8]) cube([1, 8, 2]);    // muescas
}

if (pieza == "pared" || pieza == "todo") pared();
if (pieza == "insertos") insertos();
if (pieza == "todo") translate([W + 8, 0, 0]) insertos();
