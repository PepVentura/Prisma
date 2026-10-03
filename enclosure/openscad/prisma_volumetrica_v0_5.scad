// Prisma — volumétrico v0.5 (D031: vuelta al boceto original; D033: franjas de luz)
// Maqueta de distribución: envolvente, cámara acústica y componentes.
//
//  - Frontal inclinado 11° de arriba abajo, aristas redondeadas (r = 9 mm).
//  - Altavoz en el frontal inclinado, detrás de una banda de lamas a todo lo ancho.
//  - Cámara acústica: bloque inferior completo + bloque superior-trasero detrás de un
//    tabique paralelo al frontal (la pantalla queda delante del tabique).
//  - Electrónica en la bahía superior; pantalla, LED y cámara en el frontal.
//
// Uso: openscad -D 'part="chamber_air"' -o aire.stl prisma_volumetrica_v0_5.scad

include <parametros.scad>;
$fn = 48;

part = "all";

// ---------------------------------------------------------------------------
// Geometría base
// ---------------------------------------------------------------------------
fa = front_angle;
function front_y(z) = z * tan(fa);                       // cara exterior del frontal
function sn2y(s, n) = s * sin(fa) + n * cos(fa);
function sn2z(s, n) = s * cos(fa) - n * sin(fa);

// Marco local del frontal: x igual, y local = n (hacia dentro), z local = s (a lo largo)
module on_front() rotate([-fa, 0, 0]) children();

// Envolvente redondeada con retranqueo i (0 = exterior, wall = interior)
module body(i = 0) {
    // esferas circunscritas (corrige el facetado para que las caras planas queden en su sitio)
    r = corner_r; rr = max(r - i, 0.3) / cos(180 / 32);
    hull() for (x = [r, outer_w - r], z = [r, outer_h - r]) {
        translate([x, z * tan(fa) + r / cos(fa), z]) sphere(rr, $fn = 32);
        translate([x, outer_d - r, z]) sphere(rr, $fn = 32);
    }
}
module shell() { difference() { body(0); body(wall); } }

// Semiespacio por detrás de un plano paralelo al frontal a profundidad n
module behind(n) on_front() translate([-50, n, -100]) cube([outer_w + 100, 400, 600]);

module cut() {
    if (section_x) intersection() { children(); translate([outer_w / 2, -10, -10]) cube([outer_w, outer_d + 20, outer_h + 20]); }
    else children();
}

pin_y_ = front_y(chamber_low_top + wall_int) + pin_n;   // pasadores capucha ↔ bandeja (D029)

// ---------------------------------------------------------------------------
// Franjas de luz de los cantos (D033). Marco local del frontal: x, n, s.
// Cada franja: ranura en la pared + inserto transparente + canal cerrado detrás con la tira de LEDs.
// ---------------------------------------------------------------------------
module both_edges() { children(); translate([outer_w, 0, 0]) mirror([1, 0, 0]) children(); }
// (entre z 108 y 113 no hay canal: ahí la bandeja, con su muesca, hace de pared)
module edge_channel_solid() difference() {
    intersection() {
        both_edges() on_front() translate([-1, -1, edge_strip_s0 - 3 - edge_ch_t])
            cube([edge_strip_xc + edge_ch_w / 2 + edge_ch_t + 1, edge_ch_n + edge_ch_t + 1, edge_strip_s1 - edge_strip_s0 + 6 + 2 * edge_ch_t]);
        body(wall - 0.01);
    }
    translate([-1, -1, chamber_low_top]) cube([outer_w + 2, outer_d + 2, wall_int]);
}
module edge_channel_void() both_edges() on_front()
    translate([edge_strip_xc - edge_ch_w / 2, wall - 0.01, edge_strip_s0 - 3]) cube([edge_ch_w, edge_ch_n - wall + 0.01, edge_strip_s1 - edge_strip_s0 + 6]);
module edge_slot() both_edges() on_front()
    translate([edge_strip_xc - edge_strip_w / 2, -1, edge_strip_s0]) cube([edge_strip_w, wall + 1.02, edge_strip_s1 - edge_strip_s0]);
// salida de cables por la trasera del canal, en su extremo superior (a la bahía)
module edge_cable_exit() both_edges() on_front()
    translate([edge_strip_xc - 2, edge_ch_n - 0.01, edge_strip_s1 - 8]) cube([4, edge_ch_t + 1, 6]);
