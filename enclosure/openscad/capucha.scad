// Prisma — CAPUCHA v0.3 (pieza 3 de la carcasa) — diseño del boceto original (D031)
//
// Todo lo que queda por encima de la cubeta (z > 108 mm): frontal inclinado con la franja
// LED, la pantalla y la cámara; laterales lisos con aristas redondeadas; trasera con
// perforado de ventilación, conector DC y botón de encendido; techo con micrófonos,
// botones de volumen e interruptor de silencio.
//
// Franjas de luz (D033): ranura de 4 mm en los cantos del frontal + canal detrás para la tira
// WS2812B, con salida de cables a la bahía por arriba; el inserto "franja_sup" entra por abajo.
//
// Material: PLA negro mate (D027). Impresión: BOCA ABAJO, con el techo sobre la cama.
// Medidas: 205 × 150 × 154 mm (cabe en la Kobra X).
//
// Piezas en este archivo (variable `pieza`):
//   "capucha", "capucha_impresion" (ya girada), "difusor", "corredera",
//   "capuchon" (botón de 8 mm), "deslizador" (mando del silencio), "placa_botones",
//   "franja_sup" (inserto transparente de las franjas, imprimir 2), "montaje"

use <prisma_volumetrica_v0_5.scad>;
include <parametros.scad>;
$fn = 40;

pieza = "capucha";

// ---------------------------------------------------------------------------
// Parámetros
// ---------------------------------------------------------------------------
split_z = chamber_low_top;     // 108

// Perforado trasero (ventilación de la bahía)
perf_d = 3.5; perf_pitch = 5.5;
perf_zone = [22, outer_w - 22, bay_floor_z + 6, dc_z - 9];   // x0, x1, z0, z1

// Pantalla
win_margin = 0.5; win_chamfer = 1.5;
boss_d = 6; pilot_d = 2.2; pilot_depth = 6;          // M2.5 × 6 autorroscantes
// Cámara y tapa deslizante (D026)
cam_boss_d = 4.5; cam_pilot_d = 1.6;
track_h = 12; track_d = 1.6; dovetail = 0.6; slider_l = 16; travel = 14; clear = 0.25; grip_h = 1.0; detent = 0.3;
// Franja LED
led_slot_w = 142; led_slot_h = 3;
diff_flange = 3; diff_flange_t = 1.2;
// Micrófonos
mic_hole_d = 1.2; mic_cluster_r = 3; mic_rail_w = 3;
// Botones (D032)
cap_hole = btn_cap_d + 0.4; cap_flange = 11; cap_flange_t = 1.2; cap_proud = 0.5;
switch_h = 5;                                        // pulsador 6 × 6 × 5 mm
mute_slot = [mute_knob[0] + 0.4, mute_knob[1] + mute_travel + 0.4];
btn_plate = [18, mute_y - btn_y[0] + 18, 2];         // placa bajo el techo
btn_plate_z = outer_h - wall - switch_h - cap_flange_t - btn_plate[2] - 0.2;   // 0,2 mm de holgura: el pulsador no queda presionado
// Uniones (D029)
rear_screw_x = [40, outer_w - 40]; rear_screw_z = 150; rear_screw_d = 3.4; rear_csk_d = 6.5;
pin_z = split_z + wall_int;                          // cara superior de la bandeja

// ---------------------------------------------------------------------------
// Geometría derivada
// ---------------------------------------------------------------------------
fa = front_angle;
screen_x0 = (outer_w - screen_w) / 2;
cam_s0 = glass_z0 + glass_h + cam_gap;
cam_x = outer_w / 2 - screen_x0;
cam_lz = cam_s0 + cam_lens_from_bottom;
hole_x0 = (screen_w - screen_hole_dx) / 2;
screen_holes = [for (dx = [0, screen_hole_dx], dz = [0, screen_hole_dz]) [hole_x0 + dx, screen_hole_z0 + dz]];
cam_holes = [for (dx = [-cam_hole_dx / 2, cam_hole_dx / 2], dz = [0, -cam_hole_dz]) [cam_x + dx, cam_lz + dz]];
mic_cx = [outer_w / 2 - mic_spacing / 2, outer_w / 2 + mic_spacing / 2];
mic_cy = mic_y + mic_d / 2;
pin_y = pin_z * tan(fa) + pin_n;

