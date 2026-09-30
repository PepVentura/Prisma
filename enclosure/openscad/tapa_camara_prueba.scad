// Prisma — tapa deslizante de la cámara, PIEZA DE PRUEBA v0.1 (D026)
//
// Un trozo de frontal de 3 mm (el mismo grosor de pared que la carcasa) con el agujero del
// objetivo y la guía en cola de milano, más la corredera. Sirve para ajustar holguras antes
// de incorporar la guía al frontal definitivo.
//
// Impresión: las dos piezas planas sobre la cama, cara vista hacia arriba, sin soportes.
// La corredera entra por el extremo abierto de la guía y queda retenida por la cola de milano.
// Dos pequeños resaltes marcan las posiciones «abierta» y «cerrada».

$fn = 48;

wall       = 3;      // grosor del frontal (como la carcasa)
lens_d     = 8;      // agujero del objetivo (Camera Module 3)
track_h    = 12;     // ancho de la guía (en la cara vista)
track_d    = 1.6;    // profundidad de la guía
dovetail   = 0.6;    // rebaje de la cola de milano a cada lado
slider_l   = 16;     // largo de la corredera
travel     = 14;     // recorrido: con 14 mm el objetivo queda totalmente libre
clear      = 0.25;   // holgura corredera-guía por lado
grip_h     = 1.0;    // resalte para empujar con el dedo
detent     = 0.3;    // altura de los resaltes de retención

plate_l = slider_l + travel + 14;
plate_h = 24;
lens_x  = 10;        // posición del objetivo sobre la placa de prueba

// Sección en cola de milano (más ancha abajo), extruida a lo largo de X
module dovetail_profile(w, d, u, len) {
    rotate([90, 0, 90]) linear_extrude(len)
        polygon([[-w / 2 - u, 0], [w / 2 + u, 0], [w / 2, d], [-w / 2, d]]);
}

module placa() {
    difference() {
        cube([plate_l, plate_h, wall]);
        // agujero del objetivo
        translate([lens_x, plate_h / 2, -1]) cylinder(d = lens_d, h = wall + 2);
        // guía abierta por el extremo derecho
        translate([lens_x - slider_l / 2 - 1, plate_h / 2, wall - track_d])
            dovetail_profile(track_h, track_d + 0.01, dovetail, plate_l);
    }
    // resaltes de retención en el fondo de la guía (cerrada y abierta)
    for (x = [lens_x - slider_l / 2 + 1.5, lens_x + travel - slider_l / 2 + 1.5])
        translate([x, plate_h / 2 - track_h / 2 + 1, wall - track_d - 0.02]) cube([0.8, track_h - 2, detent + 0.02]);
}

module corredera() {
    w = track_h - 2 * clear;
    d = track_d - clear;
    difference() {
        union() {
            dovetail_profile(w, d, dovetail, slider_l);
            // resalte para el dedo
            translate([slider_l / 2 - 2, -3, d - 0.05]) cube([4, 6, grip_h + 0.05]);
        }
        // muescas para los resaltes de retención
        for (x = [1.5, slider_l - 2.3])
            translate([x - 0.1, -w / 2 - 1, -0.01]) cube([1, w + 2, detent + 0.1]);
    }
}

placa();
// la corredera se imprime al lado; para verla montada: translate([lens_x - slider_l / 2, plate_h / 2, wall - track_d])
translate([0, plate_h + 8 + track_h / 2, 0]) corredera();
