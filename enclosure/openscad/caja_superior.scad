// Prisma — CAJA SUPERIOR v0.1 (pieza 2b de la carcasa) — D027, D034
//
// Parte alta de la cámara acústica, detrás de la pantalla: tabique inclinado paralelo al
// frontal, laterales, trasera y tapa. Abierta por abajo, sobre el bloque inferior de la cubeta.
// La tapa es el suelo de la bahía de electrónica.
//  - Se apoya en los rebordes laterales y trasero de la cubeta y en el anillo del radiador;
//    el tabique pisa la parte trasera de la bandeja (2a). Burlete de espuma en todo el apoyo.
//  - 4 tubos con tornillos M3 × 80 avellanados desde la tapa hasta los insertos de la cubeta.
//  - 2 resaltes con inserto M3 en la trasera para los tornillos de la capucha (D029).
//  - Paso de los cables del altavoz con un agujero de 5 mm (sellar con silicona).
//  - Bahía: insertos ciegos en la tapa para la Pi 5 (M2.5, con separadores de 3 mm) y para las
//    4 patas de la balda del KABD-250 (M3). La tapa queda lisa para poder imprimirla en la cama.
//
// Material: PETG. Impresión: boca abajo (tapa en la cama), sin soportes; "impresion" la deja girada.
// La balda del KABD es una pieza aparte ("balda"); sus taladros del amplificador se añadirán al medirlo.

use <prisma_volumetrica_v0_5.scad>;
include <parametros.scad>;
$fn = 40;

pieza = "caja";   // "caja" | "impresion" | "balda" | "montaje"

H = chamber_low_top;
top = chamber_up_top + wall_int;     // 187: cara superior de la tapa = suelo de la bahía
fa = front_angle;

insert_hole = 4.0; insert_depth = 5;
tube_d = 7.5;
rear_screw_x = [40, outer_w - 40]; rear_screw_z = 150;      // como en la capucha
cable_hole = [outer_w - 30, 110]; cable_d = 5;

// Bahía (posiciones del volumétrico)
pi_pos = [8, outer_d - wall - pi_d - 2, bay_floor_z];
pi_holes = [for (dx = [3.5, 61.5], dy = [3.5, 52.5]) [pi_pos[0] + dx, pi_pos[1] + dy]];
pi_standoff_h = 3;     // la Pi apoya sobre separadores de 3 mm con inserto M2.5
kabd_pos = [98, outer_d - wall - kabd_d - 1.5];
shelf = [kabd_pos[0] - 2, kabd_pos[1] - 1, kabd_w + 4, kabd_d + 2, 3];   // x, y, ancho, fondo, grueso
post_xy = [[99, 82], [188, 82], [145, 141], [188, 141]];                  // libres de puertos, buck y DAC
post_d = 8;

module envelope() difference() {
    intersection() {
        translate([-1, -1, H]) cube([outer_w + 2, outer_d + 2, top - H]);
        behind(part_n);
        body(wall + box_gap);
    }
    // encima de la bandeja (z 108–113, delante del tabique trasero) no hay caja
    intersection() {
        translate([-1, -1, H - 1]) cube([outer_w + 2, outer_d + 2, wall_int + 1]);
        difference() { translate([-1, -1, H - 2]) cube([outer_w + 2, outer_d + 2, wall_int + 4]); behind(part_n + wall_int); }
    }
}
module hollow() intersection() {
    translate([-1, -1, H - 1]) cube([outer_w + 2, outer_d + 2, chamber_up_top - H + 1]);
    behind(part_n + wall_int);
    body(wall + box_gap + box_t);
}
module tubes() for (x = [box_screw_x, outer_w - box_screw_x], y = box_screw_y)
    translate([x, y, H]) cylinder(d = tube_d, h = top - H);
module tube_holes() for (x = [box_screw_x, outer_w - box_screw_x], y = box_screw_y) translate([x, y, H - 1]) {
    cylinder(d = 3.4, h = top - H + 2);
    translate([0, 0, top - H + 1 - 1.8]) cylinder(d1 = 3.4, d2 = 6.6, h = 1.82);
}
// resaltes de los tornillos traseros, con cuña hacia arriba (imprimible boca abajo)
rear_in = outer_d - wall - box_gap;
module rear_bosses() for (x = rear_screw_x) hull() {
    translate([x, rear_in + 0.01, rear_screw_z]) rotate([90, 0, 0]) cylinder(d = 10, h = box_t + 6);
    translate([x - 5, rear_in - 0.5, rear_screw_z]) cube([10, 0.5, box_t + 8]);
}
module rear_insert_holes() for (x = rear_screw_x)
    translate([x, rear_in + 0.1, rear_screw_z]) rotate([90, 0, 0]) cylinder(d = insert_hole, h = insert_depth + 1.5);

// Bahía: insertos ciegos en la tapa (4 mm de 5: no abren la cámara)
module bay_insert_holes() {
    for (p = pi_holes) translate([p[0], p[1], top - 4]) cylinder(d = 3.5, h = 4.01);          // M2.5 × 4 (Pi, con separadores de 3 mm)
    for (p = post_xy) translate([p[0], p[1], top - 4]) cylinder(d = insert_hole, h = 4.01);   // M3 × 4 (patas de la balda)
}

module caja() {
    difference() {
        union() {
            difference() { envelope(); hollow(); }
            intersection() { union() { tubes(); rear_bosses(); } envelope(); }
        }
        bay_insert_holes();
        tube_holes();
        rear_insert_holes();
        translate([cable_hole[0], cable_hole[1], chamber_up_top - 1]) cylinder(d = cable_d, h = wall_int + 2);
    }
}

// Balda del KABD-250 (PLA o PETG) con 4 patas; tornillos M3 × 35 desde arriba, por dentro de
// las patas, a los insertos de la tapa. Se imprime con la placa en la cama.
leg_h = bracket_z - top;
module balda() difference() {
    union() {
        translate([shelf[0], shelf[1], leg_h]) cube([shelf[2], shelf[3], shelf[4]]);
        for (p = post_xy) translate([p[0], p[1], 0]) cylinder(d = post_d, h = leg_h + 0.01);
    }
    for (p = post_xy) translate([p[0], p[1], -1]) { cylinder(d = 3.4, h = leg_h + 10); translate([0, 0, leg_h + 1]) cylinder(d = 6.2, h = 10); }
    translate([shelf[0] + 20, shelf[1] + 18, leg_h - 1]) cube([shelf[2] - 40, shelf[3] - 36, 10]);   // aligerado y paso de aire
}

if (pieza == "caja") caja();
if (pieza == "impresion") translate([0, outer_d, top]) rotate([180, 0, 0]) caja();
module balda_en_sitio() translate([0, 0, top]) balda();
if (pieza == "balda") translate([0, outer_d, leg_h + shelf[4]]) rotate([180, 0, 0]) balda();   // placa en la cama
if (pieza == "montaje") { caja(); translate([0, 0, top]) balda(); color([0.3, 0.3, 0.3, 0.3]) component("shell"); }