module on_front_() rotate([-fa, 0, 0]) children();
// marco local de la pantalla (cara interior del frontal, borde inferior de las pestañas)
module on_screen() on_front_() translate([screen_x0, wall, screen_s0]) children();

// ---------------------------------------------------------------------------
module upper() translate([-1, -1, split_z]) cube([outer_w + 2, outer_d + 2, outer_h]);
module shell_upper() intersection() { component("shell"); upper(); }

module rear_perforation() {
    for (row = [0 : floor((perf_zone[3] - perf_zone[2]) / perf_pitch)])
        for (x = [perf_zone[0] + (row % 2) * perf_pitch / 2 : perf_pitch : perf_zone[1]])
            translate([x, outer_d - wall - 1, perf_zone[2] + row * perf_pitch]) rotate([-90, 0, 0]) cylinder(d = perf_d, h = wall + 2, $fn = 16);
}

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

// Guía de la tapa de la cámara (cara exterior), con zona de entrada a la derecha
guide_x0 = cam_x - slider_l / 2 - 1;
guide_len = slider_l + travel + 2;
module guide() {
    translate([guide_x0, 0, cam_lz]) rotate([90, 0, 90]) linear_extrude(guide_len)
        polygon([[-wall - 0.01, -track_h / 2], [-wall - 0.01, track_h / 2],
                 [-wall + track_d, track_h / 2 + dovetail], [-wall + track_d, -track_h / 2 - dovetail]]);
    translate([guide_x0 + guide_len - 0.01, -wall - 0.01, cam_lz - track_h / 2 - dovetail])
        cube([slider_l + 1, track_d + 0.01, track_h + 2 * dovetail]);
}
module guide_detents() {
    for (p = [[cam_x - slider_l / 2 + 1.5, detent], [cam_x + travel - slider_l / 2 + 1.5, detent],
              [guide_x0 + guide_len - 0.8, detent + 0.2]])
        translate([p[0], -wall + track_d - p[1], cam_lz - track_h / 2 + 1]) cube([0.8, p[1] + 0.3, track_h - 2]);
}

module led_slot() on_front_() translate([(outer_w - led_slot_w) / 2, -1, led_s]) cube([led_slot_w, wall + 2, led_slot_h]);

module mic_holes() for (cx = mic_cx) {
    translate([cx, mic_cy, outer_h - wall - 1]) cylinder(d = mic_hole_d, h = wall + 2, $fn = 12);
    for (a = [0 : 60 : 300]) translate([cx + mic_cluster_r * cos(a), mic_cy + mic_cluster_r * sin(a), outer_h - wall - 1])
        cylinder(d = mic_hole_d, h = wall + 2, $fn = 12);
}
module mic_rails() {
    z0 = outer_h - wall - mic_rail_gap - 1.5;
    for (s = [-1, 1]) {
        y = s < 0 ? mic_y - mic_rail_w : mic_y + mic_d;
        lip_y = s < 0 ? mic_y - mic_rail_w : mic_y + mic_d - 2;
        translate([(outer_w - mic_w) / 2 - 2, y, z0]) cube([mic_w + 2, mic_rail_w, mic_rail_gap + 1.5 + 0.01]);
        translate([(outer_w - mic_w) / 2 - 2, lip_y, z0]) cube([mic_w + 2, mic_rail_w + 2, 1.5]);
    }
    translate([(outer_w + mic_w) / 2 + 0.5, mic_y - mic_rail_w, z0]) cube([2, mic_d + 2 * mic_rail_w, mic_rail_gap + 1.5 + 0.01]);
}

