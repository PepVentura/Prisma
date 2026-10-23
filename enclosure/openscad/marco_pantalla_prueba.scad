// Prisma — marco de pantalla, PIEZA DE PRUEBA v0.6 (D043) → stl/marco_pantalla_prueba_v0_6.stl
// v0.6: taladros 1 mm más abajo que en la v0.5 (comprobado con la plantilla v0.5).
// v0.5: tras montar la plantilla v0.4, taladros 2,5 mm más arriba y 5 mm a la izquierda (vista de
// frente; a la derecha mirando la placa por detrás). El PCB queda casi alineado con el cristal.
// v0.4: taladros colocados con las medidas tomadas en la pantalla (22/10): el izquierdo a 8 mm del
// borde izquierdo del cristal y el inferior a 10 mm por debajo del cristal; el superior queda a
// ≈5 mm por encima y el derecho, en el borde derecho del cristal. El PCB va 4 mm a la derecha del
// cristal, así que el marco crece por ese lado.
// v0.3: la v0.2 tenía el desplazamiento de 2,5 mm en horizontal (174 × 130,9 mm); es vertical.
// v0.2: la v0.1 salía en espejo (la ventana quedaba desplazada: 4 mm de borde negro a la
// derecha y 3 mm de imagen tapados a la izquierda). Ahora X va de izquierda a derecha
// mirando la cara vista, como en la capucha. Taladros (y PCB) 2,5 mm más arriba.
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
// Coordenadas: X = ancho de la pantalla, de izquierda a derecha mirando de frente (conectores
// a la derecha), Y = alto (Y = 0 en el borde inferior de las pestañas, flex del LCD abajo),
// Z = grosor (Z = 0 cara frontal vista). Como la cara vista va hacia abajo, la pieza se
// genera en espejo para que de frente X crezca hacia la derecha.

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
fpc_x0 = 50; fpc_x1 = 115; fpc_drop = 6;   // cubre la posición de la v0.1 (que no rozaba) y su espejo

T = skin + screen_t;   // grosor total: cara vista → cara delantera del PCB

// Posiciones derivadas (coordenadas de pantalla)
holes = screen_holes;
// Contorno del PCB (con el desplazamiento medido) y de la placa del marco, que abarca cristal y PCB
pcb = [screen_pcb_dx, screen_pcb_dz, screen_w, screen_h];
px0 = min(0, screen_pcb_dx) - fit - frame_wall;
px1 = max(screen_w, screen_pcb_dx + screen_w) + fit + frame_wall;
pz0 = min(glass_z0, screen_pcb_dz) - fit - frame_wall;
pz1 = max(glass_z0 + glass_h, screen_pcb_dz + screen_h) + fit + frame_wall;
glass = [0, glass_z0, screen_w, glass_h];                       // x, y, ancho, alto
win   = [screen_active_x0 - win_margin, screen_active_z0 - win_margin,
         screen_active_w + 2 * win_margin, screen_active_h + 2 * win_margin];

module rect(r, z0, h, grow = 0) {
    translate([r[0] - grow, r[1] - grow, z0]) cube([r[2] + 2 * grow, r[3] + 2 * grow, h]);
}

module marco() {
    difference() {
        // placa
        translate([px0, pz0, 0]) cube([px1 - px0, pz1 - pz0, T]);

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
            translate([pcb[0] - fit, pcb[1] - fit, T - pcb_relief]) cube([pcb[2] + 2 * fit, pcb[3] + 2 * fit, T]);
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
    color([0.1, 0.25, 0.5, 0.6]) translate([screen_pcb_dx, screen_pcb_dz, T]) cube([screen_w, screen_h, screen_pcb_t]);
}

// Plantilla rápida para comprobar medidas (≈20–25 min y ≈15 g): placa de 2 mm con el contorno del marco,
// el hueco exacto del cristal y los 4 taladros pasantes. Se apoya por delante sobre la pantalla con el
// cristal metido en el hueco: si un tornillo M2.5 pasa por los 4 taladros hasta el PCB, la posición vale.
plantilla_t = 2.0;
module plantilla() {
    difference() {
        translate([px0, pz0, 0]) cube([px1 - px0, pz1 - pz0, plantilla_t]);
        rect(glass, -1, plantilla_t + 2, fit);                                   // cristal
        translate([fpc_x0, glass_z0 - fit - fpc_drop, -1]) cube([fpc_x1 - fpc_x0, fpc_drop + 1, plantilla_t + 2]);  // flex
        for (h = holes) translate([h[0], h[1], -1]) cylinder(d = 2.8, h = plantilla_t + 2);                    // M2.5 pasa
        // marca en la cara de atrás (la que toca la cama no): «FLEX» en el borde del flex
        translate([(px0 + px1) / 2, pz0 + 2.2, plantilla_t - 0.6]) mirror([1, 0, 0])
            linear_extrude(1) text("FLEX ↓", size = 3.2, halign = "center");
    }
}

pieza = "marco";        // "marco" (pieza de prueba completa) o "plantilla" (comprobación rápida)
show_ref = false;
// espejo: vista desde la cara frontal (z < 0), X crece hacia la derecha
mirror([1, 0, 0]) {
    color([0.85, 0.85, 0.88]) if (pieza == "plantilla") plantilla(); else marco();
    if (show_ref) pantalla_ref();
}
