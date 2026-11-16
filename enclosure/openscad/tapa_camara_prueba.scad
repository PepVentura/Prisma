// Prisma — tapa deslizante de la cámara, PIEZA DE PRUEBA v0.2 (D026)
//
// Un trozo de frontal de 3 mm (el mismo grosor de pared que la carcasa) con el agujero del
// objetivo y la guía en cola de milano, más la corredera. Sirve para ajustar holguras antes
// de incorporar la guía al frontal definitivo.
//
// Impresión: las dos piezas planas sobre la cama, cara vista hacia arriba, sin soportes.
// La corredera entra por el extremo abierto de la guía y queda retenida por la cola de milano.
// v0.2: un único resalte en rampa (en vez de dos escalones) cae en una de las dos muescas de la
// corredera, separadas justo el recorrido: hace «clic» en abierta y en cerrada y en medio la corredera
// pasa por encima. Al final de la guía, un tope de un solo sentido deja meter la corredera pero no sacarla.

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
detent     = 0.35;   // altura del resalte de retención (rampa)
det_l      = 2;      // largo de la rampa
det_w      = 4;      // ancho del resalte (centrado en la guía)
notch_d    = 0.45;   // profundidad de las muescas en V de la corredera
notch_x    = [1.2, 1.2 + travel];   // muescas separadas exactamente el recorrido
stop_h     = 0.5;    // tope de fin de guía

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
    // resalte de retención: con la corredera cerrada cae en su muesca derecha y, abierta, en la izquierda
    translate([lens_x - slider_l / 2 + notch_x[1], plate_h / 2, wall - track_d - 0.01]) bump(det_l, det_w, detent);
    // tope de fin de guía: rampa por la derecha (se entra) y cara recta por la izquierda (no se sale)
    translate([lens_x - slider_l / 2 + slider_l + travel + 0.3, plate_h / 2, wall - track_d - 0.01]) stop(stop_h);
}
// Resalte en rampa simétrica (sección triangular en X), centrado en (0, 0)
module bump(l, w, h) translate([0, -w / 2, 0]) rotate([90, 0, 0]) mirror([0, 0, 1])
    linear_extrude(w) polygon([[-l / 2, 0], [l / 2, 0], [0, h + 0.01]]);
// Tope de un solo sentido: cara recta en x = 0, rampa hacia +x
module stop(h, l = 2.5, w = 4) translate([0, -w / 2, 0]) rotate([90, 0, 0]) mirror([0, 0, 1])
    linear_extrude(w) polygon([[0, 0], [l, 0], [0, h + 0.01]]);

module corredera() {
    w = track_h - 2 * clear;
    d = track_d - clear;
    difference() {
        union() {
            dovetail_profile(w, d, dovetail, slider_l);
            // resalte para el dedo
            translate([slider_l / 2 - 2, -3, d - 0.05]) cube([4, 6, grip_h + 0.05]);
        }
        // muescas en V para el resalte, separadas el recorrido
        for (x = notch_x) translate([x, w / 2 + dovetail + 1, -0.01]) rotate([90, 0, 0])
            linear_extrude(w + 2 * dovetail + 2) polygon([[-det_l / 2 - 0.3, 0], [det_l / 2 + 0.3, 0], [0, notch_d]]);
        // chaflanes en los extremos para que suba por la rampa y el tope
        for (x = [0, slider_l]) translate([x, 0, 0]) rotate([0, 45, 0]) cube([0.9, w + 4, 0.9], center = true);
    }
}

placa();
// la corredera se imprime al lado; para verla montada: translate([lens_x - slider_l / 2, plate_h / 2, wall - track_d])
translate([0, plate_h + 8 + track_h / 2, 0]) corredera();
