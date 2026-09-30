// Prisma v0.3 — todas las cotas en mm
// Ejes: X = ancho (izq→der), Y = fondo (frente→trasera), Z = alto.
// Origen en la esquina frontal-inferior-izquierda de la envolvente.

// ---------------------------------------------------------------------------
// Envolvente exterior (D009, provisional)
// ---------------------------------------------------------------------------
outer_w = 205;
outer_h = 266;   // 250 hasta v0.3.2: +16 mm para alojar la cámara sobre la pantalla (D025)
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
screen_t      = 7.9;     // cara del cristal → cara delantera del PCB (medido: 9,5 hasta la trasera del PCB)
screen_pcb_t  = 1.6;
screen_comp_t = 4;       // componentes generales detrás del PCB
screen_active_w = 154.21; screen_active_h = 85.92;   // área visible 1024×600
screen_active_x0 = 3.6;            // margen izquierdo cristal → área visible (derecho ≈ 7,1)
screen_active_z0 = glass_z0 + 9.0; // margen inferior ≈ 9,0 (superior ≈ 4,9)
// Taladros de fijación (plano): 156,90 × 114,96 mm entre centros, a 4,0 mm de los laterales
screen_hole_dx = 156.9; screen_hole_dz = 114.96;
screen_hole_z0 = (screen_h - screen_hole_dz) / 2;   // 4,655
screen_hole_d = 3.0;     // medido → tornillos M2.5
// Conectores en el canto derecho (plano), medidos desde el borde superior de las pestañas:
// HDMI 18–34 mm, micro-USB táctil 41–49 mm, interruptor 54–62 mm
screen_conn_top = 15;
screen_conn_bot = 65;
screen_conn_proud = 2;   // el HDMI sobresale ≈2 mm del canto
screen_conn_depth = 7;   // altura del HDMI detrás del PCB (medido)
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
pr_d      = 104; pr_depth      = 55.1; // DMA105-PR (Dayton: marco 104,1 mm, recorte 98,4 mm, fondo 55,1 mm)
audio_center_z = (wall + chamber_low_top) / 2;  // ≈ 57

// ---------------------------------------------------------------------------
// Electrónica (bahía superior, sobre la tapa de la cámara)
// ---------------------------------------------------------------------------
bay_floor_z = chamber_up_top + wall_int;   // 175

// Pi 5 en orientación normal: USB/Ethernet hacia la derecha (+X), micro-HDMI y USB-C hacia la pantalla (−Y)
pi_w = 85; pi_d = 56; pi_h = 25;   // h con Active Cooler
kabd_w = 91.4; kabd_d = 68.6; kabd_h = 23;
dac_w = 32; dac_d = 14; dac_h = 10;   // GY-PCM5102 (PCM5102A), salida jack 3,5 mm
buck_w = 25.4; buck_d = 25.4; buck_h = 9.5;   // Pololu D36V50F5 (5 V, 5,5 A)
bracket_z = bay_floor_z + pi_h + 3;   // balda para el KABD-250, por encima de Pi, buck y DAC
port_clear = 20;                      // hueco delante de los puertos de la Pi para clavijas acodadas

// Entrada DC (fuente externa 24 V, D003) — conector de panel
dc_d = 11.2; dc_depth = 20;   // conector DC de panel 5,5 × 2,1 (taladro de 11 mm)
dc_x = 30; dc_z = bay_floor_z + 65;   // trasera, por encima de la rejilla

// Iluminación y captación
led_bar_w = 140; led_bar_h = 5;  led_bar_z = 116.5;
// ReSpeaker Lite USB (XU316: 2 micrófonos, AEC, supresión de ruido): placa 86 × 35 mm
// justo bajo el techo, con 2 agujeros en la tapa. El XVF3800 (Ø 99 mm) no cabe con la pantalla inclinada.
mic_w = 86; mic_d = 35; mic_h = 8;     // placa + conectores
mic_spacing = 64;                      // separación aproximada entre micrófonos: verificar en la placa
mic_y = 97;                            // borde delantero de la placa
mic_rail_gap = 1.8;

// Uniones capucha ↔ bandeja delantera (D029): pasadores en las esquinas delanteras
pin_block = 9; pin_d = 3; pin_len = 4; pin_hole_d = 3.3;                    // la placa se desliza en raíles justo bajo el techo
// Cámara (D025): OV5647 5 MP (compatible con la cámara oficial v1.3), centrada sobre la
// pantalla, en el frontal inclinado, mirando al usuario con la misma inclinación que la pantalla.
// La Camera Module 3 tiene la misma placa: para usarla basta con subir cam_standoff y cam_t.
cam_w = 25; cam_h = 24; cam_t = 9;      // placa 25 × 24 mm; fondo total aprox. (OV5647)
cam_gap = 3;                            // separación entre el borde superior del cristal y la placa
cam_lens_d = 8;                         // agujero para el objetivo
// Taladros M2 de la placa (patrón común de las cámaras oficiales: 21 × 12,5 mm).
// El objetivo queda a la altura de la fila superior de taladros, 14,5 mm sobre el borde inferior.
cam_hole_dx = 21; cam_hole_dz = 12.5; cam_lens_from_bottom = 14.5;
cam_standoff = 5;                       // cara interior del frontal → cara delantera de la placa (≈ alto del objetivo OV5647: medir)

// ---------------------------------------------------------------------------
// Visualización
// ---------------------------------------------------------------------------
show_shell       = true;
show_screen      = true;
show_electronics = true;
show_audio       = true;
show_chamber_air = false;  // volumen de aire neto de la cámara (para inspección)
section_x        = false;  // corte por el plano medio X (vista lateral interior)
