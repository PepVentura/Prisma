// Prisma — CUBETA ACÚSTICA v0.2 (pieza 1 de la carcasa) — diseño del boceto original (D031)
//
// Parte inferior de la carcasa (z 0–108 mm): bloque inferior de la cámara acústica.
//  - Frontal inclinado 11° con la banda de lamas a todo lo ancho; detrás, el DMA105-4
//    montado por dentro sobre un anillo paralelo al frontal (las lamas solo atraviesan la
//    pared delante del cono; el resto de la banda es decorativo y no abre la cámara).
//  - Trasera con rejilla circular delante del DMA105-PR, también montado por dentro.
//  - Rebordes para la bandeja (2a) y la caja superior (2b), refuerzos y patas de TPU.
//
// Material: PLA negro mate. Impresión: de pie, suelo en la cama, sin soportes.

use <prisma_volumetrica_v0_5.scad>;
include <parametros.scad>;
$fn = 48;

pieza = "cubeta";   // "cubeta" | "pata" | "montaje"

H = chamber_low_top;             // 108
cx = outer_w / 2;
fa = front_angle;

// Lamas: ranura de 2,4 mm cada 4 mm a lo largo del frontal
slat_pitch = 4; slat_h = 2.4;
slat_blind = 1.8;                // profundidad de las lamas decorativas (pared de 3 mm)
grille_d_drv = 86;               // zona pasante delante del cono
grille_d_pr = 94; pr_ribs = [-15, 15]; rib_w = 3;

mount_zone = 112;                // anillos de montaje
insert_hole = 4.0; insert_depth = 5;

ledge_w = 7; ledge_h = 6;
side_ribs_y = [55, 105]; side_rib_t = 4; side_rib_d = 6;
foot_d = 16; foot_pocket = 1.5; foot_h = 5; foot_inset = 20;

module on_front_() rotate([-fa, 0, 0]) children();
module lower() translate([-1, -1, -1]) cube([outer_w + 2, outer_d + 2, H + 1]);
module shell_lower() intersection() { component("shell"); lower(); }

slat_s = [for (s = [grille_s0 : slat_pitch : grille_s1 - slat_h]) s];

// Banda de lamas: decorativa (ciega) en todo el ancho; pasante solo dentro del círculo del cono
module slats_blind() on_front_() for (s = slat_s)
    translate([grille_margin_x, -1, s]) cube([outer_w - 2 * grille_margin_x, slat_blind + 1, slat_h]);
module slats_through() on_front_() intersection() {
    union() for (s = slat_s) translate([cx - grille_d_drv / 2, -1, s]) cube([grille_d_drv, drv_n + 1, slat_h]);
    translate([cx, -1, drv_s]) rotate([-90, 0, 0]) cylinder(d = grille_d_drv, h = drv_n + 1);
}

// Anillo del altavoz: paralelo al frontal, de la cara interior (n = wall) al plano del marco (n = drv_n)
module drv_ring() intersection() {
    on_front_() difference() {
        translate([cx - mount_zone / 2, wall - 0.01, drv_s - mount_zone / 2]) cube([mount_zone, drv_n - wall + 0.01, mount_zone]);
        translate([cx, wall - 1, drv_s]) rotate([-90, 0, 0]) cylinder(d = drv_cut, h = drv_n);
    }
    component("body_inner");
    translate([-1, -1, wall - 0.5]) cube([outer_w + 2, outer_d + 2, H - wall + 0.5]);
}
module drv_inserts() on_front_() for (dx = [-bolt_off, bolt_off], ds = [-bolt_off, bolt_off])
    translate([cx + dx, drv_n - insert_depth, drv_s + ds]) rotate([-90, 0, 0]) cylinder(d = insert_hole, h = insert_depth + 0.01);

