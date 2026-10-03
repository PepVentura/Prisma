// Prisma — CAPUCHA v0.1 (pieza 3 de la carcasa)
//
// Todo lo que queda por encima de la cubeta acústica (z > 111 mm): frontal inclinado con
// la pantalla y la cámara, franja de LEDs, laterales y trasera con estrías de 4 mm,
// rejillas de ventilación integradas en las estrías, techo con los micrófonos,
// conector DC y uniones con la cubeta.
//
// Material: PLA (D027). Impresión: BOCA ABAJO, con el techo sobre la cama.
// Medidas de la pieza: 205 × 145 × 155 mm (cabe en la Kobra X, 260 × 260 × 260).
// Soportes: solo los que pida el laminador en las ventanas; los resaltes interiores
// llevan cartabones a 45° para imprimirse sin soporte.
//
// Piezas sueltas en este mismo archivo (variable `pieza`):
//   "capucha"   la carcasa
//   "difusor"   difusor de la barra LED (filamento translúcido)
//   "corredera" tapa deslizante de la cámara (igual que en tapa_camara_prueba.scad)
//   "montaje"   capucha + componentes, solo para ver

use <prisma_volumetrica_v0_3.scad>;
include <parametros.scad>;
$fn = 40;

pieza = "capucha";

// ---------------------------------------------------------------------------
// Parámetros de la capucha
// ---------------------------------------------------------------------------
split_z   = chamber_low_top;   // 111: unión con la cubeta acústica

// Estrías (D028)
groove_pitch = 4; groove_w = 1.6; groove_d = 0.8;
groove_margin = 6;             // sin estrías en los 6 mm junto al borde inferior y al techo

// Rejillas: las estrías de estas zonas atraviesan la pared, en tramos de 28 mm con nervios de 4 mm
vent_seg = 28; vent_rib = 4;
vent_rear = [20, 150, bay_floor_z + 8, bay_floor_z + 53];   // x0, x1, z0, z1 (trasera)
vent_side = [80, 135, bay_floor_z + 8, bay_floor_z + 48];   // y0, y1, z0, z1 (laterales)

// Pantalla
win_margin  = 0.5;             // ventana = área visible + margen
win_chamfer = 1.5;
boss_d = 6; pilot_d = 2.2; pilot_depth = 6;   // tornillos M2.5 × 6 autorroscantes

// Cámara
cam_boss_d = 4.5; cam_pilot_d = 1.6;          // tornillos M2 autorroscantes
track_h = 12; track_d = 1.6; dovetail = 0.6; slider_l = 16; travel = 14; clear = 0.25; grip_h = 1.0; detent = 0.3;

// Barra LED: ranura en el frontal vertical y difusor con pestaña interior
led_slot_w = 142; led_slot_h = 5;
diff_flange = 3; diff_flange_t = 1.2;

// Micrófonos: dos grupos de 7 agujeros de 1,2 mm (toleran ±3 mm de error de posición)
mic_hole_d = 1.2; mic_cluster_r = 3;
mic_rail_w = 3;                               // raíles donde se desliza la placa del ReSpeaker Lite (hueco: mic_rail_gap)

// Uniones con la cubeta (D029)
rear_screw_x = [40, outer_w - 40]; rear_screw_z = 150; rear_screw_d = 3.4; rear_csk_d = 6.5;
pin_z = split_z + wall_int;                   // cara superior de la bandeja

// Ventilador opcional de 40 mm tras la rejilla trasera
fan_center = [60, bay_floor_z + 30]; fan_holes = 32; fan_boss_d = 6; fan_boss_l = 4; fan_pilot = 2.5;

