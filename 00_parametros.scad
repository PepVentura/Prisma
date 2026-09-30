//
// ============================================================================
// SteamMachine UM790
// Project Phoenix
//
// Archivo : 00_parametros.scad
// Versión : 3.0
//
// ÚNICA fuente de parámetros del proyecto.
//
// ============================================================================

$fn = 64;

//=============================================================================
// INFORMACIÓN
//=============================================================================

project_name    = "SteamMachine UM790";
project_version = "3.0";

//=============================================================================
// CARCASA EXTERIOR (Steam Machine original)
//=============================================================================

case_width  = 156.0;
case_depth  = 162.4;
case_height = 152.0;   // altura EXTERIOR total, CON patas (dato original, sin modificar)

wall_thickness = 3.0;

bottom_thickness = 3.0;
top_thickness    = 3.0;

// Patas — CONFIRMADO por el usuario (2026-08-03): externas, 4 mm,
// añadidas por DEBAJO del cascarón (no van incluidas en la altura de
// trabajo interna). shell_height es la altura real del cascarón
// (suelo a techo) que usa todo el ensamblaje virtual y el chasis;
// case_height sigue siendo el dato exterior original de 152 mm.
//
// Antes de esta confirmación, todo el ensamblaje usaba case_height
// (152) directamente como altura de trabajo interna — ver
// docs/Virtual_Assembly_Report.md, sección "Patas externas (148/152 mm)".
leg_height   = 4.0;   // Dato real confirmado por el usuario (2026-08-03)
shell_height = case_height - leg_height;  // 148.0

//=============================================================================
// CÁMARA INFERIOR
//=============================================================================

lower_air_chamber = 12.0;

//=============================================================================
// BANDEJA
//=============================================================================

// tray_width — CORREGIDO (2026-08-03, pregunta del usuario: "¿podrá
// insertarse sin que nada se lo impida?"): con 150 mm (el hueco
// exacto entre paredes, sin holgura), la bandeja rozaba los rellenos
// de imanes/tornillos de las paredes laterales (sideBossPad() etc,
// que sobresalen 7 mm hacia el interior) durante el recorrido de
// bajada al insertarla — no en su posición final (eso ya estaba
// verificado sin colisión), sino en el TRAYECTO para llegar ahí.
// Reducido a 130 mm: dejando 3 mm de holgura a cada lado del canal
// libre entre rellenos (136 mm), y con margen de sobra respecto a
// los anclajes reales del UM790 (off_x = 56,5 mm). tray_depth NO
// necesita el mismo ajuste: el problema es solo con las paredes
// laterales (fijas), no con el frente/fondo (paneles separados, no
// son obstáculo durante la inserción vertical).
tray_width     = 130.0;
tray_depth     = 150.0;
tray_thickness = 3.0;

// Pilares de apoyo de la bandeja (openscad/parts/02_chassis/floor.scad,
// traySupportPosts()) y sus taladros de paso correspondientes en la
// propia bandeja (openscad/parts/01_bandeja/base.scad,
// trayScrewClearanceHoles()) — comparten estos valores para no
// desincronizarse.
//
// tray_support_inset_x = 5.0: con 12 mm de margen, el pilar caía en
// la zona HUECA de la bandeja (el marco macizo, base_frame_width =
// 10 mm, solo llega hasta 65 mm desde el centro; con inset=12 el
// pilar quedaba en X=63 mm, fuera de ese marco). Con inset=5, el
// pilar (Ø8 mm) queda centrado en X=70 mm, dentro del marco sólido
// [65,75] con margen a ambos lados.
//
// tray_support_inset_y = 35.0 (no el mismo valor que X): con el mismo
// inset en X e Y, el pilar (en la esquina, Y=70 mm) quedaba dentro
// de la zona de los rellenos de imanes/tornillos de la pared
// (sideBossPad()/rearBossPad(), que ocupan Y desde ±67,2 mm hasta el
// borde) — el relleno tapaba el hueco del inserto del pilar (aviso
// del usuario, 2026-08-03). Con Y=40 mm el pilar sigue sobre el marco
// sólido (basta con que X esté en la franja del marco) pero fuera de
// la franja de los rellenos.
tray_support_diameter = 8.0;
tray_support_inset_x  = 5.0;
tray_support_inset_y  = 35.0;