// inserto transparente: barra que rellena la ranura + pestaña en cuña (45°, imprimible) que se apoya por dentro
module edge_insert_profile(c = edge_ins_clear) {
    a = edge_strip_w / 2 - c; b = edge_ch_w / 2 - 0.3;
    polygon([[-a, 0], [a, 0], [a, wall], [b, wall + b - a], [b, wall + b - a + 0.4], [-b, wall + b - a + 0.4], [-b, wall + b - a], [-a, wall]]);
}
module edge_inserts() both_edges() on_front() translate([edge_strip_xc, 0, edge_strip_s0 + edge_ins_clear])
    linear_extrude(edge_strip_s1 - edge_strip_s0 - 2 * edge_ins_clear) edge_insert_profile();
module edge_leds() color([0.9, 0.9, 1]) cut() both_edges() on_front()
    translate([edge_strip_xc - 2.5, edge_ch_n - 1.6, edge_strip_s0]) cube([5, 1.6, edge_strip_s1 - edge_strip_s0]);

// ---------------------------------------------------------------------------
// Cámara acústica
// ---------------------------------------------------------------------------
module chamber_region() {
    translate([-1, -1, wall - 1]) cube([outer_w + 2, outer_d + 2, chamber_low_top - wall + 1]);
    intersection() {
        translate([-1, -1, chamber_low_top - 0.01]) cube([outer_w + 2, outer_d + 2, chamber_up_top - chamber_low_top + 0.01]);
        behind(part_n + wall_int);
    }
}

module chamber_walls() {
    color([0.35, 0.35, 0.4]) cut() intersection() {
        body(wall - 0.01);
        union() {
            // bandeja: techo del bloque inferior delante del tabique, con los agujeros de los pasadores
            difference() {
                intersection() {
                    translate([-1, -1, chamber_low_top]) cube([outer_w + 2, outer_d + 2, wall_int]);
                    difference() { translate([-1, -1, -1]) cube([outer_w + 2, outer_d + 2, outer_h]); behind(part_n + wall_int); }
                }
                for (x = [wall + pin_block / 2, outer_w - wall - pin_block / 2])
                    translate([x, pin_y_, chamber_low_top + wall_int - pin_len - 0.5])
                        cylinder(d = pin_hole_d, h = pin_len + 1);
                edge_channel_void();   // muesca: la bandeja cierra el canal de las franjas entre z 108 y 113
            }
            // tabique inclinado
            intersection() {
                translate([-1, -1, chamber_low_top]) cube([outer_w + 2, outer_d + 2, chamber_up_top + wall_int - chamber_low_top]);
                difference() { behind(part_n); behind(part_n + wall_int); }
            }
            // tapa (suelo de la bahía)
            intersection() {
                translate([-1, -1, chamber_up_top]) cube([outer_w + 2, outer_d + 2, wall_int]);
                behind(part_n);
            }
        }
    }
}

// Volumen que ocupan los transductores dentro de la cámara (aprox. conservadora)
module speaker_displacement() {
    translate([outer_w / 2, 0, 0]) on_front() translate([0, drv_n, drv_s]) rotate([-90, 0, 0])
        cylinder(d1 = speaker_d * 0.9, d2 = 50, h = speaker_depth);
}
module pr_displacement() {
    translate([outer_w / 2, pr_flange_y, audio_center_z]) rotate([90, 0, 0]) cylinder(d1 = pr_d * 0.95, d2 = 70, h = pr_depth);
}
module chamber_air() {
    difference() {
        intersection() { body(wall); chamber_region(); }
        edge_channel_void();   // (las paredes del canal las descuenta la comprobación de la cubeta)
        speaker_displacement();
        pr_displacement();
    }
}

// ---------------------------------------------------------------------------
// Componentes
// ---------------------------------------------------------------------------
screen_x0 = (outer_w - screen_w) / 2;
// marco local de la pantalla: origen en la cara del cristal (cara interior del frontal), borde inferior de las pestañas
module on_screen_plane() on_front() translate([screen_x0, wall, screen_s0]) children();