// ---------------------------------------------------------------------------
// Geometría derivada (mismas fórmulas que el volumétrico)
// ---------------------------------------------------------------------------
screen_x0 = (outer_w - screen_w) / 2;
screen_z0 = front_split_z + screen_margin * cos(screen_angle);
screen_y0 = front_y(screen_z0) + wall / cos(screen_angle);
cam_s0    = glass_z0 + glass_h + cam_gap;
cam_x     = outer_w / 2 - screen_x0;              // centro de la cámara (coordenadas de pantalla)
cam_lz    = cam_s0 + cam_lens_from_bottom;        // centro del objetivo
hole_x0   = (screen_w - screen_hole_dx) / 2;
screen_holes = [for (dx = [0, screen_hole_dx], dz = [0, screen_hole_dz]) [hole_x0 + dx, screen_hole_z0 + dz]];
cam_holes = [for (dx = [-cam_hole_dx / 2, cam_hole_dx / 2], dz = [0, -cam_hole_dz]) [cam_x + dx, cam_lz + dz]];
mic_cx = [outer_w / 2 - mic_spacing / 2, outer_w / 2 + mic_spacing / 2];
mic_cy = mic_y + mic_d / 2;

module on_screen() {
    translate([screen_x0, screen_y0, screen_z0]) rotate([-screen_angle, 0, 0]) children();
}

// ---------------------------------------------------------------------------
// Carcasa base
// ---------------------------------------------------------------------------
module upper(z0 = split_z) translate([-1, -1, z0]) cube([outer_w + 2, outer_d + 2, outer_h]);

module shell_upper() intersection() { difference() { body(0); body(wall); } upper(); }

// Surcos horizontales en laterales y trasera; en las zonas de rejilla atraviesan la pared
module grooves() {
    for (z = [split_z + groove_margin : groove_pitch : outer_h - groove_margin - groove_w]) {
        translate([-1, -1, z]) cube([groove_d + 1, outer_d + 2, groove_w]);
        translate([outer_w - groove_d, -1, z]) cube([groove_d + 1, outer_d + 2, groove_w]);
        translate([-1, outer_d - groove_d, z]) cube([outer_w + 2, groove_d + 1, groove_w]);
    }
}
function in_band(z, r) = z >= r[2] && z + groove_w <= r[3];
module vents() {
    for (z = [split_z + groove_margin : groove_pitch : outer_h - groove_margin - groove_w]) {
        if (in_band(z, vent_rear))
            for (x = [vent_rear[0] : vent_seg + vent_rib : vent_rear[1] - vent_seg])
                translate([x, outer_d - wall - 1, z]) cube([vent_seg, wall + 2, groove_w]);
        if (in_band(z, vent_side))
            for (y = [vent_side[0] : vent_seg + vent_rib : vent_side[1] - vent_seg + 0.01])
                for (x = [-1, outer_w - wall - 1]) translate([x, y, z]) cube([wall + 2, vent_seg, groove_w]);
    }
}

// Resalte perpendicular al frontal con cartabón a 45° hacia el techo (imprimible boca abajo)
module screen_boss(x, z, d, len, pilot, pdepth) {
    difference() {
        hull() {
            translate([x, -0.5, z]) rotate([-90, 0, 0]) cylinder(d = d, h = len + 0.5);
            translate([x - d / 2, -0.5, z + len]) cube([d, 0.5, 0.01]);
        }
        translate([x, len - pdepth, z]) rotate([-90, 0, 0]) cylinder(d = pilot, h = pdepth + 0.1);
    }
}

module screen_window() {
    on_screen() hull() {
        translate([screen_active_x0 - win_margin, -0.01, screen_active_z0 - win_margin])
            cube([screen_active_w + 2 * win_margin, 0.02, screen_active_h + 2 * win_margin]);
        translate([screen_active_x0 - win_margin - win_chamfer, -wall - 0.5, screen_active_z0 - win_margin - win_chamfer])
            cube([screen_active_w + 2 * (win_margin + win_chamfer), 0.02, screen_active_h + 2 * (win_margin + win_chamfer)]);
    }
    on_screen() translate([screen_active_x0 - win_margin, -0.5, screen_active_z0 - win_margin])
        cube([screen_active_w + 2 * win_margin, 1, screen_active_h + 2 * win_margin]);
}