base_frame_width   = 10.0;
base_outer_chamfer = 4.0;
base_inner_chamfer = 4.0;

// Parámetros que faltaban (base.scad los usaba sin que existieran en
// este archivo — bandeja no renderizaba correctamente). Añadidos
// ahora, sin modificar ningún otro valor de la bandeja.
base_island_size  = 16.0;  // lado de cada isla de apoyo bajo los postes
base_bridge_width = 8.0;   // ancho de los refuerzos en cruz de la base

//=============================================================================
// PCB UM790
//=============================================================================

pcb_width     = 122.0;
pcb_depth     = 119.5;
pcb_thickness = 1.60;

um790_mount_spacing_x = 113.0;
um790_mount_spacing_y = 99.0;

//=============================================================================
// POSTES
//=============================================================================

// Altura de postes — RECONCILIADA con el valor confirmado por el
// usuario en el ensamblaje virtual v1 (docs/Virtual_Assembly_Report.md).
// Antes: 6.0 mm (no dejaba hueco suficiente para el pulsador/USB
// frontal tras el panel; ver informe, hallazgo de colisión con la PCB
// y los postes).
um790_post_height   = 20.0;
um790_post_diameter = 7.0;

insert_diameter = 4.10;
insert_depth    = 5.00;

// Compartido entre openscad/parts/02_chassis/top.scad (taladros de
// paso) y walls.scad (insertos): deben coincidir en X/Y, por eso es
// un único parámetro y no un valor duplicado en cada archivo.
top_screw_y_inset = 15.0;

// Compartido entre walls.scad (topInsertPad) y top.scad (topInsertRelief).
top_insert_pad_depth = 8.0;  // grosor local en los insertos de la tapa (>= insert_diameter + margen)

//=============================================================================
// DERIVADOS
//=============================================================================

off_x = um790_mount_spacing_x/2;
off_y = um790_mount_spacing_y/2;

// PEDIDO POR EL USUARIO (2026-08-03): "desplazar los pilares que
// sujetan el UM790 para aproximar esta al panel posterior" — la
// placa quedaba 21,45mm corta respecto al panel trasero (confirmado
// por el usuario con la placa real montada, ~2cm de hueco). Se
// desplaza hacia atrás (+Y): los 4 postes (posts.scad), las islas de
// apoyo bajo ellos (base.scad) y la posición de referencia de la
// placa (um790_pos, assembly_positions.scad) — deja ~3,45mm de hueco
// restante hasta el panel, razonable para tolerancia y el grosor de
// los conectores. NO afecta a los nervios/marco exterior de la
// bandeja (siguen en su sitio, estructura distinta).
um790_post_y_offset = 18.0;

//=============================================================================
// NERVIOS
//=============================================================================

rib_width  = 3.0;
rib_height = 5.0;

//=============================================================================
// VENTILACIÓN
//=============================================================================

// PEDIDO POR EL USUARIO (2026-08-03): el suelo debe ser una rejilla
// en su práctica totalidad, para recoger más caudal de aire externo.
// Antes: 12 mm de margen por lado (dejaba 132x138,4 mm de rejilla
// sobre 156x162,4 mm de suelo). Ahora: 3 mm — el mínimo razonable
// para que el borde del suelo siga teniendo algo de material sólido
// donde apoyan las paredes, sin restar apenas superficie de rejilla.
bottom_grill_margin = 3.0;

// top_grill_margin — CORREGIDO (2026-08-03, aviso del usuario: "no
// se ve ningún agujero cuadrado, solo las tiras del ventilador"): con
// 16 mm, la zona de rejilla (124x130 mm) quedaba MÁS PEQUEÑA que la
// zona de exclusión del ventilador (136x136 mm, ver topVentCut() en
// top.scad) — la exclusión se comía la rejilla entera, no quedaba
// ningún hueco cuadrado real, solo se veían las tiras del protector
// de dedos del ventilador. Bajado a 6 mm (deja justo un anillo de
// huecos cuadrados alrededor del ventilador — el propio ventilador ya
// ocupa la mayor parte del área de ventilación disponible).
top_grill_margin = 6.0;