module screen() {
    color([0.08, 0.08, 0.08]) cut() on_screen_plane() translate([0, 0, glass_z0]) cube([screen_w, screen_t, glass_h]);
    color([0.1, 0.25, 0.5]) cut() on_screen_plane() difference() {
        union() {
            translate([0, screen_t, (screen_h - screen_body_h) / 2]) cube([screen_w, screen_pcb_t, screen_body_h]);
            for (x = [0, screen_w - (screen_w - screen_tab_gap) / 2], z = [0, (screen_h + screen_body_h) / 2])
                translate([x, screen_t, z]) cube([(screen_w - screen_tab_gap) / 2, screen_pcb_t, (screen_h - screen_body_h) / 2]);
        }
        for (dx = [0, screen_hole_dx], dz = [0, screen_hole_dz])
            translate([(screen_w - screen_hole_dx) / 2 + dx, screen_t - 1, screen_hole_z0 + dz]) rotate([-90, 0, 0]) cylinder(d = screen_hole_d, h = screen_pcb_t + 2);
    }
    color([0.15, 0.3, 0.2]) cut() on_screen_plane() translate([10, screen_t + screen_pcb_t, 12]) cube([screen_w - 40, screen_comp_t, screen_h - 24]);
}
module screen_active() {
    color([0.25, 0.55, 0.95]) cut() on_screen_plane() translate([screen_active_x0, -0.4, screen_active_z0]) cube([screen_active_w, 0.4, screen_active_h]);
}
module screen_connectors() {
    color([0.85, 0.55, 0.1]) cut() on_screen_plane() translate([0, 0, screen_h - screen_conn_bot]) {
        translate([screen_w, screen_t, 0]) cube([screen_conn_proud + plug_clear, screen_pcb_t + screen_conn_depth + 1, screen_conn_bot - screen_conn_top]);
        translate([screen_w - 26, screen_t + screen_pcb_t, 0]) cube([26, screen_conn_depth + 1, screen_conn_bot - screen_conn_top]);
    }
}

// Altavoz montado por dentro en el frontal inclinado; radiador en la trasera
module speaker() {
    color([0.18, 0.18, 0.18]) cut() translate([outer_w / 2, 0, 0]) on_front() translate([0, 0, drv_s]) rotate([-90, 0, 0]) {
        translate([-drv_frame / 2, -drv_frame / 2, drv_n]) cube([drv_frame, drv_frame, 4]);
        translate([0, 0, drv_n]) cylinder(d = 85, h = speaker_depth - 1);
        translate([0, 0, drv_n - 3]) cylinder(d = 86, h = 3.01);
    }
}
module pr() {
    color([0.25, 0.25, 0.28]) cut() translate([outer_w / 2, outer_d, audio_center_z]) rotate([90, 0, 0]) {
        translate([-pr_frame / 2, -pr_frame / 2, outer_d - pr_flange_y]) cube([pr_frame, pr_frame, 4]);
        translate([0, 0, outer_d - pr_flange_y]) cylinder(d = 90, h = pr_depth);
        translate([0, 0, wall + 1]) cylinder(d = 92, h = outer_d - pr_flange_y - wall - 0.99);
    }
}

// Bahía de electrónica: su frente es la cara trasera del tabique
function bay_front_y(z) = sn2y((z + (part_n + wall_int) * sin(fa)) / cos(fa), part_n + wall_int);
pi_pos   = [8, outer_d - wall - pi_d - 2, bay_floor_z];
buck_pos = [pi_pos[0] + pi_w + port_clear + 2, outer_d - wall - buck_d - 6, bay_floor_z];
dac_pos  = [buck_pos[0] + buck_w + 10, outer_d - wall - dac_d - 10, bay_floor_z];
kabd_pos = [98, outer_d - wall - kabd_d - 1.5, bracket_z + 3];