// Botones del techo: agujeros de los capuchones, ranura del deslizador y 2 resaltes para la placa
module top_button_holes() {
    for (y = btn_y) translate([btn_x, y, outer_h - wall - 1]) cylinder(d = cap_hole, h = wall + 2);
    translate([btn_x - mute_slot[0] / 2, mute_y - mute_slot[1] / 2, outer_h - wall - 1]) cube([mute_slot[0], mute_slot[1], wall + 2]);
    // punto para pintar (o rellenar con filamento rojo): visible con el micro silenciado
    translate([btn_x - 5.5, mute_y + mute_slot[1] / 2 - 1.5, outer_h - 0.6]) cylinder(d = 2, h = 1);
}
btn_plate_holes = [[btn_x, btn_y[0] - 7], [btn_x, mute_y + 7]];
module top_button_bosses() for (p = btn_plate_holes) translate([p[0], p[1], btn_plate_z + btn_plate[2]])
    difference() { cylinder(d = 6, h = outer_h - wall - btn_plate_z - btn_plate[2] + 0.01); translate([0, 0, -0.01]) cylinder(d = 2.2, h = 6); }

// Botón de encendido trasero: agujero del capuchón y 2 resaltes para un pulsador en placa
module power_hole() translate([power_btn_x, outer_d - wall - 1, power_btn_z]) rotate([-90, 0, 0]) cylinder(d = cap_hole, h = wall + 2);
module power_bosses() for (dx = [-8, 8]) translate([power_btn_x + dx, outer_d - wall + 0.01, power_btn_z])
    rotate([90, 0, 0]) difference() { cylinder(d = 5, h = switch_h + cap_flange_t); translate([0, 0, 1]) cylinder(d = 2.2, h = 10); }

module rear_screws() for (x = rear_screw_x) {
    translate([x, outer_d - wall - 1, rear_screw_z]) rotate([-90, 0, 0]) cylinder(d = rear_screw_d, h = wall + 2);
    translate([x, outer_d - 1.8, rear_screw_z]) rotate([-90, 0, 0]) cylinder(d1 = rear_screw_d, d2 = rear_csk_d, h = 1.81);
}
module front_pin_blocks() for (x = [wall, outer_w - wall - pin_block]) {
    translate([x, pin_y - pin_block / 2, pin_z]) cube([pin_block, pin_block, 12]);
    translate([x + pin_block / 2, pin_y, pin_z - pin_len]) cylinder(d = pin_d, h = pin_len + 0.01);
}

// ---------------------------------------------------------------------------
module capucha() {
    difference() {
        union() {
            shell_upper();
            on_screen() {
                for (h = screen_holes) screen_boss(h[0], h[1], boss_d, screen_t, pilot_d, pilot_depth);
                for (h = cam_holes) screen_boss(h[0], h[1], cam_boss_d, cam_standoff, cam_pilot_d, 5);
            }
            intersection() { union() { mic_rails(); front_pin_blocks(); top_button_bosses(); power_bosses(); } component("body_inner"); }
            // canal de la franja: empieza sobre la bandeja, que lo cierra entre z 108 y 113
            intersection() { component("edge_channel"); translate([-1, -1, pin_z]) cube([outer_w + 2, outer_d + 2, outer_h]); }
            for (x = [wall, outer_w - wall - pin_block])
                translate([x + pin_block / 2, pin_y, pin_z - pin_len]) cylinder(d = pin_d, h = pin_len + 0.01);
        }
        rear_perforation();
        screen_window();
        on_screen() { translate([cam_x, 1, cam_lz]) rotate([90, 0, 0]) cylinder(d = cam_lens_d, h = wall + 2); guide(); }
        led_slot();
        component("edge_void");
        component("edge_slot");
        component("edge_exit");
        mic_holes();
        top_button_holes();
        power_hole();
        rear_screws();
        translate([dc_x, outer_d - wall - 1, dc_z]) rotate([-90, 0, 0]) cylinder(d = dc_d, h = wall + 2);
    }
    on_screen() guide_detents();
}