vent_slot_width  = 4.0;
vent_slot_length = 40.0;
vent_spacing     = 8.0;

//=============================================================================
// VENTILADOR SUPERIOR
//=============================================================================

fan_size       = 120.0;
fan_thickness  = 15.0;
fan_hole_pitch = 105.0;

//=============================================================================
// PANEL FRONTAL
//=============================================================================

front_panel_thickness = 3.0;

// Marco elevado en la cara frontal de los paneles NFC/inferior — PEDIDO
// POR EL USUARIO (2026-08-03, foto de referencia de la Steam Machine
// original: "profundidad de unos 5mm" en el borde del panel frontal).
// Puramente AÑADIDO hacia fuera (no toca front_panel_thickness, que
// la pared ya impresa usa para calcular dónde reculan sus imanes y
// tornillos — cambiar ese valor habría desalineado la pieza real ya
// fabricada). Con 2mm de bisel + 3mm de grosor base = ~5mm de
// profundidad visible en el borde, igual que en la foto.
front_bezel_depth  = 2.0;  // ESTIMADO — cuánto sobresale el marco hacia fuera
front_bezel_border  = 4.0;  // ESTIMADO — anchura visible del marco

power_button_diameter = 8.0;

//=============================================================================
// BARRA LED
//=============================================================================

led_bar_width  = 110.0;
led_bar_strip_width = 10.0;              // Dato real proporcionado por el usuario (tira LED)
led_bar_margin       = 1.0;              // Dato real confirmado por el usuario (2026-08-03)
led_bar_height = led_bar_strip_width + 2*led_bar_margin;  // Antes: 8.0 (estimado). Actualizado con dato real.
led_bar_depth  = 3.0;

//=============================================================================
// PANEL NFC
//=============================================================================

// nfc_panel_width — CORREGIDO (2026-08-03): el valor anterior (70,0)
// no llegaba a los imanes de las paredes laterales. Los imanes están
// embebidos en la pared, con su cara accesible en la cara interior de
// la pared (X = ±(case_width/2 - wall_thickness) = ±75) — el panel
// debe llegar exactamente ahí para apoyar sobre ellos.
// docs/02_Mechanical_Layout.md, sección 3, Panel NFC: "Ocupará
// prácticamente todo el ancho frontal."
// PEDIDO POR EL USUARIO (2026-08-03): "Los paneles inferior y
// exterior no tienen el mismo ancho" — el panel inferior ya tenía
// +1mm de sobredimensionado (lower_panel_width_oversize, para
// compensar la merma de impresión FDM, confirmado con una impresión
// real) que este panel no tenía. Igualado a 151mm para que ambos
// coincidan.
//
// AJUSTADO (2026-08-16, confirmado con probeta impresa real): a
// 151mm, el panel real medía 150mm (1mm de merma) — pero el hueco
// interior real del chasis medía solo 149mm (también con merma
// propia), así que el panel real quedaba MÁS ANCHO que el hueco.
// Una segunda probeta a 149mm de diseño salió en 149mm real (0mm de
// merma esta vez — la merma no es constante entre impresiones).
// Ajustado a 149mm, confirmado por el usuario tras la prueba física.
nfc_panel_width  = 149.0;  // antes 151,0 — confirmado con probeta real (ver historial arriba)

// Ancho del panel trasero — mismo criterio que nfc_panel_width y
// lower_panel_width_oversize, confirmado con probeta real (2026-08-16):
// el hueco interior real del chasis mide 149mm, no 150mm. Definido
// aquí (no en rear_panel.scad) para que probeta_panel_trasero.scad
// pueda reutilizar el mismo valor sin depender de un `use` a ese
// archivo (las variables no se exponen con `use`, solo los módulos).
rear_panel_width = case_width - 2*wall_thickness - 1.0;  // 149mm — antes 150mm