module pi5()  { color([0.1, 0.45, 0.15]) cut() translate(pi_pos)   cube([pi_w, pi_d, pi_h]); }
module kabd() { color([0.15, 0.3, 0.7]) cut()  translate(kabd_pos) cube([kabd_w, kabd_d, kabd_h]); }
module buck() { color([0.3, 0.6, 0.55]) cut()  translate(buck_pos) cube([buck_w, buck_d, buck_h]); }
module dac()  { color([0.5, 0.3, 0.7]) cut()   translate(dac_pos)  cube([dac_w, dac_d, dac_h]); }
module bracket() {
    color([0.5, 0.5, 0.5]) cut() translate([kabd_pos[0] - 2, kabd_pos[1] - 1, bracket_z]) cube([kabd_w + 4, kabd_d + 2, 3]);
}
module pi_port_clear() {
    color([1, 1, 0.2, 0.3]) cut() {
        translate([pi_pos[0] + pi_w, pi_pos[1] + 2, bay_floor_z + 2]) cube([port_clear, pi_d - 4, 17]);
        translate([pi_pos[0] + 5, pi_pos[1] - port_clear, bay_floor_z + 2]) cube([50, port_clear, 10]);
    }
}
module dc_jack() {
    color([0.9, 0.7, 0.1]) cut() translate([dc_x, outer_d - dc_depth, dc_z]) rotate([-90, 0, 0]) cylinder(d = dc_d, h = dc_depth);
}
module power_button() {
    color([0.9, 0.7, 0.1]) cut() translate([power_btn_x - 6, outer_d - wall - 12, power_btn_z - 6]) cube([12, 12, 12]);
}
module top_buttons() {
    // placa con los pulsadores y el interruptor bajo el techo
    color([0.9, 0.7, 0.1]) cut() translate([btn_x - 9, btn_y[0] - 9, outer_h - wall - 1 - 9]) cube([18, mute_y - btn_y[0] + 18, 9]);
}
module led_bar() {
    color([0.2, 0.6, 1]) cut() on_front() translate([(outer_w - led_bar_w) / 2, wall, led_s]) cube([led_bar_w, 2.5, led_bar_h + 2]);
}
module mics() {
    color([0.8, 0.2, 0.2]) cut() {
        translate([(outer_w - mic_w) / 2, mic_y, outer_h - wall - mic_rail_gap + 0.1]) cube([mic_w, mic_d, 1.6]);
        translate([(outer_w - mic_w) / 2 + 3, mic_y + 5, outer_h - wall - mic_rail_gap + 0.1 - (mic_h - 1.6)]) cube([mic_w - 6, mic_d - 10, mic_h - 1.6]);
    }
}
cam_s0 = glass_z0 + glass_h + cam_gap;
module camera() {
    color([0.2, 0.7, 0.3]) cut() on_screen_plane() {
        translate([outer_w / 2 - screen_x0 - cam_w / 2, cam_standoff, cam_s0]) cube([cam_w, 1, cam_h]);
        translate([outer_w / 2 - screen_x0 - cam_w / 2 + 3, cam_standoff + 1, cam_s0 + 3]) cube([cam_w - 6, cam_t - cam_standoff - 1, cam_h - 6]);
        translate([outer_w / 2 - screen_x0, 0.5, cam_s0 + cam_lens_from_bottom]) rotate([-90, 0, 0]) cylinder(d = 8.5, h = cam_standoff - 0.5);
    }
}

module component(name) {
    if      (name == "screen")        screen();
    else if (name == "screen_conn")   screen_connectors();
    else if (name == "pi_port_clear") pi_port_clear();
    else if (name == "speaker")       speaker();
    else if (name == "pr")            pr();
    else if (name == "pi5")           pi5();
    else if (name == "kabd")          kabd();
    else if (name == "buck")          buck();
    else if (name == "dac")           dac();
    else if (name == "bracket")       bracket();
    else if (name == "dc_jack")       dc_jack();
    else if (name == "power_button")  power_button();
    else if (name == "top_buttons")   top_buttons();
    else if (name == "led_bar")       led_bar();
    else if (name == "mics")          mics();
    else if (name == "camera")        camera();
    else if (name == "chamber_walls") chamber_walls();
    else if (name == "chamber_air")   chamber_air();
    else if (name == "body_inner")    body(wall);
    else if (name == "edge_channel")  edge_channel_solid();
    else if (name == "edge_void")     edge_channel_void();
    else if (name == "edge_slot")     edge_slot();
    else if (name == "edge_exit")     edge_cable_exit();
    else if (name == "edge_inserts")  edge_inserts();
    else if (name == "edge_leds")     edge_leds();
    else if (name == "shell")         shell();
}

module scene() {
    if (show_screen) { screen(); screen_active(); screen_connectors(); }
    if (show_audio)  { speaker(); pr(); }
    if (show_electronics) { pi5(); pi_port_clear(); kabd(); bracket(); buck(); dac(); dc_jack(); power_button(); top_buttons(); led_bar(); edge_leds(); mics(); camera(); }
    chamber_walls();
    if (show_chamber_air) color([0.2, 0.7, 1, 0.35]) cut() chamber_air();
    if (show_shell) color([0.15, 0.15, 0.17, 0.25]) cut() shell();
}

if (part == "all") scene(); else component(part);