// Radiador: anillo en la trasera y rejilla circular con dos nervios
module pr_ring() intersection() {
    difference() {
        translate([cx - mount_zone / 2, pr_flange_y, wall - 0.01]) cube([mount_zone, outer_d - wall - pr_flange_y + 0.01, H - wall]);
        translate([cx, pr_flange_y - 1, audio_center_z]) rotate([-90, 0, 0]) cylinder(d = pr_cut, h = outer_d);
    }
    component("body_inner");
}
module pr_grille() difference() {
    intersection() {
        union() for (z = [audio_center_z - grille_d_pr / 2 : slat_pitch : audio_center_z + grille_d_pr / 2])
            translate([cx - grille_d_pr / 2, outer_d - wall - 1, z]) cube([grille_d_pr, wall + 2, slat_h]);
        translate([cx, outer_d - wall - 1, audio_center_z]) rotate([-90, 0, 0]) cylinder(d = grille_d_pr, h = wall + 2);
    }
    for (dx = pr_ribs) translate([cx + dx - rib_w / 2, outer_d - wall - 2, audio_center_z - grille_d_pr / 2]) cube([rib_w, wall + 4, grille_d_pr]);
}
module pr_inserts() for (dx = [-bolt_off, bolt_off], dz = [-bolt_off, bolt_off])
    translate([cx + dx, pr_flange_y - 0.01, audio_center_z + dz]) rotate([-90, 0, 0]) cylinder(d = insert_hole, h = insert_depth + 0.01);

// Rebordes: laterales completos (desde detrás del altavoz) y trasero fuera del radiador
module ledges() {
    module ledge_x(x0, y0, ly, side) translate([x0, y0, H - ledge_h]) hull() {
        translate([0, 0, ledge_h - 0.01]) cube([ledge_w, ly, 0.01]);
        translate([side < 0 ? 0 : ledge_w - 0.01, 0, 0]) cube([0.01, ly, 0.01]);
    }
    module ledge_y(x0, x1) translate([x0, outer_d - wall - ledge_w, H - ledge_h]) hull() {
        translate([0, 0, ledge_h - 0.01]) cube([x1 - x0, ledge_w, 0.01]);
        translate([0, ledge_w - 0.01, 0]) cube([x1 - x0, 0.01, 0.01]);
    }
    y0 = front_y(H) + wall + 2;
    intersection() {
        union() {
            ledge_x(wall - 0.01, y0, outer_d - wall - y0, -1);
            ledge_x(outer_w - wall - ledge_w + 0.01, y0, outer_d - wall - y0, 1);
            ledge_y(wall, cx - pr_frame / 2 - 2);
            ledge_y(cx + pr_frame / 2 + 2, outer_w - wall);
        }
        component("body_inner");
    }
}
ledge_inserts_y = [40, 70, 100, 130];
module ledge_insert_holes() for (x = [wall + ledge_w / 2, outer_w - wall - ledge_w / 2], y = ledge_inserts_y)
    translate([x, y, H - insert_depth]) cylinder(d = insert_hole, h = insert_depth + 0.01);

module side_ribs() intersection() {
    for (x = [wall - 0.01, outer_w - wall - side_rib_d + 0.01], y = side_ribs_y)
        translate([x, y - side_rib_t / 2, wall - 0.01]) cube([side_rib_d, side_rib_t, H - ledge_h - wall]);
    component("body_inner");
}

module foot_pockets() for (x = [foot_inset, outer_w - foot_inset], y = [foot_inset + 8, outer_d - foot_inset])
    translate([x, y, -0.01]) cylinder(d = foot_d + 0.4, h = foot_pocket + 0.01);

module cubeta() {
    difference() {
        union() { shell_lower(); drv_ring(); pr_ring(); ledges(); side_ribs(); }
        slats_blind();
        slats_through();
        drv_inserts();
        pr_grille();
        pr_inserts();
        ledge_insert_holes();
        foot_pockets();
    }
}

module pata() cylinder(d = foot_d, h = foot_h);

if (pieza == "cubeta") cubeta();
if (pieza == "pata") pata();
if (pieza == "montaje") { color([0.12, 0.12, 0.13]) cubeta(); component("speaker"); component("pr"); }
