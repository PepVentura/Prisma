// Prisma — volumétrico v0.3
// Maqueta de distribución, no carcasa final.
//
// Cambios respecto a v0.2:
//  - Perfil lateral: frontal inferior vertical (bafle) + frontal superior inclinado 18° (pantalla).
//  - Cámara acústica en L: bloque inferior de ancho completo + bloque superior-trasero.
//  - Electrónica en bahía superior, sobre la tapa de la cámara. Sin fuente interna (D003).
//  - DMA105-PR en la trasera inferior; ventilación y puertos solo en la bahía superior.
//  - Pantalla con medidas de la unidad real y conectores en el canto derecho.
//  - Corregida la doble rotación de altavoz y radiador de v0.2.
//
// Uso desde línea de comandos (ver tools/):
//   openscad -D 'part="chamber_air"' -o aire.stl prisma_volumetrica_v0_3.scad

include <parametros.scad>;
$fn = 64;

part = "all";   // "all" | "chamber_air" | nombre de componente (ver component())

// ---------------------------------------------------------------------------
// Geometría base
// ---------------------------------------------------------------------------
function xin(z, i) = side_taper * z / outer_h + i;
function yf(z, i)  = z <= front_split_z
                     ? i
                     : (z - front_split_z) * tan(screen_angle) + i / cos(screen_angle);
// Cara exterior del frontal a la altura z
function front_y(z) = yf(z, 0);

// Sólido de la envolvente con un retranqueo i (0 = exterior, wall = interior)
module body(i = 0) {
    hull()
        for (z = [i, front_split_z, outer_h - i])
            translate([xin(z, i), yf(z, i), z - 0.005])
                cube([outer_w - 2 * xin(z, i), outer_d - i - yf(z, i), 0.01]);
}

module shell() { difference() { body(0); body(wall); } }

// Corte de sección: se aplica a cada pieza por separado para conservar los colores
module cut() {
    if (section_x)
        intersection() {
            children();
            translate([outer_w / 2, -10, -10]) cube([outer_w, outer_d + 20, outer_h + 20]);
        }
    else children();
}

// ---------------------------------------------------------------------------
// Cámara acústica
// ---------------------------------------------------------------------------
module chamber_region() {
    // bloque inferior, ancho y fondo completos
    translate([-1, -1, wall]) cube([outer_w + 2, outer_d + 2, chamber_low_top - wall]);
    // bloque superior-trasero
    translate([-1, chamber_up_front, wall])
        cube([outer_w + 2, outer_d + 2, chamber_up_top - wall]);
}

module chamber_walls() {
    color([0.35, 0.35, 0.4]) cut() intersection() {
        body(wall - 0.01);
        union() {
            // techo del bloque inferior (suelo de la zona de pantalla)
            translate([-1, -1, chamber_low_top]) cube([outer_w + 2, chamber_up_front + 1, wall_int]);
            // pared frontal del bloque superior
            translate([-1, chamber_up_front - wall_int, chamber_low_top])
                cube([outer_w + 2, wall_int, chamber_up_top + wall_int - chamber_low_top]);
            // tapa (suelo de la bahía de electrónica)
            translate([-1, chamber_up_front - wall_int, chamber_up_top])
                cube([outer_w + 2, outer_d + 2, wall_int]);
        }
    }
}

// Volumen desplazado por los transductores dentro de la cámara (aprox. conservadora)
module speaker_displacement() {
    translate([outer_w / 2, wall, audio_center_z]) rotate([-90, 0, 0])
        cylinder(d1 = speaker_d * 0.9, d2 = 50, h = speaker_depth);
}
module pr_displacement() {
    translate([outer_w / 2, outer_d - wall, audio_center_z]) rotate([90, 0, 0])
        cylinder(d1 = pr_d * 0.95, d2 = 70, h = pr_depth);
}

module chamber_air() {
    difference() {
        intersection() { body(wall); chamber_region(); }
        speaker_displacement();
        pr_displacement();
    }
}

// ---------------------------------------------------------------------------
// Componentes
// ---------------------------------------------------------------------------
screen_x0 = (outer_w - screen_w) / 2;
screen_z0 = front_split_z + screen_margin * cos(screen_angle);
screen_y0 = front_y(screen_z0) + wall / cos(screen_angle);

