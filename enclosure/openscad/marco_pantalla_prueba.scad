// Prisma — marco de pantalla, PIEZA DE PRUEBA v0.1
// Waveshare 7" HDMI LCD (C) Rev4.1, montada en horizontal.
//
// Sirve para comprobar el encaje real de la pantalla antes de imprimir la carcasa:
// ventana del área visible, alojamiento del cristal, apoyo del PCB y los 4 taladros.
// No lleva todavía la unión a la carcasa (eso irá en el frontal definitivo).
//
// Impresión: cara frontal sobre la cama (Z = 0 abajo), sin soportes.
// Montaje: el cristal entra en el alojamiento desde atrás; el PCB apoya en 4
// resaltes y se fija con 4 tornillos M2.5 × 6 autorroscantes (o insertos M2.5).
//
// Coordenadas: X = ancho de la pantalla, Y = alto (Y = 0 en el borde inferior de las
// pestañas, flex del LCD abajo), Z = grosor (Z = 0 cara frontal vista).

include <parametros.scad>;
$fn = 48;

// ---------------------------------------------------------------------------
// Parámetros del marco
// ---------------------------------------------------------------------------
fit        = 0.3;   // holgura por lado alrededor del cristal y del PCB
skin       = 2.0;   // grosor delante del cristal
frame_wall = 3.0;   // borde exterior alrededor del PCB
win_margin = 0.5;   // la ventana es el área visible + este margen por lado
win_chamfer = 1.5;  // chaflán de la ventana hacia delante (ángulo de visión)
pcb_relief = 1.5;   // rebaje detrás para que el PCB solo apoye en los resaltes
boss_d     = 6;     // resaltes de apoyo en los taladros
pilot_d    = 2.2;   // agujero para M2.5 autorroscante (3,5 para inserto M2.5)
pilot_depth = 6;

// Flex del LCD: sobresale por debajo del cristal, entre LCD y PCB
fpc_x0 = 50; fpc_x1 = 106; fpc_drop = 6;

T = skin + screen_t;   // grosor total: cara vista → cara delantera del PCB

// Posiciones derivadas (coordenadas de pantalla)
hole_x0 = (screen_w - screen_hole_dx) / 2;
holes = [for (dx = [0, screen_hole_dx], dz = [0, screen_hole_dz])
            [hole_x0 + dx, screen_hole_z0 + dz]];
glass = [0, glass_z0, screen_w, glass_h];                       // x, y, ancho, alto
win   = [screen_active_x0 - win_margin, screen_active_z0 - win_margin,
         screen_active_w + 2 * win_margin, screen_active_h + 2 * win_margin];

module rect(r, z0, h, grow = 0) {
    translate([r[0] - grow, r[1] - grow, z0]) cube([r[2] + 2 * grow, r[3] + 2 * grow, h]);
}

module marco() {
    difference() {
        // placa
        translate([-fit - frame_wall, -fit - frame_wall, 0])
            cube([screen_w + 2 * (fit + frame_wall), screen_h + 2 * (fit + frame_wall), T]);

        // ventana con chaflán hacia la cara vista
        hull() {
            rect(win, skin - 0.01, 0.02);
            rect(win, -0.01, 0.02, win_chamfer);
        }
        rect(win, skin - 0.1, T);

        // alojamiento del cristal
        rect(glass, skin, T, fit);

        // rebaje del PCB (contorno completo con pestañas), excepto los resaltes
        difference() {
            translate([-fit, -fit, T - pcb_relief]) cube([screen_w + 2 * fit, screen_h + 2 * fit, T]);
            for (h = holes) translate([h[0], h[1], 0]) cylinder(d = boss_d, h = T);
        }

        // hueco para el flex del LCD bajo el cristal
        translate([fpc_x0, glass_z0 - fit - fpc_drop, skin + 1])
            cube([fpc_x1 - fpc_x0, fpc_drop + 1, T]);

        // agujeros de los tornillos
        for (h = holes) translate([h[0], h[1], T - pilot_depth]) cylinder(d = pilot_d, h = pilot_depth + 1);
    }
}

// Referencia visual de la pantalla (no se imprime)
module pantalla_ref() {
    color([0.1, 0.1, 0.1, 0.6]) rect(glass, skin, screen_t);
    color([0.1, 0.25, 0.5, 0.6]) translate([0, 0, T]) cube([screen_w, screen_h, screen_pcb_t]);
}

show_ref = false;
color([0.85, 0.85, 0.88]) marco();
if (show_ref) pantalla_ref();
