// Prisma v0.5 — todas las cotas en mm
// Ejes: X = ancho (izq→der), Y = fondo (frente→trasera), Z = alto.
// Origen en la esquina frontal-inferior-izquierda de la envolvente.
//
// v0.5 vuelve al boceto original (D031): frontal inclinado continuo de arriba abajo,
// aristas redondeadas, banda de lamas bajo la pantalla y acabado negro mate.
//
// Sistema del frontal: s = distancia a lo largo de la cara exterior inclinada desde la base,
// n = profundidad hacia dentro, perpendicular al frontal.
//   y = s·sen(a) + n·cos(a)      z = s·cos(a) − n·sen(a)

// ---------------------------------------------------------------------------
// Envolvente exterior (D009, D031)
// ---------------------------------------------------------------------------
outer_w = 205;
outer_h = 262;    // altavoz + bandeja + pantalla + cámara apilados en el frontal inclinado
outer_d = 150;    // +5 mm respecto a v0.4 para compensar el volumen que quita el frontal inclinado
corner_r = 9;     // radio de las aristas redondeadas

wall      = 3;    // pared exterior
wall_int  = 5;    // tabiques internos (cámara acústica: más rígidos)

front_angle = 11;               // inclinación del frontal (y de la pantalla y el altavoz)
screen_angle = front_angle;     // alias usado por las piezas de prueba
top_setback = outer_h * tan(front_angle);   // ≈ 50,9

// ---------------------------------------------------------------------------
// Pantalla Waveshare 7" HDMI LCD (C) Rev4.1
// Cotas del PCB, taladros y conectores: plano oficial de Waveshare.
// Cristal y área visible: medidos sobre fotos de la unidad real (±1 mm).
// Montada en HORIZONTAL; mirando de frente, el flex del LCD queda abajo y los
// conectores (HDMI, micro-USB táctil, interruptor de retroiluminación) en el
// canto DERECHO, en la mitad superior.
// Coordenadas locales: x desde el borde izquierdo, z desde el borde inferior de
// las pestañas, y hacia atrás desde la cara del cristal.
// ---------------------------------------------------------------------------
screen_w      = 164.9;   // ancho total (plano)
screen_h      = 124.27;  // alto total con pestañas (plano)
screen_body_h = 106.96;  // alto del PCB entre pestañas (plano)
screen_tab_gap = 148.9;  // hueco entre pestañas (plano)
glass_h       = 99.8;    // alto del cristal (foto)
glass_z0      = 16.4;    // borde inferior del cristal sobre el borde inferior de las pestañas (foto)
screen_t      = 7.9;     // cara del cristal → cara delantera del PCB (medido: 9,5 hasta la trasera del PCB)
screen_pcb_t  = 1.6;
screen_comp_t = 4;       // componentes generales detrás del PCB
screen_active_w = 154.21; screen_active_h = 85.92;   // área visible 1024×600
screen_active_x0 = 3.6;            // margen izquierdo cristal → área visible (derecho ≈ 7,1)
screen_active_z0 = glass_z0 + 9.0; // margen inferior ≈ 9,0 (superior ≈ 4,9)
screen_hole_dx = 156.9; screen_hole_dz = 114.96;    // taladros (plano), a 4,0 mm de los laterales
screen_hole_z0 = (screen_h - screen_hole_dz) / 2;   // 4,655
screen_hole_d = 3.0;     // medido → tornillos M2.5
// Conectores en el canto derecho (plano), desde el borde superior de las pestañas:
// HDMI 18–34 mm, micro-USB táctil 41–49 mm, interruptor 54–62 mm
screen_conn_top = 15;
screen_conn_bot = 65;
screen_conn_proud = 2;
screen_conn_depth = 7;
plug_clear = 15;         // hueco lateral para clavijas acodadas a 90°
screen_s0 = 118.5;       // posición del borde inferior de las pestañas a lo largo del frontal (s)

// ---------------------------------------------------------------------------
// Cámara acústica (D016, D031): bloque inferior de ancho y fondo completos +
// bloque superior-trasero tras un tabique paralelo al frontal (detrás de la pantalla)
// ---------------------------------------------------------------------------
chamber_low_top  = 108;  // techo del bloque inferior = cara inferior de la bandeja = unión cubeta/capucha
part_n           = 26;   // cara delantera del tabique inclinado (profundidad n desde la cara exterior)
chamber_up_top   = 182;  // techo interior del bloque superior-trasero
acoustic_target_l = 3.5;
bracing_allow_l   = 0.10;

// ---------------------------------------------------------------------------
// Audio
// ---------------------------------------------------------------------------
speaker_d = 105; speaker_depth = 48;   // DMA105-4 (marco / fondo total; SoundImports: fondo 47,2 mm)
drv_frame = 104.1; drv_cut = 90;       // marco cuadrado y recorte (3,54") — confirmar con la pieza
pr_frame  = 104.1; pr_cut  = 98.4;     // DMA105-PR: marco y recorte (3,875")
pr_d      = 104; pr_depth  = 55.1;
drv_clear = 7;                          // marco del altavoz a 7 mm de la rejilla (suspensión + Xmax + margen)
pr_clear  = 14;                         // radiador: Xmax 9 mm
bolt_off  = 44.9;                       // taladros en las esquinas, ±44,9 mm — medir
drv_s     = 58.5;                       // centro del altavoz a lo largo del frontal (s)
drv_n     = wall + drv_clear;           // plano del marco del altavoz (n)
audio_center_z = drv_s * cos(front_angle) - drv_n * sin(front_angle);   // ≈ 55,5
pr_flange_y = outer_d - wall - pr_clear;