// Ventana funcional del tag NFC (más pequeña, centrada en el panel).
// Dato real confirmado por el usuario (2026-08-03).
nfc_window_width  = 60.0;
nfc_window_height = 40.0;

// nfc_panel_height — MAXIMIZADA a costa de dejar el panel inferior
// fijo en su tamaño mínimo imprescindible (petición del usuario).
// Antes: 70.0 (valor original, sin relación con el resto de zonas).
//
// Derivación (ver openscad/reference/components/assembly_positions.scad
// para el cálculo completo, y docs/Virtual_Assembly_Report.md):
//   1. Envolvente del clúster inferior (pulsador + OLED + USB doble),
//      con front_cluster_z = 19 mm: Z 1,5 - 36,5 mm.
//   2. Panel inferior fijo mínimo = envolvente + 3 mm de margen = 0-39,5 mm.
//   3. Barra LED (led_bar_height, dato real) justo encima: 39,5-51,5 mm.
//   4. Todo lo que queda hasta nfc_panel_margin_top, para el panel NFC:
//      shell_height - 51,5 - 12 = 148 - 51,5 - 12 = 84,5 mm.
//
// RECALCULADO (2026-08-03): usaba case_height (152) antes de que el
// usuario confirmara que las patas son externas y de 148 mm de
// cascarón (shell_height, ver 00_parametros.scad). Valor anterior:
// 88.5 (dejaba el panel NFC solapado 4 mm con la barra LED — lo
// detectó front_panel_zones_consistent en
// assembly_positions.scad).
// AJUSTADO (2026-08-17, medidas reales del usuario): "el espacio
// total de la altura interior del chasis es de 145mm, y los paneles
// miden 50mm el inferior y 96mm el superior... le quitaría 2mm de
// altura [al panel superior]" — la suma real (146mm) superaba el
// interior real (145mm) en 1mm. Reducido 2mm (96,5 → 94,5) para
// dejar margen de seguridad. El borde inferior del panel se mantiene
// fijo (sigue conectando igual con el panel inferior); el recorte es
// por arriba. Verificado: imanes (nfc_magnet_z_low/high) y hueco del
// tag NFC (nfc_tag_pocket_z) son valores absolutos fijos, no
// dependen de esta altura — siguen intactos.
nfc_panel_height = 94.5;  // antes 96.5

nfc_panel_depth  = 3.0;

//=============================================================================
// LECTOR NFC
//=============================================================================

nfc_reader_width  = 60.0;
nfc_reader_height = 40.0;
nfc_reader_depth  = 10.0;

//=============================================================================
// HUB USB (CJMCU-204)
//=============================================================================

// FALLO CORREGIDO (2026-08-15, aviso del usuario con fotos del hub
// montado en la pared real): la separación VERTICAL entre postes
// (eje Z en la pared — ver hubMountBosses() en walls.scad) estaba
// mal, calculaba 36,1mm entre los postes de arriba y abajo, cuando
// la separación real es 21mm (los dos postes de abajo, ya
// atornillados en la pieza real, estaban bien; los de arriba no).
// La separación horizontal (36,1mm, entre columnas de USB) es
// correcta, confirmada por el usuario.
//
// USB_HUB_WIDTH define TAMBIÉN el tamaño físico exterior de la
// placa (usado en hub_usb.scad para el cuerpo/keepout) — no se debe
// tocar solo para ajustar la separación de postes, o se encogería
// la placa entera por error. La separación de postes en el eje
// vertical se ajusta con un inset distinto en hubMountBosses() y
// hubUsbMountHoles() (usb_hub_mount_inset_z), no aquí.
usb_hub_width  = 44.1;
usb_hub_depth  = 44.1;
usb_hub_height = 12.0;

usb_hub_mount_hole = 3.0;
usb_hub_mount_inset_z = 11.55;  // separación vertical real entre postes = 21mm (44.1/2 - 11.55 = 10.5, x2 = 21)
usb_hub_mount_inset_y = 4.0;    // separación horizontal = 36.1mm, sin cambios (confirmada correcta por el usuario)