// Guía en cola de milano de la tapa de la cámara (D026), rebajada en la cara exterior.
// Coordenadas locales de pantalla: X a lo largo, Y hacia dentro (−wall = cara exterior), Z por el plano.
// Tramo en cola de milano (posiciones cerrada y abierta) + zona de entrada recta a la derecha,
// por donde la corredera se mete de frente y luego se desliza hacia la izquierda.
guide_x0 = cam_x - slider_l / 2 - 1;
guide_len = slider_l + travel + 2;
module guide() {
    // sección (y, z) extruida a lo largo de X
    translate([guide_x0, 0, cam_lz]) rotate([90, 0, 90]) linear_extrude(guide_len)
        polygon([[-wall - 0.01, -track_h / 2], [-wall - 0.01, track_h / 2],
                 [-wall + track_d, track_h / 2 + dovetail], [-wall + track_d, -track_h / 2 - dovetail]]);
    // zona de entrada: paredes rectas con el ancho del fondo
    translate([guide_x0 + guide_len - 0.01, -wall - 0.01, cam_lz - track_h / 2 - dovetail])
        cube([slider_l + 1, track_d + 0.01, track_h + 2 * dovetail]);
}
module guide_detents() {
    // retenes en las posiciones cerrada y abierta, y uno más alto antes de la entrada
    for (p = [[cam_x - slider_l / 2 + 1.5, detent], [cam_x + travel - slider_l / 2 + 1.5, detent],
              [guide_x0 + guide_len - 0.8, detent + 0.2]])
        translate([p[0], -wall + track_d - p[1], cam_lz - track_h / 2 + 1]) cube([0.8, p[1] + 0.3, track_h - 2]);
}

// Barra LED: ranura pasante
module led_slot() translate([(outer_w - led_slot_w) / 2, -1, led_bar_z]) cube([led_slot_w, wall + 2, led_slot_h]);

// Micrófonos: agujeros en el techo y raíles para la placa
module mic_holes() {
    for (cx = mic_cx) {
        translate([cx, mic_cy, outer_h - wall - 1]) cylinder(d = mic_hole_d, h = wall + 2, $fn = 12);
        for (a = [0 : 60 : 300]) translate([cx + mic_cluster_r * cos(a), mic_cy + mic_cluster_r * sin(a), outer_h - wall - 1])
            cylinder(d = mic_hole_d, h = wall + 2, $fn = 12);
    }
}
module mic_rails() {
    // dos raíles en L a lo largo de X; la placa entra por un lateral hasta el tope
    for (s = [-1, 1]) {
        y = s < 0 ? mic_y - mic_rail_w : mic_y + mic_d;
        lip_y = s < 0 ? mic_y - mic_rail_w : mic_y + mic_d - 2;
        translate([(outer_w - mic_w) / 2 - 2, y, outer_h - wall - mic_rail_gap - 1.5]) cube([mic_w + 2, mic_rail_w, mic_rail_gap + 1.5 + 0.01]);
        translate([(outer_w - mic_w) / 2 - 2, lip_y, outer_h - wall - mic_rail_gap - 1.5]) cube([mic_w + 2, mic_rail_w + 2, 1.5]);
    }
    // tope
    translate([(outer_w + mic_w) / 2 + 0.5, mic_y - mic_rail_w, outer_h - wall - mic_rail_gap - 1.5]) cube([2, mic_d + 2 * mic_rail_w, mic_rail_gap + 1.5 + 0.01]);
}

// Uniones
module rear_screws() for (x = rear_screw_x) {
    translate([x, outer_d - wall - 1, rear_screw_z]) rotate([-90, 0, 0]) cylinder(d = rear_screw_d, h = wall + 2);
    translate([x, outer_d - 1.8, rear_screw_z]) rotate([-90, 0, 0]) cylinder(d1 = rear_screw_d, d2 = rear_csk_d, h = 1.81);
}
module front_pin_blocks() for (x = [wall, outer_w - wall - pin_block]) {
    translate([x, wall, pin_z]) cube([pin_block, pin_block, 12]);
    translate([x + pin_block / 2, wall + pin_block / 2, pin_z - pin_len]) cylinder(d = pin_d, h = pin_len + 0.01);
}