// Banda de lamas del frontal (D031)
grille_s0 = 12; grille_s1 = 104;        // tramo de la banda a lo largo del frontal
grille_margin_x = 22;                   // la banda ocupa todo el ancho salvo 22 mm por lado

// ---------------------------------------------------------------------------
// Electrónica (bahía superior, sobre la tapa de la cámara)
// ---------------------------------------------------------------------------
bay_floor_z = chamber_up_top + wall_int;   // 187

pi_w = 85; pi_d = 56; pi_h = 25;   // Pi 5 con Active Cooler; USB a la derecha, micro-HDMI/USB-C hacia delante
kabd_w = 91.4; kabd_d = 68.6; kabd_h = 23;
dac_w = 32; dac_d = 14; dac_h = 10;            // GY-PCM5102
buck_w = 25.4; buck_d = 25.4; buck_h = 9.5;    // Pololu D36V50F5
bracket_z = bay_floor_z + pi_h + 3;            // balda del KABD-250
port_clear = 20;

// Entrada DC y botón de encendido en la trasera
dc_d = 11.2; dc_depth = 20;
dc_x = 30; dc_z = bay_floor_z + 58;
power_btn_x = 52; power_btn_z = dc_z;

// Botones del techo (D032): capuchones de 8 mm enrasados sobre pulsadores de 6 × 6 mm,
// e interruptor deslizante de silencio de micrófonos (corta la alimentación USB del ReSpeaker)
btn_cap_d = 8; btn_x = outer_w - 26;
btn_y = [78, 96];               // volumen −, volumen +
mute_y = 118;                   // interruptor deslizante
mute_travel = 4; mute_knob = [3, 4];

// Iluminación y captación
led_bar_w = 140; led_bar_h = 3;
led_s = 117;                    // franja LED a lo largo del frontal (s)
mic_w = 86; mic_d = 35; mic_h = 8;     // ReSpeaker Lite USB
mic_spacing = 64;                      // verificar en la placa
mic_y = 97;
mic_rail_gap = 1.8;

// Franjas de luz en los cantos del frontal (D033): insertos transparentes en una ranura de la
// pared y, detrás, un canal cerrado con una tira WS2812B de 5 mm que da el color según el estado
edge_strip_w  = 4;                      // ancho visible de la franja
edge_strip_xc = corner_r + 1.5 + edge_strip_w / 2;   // centro, desde cada lateral (12,5): justo dentro del redondeo
edge_strip_s0 = grille_s0;              // empieza a la altura de la banda de lamas
edge_strip_s1 = 248;                    // y acaba antes del redondeo del techo
edge_ch_w   = 7;                        // hueco del canal (tira de 5 mm + holgura)
edge_ch_n   = 9;                        // fondo del hueco (la tira queda a ≈6 mm de la cara exterior)
edge_ch_t   = 1.5;                      // paredes del canal
edge_ins_clear = 0.15;                  // holgura por lado de los insertos

// Bandeja (2a) y caja superior (2b) de la cámara acústica (D027, D034)
tray_screw_x = 25;          // 2 tornillos M3 avellanados de la bandeja a insertos en la cubeta (x desde cada lateral)
tray_screw_n = 10;          // ... a 10 mm detrás de la cara exterior del frontal, en z = chamber_low_top
tray_front_gap = 1.0;       // holgura delantera: la capucha baja en vertical y su frontal inclinado avanza ≈1 mm en los últimos 5 mm
box_t   = 2.5;              // paredes de la caja superior (PETG)
box_gap = 0.3;              // holgura entre la caja y la capucha
box_screw_y = [80, 135];    // 4 tubos con tornillos M3 × 80 desde el suelo de la bahía hasta los rebordes de la cubeta
box_screw_x = wall + 3.5;   // centro de los rebordes laterales (6,5)

// Uniones capucha ↔ bandeja delantera (D029)
pin_block = 9; pin_d = 3; pin_len = 4; pin_hole_d = 3.3;
pin_n = 19;     // centro de los pasadores detrás del frontal (y = front_y(z bandeja) + pin_n), tras el canal de las franjas

// Cámara (D025): OV5647 sobre la pantalla
cam_w = 25; cam_h = 24; cam_t = 9;
cam_gap = 1;
cam_lens_d = 8;
cam_hole_dx = 21; cam_hole_dz = 12.5; cam_lens_from_bottom = 14.5;
cam_standoff = 5;

// ---------------------------------------------------------------------------
// Visualización
// ---------------------------------------------------------------------------
show_shell       = true;
show_screen      = true;
show_electronics = true;
show_audio       = true;
show_chamber_air = false;
section_x        = false;