// Mediremos estas distancias directamente del STL
usb_port_pitch_x = 0;
usb_port_pitch_y = 0;

//=============================================================================
// ESP32
//=============================================================================

esp32_width  = 51.0;
esp32_depth  = 28.0;
esp32_height = 13.0;

//=============================================================================
// PLACA ADAPTADORA ESP32
//=============================================================================

esp32_board_width  = 76.0;
esp32_board_depth  = 76.0;
esp32_board_height = 15.0;

//=============================================================================
// IMANES
//=============================================================================

magnet_diameter = 8.0;
magnet_height   = 3.0;
magnet_clearance = 0.15;  // holgura, según docs/DESIGN_RULES.md ("Imanes: 0.15 mm")

//=============================================================================
// TORNILLERÍA
//=============================================================================

mount_hole = 3.4;

//=============================================================================
// COMPATIBILIDAD CON VERSIONES ANTERIORES
//=============================================================================

pcb_x = pcb_width;
pcb_y = pcb_depth;

hole_dist_x = um790_mount_spacing_x;
hole_dist_y = um790_mount_spacing_y;

standoff_height = um790_post_height;
standoff_dia    = um790_post_diameter;

insert_dia = insert_diameter;

base_thickness = tray_thickness;

//=============================================================================
// ENSAMBLAJE VIRTUAL V1 — PARÁMETROS ADICIONALES
//=============================================================================
//
// Sección añadida para openscad/reference/virtual_assembly_v1.scad
// y sus módulos en openscad/reference/components/.
//
// Regla: SOLO se añaden parámetros nuevos. No se modifica ni se
// elimina ningún valor ya existente en este archivo, para no
// alterar piezas ya construidas (bandeja, chasis, paneles).
//
// Los valores marcados "Estimado" no proceden de una medición
// directa del componente físico y deberán verificarse antes de
// diseñar piezas imprimibles definitivas.
//
//=============================================================================

//-----------------------------------------------------------------------
// UM790 Pro — disipador, IO trasera, separadores
//-----------------------------------------------------------------------

// Altura de separadores — CONFIRMADA por el usuario para el
// ensamblaje virtual v1 (2026-08-03).
//
// NOTA — sigue habiendo otros dos valores en el proyecto que deben
// reconciliarse antes del diseño definitivo del chasis (fuera del
// alcance de este ensamblaje virtual, que solo verifica; no modifica
// piezas ya construidas ni el DIM aprobado):
//   - openscad/parts/01_bandeja/posts.scad (bandeja física ya construida): 6 mm
//   - docs/02_Mechanical_Layout.md (DIM v1.0, Approved):                   8 mm
//
// A 20 mm, combinado con el reposicionamiento en X del pulsador y el
// USB frontal (también confirmado, ver assembly_positions.scad), la
// PCB, el disipador y los 4 postes de anclaje quedan libres del
// pulsador y del USB frontal: 28/28 pares sin colisión.
// Ver docs/Virtual_Assembly_Report.md.
um790_standoff_height = 20.0;

um790_cooler_width  = 88.0;   // Estimado (openscad/reference/um790_reference.scad)
um790_cooler_depth  = 88.0;   // Estimado
um790_cooler_height = 26.0;   // Estimado

um790_rearIO_width  = 90.0;   // Estimado, ancho del bloque de conectores traseros
um790_rearIO_height = 20.0;   // Estimado, altura del conjunto de puertos traseros
um790_rearIO_depth  =
    case_depth/2 - wall_thickness - pcb_depth/2 - um790_post_y_offset;   // Calculado: hueco REAL hasta el panel trasero, descontado el desplazamiento de los postes (antes 21,45mm, ahora ~3,45mm)

um790_cable_margin = 15.0;    // Margen del volumen de seguridad de cableado alrededor de la PCB

//-----------------------------------------------------------------------
// Ventilador Noctua NF-A12x15 (fan_size / fan_thickness / fan_hole_pitch ya existían)
//-----------------------------------------------------------------------

fan_frame_corner_r = 12.0;   // Estimado, radio de esquina del marco del ventilador
fan_hub_diameter    = 40.0;  // Estimado, solo visual