module on_screen_plane() {
    translate([screen_x0, screen_y0, screen_z0]) rotate([-screen_angle, 0, 0]) children();
}

// Cristal + LCD + marco, PCB con pestañas y componentes traseros
module screen() {
    color([0.08, 0.08, 0.08]) cut() on_screen_plane()
        translate([0, 0, glass_z0]) cube([screen_w, screen_t, glass_h]);
    color([0.1, 0.25, 0.5]) cut() on_screen_plane()
        difference() {
            union() {
                translate([0, screen_t, (screen_h - screen_body_h) / 2]) cube([screen_w, screen_pcb_t, screen_body_h]);
                for (x = [0, screen_w - (screen_w - screen_tab_gap) / 2], z = [0, (screen_h + screen_body_h) / 2])
                    translate([x, screen_t, z]) cube([(screen_w - screen_tab_gap) / 2, screen_pcb_t, (screen_h - screen_body_h) / 2]);
            }
            for (dx = [0, screen_hole_dx], dz = [0, screen_hole_dz])
                translate([(screen_w - screen_hole_dx) / 2 + dx, screen_t - 1, screen_hole_z0 + dz])
                    rotate([-90, 0, 0]) cylinder(d = screen_hole_d, h = screen_pcb_t + 2);
        }
    color([0.15, 0.3, 0.2]) cut() on_screen_plane()
        translate([10, screen_t + screen_pcb_t, 12]) cube([screen_w - 40, screen_comp_t, screen_h - 24]);
}
// Área visible 1024×600 (solo visual; no entra en las comprobaciones)
module screen_active() {
    color([0.25, 0.55, 0.95]) cut() on_screen_plane()
        translate([screen_active_x0, -0.4, screen_active_z0]) cube([screen_active_w, 0.4, screen_active_h]);
}
// Conectores del canto derecho + hueco para clavijas acodadas (HDMI y micro-USB)
module screen_connectors() {
    color([0.85, 0.55, 0.1]) cut() on_screen_plane()
        translate([0, 0, screen_h - screen_conn_bot]) {
            // conectores asomando por el canto + clavijas acodadas
            translate([screen_w, screen_t, 0])
                cube([screen_conn_proud + plug_clear, screen_pcb_t + screen_conn_depth + 1,
                      screen_conn_bot - screen_conn_top]);
            // cuerpo de los conectores detrás del PCB
            translate([screen_w - 26, screen_t + screen_pcb_t, 0])
                cube([26, screen_conn_depth + 1, screen_conn_bot - screen_conn_top]);
        }
}

module speaker() {
    color([0.18, 0.18, 0.18]) cut() translate([outer_w / 2, 0, audio_center_z]) rotate([-90, 0, 0])
        cylinder(d = speaker_d, h = speaker_depth + wall);
}
module pr() {
    color([0.25, 0.25, 0.28]) cut() translate([outer_w / 2, outer_d, audio_center_z]) rotate([90, 0, 0])
        cylinder(d = pr_d, h = pr_depth + wall);
}

pi_pos   = [8, 72, bay_floor_z];
buck_pos = [pi_pos[0] + pi_w + port_clear + 2, outer_d - wall - buck_d - 6, bay_floor_z];
dac_pos  = [buck_pos[0] + buck_w + 10, outer_d - wall - dac_d - 10, bay_floor_z];
kabd_pos = [98, outer_d - wall - kabd_d - 2, bracket_z + 3];

module pi5()  { color([0.1, 0.45, 0.15]) cut() translate(pi_pos)   cube([pi_w, pi_d, pi_h]); }
module kabd() { color([0.15, 0.3, 0.7]) cut()  translate(kabd_pos) cube([kabd_w, kabd_d, kabd_h]); }
module buck() { color([0.3, 0.6, 0.55]) cut()  translate(buck_pos) cube([buck_w, buck_d, buck_h]); }
module dac()  { color([0.5, 0.3, 0.7]) cut()   translate(dac_pos)  cube([dac_w, dac_d, dac_h]); }
module bracket() {
    color([0.5, 0.5, 0.5]) cut() translate([kabd_pos[0] - 2, kabd_pos[1] - 2, bracket_z]) cube([kabd_w + 4, kabd_d + 3, 3]);
}
// Huecos reservados para clavijas: USB/Ethernet (derecha de la Pi) y micro-HDMI/USB-C (delante)
module pi_port_clear() {
    color([1, 1, 0.2, 0.3]) cut() {
        translate([pi_pos[0] + pi_w, pi_pos[1] + 2, bay_floor_z + 2]) cube([port_clear, pi_d - 4, 17]);
        translate([pi_pos[0] + 5, pi_pos[1] - port_clear, bay_floor_z + 2]) cube([50, port_clear, 10]);
    }
}

