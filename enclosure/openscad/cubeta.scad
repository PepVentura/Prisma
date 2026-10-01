// Prisma — CUBETA ACÚSTICA v0.1 (pieza 1 de la carcasa)
//
// Parte inferior de la carcasa (z 0–111 mm): bloque inferior de la cámara acústica, con el
// DMA105-4 delante y el DMA105-PR detrás, ambos montados POR DENTRO detrás de una rejilla de
// ranuras integrada en la pared (D030). Laterales y trasera con las mismas estrías de 4 mm
// que la capucha.
//
// Material: PLA (D027). Impresión: de pie, con el suelo en la cama, sin soportes
// (las ranuras de la rejilla son puentes de ≤ 30 mm).
// Montaje: altavoz y radiador se meten por arriba y se atornillan desde dentro con
// insertos M3 en la pared; junta de espuma de 2 mm entre marco y pared.
// Encima van la bandeja (2a) y la caja superior (2b), apoyadas en los rebordes interiores.

use <prisma_volumetrica_v0_3.scad>;
include <parametros.scad>;
$fn = 48;

pieza = "cubeta";   // "cubeta" | "pata" | "montaje"

// ---------------------------------------------------------------------------
// Parámetros
// ---------------------------------------------------------------------------
H = chamber_low_top;            // 111: unión con la capucha
cx = outer_w / 2;
cz = audio_center_z;            // centro de altavoz y radiador

// Estrías: misma rejilla que la capucha (surcos en z = 117 − 4k); se deja una franja lisa junto a la unión
groove_pitch = 4; groove_w = 1.6; groove_d = 0.8;
groove_top = 105; groove_bottom = 6;

// Rejilla delantera (altavoz) y trasera (radiador)
slot_h = 2.4;                   // ranura centrada en cada estría (60 % de hueco)
grille_d_drv = 86;              // algo menor que el recorte del altavoz (90)
grille_d_pr  = 94;              // algo menor que el recorte del radiador (98,4)
grille_ribs  = [-15, 15];       // nervios verticales de 3 mm: puentes de ≤ 30 mm
rib_w = 3;

// Anillos de montaje (por dentro): separan el marco de la rejilla lo justo para que el cono no la toque
// drv_clear y pr_clear están en parametros.scad
mount_zone = 112;               // cuadrado del anillo (marco de 104 mm + margen)
baffle_t = wall + pr_clear;     // fondo máximo que atraviesan las ranuras
insert_hole = 4.0; insert_depth = 5;   // insertos M3 de latón
gasket = 2;                     // junta de espuma entre marco y pared (no se modela)

// Rebordes interiores para la bandeja y la caja superior
ledge_w = 7; ledge_h = 6;

// Refuerzos verticales en los laterales
side_ribs_y = [45, 100]; side_rib_t = 4; side_rib_d = 6;

// Patas (TPU)
foot_d = 16; foot_pocket = 1.5; foot_h = 5; foot_inset = 18;

// ---------------------------------------------------------------------------
module lower(z1 = H) translate([-1, -1, -1]) cube([outer_w + 2, outer_d + 2, z1 + 1]);
module shell_lower() intersection() { difference() { body(0); body(wall); } lower(); }

function groove_zs() = [for (z = [groove_top - groove_pitch * floor((groove_top - groove_bottom) / groove_pitch) : groove_pitch : groove_top]) z];

module grooves() for (z = groove_zs()) {
    translate([-1, -1, z]) cube([groove_d + 1, outer_d + 2, groove_w]);
    translate([outer_w - groove_d, -1, z]) cube([groove_d + 1, outer_d + 2, groove_w]);
    translate([-1, outer_d - groove_d, z]) cube([outer_w + 2, groove_d + 1, groove_w]);
}

// Ranuras de la rejilla dentro de un círculo, en la pared delantera (y = 0) o trasera (y = outer_d)
module grille(d, back = false) {
    y0 = back ? outer_d - baffle_t - 1 : -1;
    difference() {
        intersection() {
            union() for (z = groove_zs()) translate([cx - d / 2, y0, z + groove_w / 2 - slot_h / 2]) cube([d, baffle_t + 2, slot_h]);
            translate([cx, y0, cz]) rotate([-90, 0, 0]) cylinder(d = d, h = baffle_t + 2);
        }
        for (dx = grille_ribs) translate([cx + dx - rib_w / 2, y0 - 1, cz - d / 2]) cube([rib_w, baffle_t + 4, d]);
    }
}