//-----------------------------------------------------------------------
// ESP32 Terminal Adapter (dimensiones reales de la placa adaptadora)
//-----------------------------------------------------------------------

esp32_adapter_width          = 78.0;
esp32_adapter_depth          = 63.0;
esp32_adapter_thickness      = 1.6;
esp32_adapter_hole_spacing_x = 73.0;
esp32_adapter_hole_spacing_y = 58.0;
esp32_adapter_hole_diameter  = 3.2;   // Holgura para M3

esp32_adapter_component_height = 18.0; // Estimado: ESP32 + regletas + cableado por encima de la placa

//-----------------------------------------------------------------------
// RC522 (nfc_reader_* ya existían) — soporte
//-----------------------------------------------------------------------

rc522_bracket_thickness = 3.0;   // Estimado, brazos de soporte a los laterales del chasis
rc522_bracket_width     = 10.0;  // Estimado, ancho de cada brazo

//-----------------------------------------------------------------------
// Hub USB CJMCU-204 (usb_hub_* ya existían) — sin parámetros nuevos
//-----------------------------------------------------------------------

//-----------------------------------------------------------------------
// OLED 27x27 mm
//-----------------------------------------------------------------------

oled_module_width      = 27.0;
oled_module_height     = 27.0;
oled_module_thickness  = 1.5;   // Estimado, cristal + PCB
oled_module_pin_height = 6.0;   // Estimado, pines/soldadura por detrás del módulo

//-----------------------------------------------------------------------
// Pulsador M16 x 55 mm
//-----------------------------------------------------------------------

// PEDIDO POR EL USUARIO (2026-08-03, tras probar la impresión real):
// "el pulsador de encendido no acaba de entrar, habría que darle un
// poco más de margen". Antes 16.0 (la medida exacta de la rosca, sin
// ninguna holgura) — con la merma típica de impresión FDM, un
// agujero justo a medida suele quedar más pequeño de lo real.
// Aumentado a 16.5 (0,5mm de holgura). Si sigue sin entrar bien,
// puede subirse más.
pushbutton_thread_diameter = 16.5;
pushbutton_cap_diameter    = 19.5;  // Estimado, diámetro del embellecedor visible en el panel
pushbutton_total_length    = 55.0;  // Dato real proporcionado (rosca + cuerpo del mecanismo)

//-----------------------------------------------------------------------
// USB empotrable frontal — unidad DOBLE de un solo cuerpo (2 puertos
// USB-A en una sola brida/rosca, conectada al HUB mediante dos cables
// flexibles con conector USB-A macho), según el componente real
// localizado por el usuario. Sustituye al diseño anterior de dos
// unidades independientes (usb_front_pair_spacing, obsoleto).
//-----------------------------------------------------------------------

usb_front_hole_diameter   = 30.0;  // Dato real confirmado por el usuario (2026-08-03) — corregido de 29 a 30
usb_front_flange_diameter = 35.0;  // Estimado, brida/rosca (algo mayor que la versión de un puerto, aloja 2 USB-A)
usb_front_body_length     = 30.0;  // Dato real confirmado por el usuario (2026-08-03). Antes: 22.0 (estimado)
usb_front_cable_diameter  = 5.0;   // Estimado, cada uno de los 2 cables flexibles
usb_front_cable_length    = 120.0; // Estimado, longitud de cable disponible hasta el conector USB-A macho

// Parámetro obsoleto (diseño anterior, 2 unidades independientes).
// Se mantiene documentado por si se recupera esa opción más adelante.
// usb_front_pair_spacing = 34.0;

//=============================================================================
// FILOSOFÍA DEL PROYECTO
//=============================================================================
//
// - Chasis principal fijo.
// - Panel trasero desmontable.
// - Panel superior desmontable.
// - Panel NFC intercambiable.
// - Módulo USB + pulsador independiente y sustituible.
// - Soporte ESP32 desmontable.
// - Toda pieza deberá obtener sus dimensiones EXCLUSIVAMENTE
//   desde este archivo.
//