// ---------------------------------------------------------------------------
// Piezas pequeñas
// ---------------------------------------------------------------------------
module difusor() {   // transparente (D033): rellena la ranura; la pestaña se pega por dentro
    cube([led_slot_w - 0.3, led_slot_h - 0.3, wall]);
    translate([-diff_flange, -diff_flange, wall]) cube([led_slot_w - 0.3 + 2 * diff_flange, led_slot_h - 0.3 + 2 * diff_flange, diff_flange_t]);
}
module corredera() {
    w = track_h - 2 * clear; d = track_d - clear;
    difference() {
        union() {
            rotate([90, 0, 90]) linear_extrude(slider_l) polygon([[-w / 2 - dovetail, 0], [w / 2 + dovetail, 0], [w / 2, d], [-w / 2, d]]);
            translate([slider_l / 2 - 2, -3, d - 0.05]) cube([4, 6, grip_h + 0.05]);
        }
        for (x = [1.5, slider_l - 2.3]) translate([x - 0.1, -w / 2 - 2, -0.01]) cube([1, w + 4, detent + 0.1]);
    }
}
// Capuchón de 8 mm: asoma 0,5 mm; pestaña interior que lo retiene; símbolo grabado (0 = −, 1 = +, 2 = liso)
module capuchon(symbol = 0) {
    h = wall + cap_proud;
    difference() {
        union() { cylinder(d = btn_cap_d, h = h); cylinder(d = cap_flange, h = cap_flange_t); }
        translate([0, 0, h - 0.5]) {
            if (symbol <= 1) translate([-2.5, -0.5, 0]) cube([5, 1, 1]);
            if (symbol == 1) translate([-0.5, -2.5, 0]) cube([1, 5, 1]);
        }
    }
}
// Mando del interruptor deslizante: encaja en la palanca de un SS12D00 (agujero 1,6 × 1,6)
module deslizador() difference() {
    union() { translate([-mute_knob[0] / 2, -mute_knob[1] / 2, 0]) cube([mute_knob[0], mute_knob[1], wall + cap_proud]);
              translate([-4, -mute_knob[1] / 2 - 1.5, 0]) cube([8, mute_knob[1] + 3, 1]); }
    translate([-0.85, -0.85, -0.01]) cube([1.7, 1.7, 2.5]);
}
// Placa de botones (va bajo el techo con 2 tornillos M2): 2 pulsadores de 6 × 6 y el SS12D00
module placa_botones() difference() {
    translate([-btn_plate[0] / 2, -7 - 9 + 7, 0]) translate([0, btn_y[0] - btn_y[0], 0]) cube([btn_plate[0], btn_plate[1], btn_plate[2]]);
    for (p = btn_plate_holes) translate([p[0] - btn_x, p[1] - btn_y[0], -1]) cylinder(d = 2.4, h = 5);
    for (y = btn_y) translate([-3.1, y - btn_y[0] - 3.1, 1]) cube([6.2, 6.2, 2]);                 // alojamiento pulsadores
    translate([-1.9, mute_y - btn_y[0] - 4.4, 0.6]) cube([3.8, 8.8, 2]);                            // alojamiento SS12D00
    for (y = btn_y) translate([-4, y - btn_y[0] - 1, -1]) cube([1, 2, 5]);                          // pasos de cables
}

if (pieza == "capucha") capucha();
if (pieza == "capucha_impresion") translate([0, 0, outer_h]) rotate([180, 0, 0]) capucha();
if (pieza == "difusor") difusor();
if (pieza == "corredera") corredera();
if (pieza == "capuchon") { capuchon(0); translate([14, 0, 0]) capuchon(1); translate([28, 0, 0]) capuchon(2); }
if (pieza == "deslizador") deslizador();
if (pieza == "placa_botones") placa_botones();
// Inserto transparente superior (imprimir 2), tumbado con la cara vista sobre la cama
if (pieza == "franja_sup") for (i = [0, 1]) translate([edge_strip_s0 - split_z / cos(fa), i * 10, 0])
    multmatrix([[0, 0, 1, -edge_strip_s0], [1, 0, 0, -edge_strip_xc], [0, 1, 0, 0]]) rotate([fa, 0, 0])
        intersection() { component("edge_inserts"); translate([-1, -50, split_z]) cube([outer_w / 2, outer_d + 100, outer_h]); }
if (pieza == "montaje") {
    color([0.12, 0.12, 0.13]) capucha();
    component("screen"); component("camera"); component("mics"); component("led_bar");
    color([0.85, 0.95, 1, 0.6]) intersection() { component("edge_inserts"); upper(); }
}