// Anillo: cuadrado con el recorte; el marco apoya en su cara interior
module mount_ring(back = false) {
    t = back ? pr_clear : drv_clear;
    cut = back ? pr_cut : drv_cut;
    y = back ? outer_d - wall - t : wall - 0.01;
    intersection() {
        difference() {
            translate([cx - mount_zone / 2, y, wall - 0.01]) cube([mount_zone, t + 0.01, H - wall]);
            translate([cx, y - 1, cz]) rotate([-90, 0, 0]) cylinder(d = cut, h = t + 2);
        }
        body(0);
    }
}
module inserts(back = false) for (dx = [-bolt_off, bolt_off], dz = [-bolt_off, bolt_off]) {
    // agujero ciego desde la cara del marco hacia la rejilla
    y = back ? outer_d - wall - pr_clear - 0.01 : wall + drv_clear - insert_depth;
    translate([cx + dx, y, cz + dz]) rotate([-90, 0, 0]) cylinder(d = insert_hole, h = insert_depth + 0.01);
}

// Rebordes: laterales completos; delante y detrás solo fuera de los marcos
module ledges() {
    module ledge(x, y, lx, ly) translate([x, y, H - ledge_h]) hull() {
        translate([0, 0, ledge_h - 0.01]) cube([lx, ly, 0.01]);
        // chaflán a 45° por debajo para imprimir sin soporte
        translate([lx == ledge_w && x < cx ? 0 : (lx == ledge_w ? lx - 0.01 : 0), ly == ledge_w && y < outer_d / 2 ? 0 : (ly == ledge_w ? ly - 0.01 : 0), 0])
            cube([lx == ledge_w ? 0.01 : lx, ly == ledge_w ? 0.01 : ly, 0.01]);
    }
    ledge(wall - 0.01, wall, ledge_w, outer_d - 2 * wall);                 // lateral izquierdo
    ledge(outer_w - wall - ledge_w + 0.01, wall, ledge_w, outer_d - 2 * wall); // lateral derecho
    for (x = [[wall, cx - drv_frame / 2 - 2], [cx + drv_frame / 2 + 2, outer_w - wall]])
        ledge(x[0], wall - 0.01, x[1] - x[0], ledge_w);                     // delante, fuera del altavoz
    for (x = [[wall, cx - pr_frame / 2 - 2], [cx + pr_frame / 2 + 2, outer_w - wall]])
        ledge(x[0], outer_d - wall - ledge_w + 0.01, x[1] - x[0], ledge_w);  // detrás, fuera del radiador
}
// Insertos M3 en los rebordes laterales para atornillar la bandeja y la caja superior
ledge_inserts_y = [20, 50, 95, 125];
module ledge_insert_holes() for (x = [wall + ledge_w / 2, outer_w - wall - ledge_w / 2], y = ledge_inserts_y)
    translate([x, y, H - insert_depth]) cylinder(d = insert_hole, h = insert_depth + 0.01);

module side_ribs() for (x = [wall - 0.01, outer_w - wall - side_rib_d + 0.01], y = side_ribs_y)
    translate([x, y - side_rib_t / 2, wall - 0.01]) cube([side_rib_d, side_rib_t, H - ledge_h - wall]);

module foot_pockets() for (x = [foot_inset, outer_w - foot_inset], y = [foot_inset, outer_d - foot_inset])
    translate([x, y, -0.01]) cylinder(d = foot_d + 0.4, h = foot_pocket + 0.01);

module cubeta() {
    difference() {
        union() {
            difference() { shell_lower(); grooves(); }
            mount_ring(false); mount_ring(true);
            ledges(); side_ribs();
        }
        grille(grille_d_drv, false); grille(grille_d_pr, true);
        inserts(false); inserts(true);
        ledge_insert_holes();
        foot_pockets();
    }
}

module pata() cylinder(d = foot_d, h = foot_h);   // TPU; se pega en el alojamiento de 1,5 mm

if (pieza == "cubeta") cubeta();
if (pieza == "pata") pata();
if (pieza == "montaje") { color([0.85, 0.85, 0.83]) cubeta(); component("speaker"); component("pr"); }