// Ventilador opcional
module fan_bosses() for (dx = [-1, 1], dz = [-1, 1]) {
    p = [fan_center[0] + dx * fan_holes / 2, fan_center[1] + dz * fan_holes / 2];
    difference() {
        hull() {
            translate([p[0], outer_d - wall + 0.01, p[1]]) rotate([90, 0, 0]) cylinder(d = fan_boss_d, h = fan_boss_l);
            translate([p[0] - fan_boss_d / 2, outer_d - wall - 0.01, p[1] + fan_boss_l]) cube([fan_boss_d, 0.02, 0.01]);
        }
        translate([p[0], outer_d - wall + 0.02, p[1]]) rotate([90, 0, 0]) cylinder(d = fan_pilot, h = fan_boss_l + 0.1);
    }
}

// ---------------------------------------------------------------------------
// Pieza completa
// ---------------------------------------------------------------------------
module capucha() {
    difference() {
        union() {
            difference() { shell_upper(); grooves(); }
            // resaltes de la pantalla y de la cámara (dentro del frontal)
            on_screen() {
                for (h = screen_holes) screen_boss(h[0], h[1], boss_d, screen_t, pilot_d, pilot_depth);
                for (h = cam_holes) screen_boss(h[0], h[1], cam_boss_d, cam_standoff, cam_pilot_d, 5);
            }
            intersection() { union() { mic_rails(); front_pin_blocks(); fan_bosses(); } body(0); }
            // los pasadores sobresalen por debajo del borde
            for (x = [wall, outer_w - wall - pin_block])
                translate([x + pin_block / 2, wall + pin_block / 2, pin_z - pin_len]) cylinder(d = pin_d, h = pin_len + 0.01);
        }
        vents();
        screen_window();
        on_screen() {
            translate([cam_x, 1, cam_lz]) rotate([90, 0, 0]) cylinder(d = cam_lens_d, h = wall + 2);
            guide();
        }
        led_slot();
        mic_holes();
        rear_screws();
        translate([dc_x, outer_d - wall - 1, dc_z]) rotate([-90, 0, 0]) cylinder(d = dc_d, h = wall + 2);
    }
    // retenes de la tapa, en el fondo de la guía
    on_screen() guide_detents();
}

module difusor() {
    // translúcido: la parte delantera rellena la ranura; la pestaña se pega por dentro
    cube([led_slot_w - 0.3, led_slot_h - 0.3, wall]);
    translate([-diff_flange, -diff_flange, wall]) cube([led_slot_w - 0.3 + 2 * diff_flange, led_slot_h - 0.3 + 2 * diff_flange, diff_flange_t]);
}

module corredera() {
    w = track_h - 2 * clear; d = track_d - clear;
    difference() {
        union() {
            rotate([90, 0, 90]) linear_extrude(slider_l)
                polygon([[-w / 2 - dovetail, 0], [w / 2 + dovetail, 0], [w / 2, d], [-w / 2, d]]);
            translate([slider_l / 2 - 2, -3, d - 0.05]) cube([4, 6, grip_h + 0.05]);
        }
        for (x = [1.5, slider_l - 2.3]) translate([x - 0.1, -w / 2 - 2, -0.01]) cube([1, w + 4, detent + 0.1]);
    }
}

if (pieza == "capucha") capucha();
if (pieza == "capucha_impresion") translate([0, 0, outer_h]) rotate([180, 0, 0]) capucha();
if (pieza == "difusor") difusor();
if (pieza == "corredera") corredera();
if (pieza == "montaje") {
    color([0.85, 0.85, 0.83]) capucha();
    component("screen"); component("camera"); component("mics"); component("led_bar");
}
