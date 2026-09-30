// Prisma v0.3 — todas las cotas en mm
// Ejes: X = ancho (izq→der), Y = fondo (frente→trasera), Z = alto.
// Origen en la esquina frontal-inferior-izquierda de la envolvente.

// ---------------------------------------------------------------------------
// Envolvente exterior (D009, provisional)
// ---------------------------------------------------------------------------
outer_w = 205;
outer_h = 250;
outer_d = 145;

wall      = 3;    // pared exterior
wall_int  = 5;    // tabiques internos (cámara acústica: más rígidos)
side_taper = 0;   // laterales rectos, como en el render de concepto. Con 8 mm no cabían las clavijas de la pantalla

// Perfil lateral (D015): frontal inferior vertical + frontal superior inclinado
screen_angle  = 18;   // inclinación del frontal superior y de la pantalla
front_split_z = 122;  // altura donde empieza el frontal inclinado
top_setback   = (outer_h - front_split_z) * tan(screen_angle); // ≈ 41,6

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
screen_t      = 8;       // cara del cristal → cara delantera del PCB (foto: ≈9,5 hasta la trasera del PCB)
screen_pcb_t  = 1.6;
screen_comp_t = 4;       // componentes generales detrás del PCB
screen_active_w = 154.21; screen_active_h = 85.92;   // área visible 1024×600
screen_active_x0 = 3.6;            // margen izquierdo cristal → área visible (derecho ≈ 7,1)
screen_active_z0 = glass_z0 + 9.0; // margen inferior ≈ 9,0 (superior ≈ 4,9)
// Taladros de fijación (plano): 156,90 × 114,96 mm entre centros, a 4,0 mm de los laterales
screen_hole_dx = 156.9; screen_hole_dz = 114.96;
screen_hole_z0 = (screen_h - screen_hole_dz) / 2;   // 4,655
screen_hole_d = 3.2;     // diámetro: medir (M3 → 3,2)
// Conectores en el canto derecho (plano), medidos desde el borde superior de las pestañas:
// HDMI 18–34 mm, micro-USB táctil 41–49 mm, interruptor 54–62 mm
screen_conn_top = 15;
screen_conn_bot = 65;
screen_conn_proud = 2;   // el HDMI sobresale ≈2 mm del canto
screen_conn_depth = 7;   // altura del HDMI detrás del PCB
plug_clear = 15;         // hueco lateral para clavijas acodadas a 90°
screen_margin = 3;       // del inicio del plano inclinado al borde inferior de las pestañas

// ---------------------------------------------------------------------------
// Cámara acústica en L (D016)
// ---------------------------------------------------------------------------
chamber_low_top  = 111;  // techo interior del bloque inferior (ancho completo)
chamber_up_front = 64;   // cara interior frontal del bloque superior-trasero
chamber_up_top   = 170;  // techo interior del bloque superior-trasero
acoustic_target_l = 3.5; // objetivo 3–4 L netos
bracing_allow_l   = 0.10; // reserva para refuerzos, espuma y cableado

// ---------------------------------------------------------------------------
// Audio
// ---------------------------------------------------------------------------
speaker_d = 105; speaker_depth = 48;   // DMA105-4 (marco / fondo total)
pr_d      = 104; pr_depth      = 53;   // DMA105-PR
audio_center_z = (wall + chamber_low_top) / 2;  // ≈ 57

// ---------------------------------------------------------------------------
// Electrónica (bahía superior, sobre la tapa de la cámara)
// ---------------------------------------------------------------------------
bay_floor_z = chamber_up_top + wall_int;   // 175

// Pi 5 en orientación normal: USB/Ethernet hacia la derecha (+X), micro-HDMI y USB-C hacia la pantalla (−Y)
pi_w = 85; pi_d = 56; pi_h = 25;   // h con Active Cooler
kabd_w = 91.4; kabd_d = 68.6; kabd_h = 23;
dac_w = 45; dac_d = 35; dac_h = 15;
buck_w = 60; buck_d = 35; buck_h = 20;
bracket_z = bay_floor_z + pi_h + 3;   // balda para el KABD-250, por encima de Pi, buck y DAC
port_clear = 20;                      // hueco delante de los puertos de la Pi para clavijas acodadas

// Entrada DC (fuente externa 24 V, D003) — conector de panel
dc_d = 12; dc_depth = 20;

// Iluminación y captación
led_bar_w = 140; led_bar_h = 5;  led_bar_z = 116.5;
mic_count = 4; mic_d = 8; mic_spacing = 45;
cam_d = 10;

// ---------------------------------------------------------------------------
// Visualización
// ---------------------------------------------------------------------------
show_shell       = true;
show_screen      = true;
show_electronics = true;
show_audio       = true;
show_chamber_air = false;  // volumen de aire neto de la cámara (para inspección)
section_x        = false;  // corte por el plano medio X (vista lateral interior)