module dc_jack() {
    color([0.9, 0.7, 0.1]) cut() translate([30, outer_d - dc_depth, bay_floor_z + 45])
        rotate([-90, 0, 0]) cylinder(d = dc_d, h = dc_depth);
}

module led_bar() {
    color([0.2, 0.6, 1]) cut() translate([(outer_w - led_bar_w) / 2, wall, led_bar_z])
        cube([led_bar_w, 6, led_bar_h]);
}

module mics() {
    color([0.8, 0.2, 0.2]) cut()
        translate([(outer_w - mic_w) / 2, mic_y, outer_h - wall - 1 - mic_h]) cube([mic_w, mic_d, mic_h]);
}
// Cámara opcional: sin sitio en el techo con el XVF3800; posición pendiente
// Cámara sobre la pantalla, en el plano inclinado (coordenadas locales de la pantalla)
cam_s0 = glass_z0 + glass_h + cam_gap;   // borde inferior de la placa sobre el borde inferior de las pestañas
module camera() {
    color([0.2, 0.7, 0.3]) cut() on_screen_plane()
        translate([outer_w / 2 - screen_x0 - cam_w / 2, 0, cam_s0]) cube([cam_w, cam_t, cam_h]);
    // objetivo: agujero en el frontal
    color([0.9, 0.9, 0.9]) cut() on_screen_plane()
        translate([outer_w / 2 - screen_x0, 0.01, cam_s0 + cam_h / 2]) rotate([90, 0, 0])
            cylinder(d = cam_lens_d, h = wall / cos(screen_angle) + 0.02);
}

// Tapa deslizante de la cámara (D026): guía en cola de milano rebajada en el frontal,
// recorrido de 14 mm hacia la derecha. Solo visual; la geometría está en tapa_camara_prueba.scad
module camera_shutter() {
    color([0.95, 0.75, 0.2]) cut() on_screen_plane()
        translate([outer_w / 2 - screen_x0 - 8, -wall / cos(screen_angle), cam_s0 + cam_h / 2 - 6])
            cube([16, 1.4, 12]);
}

// Zonas de ventilación (solo bahía de electrónica, D017) — referencia visual
module vents() {
    color([1, 0.4, 0.1, 0.35]) cut() {
        translate([20, outer_d - wall - 0.5, bay_floor_z + 8]) cube([130, wall + 1, 45]);   // trasera superior
        for (x = [-0.5, outer_w - wall - 0.5])                                               // laterales
            translate([x, 80, bay_floor_z + 8]) cube([wall + 1, 55, 40]);
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
    else if (name == "led_bar")       led_bar();
    else if (name == "mics")          mics();
    else if (name == "camera")        camera();
    else if (name == "chamber_walls") chamber_walls();
    else if (name == "chamber_air")   chamber_air();
    else if (name == "body_inner")    body(wall);
    else if (name == "shell")         shell();
}

// ---------------------------------------------------------------------------
// Escena
// ---------------------------------------------------------------------------
module scene() {
    if (show_screen) { screen(); screen_active(); screen_connectors(); }
    if (show_audio)  { speaker(); pr(); }
    if (show_electronics) { pi5(); pi_port_clear(); kabd(); bracket(); buck(); dac(); dc_jack(); led_bar(); mics(); camera(); camera_shutter(); vents(); }
    chamber_walls();
    if (show_chamber_air) color([0.2, 0.7, 1, 0.35]) cut() chamber_air();
    if (show_shell) color([0.15, 0.15, 0.17, 0.25]) cut() shell();
}

if (part == "all") {
    scene();
} else {
    component(part);
}
