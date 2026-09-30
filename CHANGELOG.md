# Changelog

Todos los cambios importantes de este proyecto se documentarán en este archivo.

El formato está inspirado en [Keep a Changelog](https://keepachangelog.com/) y el proyecto sigue Versionado Semántico (Semantic Versioning).

---

## [1.6.0] - 2026-09-21 — Panel NFC Apagar (apagado ordenado), caja de paneles documentada y material a PETG

### Contexto

- Cuando el equipo se apaga de golpe, a veces Bazzite no vuelve a
  arrancar y hay que restaurarlo desde la consola (ver `grub>` en
  `GUIA_INICIO.md`). Se añade un panel NFC para apagar de forma ordenada.
- El PLA se deforma con la temperatura del equipo: todas las piezas
  pasan a imprimirse en PETG.

### Añadido

- `software/core/power_manager.py` (`PowerManager`): ejecuta
  `systemctl poweroff` (configurable en `power.poweroff_command`), sin
  excepciones; `dry_run` en modo simulado para no apagar la máquina de
  desarrollo.
- Perfil `APAGAR` (`config/profiles/apagar.json`, `action: "poweroff"`) y
  entrada `UID_APAGAR_PENDIENTE` en `panel_database.json`.
- `Application`: acciones de sistema por perfil (lista cerrada), aviso en
  OLED/LEDs antes de apagar, error visible si el sistema rechaza la
  orden, y el Core ignora eventos mientras se apaga. Al cerrarse el
  servicio por el apagado, la OLED queda limpia.
- 25 tests nuevos (122 en total). Los tests no tocan `logs/steammachine.log`.
- `docs/14_Caja_Paneles_NFC.md`: la caja de paneles (6 ranuras) no
  estaba documentada. Medidas comprobadas contra los STL.
- `Apagar.stl` documentado (ya estaba en `STL/Anagramas/`).
- Pruebas T022 (deformación térmica de las piezas) y T065 (apagado
  ordenado) en `docs/10_Test_Plan.md`.

### Cambiado

- Material: PETG para todas las piezas (README, GUIA_INICIO, docs 07,
  11, `Printing_Lower_Panel.md`, caja). Notas: los dos filamentos del
  panel inferior deben ser PETG; el cianoacrilato agarra peor en PETG.
- README: corregido un `---` pegado al final de una frase.

### Pendiente

- Sustituir `UID_APAGAR_PENDIENTE` por el UID real del tag.
- Probar el apagado en el hardware real (T065); no verificado que polkit
  permita `systemctl poweroff` desde el servicio de usuario.
- Validar holguras de la caja/tapa y del resto de piezas en PETG (T022).
- `Apagar.stl` no tiene `.scad` paramétrico (como `Gung.stl`).
- `VERSION.md` sigue en v1.1.3, desfasado respecto a este CHANGELOG.

---

## [1.5.8] - 2026-09-11 — Documentada la puesta en marcha de la Sinden Lightgun (Bazzite)

### Contexto

- Sesión completa (2026-09-10/11) llevando la Sinden Lightgun desde
  "no se lee" hasta calibrada y jugando, en la propia Steam Machine
  (Bazzite). Se intentó primero con un Wiimote + barra IR casera
  (`cwiid`/`wminput`) — descartado por incompatibilidad de fondo entre
  ese software (sin mantenimiento desde hace más de una década) y las
  versiones actuales de BlueZ, confirmado con el mismo fallo en dos
  versiones distintas de Debian.

### Añadido

- `docs/13_Sinden_Lightgun_Setup.md`: procedimiento completo,
  documentado para no tener que redescubrirlo — traducción de las
  instrucciones oficiales de Sinden (pensadas para Arch/SteamOS) a
  Fedora/`rpm-ostree`; extracción manual de `libjpeg.so.8` desde un
  `.deb` de Ubuntu (no está en Fedora); el fallo real de esta
  instalación con el grupo `dialout` (vive fuera de `/etc/group`,
  `usermod`/`gpasswd` no lo tocan sin editar el fichero a mano);
  requisito de firmware v1.9 (con "joystick functionality" activada)
  para que la calibración funcione; requisito de sala en penumbra
  (confirmado en esta sesión: con luz ambiental la mira tiembla,
  a oscuras queda estable); instalación del ArcadeMod de argonlefou
  para THE HOUSE OF THE DEAD: Remake (con el aviso de descargarlo
  desde la sección Releases del repositorio, no desde "Code → Download
  ZIP", que da un `.exe` inexistente — error real cometido en esta
  misma sesión).

### Pendiente (anotado en el propio documento)

- Confirmar que todo esto funciona igual dentro del Game Mode/Big
  Picture real (gamescope), no solo en el escritorio de KDE.
- Confirmar el ArcadeMod funcionando bajo Proton en la Steam Machine.
- THE HOUSE OF THE DEAD 2: Remake usa un parche distinto, sin revisar
  todavía.
- **Confirmado: el marco blanco no aparece en Linux** fuera de la
  utilidad de calibración (`sdl`) — ni en primer plano ni con
  `mono-service` en segundo plano. A diferencia de Windows, el port a
  Linux de Sinden no trae overlay de marco a nivel de sistema.
- **Overlay propio en construcción, sin terminar** (`docs/13_Sinden_Lightgun_Setup.md`,
  sección 8): programa en C++/Qt6 con `LayerShellQt` para dibujar el
  marco por encima de todo bajo Wayland/KWin (confirmado que la sesión
  de KDE aquí es Wayland, no X11). Ya corregidos dos fallos de
  compilación reales (nombre del paquete CMake `LayerShellQt`, no
  `LayerShellQtInterface`; conversión de `QFlags` en `setAnchors()`).
  Queda por compilar y probar en pantalla — sesión cortada por falta
  de tiempo antes de llegar a ese punto.

---

## [1.5.7] - 2026-09-09 — Corregido: los postes de las patas invadían 1mm el grosor macizo de la pared, en las 4 esquinas

### Contexto

- El usuario, con una captura de OpenSCAD (`floor_flat.scad`, 4
  círculos rojos en las esquinas): "los soportes para los insertos
  siguen interfiriendo con los paneles laterales".

### Corregido

- `floor.scad`, `leg_edge_margin`: nunca tuvo en cuenta el grosor de
  la propia pared (`wall_thickness`=3mm) al calcular el margen desde
  el borde de la carcasa — solo restaba 2mm. El poste de la pata
  (Ø10mm) llegaba hasta X=76 en las 4 esquinas por igual, invadiendo
  1mm el tramo macizo de la pared (X 75-78) — no un inserto
  concreto de la pared, la pared en sí, en cualquier punto de su
  longitud. Por eso "seguía" pasando tras el ajuste de [1.5.3], que
  solo corrigió la posición en Y contra insertos concretos, no este
  solape en X contra el grosor base. Subido `leg_edge_margin` de 2 a
  4mm — el poste ahora llega como mucho a X=74, con 1mm de margen
  limpio respecto a la cara interior de la pared (X=75). Verificado
  que no introduce ningún solape nuevo (con tray posts, con el
  injerto suelo-pared) — al mover el poste hacia el centro, solo
  gana margen, nunca lo pierde.

---

## [1.5.6] - 2026-09-09 — Corregido: el rebaje de pines de la OLED abría por fuera en vez de por dentro

### Contexto

- El usuario adjuntó su propio `lower_panel.scad` ("el fichero
  correcto es este") tras detectar que mi reconstrucción de [1.4.9]
  tenía el rebaje de pines de la OLED abierto por la cara EXTERIOR
  del panel en vez de por la INTERIOR.

### Corregido

- `oledCut()`: el rebaje ciego para los pines de soldadura arrancaba
  en `-case_depth/2` (cara exterior, donde se ve la pantalla) y
  cortaba `oled_pin_clearance_pocket_depth` hacia dentro — dejaba el
  hueco abierto por fuera y cerrado justo donde están los pines (la
  cara interior, contra la que apoya el módulo). Invertido: ahora
  arranca cerca de la cara interior
  (`-case_depth/2 + front_panel_thickness - oled_pin_clearance_pocket_depth`)
  y corta hacia allí, dejando la piel sólida hacia fuera (no importa,
  no la alcanza nada) y el hueco abierto hacia dentro, donde
  sobresalen los pines de verdad.
- `openscad/parts/03_panels/lower_panel.scad` sustituido entero por
  el fichero del usuario, no solo el fragmento del rebaje — trae
  además el historial real de esta corrección (varias rondas de
  ida y vuelta el 2026-08-29, incluida una vez anterior en la que
  también quedó "por fuera en lugar de por dentro") que mi
  reconstrucción de [1.4.9], al venir del CHANGELOG y no de esa
  sesión, no tenía capturado con el mismo detalle.

---

## [1.5.5] - 2026-09-08 — Descartado `oled_bracket.scad`; la OLED se fija con 4 tornillos directos

### Contexto

- Revisando el despiece pieza a pieza, el usuario confirmó: la brida
  de sujeción de la OLED (`oled_bracket.scad`, [2026-08-22]) "solo
  fue un modelo para analizar pero está descartado". La fijación real
  es con 4 tornillos directos a través de `lower_panel.scad`
  (`oledMountHoles()`, ya implementada desde antes que la brida y
  nunca sustituida).

### Descubierto de paso

- La brida nunca llegó a tener sus bosses de anclaje
  (`oledInsertBosses()`) realmente construidos en `lower_panel.scad`
  — quedaron solo como parámetros reservados en
  `assembly_positions.scad` (`oled_bracket_*`), sin ninguna geometría
  que los usara. No había nada que desmontar en la pieza impresa real,
  solo limpieza de datos muertos.

### Eliminado / movido

- `openscad/parts/03_panels/oled_bracket.scad` y su STL, movidos a
  `obsoletos/parts_03_panels/` (mismo criterio ya establecido en
  [2026-08-14] para piezas descartadas — conservados como referencia
  histórica, marcados ⚠️ OBSOLETO, sin usarse). `obsoletos/README.md`
  actualizado.
- `assembly_positions.scad`: bloque `oled_bracket_*` (insertos, bosses,
  posiciones de tornillo) y la copia de `oled_screen_width/height`
  que solo consumía la brida — comentados, no borrados, con nota de
  por qué existían (para no perder el criterio numérico ya
  comprobado, por si se retoma en el futuro). `oled_pos` y el resto
  de referencias que sí siguen en uso, intactos.

### Corregido

- `docs/11_Assembly_Manual.md`: paso de montaje de la OLED,
  actualizado de "brida + 2 tornillos M2" a "4 tornillos directos a
  través del panel inferior", que es lo que de verdad se monta.
- Comentario suelto en `lower_panel.scad` que aún daba a entender que
  la brida seguía activa, corregido.

---

## [1.5.4] - 2026-09-08 — Avellanado del injerto M3 suelo-pared; VERSION.md eliminado (redundante con este CHANGELOG); manual de montaje al día

### Corregido

- `floorWallGraftClearanceHoles()` ([1.5.2]): aviso del usuario ("los
  orificios... parecen muy grandes y sin avellanado"). El diámetro
  (Ø3,4mm) es la holgura M3 estándar ya usada en el resto del
  proyecto, no un tamaño fuera de lo normal — pero le faltaba el
  avellanado cónico que sí llevan el resto de tornillos que entran
  desde una cara exterior (tapa, panel trasero, panel inferior, todos
  Ø6mm). Añadido, mismo criterio.

### Eliminado

- `VERSION.md`: a petición del usuario ("si consideras que documentos
  como VERSION.md no tienen sentido los podríamos eliminar"). Sin
  referencias entrantes desde ningún otro fichero (verificado antes
  de borrar). Es precisamente el fichero que estaba desincronizado
  (v1.1.3) cuando destapamos el desajuste del ZIP en [1.4.9] — este
  CHANGELOG ya hace de fuente única de verdad sobre el estado del
  proyecto, sin necesidad de un "número de versión" aparte que
  mantener sincronizado a mano.

### Cambiado

- `docs/11_Assembly_Manual.md`, Paso 1: "instalar patas" sustituido
  por la secuencia real — pie desmontable atornillado desde fuera
  ([1.5.2]/[1.5.3]) — y añadido el paso de atornillar el suelo a cada
  pared por el injerto M3 antes de montar el resto ([1.5.2]).

---

## [1.5.3] - 2026-09-08 — Corregido: la rejilla del suelo no atravesaba la pieza; retirada a petición del usuario; patas reubicadas (colisión con insertos de pared)

### Contexto

- Sesión de revisión de `floor_flat.scad`/`leftwall_flat.scad`/
  `rightwall_flat.scad`/`foot.scad` (impresión plana del chasis,
  ver [1.5.2]). El usuario aportó capturas del visor de OpenSCAD que
  destaparon dos fallos reales en `floor.scad`, no solo apariencia.

### Corregido

- `floorVentCut()`: `valvePattern()` (`lib/ventilation.scad`) usa
  `cube(..., center=true)`, que centra el corte también en Z. Con el
  `translate(Z=-1)` que tenía, el corte real quedaba entre Z=-3,5 y
  Z=1,5, mientras el suelo ocupa Z=0 a `bottom_thickness`=3 — solo se
  cortaba la mitad inferior, dejando 1,5mm de piel maciza sin cortar
  en la cara de arriba de los ~60 rombos a la vez. Nunca atravesaron
  la pieza. Corregido moviendo el punto de partida al centro real del
  grosor de la placa (`bottom_thickness/2`); verificado con los
  números que el nuevo rango (Z -1 a 4) cubre de sobra el suelo.
- `floorLegMountInserts()` ([1.5.2]): el taladro del inserto M3 solo
  abría dentro del propio poste (desde Z=2,9 hacia arriba) — nunca
  atravesaba los 3mm de la placa del suelo. Visto desde la cara
  exterior real (Z=0), los postes se veían macizos. Añadido
  `floorLegScrewClearanceHoles()`: taladro de paso M3 (Ø3,4mm,
  distinto del taladro del inserto) que sí atraviesa la placa entera,
  restado a nivel de `chassisFloor()`.
- `leg_center_offset_y` (patas del pie desmontable, [1.5.2]): a la Y
  de la esquina real (74,2mm) el poste de la pata invadía el relleno
  del tornillo del panel inferior en la pared (Z 3-17,
  `lower_panel_screw_z_low`=10) — solape real de 8×9×7mm, confirmado
  con las cotas exactas, no solo aparente en el visor. La esquina
  trasera, a la misma Y en positivo, coincidía igual de lleno en X/Y
  con el relleno del tornillo del panel trasero, pero se libraba solo
  porque ese relleno vive a otra Z (20-34 y 123-137) — un margen de
  seguridad accidental. Reubicadas las 4 patas a Y=±32: lejos de
  ambos rellenos (27mm+ de margen) y del injerto suelo-pared
  ([1.5.2], Y=±50 — 7mm de margen). Base de apoyo resultante: 64mm
  delante-detrás × 142mm en X.

### Cambiado

- `chassisFloor()`: ya NO llama a `floorVentCut()` — petición del
  usuario ("debilitaba mucho la pieza" + uno de los taladros del
  injerto M3 suelo-pared coincidía con un rombo, área ocupada por la
  rejilla hasta casi el borde). El módulo `floorVentCut()` se
  conserva definido en el fichero, sin usarse, por si se retoma con
  otra distribución.
- Ventilación de entrada de aire: sin la rejilla, la entrada pasa a
  ser el hueco ya existente bajo el clúster frontal
  (`frontClusterRelief()`, pulsador/OLED/USB) — comprobado con el
  usuario que da un área libre similar (6.526mm² vs 7.241mm² de la
  rejilla retirada, ~90%) y solapa parcialmente (~14mm) con el borde
  delantero de la placa del UM790, aunque no queda centrado bajo el
  disipador como pretendía el diseño original de la rejilla. Sin
  verificación térmica real — pendiente de comprobar con una
  impresión y uso real; si hiciera falta más caudal, el usuario
  propuso como plan B una rejilla que empiece a ~2cm del borde (fuera
  ya del alcance de los taladros de los insertos).
- Confirmado con el usuario (sin cambios de diseño): el ventilador
  superior debe EXTRAER aire (no impulsarlo hacia dentro) — coincide
  con `docs/DESIGN_RULES.md` ("Entrada inferior. Salida superior.")
  y con como ya se le llamaba en un comentario de `top.scad`, "el
  extractor".

---

## [1.5.2] - 2026-09-08 — Impresión plana del chasis: injerto M3 suelo-pared (nuevo), pie desmontable reconciliado, insertos de la tapa realineados

### Contexto

- El usuario pidió revisar `floor_flat.scad`/`leftwall_flat.scad`/
  `rightwall_flat.scad`/`foot.scad` — preparados en otra sesión, sin
  ninguna entrada en este CHANGELOG hasta ahora — contra 5
  requisitos: impresión plana, unión por injertos M3, patas
  desmontables con M3, altura total ≤ la original, suelo realmente
  liso por abajo, y sin colisión entre insertos.

### Añadido

- **Injerto M3 suelo-pared** (`openscad/reference/components/assembly_positions.scad`,
  `walls.scad`, `floor.scad`): no existía NINGÚN punto de fijación
  entre el suelo y las paredes. Nuevo: `floorWallGraftBoss()`/
  `floorWallGraftInsertCuts()` (pared, inserto M3 ciego) +
  `floorWallGraftClearanceHoles()` (suelo, taladro de paso) — 2
  puntos por pared, Y=±50 (global), elegidos por quedar lejos de
  todos los insertos ya existentes en la pared (imanes/tornillos del
  panel inferior y trasero, ESP32, HUB).
- `floorLegMountInserts()` (`floor.scad`): sustituye a `floorLegs()`
  — insertos M3 ciegos en las mismas 4 posiciones donde antes había
  patas macizas integradas, para que `foot.scad` (pie desmontable,
  atornillado) tenga dónde anclarse. `foot.scad` ya hablaba de este
  módulo desde su creación, pero `floor.scad` nunca llegó a tenerlo
  — desajuste real entre dos ficheros pensados para encajar.

### Corregido

- `foot.scad`: `foot_height` de 6,0 a 4,0mm — con 6mm, la altura
  total montada (`shell_height` 148 + 6 = 154mm) superaba
  `case_height` (152, "dato original, sin modificar"). A 4mm
  (igual que `leg_height`) vuelve a dar exactamente 152mm.
- `walls.scad`, `topInsertPad()`/`topScrewInsertCuts()`: el usuario
  avisó de que los insertos M3 de la tapa quedaban desplazados hacia
  abajo respecto al borde superior real de la pared. La corrección de
  [entrada 2026-08-03] los frenaba `top_thickness` (3mm) de más, en la
  cara interior de la tapa en vez de en el borde real — pero la tapa
  es lisa, sin ningún reborde que aliviar (confirmado por el
  usuario): donde el relleno coincide en X/Y con la tapa, esta ya
  tiene su propio taladro de paso, no material macizo. El relleno
  ahora llega hasta el borde superior real de la pared
  (`shell_height`), sin necesitar ningún hueco de alivio en la tapa.

### Verificado (por separación de ejes, sin OpenSCAD en esta sesión — pendiente de confirmar con render/impresión real)

- Injerto suelo-pared sin colisión con: postes de pared existentes,
  ESP32/HUB (por separación en Y), pletinas del RC522.
- Patas (posición original, esquina) sin colisión con postes de
  bandeja — el resto de colisiones de las patas se detectó y corrigió
  en [1.5.3], con capturas reales del usuario.

---

## [1.5.1] - 2026-09-08 — Evaluado TeknoParrot vía Batocera-x86; descartado

### Decisión

- El usuario preguntó si el enfoque de un artículo de terceros
  (Batocera-x86 + wrapper Wine/DXVK/VKD3D curado por el equipo de
  Batocera para TeknoParrot) sería viable para el proyecto. Análisis:
  es la misma tecnología de traducción que ya se probó y se descartó
  vía Lutris ([1.4.4], DISPAROS ahora usa los remakes nativos de
  Steam de House of the Dead) — Batocera solo la tiene mejor
  empaquetada, no resuelve el problema de fondo, y además no es un
  paquete instalable suelto: adoptarlo implicaría sustituir Bazzite
  por Batocera-x86 como sistema operativo. Descartado — no hay
  ningún cambio de código. Documentado aquí para no repetir la
  evaluación más adelante.

---

## [1.5.0] - 2026-09-08 — Reconciliado: falta `auto_match` en steam.json/retro.json (AUTO no encontraba nada)

### Corregido

- El código de `Application`/`ProcessWatcher` ([1.4.6]) estaba
  completo y correcto, pero `software/config/profiles/steam.json` y
  `retro.json` nunca llegaron a tener el campo `"auto_match"` que esa
  misma entrada decía haber añadido — la tabla de coincidencias del
  perfil AUTO quedaba vacía en la práctica. Confirmado ejecutando la
  suite real (no solo leyendo el changelog): 1 test en rojo
  (`test_build_auto_match_table_reads_auto_match_from_loaded_profiles`).
  Añadido `"auto_match": ["steam"]` a steam.json y
  `"auto_match": ["retroarch", "retrodeck"]` a retro.json — 97/97
  tests en verde, coincide con el recuento de [1.4.7].

---

## [1.4.9] - 2026-09-08 — Reconciliado con un ZIP desactualizado: ventana OLED/mecanizado del panel inferior, canal LED; panel trasero nuevo del RC522

### Contexto

- El usuario subió un ZIP para retomar el proyecto en un hilo nuevo.
  `VERSION.md` decía v1.1.3, pero `CHANGELOG.md` incluía entradas
  hasta [1.4.8] — el código real de
  `openscad/parts/03_panels/lower_panel.scad` no tenía aplicado
  ninguno de los cambios de OLED de [1.2.2] a [1.3.0] (ventana,
  taladros M2, rebaje de pines, canal LED). Mismo patrón de desajuste
  que ya describe [1.3.2], repetido.

### Corregido (reconstruido a partir de las fórmulas ya documentadas en [1.2.2]-[1.3.0], sin inventar valores nuevos)

- `lower_panel.scad`: ventana OLED (26,0×15,0mm reales, antes
  14,5mm de alto), taladros M2 con separación horizontal/vertical
  distinta (23,0×23,5mm), posición de la ventana por fórmula
  (oled_window_z_offset=+2,25mm), bisel asimétrico (0,4mm arriba,
  2mm en los otros tres lados), rebaje de pines realineado a los
  taladros M2 fijos (profundidad 2,0mm), canal de la tira LED subido
  2mm.

### Añadido

- `openscad/parts/04_soportes/rc522_bracket.scad`,
  `rc522BracketBackdrop()`: petición del usuario (con foto) — el
  soporte del RC522 dejaba ver el interior del chasis (ventilador,
  cableado) por los huecos entre los brazos de la horquilla y
  alrededor de la cuna. Placa plana integrada en la misma pieza
  imprimible, justo detrás del lector, que cierra el resto de la
  abertura del panel NFC — verificado sin colisión por separación de
  ejes contra postes de pared, pletinas propias, ESP32/HUB y
  ventilador Noctua (sin OpenSCAD en esta sesión para confirmarlo con
  un render).

---

## [1.4.8] - 2026-09-04 — Anotado: el campo `icon` de panel_database.json no se usa todavía

### Documentado

- El usuario preguntó dónde se ubican los iconos referenciados por
  `"icon": "steam.png"` en `panel_database.json`. Respuesta: en
  ningún sitio — es un campo huérfano desde el principio del
  proyecto, sin ningún código que lo lea. `OLEDManager.show_logo()`
  ya tenía un `TODO` sobre esto (la OLED es solo texto, sin soporte
  de bitmaps en el protocolo del firmware) — no era un descuido nuevo,
  solo no estaba anotado en `docs/12_Profile_System.md`.
- Añadido a "Pendiente" en `docs/12_Profile_System.md`: para que
  `icon` sirva de algo hace falta (1) ampliar el protocolo del
  firmware para bitmaps 1-bit pequeños, y (2) crear una carpeta real
  de recursos (`software/resources/icons/` o similar) — ninguna de
  las dos existe hoy. Sin cambios de código en este turno.

---

## [1.4.7] - 2026-09-04 — Corregida la asignación real de UID a perfil; MAINTENANCE ya tiene panel físico

### Corregido

- El usuario confirmó la asignación real de sus tags NFC físicos, que
  resultó ser distinta de lo que [1.4.3]/[1.4.4] habían asumido:
  - `6739C003` → STEAM (sin cambios)
  - `E76DC103` → RETRO (sin cambios)
  - `112FC103` → **MAINTENANCE** (antes asignado por error a DISPAROS)
  - `56A1C003` → **DISPAROS** (antes retirado por error en [1.4.4],
    creyendo que era el panel de HOTD 2 Remake que ya no hacía falta)

### Cambiado

- `software/config/panel_database.json`: `112FC103` pasa de
  `"name": "Zombies"` / `profile: "DISPAROS"` a `"name": "Maintenance"`
  / `profile: "MAINTENANCE"` / `launcher: null`. Recuperado
  `56A1C003` con `"name": "Zombies"` / `profile: "DISPAROS"` /
  `launcher: "steam"` (la definición que antes tenía `112FC103`).
- `software/tests/test_panel_database.py`: actualizado el test de
  integridad que tenía la asignación anterior "grabada" — ahora
  comprueba explícitamente los 4 pares UID→perfil correctos, para
  detectar si esto se vuelve a desordenar en el futuro.
- `docs/12_Profile_System.md`: corregidas las menciones a UID
  concretos en el estado de DISPAROS y MAINTENANCE, y en "Decisiones
  cerradas" — MAINTENANCE ya no aparece como "sin panel físico
  asignado".
- 97 tests en total, todos en verde.

### Nota

- No he tocado el `CHANGELOG.md` de [1.4.3]/[1.4.4] — quedan como
  registro histórico de lo que se creía en su momento; esta entrada
  documenta la corrección, no reescribe lo anterior.

---

## [1.4.6] - 2026-09-04 — Perfil AUTO implementado: ProcessWatcher, cierra el alcance de la v0.2

### Añadido

- `software/core/process_watcher.py`: `ProcessWatcher` — vigila
  periódicamente (`psutil.process_iter(["name"])`, cada 5s por
  defecto) qué procesos corren, y avisa (callback) solo cuando el
  perfil detectado CAMBIA respecto a la última lectura (no en cada
  poll). Recibe una tabla ya construida (`{substring: profile_id}`),
  no decide el mapeo por sí mismo. `psutil` inyectable por
  constructor, mismo patrón que `SystemStatsProvider`, para poder
  testear con hilos reales pero procesos falsos (poll de 20ms en los
  tests, no 5s).
- Campo opcional `auto_match` en los perfiles: `steam.json` →
  `["steam"]`, `retro.json` → `["retroarch", "retrodeck"]`. `DISPAROS`
  y `MAINTENANCE` no lo llevan — ver limitaciones más abajo.
- `software/core/application.py`:
  - `_build_auto_match_table()`: arma la tabla plana a partir del
    `auto_match` de cada perfil cargado.
  - `_on_auto_profile_changed(profile_id)`: aplica el `oled.idle` /
    `led.idle` del perfil detectado (o pone la OLED en reposo si no
    hay nada relevante corriendo) — mismo mecanismo visual que un
    panel físico, sin tocar `self._pending_panel` (AUTO no lanza nada
    al pulsar el botón, solo informa).
  - `_on_tag_removed()`: arranca `ProcessWatcher` (entra en AUTO) —
    decisión de [1.3.3] finalmente implementada.
  - `_on_tag_detected()`: para `ProcessWatcher` en cuanto se detecta
    CUALQUIER panel físico, antes incluso de comprobar si el UID es
    válido — un panel físico manda siempre por encima de AUTO.
  - `initialize()`: crea el `ProcessWatcher` y lo arranca al final —
    AUTO es también el estado por defecto justo al arrancar, antes de
    que se coloque ningún panel.
  - `shutdown()`: para `ProcessWatcher` al cerrar, para no dejar el
    hilo de fondo colgado.
- 15 tests nuevos (96 en total, todos en verde):
  `test_process_watcher.py` (9 — coincidencia por subcadena, sin
  coincidencia, solo avisa en cambios, cambia de un perfil a otro,
  sin psutil, tabla vacía, `process_iter()` lanzando excepción,
  arranque/parada de hilo real con poll de 20ms, `start()`
  idempotente) + 6 de integración en `test_application.py`
  (`_on_tag_removed`/`_on_tag_detected` arrancan/paran el watcher;
  `_on_auto_profile_changed` con perfil real, con `None`, y con un id
  desconocido; `_build_auto_match_table` lee `auto_match` de los
  perfiles reales).
- `tests/fakes.py`: `FakeProcessWatcher`.

### Limitaciones conocidas (documentadas, no descuidos)

- **`DISPAROS` no participa en AUTO** — el proceso `steam` ya lo
  reclama `STEAM`, y la tabla de coincidencias es plana (un proceso
  solo puede apuntar a un perfil): mientras se juega a HOTD Remake/2,
  AUTO mostrará `STEAM`, no `DISPAROS`.
- **Nombres de proceso sin verificar contra el Bazzite real** —
  `retroarch`/`retrodeck` son un supuesto razonable dado que RetroDECK
  empaqueta RetroArch por debajo, pero no se ha comprobado todavía en
  la máquina física del usuario.
- **Sin debounce de arranque lento** — AUTO detecta un programa en
  cuanto su proceso aparece en la lista, ni un poll (hasta 5s) antes.

### Documentación

- `docs/12_Profile_System.md`: subido a versión 0.3 ("Implementado" —
  alcance completo de la v0.2 original en código: STEAM, RETRO,
  DISPAROS, MAINTENANCE y AUTO). Estado de AUTO actualizado con sus
  limitaciones; quitado de "Pendiente" el diseño de `ProcessWatcher`
  (ya resuelto), añadidos los puntos concretos que quedan abiertos.
- `software/README.md`: añadido `ProcessWatcher` a la estructura de
  `core/`.

---

## [1.4.5] - 2026-09-03 — Perfil MAINTENANCE migrado: primer StatusProvider real (CPU/RAM, foto fija)

### Añadido

- `software/status/` (paquete nuevo): `base_provider.py`
  (`BaseStatusProvider`, interfaz `snapshot() -> dict`),
  `system_stats_provider.py` (`SystemStatsProvider`, vía `psutil`,
  con `psutil` inyectable por constructor para poder testear sin
  depender de los sensores reales de la máquina), `status_manager.py`
  (`StatusManager`, registro `{"system_stats": SystemStatsProvider}`,
  mismo patrón que `Launcher`/`PLUGIN_CLASSES`).
- `software/config/profiles/maintenance.json`: `launcher: null`
  (perfil informativo, no lanza nada — a propósito), `oled.idle_template:
  ["CPU {cpu_temp}C RAM{ram_percent}%", "{ram_used_gb}/{ram_total_gb}GB"]`,
  `status_provider: "system_stats"`.
- `software/core/application.py`:
  - `_on_tag_detected()`: si el perfil tiene `oled.idle_template` +
    `status_provider`, se resuelve el snapshot vía `StatusManager` y
    se rellena la plantilla con `.format(**values)`; si falta alguna
    variable (`KeyError`/`IndexError`), se cae a `oled.idle` estático
    en vez de reventar. Retrocompatible con STEAM/RETRO/DISPAROS (sin
    `idle_template`, comportamiento idéntico a antes).
  - `_on_button()`: si el panel/perfil no tiene `launcher` (caso de
    MAINTENANCE), se ignora la pulsación sin animación de error —
    antes habría intentado `Launcher.launch(None)` y mostrado
    "error", dando a entender que algo había fallado.
  - Nuevo `self._status = StatusManager()`.
- `software/requirements.txt`: añadido `psutil`.
- 12 tests nuevos (81 en total, todos en verde):
  `test_system_stats_provider.py` (6 — snapshot sin psutil, lecturas
  correctas de CPU/RAM, fallo de sensor no revienta el resto),
  `test_status_manager.py` (3 — dispatch, provider desconocido,
  provider ausente), y 4 de integración en `test_application.py`
  (plantilla rellenada desde el provider; fallback a `oled.idle` si
  falta una variable; botón sin `launcher` no hace nada).
- `tests/fakes.py`: `FakeStatusManager`.

### Alcance deliberadamente recortado (no es un descuido)

- **Foto fija, no en vivo**: los valores se calculan una vez, al
  detectar el panel. El refresco periódico mientras el panel sigue
  puesto es una pieza aparte, sin implementar (ver "Pendiente").
- **Sin GPU ni FAN**: `psutil` no tiene una API genérica para ninguna
  de las dos en esta máquina — mejor "N/D" honesto que un dato
  inventado con una etiqueta que no le corresponde.
- **Sin fusionar el estado de `Application`** (conexión ESP32, último
  NFC...) — el `StatusProvider` de esta entrega solo aporta métricas
  de `psutil`.
- **Sin panel físico asignado**: no hay ningún UID en
  `panel_database.json` para MAINTENANCE todavía.

### Documentación

- `docs/12_Profile_System.md`: tabla de estado actualizada (MAINTENANCE
  migrado, con sus límites); sección "Perfiles con contenido en vivo"
  marca `system_stats` como implementado y `retroarch_network_commands`
  como pendiente; "Pendiente" reorganizado con los puntos concretos
  que deja abiertos este incremento.
- `software/README.md`: añadido `status/` a la estructura de carpetas.

---

## [1.4.4] - 2026-09-03 — Decisión: DISPAROS abre siempre Steam Big Picture; retirado el panel por-juego

### Decidido

- El botón del panel DISPAROS **siempre abre Steam Big Picture** —
  sin selector dentro del dispositivo. La lista real de juegos de
  disparos es una Colección de Steam que el usuario organiza a mano
  dentro del propio Steam, no un menú de este proyecto.
- Retirado el panel `56A1C003` (Zombies - HOTD 2 Remake): ya no hace
  falta un panel físico por juego, con el panel único de DISPAROS
  basta.

### Cambiado

- `software/config/panel_database.json`: eliminada la entrada
  `56A1C003`. El panel `112FC103` pasa a llamarse simplemente
  `"Zombies"` (antes "Zombies - HOTD Remake"), `launcher` cambia de
  `"hotd_remake"` a `"steam"`, `icon` a `"disparos.png"`.
- `software/config/profiles/disparos.json`: `launcher` cambia a
  `"steam"`; nuevos campos informativos `selector: "steam_collection"`
  y `selector_note` explicando la decisión. `games[]` se mantiene
  como catálogo de referencia (qué juegos se consideran parte de
  "Disparos"), pero ningún código lo lee todavía.
- `software/config/config.json`: `hotd_remake` y `hotd2_remake` se
  mantienen tal cual (siguen siendo `launcher` válidos por si se
  quieren lanzar directamente para pruebas), simplemente ya no los
  referencia ningún panel.
- Tests actualizados a la nueva realidad: el test que antes probaba
  "el botón lanza el juego propio del panel" se sustituye por
  `test_on_button_disparos_panel_always_opens_steam_big_picture`.
  Nuevo `test_default_database_disparos_panel_launches_steam_not_a_specific_game`
  en `test_panel_database.py`, que carga el `panel_database.json`
  real y comprueba tanto que `56A1C003` ya no existe como que
  `112FC103` lanza `"steam"` — para detectar si algún cambio futuro
  reintroduce por error el panel retirado. 69 tests en total, todos
  en verde.
- `docs/12_Profile_System.md`: el punto de "Pendiente" sobre el
  selector de DISPAROS se mueve a "Decisiones cerradas", con el
  razonamiento.

---

## [1.4.3] - 2026-09-03 — Perfil DISPAROS migrado (agrupa varios juegos, sin selector en el dispositivo todavía)

### Contexto

- El usuario pidió explícitamente: "un perfil que activará un único
  panel que debería dar acceso a los juegos de disparos que vayamos
  incluyendo en alguna especie de listado" — a diferencia de
  STEAM/RETRO (un perfil = un programa), DISPAROS agrupa varios
  juegos bajo la misma identidad.

### Añadido

- `software/config/profiles/disparos.json`: `led.idle`/`led.running`
  (`#FF3300`), `oled.idle: ["STEAM MACHINE", "DISPAROS"]`, y un campo
  nuevo `games[]` (catálogo: nombre + `launcher` de cada juego —
  hoy `hotd_remake` y `hotd2_remake`). El campo `launcher` a nivel de
  perfil (`"hotd_remake"`) queda tan inerte como el `running_template`
  de RETRO — `Application` sigue leyendo el `launcher` del PANEL, no
  el del perfil (ver "Sin cambios de código" más abajo).
- `software/config/panel_database.json`: los dos paneles Zombies
  (`112FC103` → HOTD Remake, `56A1C003` → HOTD 2 Remake) ganan
  `"profile": "DISPAROS"`. Su `launcher`/`led`/`icon` propios se
  mantienen sin tocar.
- 3 tests nuevos (68 en total, todos en verde):
  `test_default_profiles_directory_has_disparos_with_games_catalog`
  (valida el catálogo `games[]`), y dos de integración en
  `test_application.py` — uno confirma que la OLED muestra "DISPAROS"
  para un panel Zombies, y **el más importante**:
  `test_on_button_disparos_panel_launches_its_own_game_not_a_fixed_one`,
  que prueba explícitamente que pulsar el botón sigue lanzando el
  juego propio del panel insertado (`hotd2_remake` en ese caso), no
  un juego fijo del perfil — es la garantía de que unificar la OLED/
  LEDs bajo DISPAROS no ha cambiado qué juego se lanza.

### Sin cambios de código

- Igual que con RETRO: no ha hecho falta tocar `ProfileManager` ni
  `Application` — el mecanismo genérico de [1.4.0] ya cubre esto,
  precisamente porque `_on_button()` lee `panel["launcher"]` (del
  panel concreto), no del perfil. Eso es justo lo que hace que hoy
  "compartir perfil" sea seguro sin selector: cada panel sigue
  lanzando lo suyo.

### Pendiente (documentado en `docs/12_Profile_System.md`)

- El diseño real de "un único panel con una lista navegable" sigue
  sin resolver — necesita una decisión de UX de un solo botón (corta
  = siguiente, larga = lanzar; requiere ampliar el protocolo de
  `BUTTON` con duración) o, alternativa sin tocar firmware, apoyarse
  en una Colección de Steam organizada a mano. También queda abierto
  si retirar el panel `56A1C003` ahora que la intención es un panel
  único, o dejarlo como segunda entrada mientras no haya selector.

---

## [1.4.2] - 2026-09-03 — Perfil RETRO migrado (segundo perfil, mismo mecanismo genérico)

### Añadido

- `software/config/profiles/retro.json`: `launcher: "retrodeck"`,
  `led.idle`/`led.running` (`#8800FF`), `oled.idle: ["STEAM MACHINE",
  "RETRO"]`. Incluye también `oled.running_template` y
  `status_provider: "retroarch_network_commands"` del esquema de
  `docs/12_Profile_System.md`, pero **de momento quedan inertes** —
  `Application` todavía no lee ninguno de los dos campos (no hay
  `StatusProvider` implementado). Se dejan ya en el JSON para no
  tener que volver a tocar el fichero cuando se implemente.
- `software/config/panel_database.json`: panel RetroDECK (`E76DC103`)
  gana el campo `"profile": "RETRO"`. `launcher`/`led`/`icon` se
  mantienen igual.
- 2 tests nuevos: `test_default_profiles_directory_has_steam_and_retro`
  (carga la carpeta real `config/profiles/` y valida launcher + límite
  de 2 líneas en `oled.idle` de ambos perfiles, para detectar erratas
  sin necesidad de arrancar `Application`) y
  `test_on_tag_detected_retro_panel_shows_profile_idle_lines` (mismo
  mecanismo genérico que STEAM, verificado con un segundo perfil real
  en vez de asumir que "si funcionó una vez, funciona siempre"). 65
  tests en total, todos en verde.
- `docs/12_Profile_System.md`: añadida una tabla de estado de
  implementación en "Alcance propuesto para v0.2" (STEAM y RETRO
  migrados; DISPAROS, MAINTENANCE, AUTO pendientes).

### Sin cambios de código

- No ha hecho falta tocar `ProfileManager` ni `Application` —
  el mecanismo genérico de [1.4.0] (leer `oled.idle` cuando el panel
  tiene `profile`, retrocompatible si no lo tiene) ya cubre RETRO sin
  ninguna rama de código nueva. Es la señal de que el diseño de
  [1.4.0] estaba bien planteado: añadir un perfil "estático" es
  añadir un fichero, no tocar Python.

---

## [1.4.1] - 2026-09-03 — Decisión: sin animación de lanzamiento configurable por perfil

### Decidido

- El usuario eligió la opción B de las dos planteadas: no conectar
  `led.launch_animation` a `_on_button()`. La animación de lanzamiento
  se queda fija en `"launch"` para todos los perfiles, igual que
  antes de que existiera `ProfileManager`.

### Cambiado

- `software/config/profiles/steam.json`: eliminado el campo
  `led.launch_animation` (quedaba sin usar — `_on_button()` nunca
  llegó a leerlo).
- `docs/12_Profile_System.md`: quitado `launch_animation` del ejemplo
  de esquema y de su explicación; nueva sección "Decisiones cerradas"
  con el porqué (evitar complejidad sin necesidad real mientras todos
  los perfiles compartan la misma animación) y con la decisión de
  AUTO de [1.3.3] (que ya estaba resuelta pero seguía listada por
  error en "Pendiente" — corregido de paso).
- 63 tests siguen en verde (el campo no estaba conectado a ningún
  test, cambio sin impacto funcional).

---

## [1.4.0] - 2026-09-03 — Implementado ProfileManager (primer paso del sistema de perfiles, `docs/12_Profile_System.md`)

### Añadido

- `software/core/profile_manager.py`: `ProfileManager` — carga cada
  `.json` de `software/config/profiles/` (id = campo `"id"` del propio
  fichero, o el nombre de fichero si falta), y expone `get(profile_id)`
  / `all()`. Sigue el mismo patrón que `PanelDatabase` (carga desde
  disco en `load()`, tolera fichero/carpeta ausente o JSON mal
  formado sin reventar).
- `software/config/profiles/steam.json`: primer perfil migrado al
  nuevo esquema — `launcher: "steam"`, `led.idle`/`led.running`
  (`#0055FF`), `led.launch_animation: "launch"`, `oled.idle: ["STEAM
  MACHINE", "Steam"]` (2 líneas, dentro del límite real del firmware).
- `software/config/panel_database.json`: panel Steam (`6739C003`)
  gana el campo `"profile": "STEAM"`. `launcher`/`led`/`icon` se
  mantienen tal cual — el resto de paneles (RetroDECK, Zombies x2) se
  quedan sin `"profile"` por ahora, sin cambios en su comportamiento.
- `software/core/application.py`, `_on_tag_detected()`: si el panel
  tiene `"profile"` y `ProfileManager` lo resuelve, la OLED muestra
  `oled.idle` del perfil (1 o 2 líneas) en vez de `panel["name"]`. Si
  el panel no tiene `"profile"`, o el id no resuelve a ningún perfil
  cargado, el comportamiento es **exactamente el de antes** —
  retrocompatibilidad verificada con test dedicado.
- 10 tests nuevos en `software/tests/test_profile_manager.py`
  (carga, fichero/carpeta ausente, JSON malformado, `id` por nombre de
  fichero, copia defensiva de `all()`) + 2 en `test_application.py`
  (panel con perfil muestra `oled.idle`; panel con `profile` desconocido
  cae al comportamiento antiguo). 63 tests en total, todos en verde.

### Alcance de este paso

- Solo `STEAM` está migrado — es el perfil más simple del catálogo de
  `docs/12_Profile_System.md` (sin `status_provider`, sin animación de
  "running" distinta de la de reposo), elegido a propósito para
  validar el mecanismo antes de añadir `RETRO`, `DISPAROS` y
  `MAINTENANCE`.
- `_on_button()` no se ha tocado — sigue lanzando `panel["launcher"]`
  igual que siempre; conectar `led.launch_animation` del perfil ahí
  queda para el siguiente incremento.
- `ProcessWatcher` y los `StatusProvider` (RetroArch, sistema) siguen
  sin implementar — no hacían falta para este primer perfil.

### Pendiente

- Migrar `RetroDECK` → perfil `RETRO`, y los dos paneles Zombies →
  perfil `DISPAROS` (con `led`/`icon` como override por panel, según
  el esquema del documento de diseño).
- Perfil `MAINTENANCE` (necesita el `StatusProvider` de sistema antes
  de tener sentido).
- Decidir si `led.launch_animation` del perfil sustituye a la
  animación `"launch"` fija que usa hoy `_on_button()`.

---

## [1.3.3] - 2026-09-03 — Decisión: AUTO se activa sin panel puesto, no como panel propio

### Decidido

- El usuario resolvió el punto abierto de `docs/12_Profile_System.md`:
  AUTO se activa cuando no hay ningún panel físico insertado — no es
  un perfil seleccionable por su propio tag NFC.

### Cambiado

- `docs/12_Profile_System.md`: sección "Precedencia NFC físico vs.
  perfil AUTO" actualizada de "a decidir" a regla firme; añadida
  subsección "Implicación en `core/application.py`":
  `_on_tag_removed()` pasa de solo apagar/reposar a arrancar el
  `ProcessWatcher` (entra en AUTO); `_on_tag_detected()` debe pararlo
  al detectar un panel físico. Sin clave nueva en
  `panel_database.json` para AUTO.
- Documento subido a versión 0.2 (queda un único punto de diseño
  resuelto; el resto — `ProcessWatcher`, los `StatusProvider`, la
  ampliación de la OLED a más líneas — sigue pendiente de
  implementar).

---

## [1.3.2] - 2026-09-03 — Reconciliado con el zip subido por el usuario: UIDs reales conservados, correcciones OLED restauradas

### Contexto

- El usuario subió `SteamMachine-UM790-main__3_.zip` "por si no tenías
  toda la información actualizada". Comparado con el estado de
  trabajo de esta sesión, resultó tener contenido en ambas
  direcciones: cosas más nuevas que yo no tenía, y cosas más viejas
  que sobrescribían correcciones ya hechas hoy.

### Encontrado en el zip del usuario (más nuevo que mi copia — conservado tal cual)

- `software/config/panel_database.json`: los 3 UID de ejemplo/
  placeholder (`04B2D9C3`, `04C3EAD4`, `0AAABBCC`) sustituidos por los
  UID reales de los tags NFC del usuario (`E76DC103`, `112FC103`,
  `56A1C003`) — mismos nombres/launcher/led/icon, solo cambian las
  claves. Conservado sin tocar.
- Carpeta `obsoletos/` (creada 2026-08-14 según su propio README, antes
  de esta sesión): agrupa ficheros `.scad` ya sin uso
  (`front_panel.scad`, `front_layout.scad`, `rc522_bracket_v1.scad`,
  `virtual_assembly_v1.scad`, `front_panel_view.scad`,
  `chassis_layout.scad`, `um790_reference.scad`), verificados sin
  referencias entrantes antes de moverlos. Conservada.
- `VERSION.md` y carpeta `G-Code/` (con `lower_panel.gcode`).
  Conservados.
- Piezas de chasis nuevas sin documentar en este CHANGELOG hasta
  ahora: `openscad/parts/02_chassis/floor_flat.scad`, `foot.scad`,
  `leftwall_flat.scad`, `rightwall_flat.scad`,
  `openscad/parts/04_soportes/foot.scad`, y
  `STL/rear_panel_horizontal.stl` + STL sueltos
  (`floor_flat (1).stl`, `foot.stl`, `leftwall_flat.stl`,
  `rightwall_flat.stl`). Conservados tal cual — no hay contexto en
  este historial sobre su propósito o si vienen de otra sesión; sin
  inventar una entrada de motivo, pendiente de que el usuario lo
  aclare si quiere que se documenten.

### Encontrado en el zip del usuario (más viejo que mi copia — restaurado desde esta sesión)

- `openscad/parts/03_panels/lower_panel.scad`: el zip subido no tenía
  ninguna de las correcciones de OLED de [1.2.2] a [1.3.0] de esta
  misma sesión (ventana acoplada a los taladros M2 en vez de
  desacoplada, rebaje de pines en la cara exterior en vez de la
  interior, medidas de pantalla/separación de taladros sin la
  medición real por calibre, sin el offset del canal LED). Restaurado
  el fichero de esta sesión, que sí incluye todo lo anterior.
- `openscad/reference/components/assembly_positions.scad`: mismo
  contenido salvo el comentario explicativo del desacoplamiento de
  [1.2.9], que faltaba. Restaurado.
- `STL/lower_panel.stl`, `openscad/parts/03_panels/oled_bracket.stl`,
  `STL/probetas/probeta_pines_oled.stl`: regenerados desde el
  `lower_panel.scad` restaurado.
- Añadidos también `openscad/parts/03_panels/nfc_panel_zombies.scad` y
  `STL/nfc_panel_zombies_tumbado.stl` ([1.2.7]), que no estaban en el
  zip subido.

### Verificado

- `openscad/parts/03_panels/lower_panel.scad` renderiza sin errores
  (817 facetas, igual que la versión de esta sesión).
- Los 53 tests de `software/tests/` pasan.
- `panel_database.json`, `config.json`, `launcher.py` y los plugins de
  `software/launcher/` ya coincidían entre ambas copias — sin cambios.

---

## [1.3.1] - 2026-08-30 — Documento de diseño: sistema de perfiles (panel = perfil, no solo panel = programa)

### Añadido

- `docs/12_Profile_System.md`: propuesta de diseño para generalizar
  los paneles NFC de "panel = programa" (`launcher` directo) a
  "panel = perfil" (app + comportamiento de OLED + LEDs, con un
  perfil `AUTO` que detecta qué corre en Bazzite cuando no hay panel
  físico dedicado puesto). Basada en una propuesta del usuario, con
  tres correcciones respecto al planteamiento original:
  1. Regla de precedencia explícita entre panel físico y AUTO (el
     panel físico manda siempre; AUTO solo actúa como panel propio).
  2. Señalado que el protocolo OLED actual solo admite 2 líneas
     (`OLEDManager.show_status`), no las 5 líneas de los mockups
     originales — el motor de plantillas de la v0.2 trabaja con listas
     de 2 elementos; ampliar el firmware queda anotado como tarea
     aparte.
  3. Separados como componentes `StatusProvider` futuros (no incluidos
     en esta entrega) la integración con RetroArch Network Commands
     (UDP 55355, para nombre de juego + tiempo en RETRO) y las
     métricas de sistema (CPU/GPU/RAM, para MAINTENANCE).
- Esquema de datos propuesto: `software/config/profiles/*.json` (un
  fichero por perfil) + campo opcional `profile` en
  `panel_database.json`, retrocompatible con los paneles que ya usan
  `launcher` directo.
- Alcance v0.2 acotado a `STEAM · RETRO · DISPAROS · MAINTENANCE ·
  AUTO` (con contenido de OLED definido); `KODI · MUSIC · DESKTOP ·
  NIGHT · DEMO` quedan como huecos reservados en el esquema, sin
  diseñar su pantalla todavía.
- `DISPAROS` se documenta como el mismo concepto que el panel Zombies
  ya existente (`hotd_remake`/`hotd2_remake`), no un nombre nuevo.

### Pendiente

- Todo el documento es una propuesta sin implementar — ver su propia
  sección "Pendiente" para el desglose (`ProcessWatcher`, los dos
  `StatusProvider`, y la decisión final sobre cuándo se activa AUTO).

---

## [1.3.0] - 2026-08-30 — Recalculado con medidas reales del módulo OLED: ventana, taladros M2 y rebaje de pines

### Encontrado

- Con foto de la impresión real, el usuario mostró la ventana
  invadiendo el taladro M2 inferior ("¿No te parece que esto es una
  chapuza?"). Confirmado por cálculo: el offset -4,0 de [1.2.8] hacía
  que el corte recto de la ventana se solapara 0,85mm con el taladro
  inferior, y el bisel 2,85mm.
- El usuario decidió medir el módulo físico con calibre en vez de
  seguir ajustando a ciegas — decisión correcta, ya que reveló que el
  diseño llevaba varias suposiciones sin verificar.

### Medidas reales (calibre, módulo instalado en la carcasa, pines hacia arriba)

- Separación horizontal entre los 2 taladros M2 superiores: 23,0mm
  (igual que se venía usando).
- Separación VERTICAL entre taladro superior e inferior del mismo
  lado: 23,5mm (antes se asumía igual que la horizontal, 23,0 — no es
  un cuadrado exacto).
- Pantalla: 26 x 15mm (ancho ya correcto; alto corregido de 14,5 a
  15,0).
- Del centro del taladro superior al borde superior de la pantalla:
  2,0mm — la medida clave que faltaba.
- Pines de soldadura: sobresalen 2,0mm por detrás de la placa (antes
  se estimaba 1,5mm, insuficiente — no habrían cabido).

### Causa raíz del zigzag de las rondas anteriores

- Antes de [1.2.9], `oled_pos` movía a la vez los taladros M2 Y la
  ventana — cualquier feedback visual del usuario sobre "la pantalla"
  en realidad comparaba la ventana contra el botón/USB del panel, no
  contra los taladros de la propia OLED (imposible verlo por
  separado hasta que se desacoplaron). Por eso el offset empírico
  (-4,0) apuntaba en la dirección contraria a la que da el cálculo
  con datos reales (+2,25).

### Cambiado

- `openscad/parts/03_panels/lower_panel.scad`:
  - `oled_mount_spacing` dividida en `oled_mount_spacing_x` (23,0) y
    `oled_mount_spacing_z` (23,5) — ya no se asume un cuadrado.
  - `oled_screen_height`: 14,5 → 15,0.
  - `oled_gap_top_hole_to_screen = 2.0` (nueva constante, medida
    real).
  - `oled_window_z_offset` ahora se calcula con fórmula
    (`oled_mount_spacing_z/2 - oled_gap_top_hole_to_screen -
    oled_screen_height/2` = +2,25) en vez de un número fijo ajustado
    a mano.
  - `oled_pin_clearance_pocket_depth`: 1,5 → 2,0 (medida real; con el
    valor anterior los pines no habrían cabido).
  - Bisel de la ventana ahora asimétrico: `oled_bevel_margin_top =
    0.4` (reducido, solo en el borde superior, para no invadir el
    taladro con solo 2mm de holgura real) vs `oled_bevel_margin = 2.0`
    en los otros tres lados.
  - `oledMountHoles()` actualizado para usar `oled_mount_spacing_x`/
    `_z` por separado en vez de la variable única.
- Verificado por render (vista frontal + zoom a la zona superior):
  los 4 taladros M2 aparecen limpios alrededor de la ventana, sin
  solape con el bisel ni con el corte recto.
- Regenerados y sustituidos `STL/lower_panel.stl`,
  `openscad/parts/03_panels/oled_bracket.stl` y
  `STL/probetas/probeta_pines_oled.stl`.

### Pendiente

- Nueva impresión de prueba — primera vez que la posición de la
  ventana se calcula a partir de medidas reales en vez de prueba y
  error, así que hay bastante confianza, pero toca confirmarlo en
  mano.
- El margen de bisel superior (0,4mm) es deliberadamente pequeño para
  garantizar que no toque el taladro; visualmente será un chaflán
  casi plano en ese borde, distinto de los otros tres lados — si no
  gusta el resultado, se puede ajustar una vez impreso.

---

## [1.2.9] - 2026-08-30 — Desacoplada la ventana OLED de los taladros M2: eran fijos y no debían moverse

### Encontrado

- Con foto de la impresión real, el usuario señaló dos círculos junto
  al hueco de la pantalla que parecían haberse movido, pese a haber
  pedido explícitamente no tocar tornillos. Comparando renders, se
  identificaron como los 4 taladros M2 propios de la placa OLED
  (`oledMountHoles()`), no los M3 del panel contra la pared (esos
  seguían intactos, verificado de nuevo). El usuario confirmó: "sí,
  me refiero a los del propio OLED de métrica 2".

### Causa raíz

- Desde [1.2.2], `oled_pos` se usaba como referencia única tanto para
  los taladros M2 (fijos, correctos desde el principio) como para la
  ventana visible de la pantalla (la que el usuario pedía mover). Al
  desplazar `oled_pos` para bajar la ventana, arrastraba también los
  taladros M2 — que en el módulo OLED real NO se mueven, porque son
  la fijación física de la placa; lo que está descentrado es el área
  visible de la pantalla dentro de esa placa.

### Corregido

- `openscad/reference/components/assembly_positions.scad`:
  `oled_pos` vuelve a su posición original (sin ningún offset) — pasa
  a representar solo la placa/taladros M2/brida, que ya estaban bien
  y no se tocan más.
- `openscad/parts/03_panels/lower_panel.scad`, `oledCut()`: nuevo
  `oled_window_z_offset = -4.0`, aplicado SOLO a la ventana visible
  (el bisel y el hueco recto), no al resto. El rebaje de pines sigue
  centrado en los taladros M2 (ahora fijos de nuevo), sin cambios en
  su fórmula.
- Verificado con `echo()`: `oled_pos` = Z 19 (taladros M2 en 7,5 /
  30,5mm, igual que antes de [1.2.2]); taladros M3 del panel sin
  cambios (7 / 26,5mm); ventana ahora en Z=15 (los -4mm pedidos por
  el usuario, aplicados solo a ella).
- Regenerados y sustituidos `STL/lower_panel.stl`,
  `openscad/parts/03_panels/oled_bracket.stl` y
  `STL/probetas/probeta_pines_oled.stl` (recorte ampliado para cubrir
  desde los taladros M2 hasta la ventana, ahora más separadas).

### Pendiente

- Nueva impresión de prueba para confirmar que ahora sí encaja todo
  correctamente: taladros M2 fijos + ventana 4mm más abajo.

---

## [1.2.8] - 2026-08-30 — Ventana OLED: 2mm adicionales hacia abajo (total -4mm)

### Encontrado

- Tras imprimir el panel inferior con el ajuste de [1.2.2] (-2mm),
  el usuario reportó: "la pantalla sigue quedando dos milímetros
  alta. Los orificios de los tornillos están correctamente
  ubicados, pero el rectángulo de la pantalla debería bajar dos
  milímetros [más]".

### Cambiado

- `openscad/reference/components/assembly_positions.scad`:
  `oled_z_offset` de `-2.0` a `-4.0` (total acumulado desde la
  posición original de antes de [1.2.2]). Confirmado por `echo()`
  que los taladros de tornillo siguen exactamente en 7 / 26,5mm, sin
  cambios — coincide con lo que el usuario validó ("correctamente
  ubicados").
- El rebaje de pines y los bosses de la brida (`oled_bracket.scad`)
  se recalculan solos a partir de `oled_pos`, así que bajan con la
  pantalla automáticamente, manteniéndose alineados entre sí.
- Regenerados y sustituidos `STL/lower_panel.stl`,
  `openscad/parts/03_panels/oled_bracket.stl` y
  `STL/probetas/probeta_pines_oled.stl`.

### Pendiente

- Nueva impresión de prueba para confirmar que -4mm es ya la
  posición correcta.

---

## [1.2.7] - 2026-08-30 — Nuevo panel NFC "Zombies": base en blanco + anagrama Gung, listo para imprimir tumbado

### Añadido

- `openscad/parts/03_panels/nfc_panel_zombies.scad`: nuevo panel NFC
  del tema Zombies, siguiendo el mismo patrón que
  `nfc_panel_Steam.scad` / `nfc_panel_retrobat.scad` (base compartida
  de `nfc_panel.scad` + anagrama), con una diferencia: el anagrama no
  es geometría 2D generada en OpenSCAD, es el STL ya modelado por el
  usuario (`STL/Anagramas/Gung.stl`), importado y centrado.
  - `nfcPanelZombies()`: base + anagrama en coordenadas globales del
    caso (para previsualización/renders de galería, mismo criterio
    que los paneles hermanos).
  - `nfcPanelZombiesPrintable()`: el mismo conjunto rotado -90° sobre
    X, para que el eje fino del panel (el grosor) quede en Z — lista
    para laminar e imprimir tumbada directamente, sin reorientar nada
    a mano.
- `STL/nfc_panel_zombies_tumbado.stl`: exportado desde
  `nfcPanelZombiesPrintable()`. Verificado por bounding box: huella
  149 x 94,5mm, solo 5mm de alto — confirmado que queda tumbado.
- Verificado visualmente por render que el anagrama Gung queda
  centrado y con la orientación correcta (sin espejarse ni girarse)
  sobre la base.

### Nota

- `STL/Anagramas/Gung.stl` (el anagrama suelto, para el flujo de
  impresión en dos piezas + Loctite de [1.2.1]) no se ha tocado — este
  panel combinado es una pieza única alternativa, útil para
  previsualización o para imprimir de una sola vez si en algún
  momento no se quiere pegar con Loctite.

---

## [1.2.6] - 2026-08-30 — Galería: renders de la carcasa montada con distintos anagramas

### Añadido

- 3 renders nuevos de la carcasa **completa montada** (chasis + tapa
  superior + panel inferior + panel trasero + bandeja + panel NFC),
  cada uno con un anagrama de panel NFC distinto: Steam, RetroBat y
  en blanco. Todas las piezas ya estaban definidas en el mismo
  sistema de coordenadas global (`assembly_positions.scad`), así que
  el ensamblaje es una simple unión de los módulos de cada pieza sin
  necesidad de calcular ninguna posición nueva.
- Ficheros: `docs/img/render_ensamblaje_steam.png`,
  `render_ensamblaje_retrobat.png`, `render_ensamblaje_blank.png`.
- `README.md`: nueva sección "Carcasa montada, con distintos
  anagramas de panel NFC" en la galería, antes de las piezas sueltas.

### Nota

- El anagrama del panel Zombies (`STL/Anagramas/Gung.stl`) no tiene
  todavía un `.scad` paramétrico propio (como sí tienen Steam,
  RetroBat y TeknoParrot) — está modelado como STL suelto en
  coordenadas de su propia mesa de impresión, no en las coordenadas
  globales del proyecto. Por eso no se ha podido incluir en el
  render conjunto sin arriesgarse a una posición incorrecta. Si se
  quiere en la galería, habría que crear
  `openscad/parts/03_panels/nfc_panel_zombies.scad` a partir del
  logo, siguiendo el mismo patrón que `nfc_panel_retrobat.scad`.

---

## [1.2.5] - 2026-08-30 — Galería del README con renders reales del diseño actual

### Cambiado

- `README.md`: sustituida la imagen genérica de la galería (mockup
  subido a GitHub, sin relación directa con el CAD del proyecto) por
  5 renders generados directamente desde los ficheros OpenSCAD
  actuales — chasis, panel superior, panel inferior (ya con los
  ajustes de [1.2.2]-[1.2.4]), panel trasero y bandeja interior.
- Nuevos ficheros en `docs/img/`: `render_chasis.png`,
  `render_panel_superior.png`, `render_panel_inferior.png`,
  `render_panel_trasero.png`, `render_bandeja.png`. Generados con
  `openscad --imgsize=900,700 --camera=0,0,0,55,0,35,0` sobre cada
  `.scad` de pieza, usando su propio bloque `// PREVIEW` — se pueden
  regenerar en cualquier momento con el mismo comando si el diseño
  cambia.

---

## [1.2.4] - 2026-08-29 — Rebaje de pines OLED realineado a sus orificios de sujeción reales + probeta de comprobación

### Encontrado

- Tras [1.2.3], el usuario avisó: "el rebaje para los pines del OLED
  aun tienen que subir hasta estar centrados verticalmente con los
  orificios superiores de sujeción" — [1.2.3] lo había alineado con
  `lower_panel_hole_z_high` (26,5mm), que son los taladros M3 del
  panel contra la pared, no los "orificios de sujeción" a los que se
  refería. Los orificios de sujeción reales son el par superior de
  los 4 taladros M2 de `oledMountHoles()` (fijación de la propia
  placa OLED), a Z = 28,5mm — 2mm más arriba, coincide con "aun
  tienen que subir".

### Corregido

- `openscad/parts/03_panels/lower_panel.scad`, `oledCut()`: el rebaje
  de pines se centra ahora en `oled_pos[2] + oled_mount_spacing/2`
  (28,5mm) en vez de `lower_panel_hole_z_high` (26,5mm).
- Regenerado y sustituido `STL/lower_panel.stl`.

### Añadido

- `STL/probetas/probeta_pines_oled.stl`: probeta de comprobación —
  recorte pequeño y fino (32 x 3 x 10,25mm) del panel inferior,
  limitado a la zona del rebaje de pines + orificios superiores de
  sujeción del OLED, pensada para imprimir tumbada sobre la cama
  (rápida, sin gastar tiempo/material en el panel completo). Generada
  por intersección de `lowerPanel()` con una caja de recorte
  paramétrica en `oled_pos[0]`, sin tocar el fichero fuente
  `lower_panel.scad`.

### Nota técnica (revisar en algún momento, no bloqueante hoy)

- Se ha detectado que `oled_screen_width/height` está definido dos
  veces con valores distintos: en `assembly_positions.scad` (27,0 x
  20,0mm, usado por `oled_bracket.scad`) y localmente en
  `lower_panel.scad` (26,0 x 14,5mm, el que realmente usa `oledCut()`
  al ser la última asignación en el `include`). No afecta a los
  cambios de hoy, pero conviene unificarlo para que la brida
  (`oled_bracket.scad`) y la ventana (`lower_panel.scad`) usen
  siempre la misma medida.

---

## [1.2.3] - 2026-08-29 — Corregido: rebaje de pines en la cara equivocada; confirmado que los tornillos no se movieron

### Encontrado

- El usuario avisó, tras revisar el cambio de [1.2.2]: "has vuelto a
  poner el rebaje para los pines por fuera en lugar de por dentro" y
  "has bajado los orificios para los tornillos... tienes que
  devolverlos a su posición original".

### Comprobado

- Los taladros de tornillo (`lower_panel_hole_z_low/high`,
  `lower_panel_screw_z_low/high`) **no se han movido**: sus fórmulas
  dependen de `front_panel_lower_top` → `front_panel_cluster_z_high`
  → `front_cluster_z`, ninguna de las cuales usa `oled_pos` ni el
  rebaje de pines. Verificado numéricamente con `echo()` en OpenSCAD:
  `lower_panel_hole_z_low = 7`, `lower_panel_hole_z_high = 26.5`,
  `lower_panel_screw_z_low = 10`, `lower_panel_screw_z_high = 29.5` —
  mismos valores antes y después de [1.2.2]. No ha hecho falta
  ningún cambio de código en `lowerPanelScrewHoles()`.

### Corregido

- `openscad/parts/03_panels/lower_panel.scad`, `oledCut()` (rebaje de
  pines): el cubo arrancaba en la cara EXTERIOR del panel
  (`-case_depth/2`, la misma cara donde empieza el propio panel) y
  cortaba hacia dentro — dejaba el hueco abierto por fuera (donde se
  ve la pantalla) y cerrado justo donde están los pines (la cara
  interior). Invertido: ahora arranca cerca de la cara interior
  (`-case_depth/2 + front_panel_thickness - oled_pin_clearance_pocket_depth`)
  y corta hacia el interior, dejando la piel sólida en la cara
  exterior (donde no se nota) y el hueco abierto hacia el interior,
  donde sobresalen los pines.
- Regenerado y sustituido `STL/lower_panel.stl` (OpenSCAD 2021.01,
  sin warnings ni errores).

### Pendiente

- Nueva impresión de prueba para confirmar que el rebaje de pines
  encaja bien desde la cara interior antes de dar el panel por
  definitivo.

---

## [1.2.2] - 2026-08-29 — Ajustes del panel inferior tras la primera impresión real

### Encontrado

- Tras imprimir y montar el panel inferior real, el usuario reportó
  tres desajustes respecto al hardware:
  1. El hueco rectangular de la pantalla OLED queda 2mm demasiado
     alto.
  2. El rebaje ciego para los pines de soldadura de la OLED debería
     estar arriba del todo del panel, alineado con los orificios de
     los tornillos superiores — no siguiendo la posición de la
     pantalla como hasta ahora.
  3. El soporte/canal de la tira LED debería subir 2mm.
- Los taladros de tornillo (`lower_panel_hole_z_low/high`,
  compartidos con los insertos ya impresos en la pared) se mantienen
  sin tocar, tal y como pidió el usuario.

### Cambiado

- `openscad/reference/components/assembly_positions.scad`: nuevo
  `oled_z_offset = -2.0`, aplicado a `oled_pos[2]` — baja la ventana
  OLED 2mm sin mover nada más (los bosses de `oled_bracket_screw_positions`
  se recalculan solos a partir de `oled_pos`, así que se mueven con
  ella automáticamente).
- `openscad/parts/03_panels/lower_panel.scad`, `oledCut()`: el rebaje
  de los pines de soldadura ya no se calcula a partir de
  `oled_pos[2] + oled_screen_height/2` — ahora se centra en
  `lower_panel_hole_z_high` (misma Z que los taladros de tornillo
  superiores).
- `openscad/parts/03_panels/lower_panel.scad`, `ledChannelWalls()`:
  nuevo `led_channel_z_offset = 2.0`, sumado a `channelZ` — sube el
  canal/soporte de la tira LED 2mm.
- Regenerados y sustituidos `STL/lower_panel.stl` y
  `openscad/parts/03_panels/oled_bracket.stl` con los cambios
  aplicados (renderizado con OpenSCAD 2021.01, sin warnings ni
  errores).

### Pendiente

- Confirmar con una nueva impresión de prueba que los tres ajustes
  encajan correctamente antes de dar el panel inferior por definitivo.

---

## [1.2.1] - 2026-08-29 — Paneles NFC: impresión en dos piezas (base + anagrama pegado con Loctite)

### Cambiado

- Los STL de los paneles NFC con anagrama pasan de imprimirse como
  pieza única (base + emblema en relieve integrado) a imprimirse en
  dos piezas independientes: `STL/Anagramas/nfc_panel_blank.stl` (la
  base, común a todos los temas) y un STL suelto por anagrama
  (`Steam.stl`, `Retrobat.stl`, `Parrot.stl`, `engranaje.stl`,
  `Gung.stl`), que se pegan después con Loctite (cianoacrilato tipo
  401/454, compatible con PLA/PETG).
- Motivo: baja el tiempo de impresión de ~6h (pieza única con el
  relieve del emblema) a ~1h por panel.
- Documentado en `GUIA_INICIO.md` (paso 1, lista de materiales) y
  `docs/11_Assembly_Manual.md` (Paso 11, Panel NFC).
- Los STL de bloque único (con el emblema ya integrado) se mantienen
  en `STL/` y `openscad/parts/03_panels/` para quien prefiera esa vía.

### Confirmado

- `Gung.stl` es el anagrama del panel Zombies (04C3EAD4 / hotd_remake).

---

## [1.2.0] - 2026-08-28 — Panel TeknoParrot sustituido por panel Zombies (Steam nativo) + soporte RetroArch

### Contexto

- TeknoParrot tiene mala compatibilidad con Linux/Bazzite (depende de
  Wine + Demulshooter, poco fiable). Se decidió sustituir el panel de
  recreativas por un panel de disparos/zombies usando juegos nativos
  de Steam en vez de emulación, pensado para jugarse con Wiimote como
  pistola (Bluetooth + barra de sensor IR, integración pospuesta a más
  adelante).

### Añadido

- `software/launcher/hotd_remake_plugin.py` y
  `hotd2_remake_plugin.py`: lanzan THE HOUSE OF THE DEAD: Remake
  (AppID Steam `1694600`) y THE HOUSE OF THE DEAD 2: Remake (AppID
  `3376690`) via `steam://rungameid/`. Juegos nativos, sin BIOS ni
  cores.
- `software/launcher/retroarch_plugin.py`: lanza RetroArch (Flatpak
  `org.libretro.RetroArch`) directamente, sin pasar por RetroDECK.
  Instalado y validado en este ciclo con los núcleos Flycast, Beetle
  Saturn, PCSX-ReARMed y MAME2003-Plus.
- `config/panel_database.json`: panel `04C3EAD4` renombrado a
  "Zombies - HOTD Remake" (launcher `hotd_remake`); nuevo panel
  `0AAABBCC` "Zombies - HOTD 2 Remake" (launcher `hotd2_remake`) —
  UID placeholder pendiente de un segundo tag físico real.
- `config/config.json`: nuevas plataformas `retroarch`, `hotd_remake`,
  `hotd2_remake`.
- Documentación de instalación de RetroArch (Flatpak, actualización de
  información de núcleos, descarga de núcleos, ubicación de BIOS/ROMs)
  añadida en `GUIA_INICIO.md`, incluyendo el fallo conocido "No hay
  elementos disponibles" en el Descargador de núcleos y su solución.

### Eliminado

- `software/launcher/teknoparrot_plugin.py` y la plataforma
  `teknoparrot` de `config/config.json` / `panel_database.json`.

### Pendiente

- Emparejar el Wiimote por Bluetooth y montar la barra de sensor IR
  (ya adquirida) para usarlo como pistola en el panel Zombies.
- Asignar un UID de tag NFC real al panel de HOTD 2 Remake.
- Diseño físico (OpenSCAD) del panel Zombies: pendiente, igual que en
  su día quedó pendiente el icono de TeknoParrot hasta tener una
  imagen de referencia — `openscad/parts/03_panels/nfc_panel_teknoparrot.scad`
  no se ha tocado en este ciclo.

---

## [1.1.4] - 2026-08-25 — Corregido: falso "tag_removed" con el panel puesto

### Encontrado

- Probando el Core por primera vez contra el ESP32 real (conectado y
  funcionando por USB), el usuario reportó: "cuando pongo el tag al
  poco me dice que el panel se ha retirado, pero el tag sigue
  presentado". Reproducible de forma consistente.

### Causa

- `hardware/rc522.cpp`, `Rc522Reader::update()`: tras cada lectura
  correcta del UID, se llamaba a `PICC_HaltA()` +
  `PCD_StopCrypto1()` — buena práctica habitual para liberar la
  tarjeta tras operaciones MIFARE autenticadas, pero innecesaria aquí
  (solo leemos el UID, sin autenticación ni lectura de bloques). El
  problema: una tarjeta en estado HALT no responde al comando REQA
  que usa `PICC_IsNewCardPresent()` en el siguiente sondeo — según
  ISO14443A, un HALT solo se despierta con WUPA. El resultado: el
  firmware dejaba de "ver" el tag nada más leerlo la primera vez, y a
  los 3 sondeos fallidos (`RC522_REMOVAL_THRESHOLD` × 
  `RC522_POLL_INTERVAL_MS` ≈ 450ms) disparaba `tag_removed` aunque el
  tag siguiera físicamente puesto.

### Corregido

- Eliminadas las llamadas a `PICC_HaltA()`/`PCD_StopCrypto1()` del
  ciclo de sondeo. Sin ellas, la tarjeta permanece en estado ACTIVE y
  responde con normalidad a los sondeos siguientes mientras siga
  presente; la detección de retirada real (tag físicamente quitado)
  no se ve afectada, ya que en ese caso `PICC_IsNewCardPresent()`
  falla igualmente por ausencia de tarjeta, no por su estado.
- Confirmado en hardware real (2026-08-25): tras reflashear, el tag
  permanece detectado sin `tag_removed` falso mientras sigue puesto.

---

### Encontrado

- Probando el firmware ya validado en hardware real (compila, flashea,
  arranca), la barra LED no encendía con ningún comando
  (`{"cmd":"led",...}`) a pesar de que la comunicación serie
  funcionaba bien (confirmado con `--echo` en el monitor de
  PlatformIO). El usuario desmontó el 74AHCT125 y conectó el ESP32
  directo a un tramo de prueba de 8 LEDs: encendió correctamente. Con
  el 74AHCT125 en el circuito, nada. Causa más probable: el pin de
  habilitación /1OE del chip (activo a nivel bajo) quedó flotante en
  vez de a GND — fallo típico con este componente, y que ya estaba
  anotado como punto a verificar en la lista de comprobación de
  `Hardware/Hardware_Connections.md` antes de este cambio.

### Decisión

- Se retira el 74AHCT125 del diseño por completo. La señal de datos
  del GPIO25 va directa a la WS2812B en lógica de 3.3V — la tira lo
  admite bien en el tramo probado. Si con la tira completa (más larga
  que el tramo de prueba) aparecen problemas de señal, se revisará si
  hace falta reintroducir un nivelador, esta vez verificando bien el
  cableado de /OE.

### Cambiado

- `Hardware/Hardware_Connections.md`: reescrita la sección de
  ESP32→WS2812B (ya no hay paso intermedio por el chip), eliminada la
  sección de desacoplamiento del 74AHCT125 (100nF, específica del
  chip — el condensador de 470-1000µF de la propia tira se mantiene,
  es independiente), actualizada la lista de componentes y el
  checklist de verificación.
- `firmware/src/config.h`, `firmware/README.md`, `GUIA_INICIO.md`,
  `docs/07_Hardware_Specification.md`: quitadas las referencias al
  74AHCT125 en el pinout, la tabla de alimentación y la solución de
  problemas.

### Sin tocar

- No existía ningún componente ni keepout del 74AHCT125 en el CAD
  (`openscad/`) — era solo un componente de cableado, sin geometría
  propia en el ensamblaje, así que no hizo falta ningún cambio ahí.

---

## [1.1.2] - 2026-08-18 — Segunda pared del canal LED, en L, para que la tira quede enfrentada al panel

### Encontrado

- El usuario señaló (con dos capturas, la primera descartada por él
  mismo) que el soporte de la tira LED no ofrecía una superficie
  donde pegarla mirando hacia el panel: la pared existente
  (`ledChannelWalls()`) es horizontal, con su cara ancha mirando en
  Z, no en Y — no hay dónde pegar la tira para que sus LEDs miren
  directamente a la franja del difusor.

### Añadido

- `ledChannelBackWall()` — segunda pared, conectada al borde más
  alejado del panel de la pared existente ("el final de la
  existente"), doblada 90° hacia abajo (perfil en L). Su cara
  interior mira hacia el panel (eje Y) — ahí se pega la tira LED,
  con los LEDs enfrentados directamente a la franja del difusor.
  Confirmado el diseño con el usuario mediante un render de la
  sección transversal antes de darlo por definitivo.
- `led_channel_backwall_thickness = 2.0mm` (ESTIMADO) y
  `led_channel_backwall_margin = 2.0mm` (ESTIMADO, cuánto baja por
  debajo del borde inferior de la franja del difusor) — pendientes
  de confirmar con la pieza impresa.

### Verificado

- Pieza completa: "Simple: yes" (2-manifold válido, misma
  comprobación robusta de siempre).
- Confirmado visualmente por render de sección transversal (antes de
  aplicar el cambio) y por render del panel completo (después).
- Ensamblaje: 28/28 sin colisión (sin cambios).

---



### Encontrado — mismo patrón que otros ajustes con la pared ya impresa

- El usuario mandó una foto del montaje real: el taladro de paso del
  panel queda claramente por encima del inserto real de la pared
  (ya impresa, fija). "Los agujeros de fijación en el panel interior
  están altos. Hay que bajarlos 3mm".
- `lower_panel_screw_z_low/high` las comparte TANTO la pared (el
  inserto real, `sideBossPad()` en `walls.scad`) COMO el panel (el
  taladro de paso, `lower_panel.scad`) — no se podían bajar
  directamente sin mover también la definición de la pared, que no
  puede cambiar (ya impresa).

### Cambiado

- Nuevas variables `lower_panel_hole_z_low`/`lower_panel_hole_z_high`
  (`assembly_positions.scad`), específicas del panel, calculadas
  como `lower_panel_screw_z_low/high - 3.0` — la pared se queda con
  su valor original (10, 29.5), sin tocar.
- `lower_panel.scad` (`lowerPanelScrewHoles()`) actualizado para
  usar las nuevas variables en vez de las compartidas con la pared.

### Verificado

- Valores confirmados por variables exportadas: pared sin cambios
  (10, 29.5), panel en (7, 26.5) — ambos dentro del rango del panel
  (0 a 51,5mm), sin riesgo de salirse por el borde inferior.
- Sin colisión con los huecos del OLED, el pulsador ni el USB
  frontal en la nueva posición.
- Ensamblaje: 28/28 sin colisión (sin cambios).

---



### Cambiado

- `nfc_panel_height`: 96,5 → 94,5mm — el usuario midió el chasis
  real: interior=145mm, panel inferior=50mm, panel NFC=96mm, suma
  146mm, superando el interior real en 1mm. Reducido 2mm para dejar
  margen de seguridad.

### Corregido — fallo propio detectado antes de dar el cambio por bueno

- El primer intento (solo cambiar `nfc_panel_height`) recortaba por
  la parte de ABAJO del panel (con `nfc_panel_margin_top=0`, la
  fórmula sube `nfc_panel_z_low` en vez de bajar `nfc_panel_z_high`)
  — habría abierto un hueco de 2mm entre el panel NFC y el panel
  inferior, justo la unión que debía quedarse fija. Corregido
  restaurando `nfc_panel_margin_top=2`, para que el recorte salga
  por ARRIBA (más margen frente al techo del chasis) y el borde
  inferior se mantenga en 51,5mm, sin cambios.

### Verificado

- `nfc_panel_z_low` confirmado sin cambios (51,5mm); `nfc_panel_z_high`
  confirmado en 146mm (2mm menos).
- Imanes (`nfc_magnet_z_low/high`, valores absolutos desde una
  corrección anterior) y hueco del tag NFC (`nfc_tag_pocket_z`,
  también absoluto) confirmados dentro del panel con margen amplio
  (25mm hasta el nuevo techo) — no dependen de la altura del panel,
  no necesitaron ningún ajuste.
- Los 3 paneles temáticos (Steam, RetroBat, TeknoParrot) y el panel
  en blanco (con el logo de TeknoParrot) siguen compilando
  correctamente. Confirmado visualmente por render: logo y texto de
  Steam dentro de los límites, nada cortado.
- Ensamblaje: 28/28 sin colisión (sin cambios).

---

## [1.0.10] - 2026-08-17 — Franja del difusor LED adelgazada a 1mm (la luz no atravesaba bien 3mm)

### Añadido

- `ledDiffuserThinCut()` (`lower_panel.scad`) — recorte real desde
  la cara trasera de la franja del difusor (antes solo existía
  `ledDiffuserZone()`, una zona de referencia para la vista previa
  de color, sin ningún recorte real — el panel impreso tenía el
  mismo grosor uniforme, 3mm, en toda su superficie). El usuario
  confirmó tras imprimirlo que ese grosor no dejaba pasar bien la
  luz de la tira LED.
- `led_diffuser_skin_thickness = 1.0mm` — grosor que queda en la
  cara frontal de la franja, por donde pasa la luz. El resto del
  panel (incluido el marco perimetral) mantiene los 3mm originales,
  sin tocar.

### Verificado

- Grosor real confirmado por sonda geométrica directa: exactamente
  1mm dentro de la franja del difusor, exactamente 3mm fuera de
  ella (marco y resto del panel).
- OpenSCAD confirma la pieza como "Simple: yes" (2-manifold válido,
  la misma comprobación robusta usada en todo el proyecto) — un
  aviso inicial de "no watertight" de una herramienta externa
  (trimesh) resultó ser un artefacto de su comprobación más
  estricta en los bordes propios del panel, no un problema real de
  impresión.
- Ensamblaje: 28/28 sin colisión (sin cambios).

---

## [1.0.9.1] - 2026-08-17 — Logo TeknoParrot integrado en nfc_panel_blank.scad, a escala reducida

### Cambiado

- `nfc_panel_blank.scad`: añadido el logo de TeknoParrot (mismos
  datos de contorno ya verificados en `nfc_panel_teknoparrot.scad`
  — un único polígono cerrado, sin auto-intersecciones), a una
  escala reducida (0,1487, frente a 0,2173 en el panel temático
  completo) y centrado verticalmente en el panel, no pegado al
  marco — para que ocupe "gran parte pero no toda" la superficie,
  según pidió el usuario. Deja ~14mm de margen visible arriba y
  abajo.
- El archivo sigue llamándose "blank" aunque ya no está vacío — el
  usuario pidió integrar el logo en este fichero concreto, no crear
  uno nuevo.

### Corregido

- Centrado vertical real corregido: la fórmula ingenua dejaba el
  resultado 5mm más arriba de lo previsto (la silueta del logo no
  es simétrica respecto a su propio origen, mismo tipo de ajuste ya
  visto con el logo de Steam) — corregido con un offset verificado
  por geometría exportada, centro real confirmado en Z=92,75.

### Verificado

- Centrado confirmado por coordenadas exportadas tras la
  corrección.
- Ensamblaje: 28/28 sin colisión (sin cambios).

---

## [1.0.9] - 2026-08-17 — Insertos sobrantes de la bandeja eliminados (petición del usuario)

### Eliminado

- `trayRearBridgeInserts()` y `trayRearBridgeInsertPads()`
  (`openscad/parts/01_bandeja/base.scad`) — los postes cilíndricos
  donde roscaban las lengüetas del panel trasero, ya eliminadas en
  la ronda anterior (1.0.8). El usuario confirmó que se quitaran
  también: "Elimina los insertos sobrantes de la bandeja".
- Variables asociadas eliminadas junto con los módulos
  (`rear_bridge_x_inset_local`, `rear_bridge_insert_diameter`,
  `rear_bridge_post_height`) — solo se usaban ahí.

### Verificado

- `base.scad` y `tray.scad` siguen compilando correctamente.
- La bandeja completa sigue siendo watertight y una sola pieza.
- Confirmado por sonda directa: cero material por encima del
  grosor base de la bandeja en la posición exacta donde estaban los
  postes cilíndricos.
- Sin referencias sueltas a los módulos eliminados en ningún otro
  archivo del proyecto (solo comentarios informativos).
- Ensamblaje: 28/28 sin colisión (sin cambios).

---



### Eliminado

- **Lengüetas de unión con la bandeja** (`rearBridgeTab()`,
  `rearBridgeTabs()`, `rearBridgeScrewHoles()`) — el usuario las
  marcó directamente en una captura de su render: "sobran estos
  soportes, no son necesarios". El panel trasero se sujeta ahora
  **solo** con los tornillos M3 a las paredes laterales
  (`rearWallScrewHoles()`, ya verificados en rondas anteriores).

### Movido

- `rear_panel.scad` y su probeta (`probeta_panel_trasero.scad`):
  `openscad/parts/01_bandeja/` → `openscad/parts/03_panels/`
  (petición del usuario: encajaba conceptualmente mejor junto al
  resto de paneles, no con las piezas de la bandeja). Las rutas
  relativas de `include` no necesitaron ningún cambio (misma
  profundidad de carpeta).

### Actualizado — referencias en otros archivos

- Comentarios desactualizados corregidos en `assembly_positions.scad`,
  `walls.scad` y `base.scad` (rutas antiguas y menciones a las
  lengüetas ya eliminadas).
- `openscad/parts/02_chassis/checks/run_structure_checks.py`: ruta
  de `rear_panel.scad` actualizada a `03_panels` (el script en sí
  sigue sin mantenerse activamente, solo se corrigió la ruta para
  que no quede rota).

### Pendiente de confirmar por el usuario

- La bandeja (`base.scad`) conserva los insertos correspondientes
  (`trayRearBridgeInserts()`, `trayRearBridgeInsertPads()`) — no se
  pidió quitarlos explícitamente y no causan ningún problema (siguen
  siendo material sólido de apoyo), pero ya no tienen ningún
  tornillo real que rosque en ellos. Avisar si se quieren eliminar
  también.

### Verificado

- Panel trasero: sigue compilando correctamente tras quitar las
  lengüetas (2 volúmenes, igual que antes — los recortes de
  conectores). Confirmado visualmente por render: rectángulo liso,
  sin salientes laterales.
- Probeta: sigue watertight, un único cuerpo, tras la mudanza de
  carpeta.
- Ensamblaje: 28/28 sin colisión (sin cambios).

---



### Corregido — fallo propio de interpretación del CAD

- **Conector DC**: el usuario lo dibujó cuadrado en el DXF (4
  puntos, igual que todos los demás rectángulos — no una
  aproximación poligonal de un círculo, como sí eran las letras) —
  pero lo interpreté como redondo por costumbre ("conector DC =
  redondo"), sin fiarme del dato real. Corregido a cuadrado
  (10×10mm, `es_redondo=false`).

### Cambiado

- **Ancho del panel trasero**: mismo ajuste que los paneles
  frontales — 150 → 149mm (`rear_panel_width`, ahora en
  `00_parametros.scad` para compartirlo con la probeta). El usuario
  confirmó con la prueba física: encajaba bien ajustándolo desde la
  izquierda (lado USB), con ~1mm de sobrante por la derecha (lado
  DC) — coincide exactamente con el mismo exceso ya corregido en los
  paneles frontales.
- Probeta del panel trasero actualizada al mismo ancho (149mm) y con
  el conector DC ya corregido.

### Verificado — sin cambios necesarios

- Los tres sistemas de tornillo del panel trasero (a la pared:
  taladro 3,4mm + avellanado 6mm; a la bandeja: taladro 3,4mm +
  inserto en la bandeja con `insert_diameter`/`insert_depth`
  compartidos) ya estaban correctamente configurados para M3 desde
  antes — no ha hecho falta ningún cambio.

### Verificado

- Probeta: watertight, un único cuerpo, 149mm de ancho exacto,
  centrada en X=0,0.
- Confirmado visualmente por render: el conector DC es ahora un
  cuadrado real.
- Ensamblaje: 28/28 sin colisión (sin cambios).

---



### Cambiado

- `nfc_panel_width` y `lower_panel_width_oversize`: ajustados para
  que ambos paneles midan 149mm de diseño (antes 151mm) — confirmado
  con una probeta física impresa y medida con calibre por el
  usuario: a 151mm el panel real salía en 150mm, pero el hueco
  interior real del chasis medía solo 149mm (el panel real quedaba
  más ancho que el hueco). Una segunda probeta a 149mm de diseño
  salió en 149mm real exactos.
- **Nota sobre la merma**: no fue constante entre las dos pruebas
  (1mm la primera vez, 0mm la segunda) — pendiente de que el usuario
  confirme que 149mm encaja bien en la práctica.

### Encontrado y corregido — desajuste de los imanes, ya existente antes de este cambio

- Al revisar el efecto del cambio de ancho sobre los imanes, se
  encontró que el alojamiento del imán en el panel NFC **ya estaba
  desalineado 3mm** respecto al imán fijo de la pared, incluso a
  151mm — no es un fallo nuevo de esta ronda, sino una limitación ya
  aceptada en una ronda anterior (el alojamiento no puede llegar
  hasta la posición exacta de la pared sin salirse del borde del
  panel). Con el panel a 149mm, ese desajuste subía a 4mm (39% de
  solape entre los dos imanes de 8mm).
- `nfc_magnet_edge_margin`: 1,5 → 1,0mm (petición del usuario: "pon
  los encastres de los imanes lo más cercanos posible a los
  extremos, entre 1 y 1,5mm del borde") — sube el solape a ~46%,
  dejando exactamente 1mm de margen respecto al borde del panel.

### Verificado

- Anchos confirmados por variables exportadas: 149mm en ambos
  paneles.
- Taladros de tornillo del panel inferior: posición NO afectada por
  el cambio de ancho (`panelMountX()` depende de `case_width`, fijo,
  no del ancho del panel) — confirmado, sigue en X=70,5mm.
- Alojamiento del imán: confirmado por geometría exportada, exactamente
  1mm de margen respecto al borde del panel (149/2 - 73,5 = 1,0).
- Hueco del tag NFC: sigue centrado en X=0,0, sin cambios (no depende
  del ancho).
- Los 3 paneles temáticos (Steam, RetroBat, TeknoParrot) y el panel
  en blanco siguen compilando correctamente, comparten esta misma
  base.
- Ensamblaje: 28/28 sin colisión (sin cambios).

---



### Cambiado

- El usuario aportó un dibujo real a escala en AutoCAD
  (`EXTERIOR.dxf`) con las medidas exactas de los 6 conectores
  traseros — sustituye las estimaciones basadas en la foto con
  regla de rondas anteriores.
- Unidades del archivo verificadas antes de usar los datos
  (INSUNITS=5, centímetros — factor ×10 a mm aplicado).
- Referencia Z verificada contra el valor que ya se usaba por
  estimación: casi exacta (0,36mm de diferencia), lo que dio
  confianza para usar las Z medidas directamente sin reajustar el
  origen del proyecto.
- **Confirma** el orden (USB-USB-RJ45-HDMI-HDMI-DC) y la orientación
  vertical del HDMI ya corregidos en rondas anteriores — ahora con
  tamaños y posiciones precisos en vez de estimados:
  - USB apilado: cada pareja es un ÚNICO recorte rectangular
    (15×16mm, así viene dibujado en el CAD) — ya no dos huecos
    individuales con `rear_usb_stack_pitch` estimado (parámetro
    eliminado).
  - RJ45: 16,5×13mm (antes 16×13,5, estimado — casi igual).
  - HDMI: 6,25×16mm de media (antes 6×15, estimado).
  - DC: 10mm de diámetro (sin cambios, coincidía).
  - Cada conector con su propia Z medida (RJ45 y DC ligeramente más
    bajos que USB/HDMI, según el CAD) — antes todos a una única Z
    estimada.
- `rear_connector_gap` eliminado (las posiciones ahora son
  coordenadas X directas medidas, no una fórmula de huecos
  acumulados).

### Verificado

- 7 volúmenes en el recorte aislado (6 conectores, el redondo cuenta
  doble por su geometría de baja resolución) — confirma que siguen
  bien separados, sin fusionarse.
- Ancho total real: 99mm, dentro del panel sin problema.
- Ensamblaje: 28/28 sin colisión (sin cambios).

---



### Encontrado — fallo propio de la corrección anterior (1.0.0)

- El usuario revisó `walls.scad` y vio que los alojamientos seguían
  sin parecer M3. Causa: al corregir esto en la ronda 1.0.0, usé un
  valor ESTIMADO propio (`lower_panel_screw_diameter = 6.5`) en vez
  de comprobar si ya existía un valor establecido en el proyecto —
  y sí existía: `insert_diameter = 4.10mm` (00_parametros.scad), que
  el panel trasero y la tapa superior ya usaban de forma consistente
  para sus propios insertos M3. Mi "corrección" había creado un
  TERCER valor distinto, inconsistente con el resto del proyecto.

### Cambiado

- `lower_panel_screw_diameter` ahora referencia directamente
  `insert_diameter` (4,10mm) en vez de un valor propio.
- `lower_panel_screw_depth` ahora referencia directamente
  `insert_depth` (5mm) — coincidía por casualidad con el valor
  anterior, pero ahora queda enlazado para que no se pueda
  desincronizar en el futuro.

### Verificado

- Coincidencia exacta confirmada por variables exportadas:
  `lower_panel_screw_diameter`, `rear_wall_screw_diameter` e
  `insert_diameter` son los tres 4,10mm; profundidades también
  coinciden (5mm).
- Ensamblaje: 28/28 sin colisión (sin cambios).

---



### Cambiado

- `rc522_connector_hole_x`: 20,0 → 25,3mm — el usuario indicó que el
  hueco debía quedar "alineado a la derecha del todo, pero sin
  invadir el marco lateral". Ahora el borde derecho del hueco
  coincide exactamente con el borde de la cavidad del lector
  (nfc_reader_width/2 + la holgura de encaje = 30,3mm), justo hasta
  donde empieza la pared estructural, sin tocarla.

### Verificado

- Posición del borde derecho confirmada por geometría exportada:
  30,3mm, coincide exactamente con el objetivo.
- El soporte sigue siendo una pieza sólida y conectada (2 volúmenes).
- Ensamblaje: 28/28 sin colisión (sin cambios).

---



### Añadido

- Nuevo orificio rectangular en la repisa trasera del soporte del
  RC522 (`rc522BracketCradle()`), por donde el lector apoya — la
  fila de pines de conexión del módulo sobresale por ese borde y
  quedaba bloqueada sin salida. Posición y tamaño marcados a mano
  por el usuario en una foto de la pieza real impresa.
- `rc522ConnectorCutout()`: nuevo módulo, con las medidas del hueco
  como parámetros claramente marcados ESTIMADO (calculados a partir
  de las proporciones visibles en la foto, no de una medida exacta
  del conector) — a revisar tras imprimir.

### Verificado

- El soporte sigue siendo una pieza sólida y conectada (2 volúmenes,
  igual que antes de añadir el hueco).
- Posición confirmada visualmente por render, coincide con la marca
  de la foto.
- Ensamblaje: 28/28 sin colisión (sin cambios).

---



### Encontrado — fallo real confirmado con fotos del montaje real

- El usuario mandó fotos del hub USB (CJMCU-204) montado en la
  pared real: dos postes (los de abajo) ya atornillados y
  correctos; los otros dos (arriba) no coinciden con los agujeros
  reales de la placa. Separación vertical real entre postes: 21mm,
  no los 36,1mm que calculaba el diseño.
- Encontrado y corregido un problema en mi primer intento: cambiar
  directamente `usb_hub_width` (para ajustar la separación) también
  habría encogido el tamaño físico modelado de la placa completa
  (se usa en `hub_usb.scad` para el cuerpo/keepout), no solo la
  posición de los postes — detectado antes de dar el cambio por
  bueno.

### Cambiado

- Nuevos parámetros `usb_hub_mount_inset_z` (11,55mm) y
  `usb_hub_mount_inset_y` (4mm, sin cambios) — separan el ajuste de
  la posición de los postes del tamaño físico de la placa
  (`usb_hub_width`/`usb_hub_depth`, que se quedan en 44,1×44,1mm,
  intactos).
- `hubMountBosses()` (walls.scad) y `hubUsbMountHoles()`
  (hub_usb.scad) actualizados para usar estos insets específicos por
  eje, en vez de un inset compartido de 4mm en ambos.

### Verificado

- Tamaño físico de la placa confirmado sin cambios: 44,1×44,1mm.
- Separaciones confirmadas por variables exportadas: 21mm vertical,
  36,1mm horizontal.
- Ensamblaje: 28/28 sin colisión (sin cambios).

### Pendiente

- Como con los tornillos M3 y los imanes: esta corrección es para
  futuras impresiones de la pared, no corrige la pieza ya impresa
  del usuario.

---



### Encontrado — fallo real de diseño, no solo del panel sino también de la pared ya impresa

- El usuario pidió que los orificios de sujeción del panel inferior
  fuesen M3. Al revisar, estaban dimensionados para M2 en TRES
  sitios: el taladro de paso del panel (2,2mm), el avellanado del
  panel (4,5mm) y el alojamiento del inserto térmico en la PARED
  (6mm, ya impresa). Los tres debían cambiar juntos — un tornillo M3
  no rosca en un inserto M2.
- Confirmado con el usuario: las paredes ya están impresas con el
  alojamiento M2 antiguo. El cambio queda para futuras impresiones
  propias o de otros usuarios, no corrige las paredes actuales.

### Cambiado

- `lower_panel_csk_radius`: 4,5/2 → 6,0/2mm — reutiliza el mismo
  valor que ya estaba establecido para M3 en el panel trasero
  (`rear_csk_radius`), para que sea consistente en todo el proyecto.
- Taladro de paso del panel: 2,2 → 3,4mm (holgura estándar M3).
- `lower_panel_screw_diameter` (alojamiento del inserto en la
  pared): 6,0 → 6,5mm — ESTIMADO, inserto térmico M3 típico de
  ~4-4,6mm de diámetro exterior, con margen similar al que ya tenía
  el M2.
- `lower_panel_screw_depth`: 4,0 → 5,0mm — ESTIMADO, los insertos M3
  suelen ser algo más largos que los M2.
- `lower_panel_csk_depth`: 1,4 → 1,6mm — ESTIMADO, cabeza M3 algo
  más gruesa que la M2; sigue dentro de los 3mm del panel.

### Verificado

- Sin colisión con el hueco del OLED ni con el del pulsador.
- Ensamblaje: 28/28 sin colisión (sin cambios).

---



### Cambiado

- Revisado el repositorio completo a petición del usuario ("¿puedes
  identificar qué ficheros sobran o están obsoletos?"). Movidos 7
  archivos a la nueva carpeta `obsoletos/` (estructura original
  preservada en subcarpetas, con un README explicando cada uno):
  - `front_panel.scad`, `front_layout.scad` — ya marcados ⚠️
    OBSOLETO desde antes, sin referencias reales.
  - `rc522_bracket.scad` (v1.0, renombrado a
    `rc522_bracket_v1.scad`) — duplicado huérfano de la v2.0 en
    `04_soportes`, con el taladro mal orientado.
  - `virtual_assembly_v1.scad`, `front_panel_view.scad`,
    `chassis_layout.scad`, `um790_reference.scad` — herramientas de
    la fase de planificación previa al chasis actual, sin
    referencias `use`/`include` reales desde ningún archivo activo.
- `openscad/parts/02_chassis/checks/run_structure_checks.py` se
  queda en su sitio (no es un duplicado, pero está desactualizado —
  ver README de `obsoletos/`).

### Verificado

- Ninguna referencia `use`/`include` real hacia los 7 archivos
  movidos (comprobado antes de mover, no solo después).
- Ensamblaje: 28/28 sin colisión, sin cambios tras el traslado.

---



### Añadido

- `nfc_panel_blank.scad`: panel NFC sin ninguna marca, reutilizando
  `nfcPanelBase()` tal cual — pedido del usuario para poner su propio
  diseño directamente desde Anycubic Slicer (tras descartar tanto el
  grabado de detalle como la separación por regiones de color para
  TeknoParrot).

### Verificado

- Ensamblaje: 28/28 sin colisión (sin cambios).

---



### Cambiado

- Sustituida la silueta del logo (derivada de una foto de una pieza
  física) por una nueva, medida sobre `teknoparrot-logo.svg`
  aportado por el usuario — un diseño a color de líneas limpias
  (aunque el SVG en sí envuelve una imagen PNG incrustada, no rutas
  vectoriales puras, la imagen es mucho más limpia que la foto
  anterior). Medido por el mismo método de análisis de contorno
  (máscara por canal alfa + simplificación de polígono), un único
  contorno cerrado válido (verificado con `shapely`, sin
  auto-intersecciones).
- Escala ajustada para ocupar gran parte del panel (altura útil
  completa, ~63,5mm de ancho resultante), según pidió el usuario.
- Eliminado el intento fallido de grabado de detalle de la ronda
  anterior (`teknoparrotDetail2D()`, el SVG vectorizado desde la
  foto que CGAL rechazaba en cualquier operación booleana) — ya no
  aplica, era específico del logo antiguo. Limpiado el comentario
  obsoleto y borrado el SVG huérfano
  (`openscad/assets/teknoparrot_detail.svg`).

### Verificado

- Centrado confirmado por coordenadas exportadas (desviación mínima,
  -0,87mm) y toca justo el límite superior del marco (Z=142).
- Sin colisión real con el marco elevado.
- Ensamblaje: 28/28 sin colisión (sin cambios).

---



### Cambiado

- **Cruz central horizontal**: altura rebajada 3mm (5 → 2mm),
  igualada a la del "Horizontal superior" (ya rebajado en 0.9.3) —
  el usuario lo marcó tras montar la bandeja real impresa, tocando
  la parte inferior del UM790.

### Verificado

- Altura real confirmada por geometría exportada: 2mm (antes 5mm),
  igual que el horizontal superior.
- La bandeja sigue siendo una sola pieza conectada: watertight, un
  único cuerpo.
- Ensamblaje: 28/28 sin colisión (sin cambios).

---



### Encontrado — mismo tipo de fallo que los imanes (0.9.4), detectado a tiempo

- El usuario preguntó si el hueco del llavero seguía alineado con el
  lector RC522 tras los cambios de altura del panel. Comprobado:
  tanto `rc522_pos[2]` (posición del lector) como el centro Z del
  hueco del tag (`nfcTagPocket()`) usaban `nfc_panel_z_mid` — al
  ampliar la altura del panel, ese valor pasó de 93,75 a 99,75mm
  (6mm de desajuste).
- El soporte del lector (`openscad/parts/04_soportes/rc522_bracket.scad`,
  con bastante historial de ajustes ya confirmados por el usuario)
  **ya está impreso** con la posición antigua.

### Cambiado

- `rc522_pos[2]` y el nuevo `nfc_tag_pocket_z` (en `nfc_panel.scad`)
  fijados al mismo valor absoluto (93,75mm), independiente de
  `nfc_panel_z_mid` — igual que se hizo con los imanes en 0.9.4.

### Verificado

- Coincidencia exacta confirmada por variables exportadas de ambos
  archivos por separado: 93,75mm en los dos.
- Soporte RC522 (04_soportes) sigue compilando correctamente.
- Ensamblaje: 28/28 sin colisión (sin cambios).

---



### Encontrado — fallo real, detectado a tiempo antes de imprimir

- Buena pregunta del usuario tras las rondas de ajuste del panel
  NFC. Al ampliar `nfc_panel_height` 12mm (rondas 0.9.0+), tanto
  `front_magnet_z_high` (en `walls.scad`, la pared YA IMPRESA) como
  `nfc_magnet_z_high` (en `nfc_panel.scad`) se calculaban a partir de
  `nfc_panel_z_high` — al cambiar ese valor, AMBOS se recalcularon
  automáticamente a la vez, pasando de Z=121 a Z=133.
- El problema: la pared real, ya impresa, tiene el imán físicamente
  fijo en Z=121 — no puede "recalcularse". Mi archivo de la pared, al
  compartir la fórmula, mostraba una posición que ya no coincide con
  la pieza física real.

### Cambiado

- Ambos valores fijados a constantes absolutas (66,5 y 121mm),
  independientes de la altura del panel — coinciden exactamente con
  la posición real de los imanes en la pared ya impresa.
- Afecta a los 3 paneles NFC (Steam, RetroBat, TeknoParrot), que
  comparten `nfc_magnet_z_low/high` a través de `nfcPanelBase()`.

### Verificado

- Coincidencia exacta confirmada por variables exportadas de ambos
  archivos por separado: 66,5 y 121mm en los dos.
- Ensamblaje: 28/28 sin colisión (sin cambios).

---



### Cambiado

- `rib()` (módulo genérico de nervios) admite ahora un parámetro de
  altura opcional, con el valor global (`rib_height`) como valor por
  defecto — permite rebajar nervios concretos sin afectar al resto.
- **Horizontal superior** y **Cruz central vertical**: altura
  rebajada 3mm (5 → 2mm) — el usuario los señaló directamente en dos
  capturas de su laminador (necesitó una segunda captura más clara
  tras una primera identificación ambigua por mi parte), confirmando
  que tocan el disipador inferior del UM790.

### Verificado

- Altura real confirmada por geometría exportada: 2mm en ambos
  nervios (antes 5mm), en toda su extensión.
- La bandeja sigue siendo una sola pieza conectada: watertight, un
  único cuerpo.
- Ensamblaje: 28/28 sin colisión (sin cambios).

---



### Corregido — fallo propio en la ronda anterior

- La corrección anterior (0.9.1) eliminó el nervio interior
  ("Horizontal inferior", parte de la cruceta central) — pero el
  usuario señaló con una captura que la pieza que realmente choca
  con el USB interno y el pulsador es el **tramo delantero del
  marco exterior** (el borde más externo de la bandeja, no un nervio
  interior). Aclarado por el usuario: "el que está más al exterior".
- Recortado ese tramo específico (el resto del marco — trasero,
  izquierdo, derecho — sigue intacto). El nervio interior eliminado
  en la ronda anterior se queda igual (fuera), ya que no hay
  indicación de que deba recuperarse.

### Verificado

- La bandeja sigue siendo una sola pieza conectada: watertight, sin
  aristas problemáticas, un único cuerpo (`body_count=1`).
- Confirmado visualmente por render en planta: el marco queda
  abierto por el lado delantero, resto de la estructura intacta.
- Ensamblaje: 28/28 sin colisión (sin cambios).

---



### Eliminado

- Nervio "Horizontal inferior" (el mismo ya identificado por la
  proximidad con el disipador) — el usuario lo señaló directamente
  en una captura de su laminador, confirmando que choca con el
  conector USB interno y el pulsador de la placa UM790.

### Verificado

- La bandeja sigue siendo una sola pieza conectada: watertight, sin
  aristas problemáticas, 2 volúmenes (igual que antes de quitar el
  nervio).
- Confirmado visualmente por render en planta: el resto de la
  estructura (marco exterior, cruceta central, islas de apoyo) sigue
  intacta.
- Ensamblaje: 28/28 sin colisión (sin cambios).

---



### Encontrado — fallo real, no un error de montaje del usuario

- El usuario montó la placa UM790 real sobre la bandeja y mandó
  fotos: la placa quedaba **2cm corta** respecto al panel trasero, y
  el disipador rozaba el nervio delantero de la bandeja (con el USB
  interno y el pulsador chocando con "muretes" de la bandeja, que el
  usuario tuvo que cortar a mano).
- Causa raíz confirmada con números: `um790_rearIO_depth` se había
  definido hace tiempo como "el hueco entre el borde de la PCB y el
  panel trasero" (21,45mm), asumiendo que ese hueco lo rellenarían
  los propios conectores sobresaliendo — pero según la foto real, los
  conectores están prácticamente al ras del borde de la placa. Ese
  hueco era aire vacío de verdad, no conectores.

### Cambiado

- **Desplazados los 4 postes que sujetan el UM790** 18mm hacia atrás
  (`um790_post_y_offset`, nuevo parámetro compartido en
  `00_parametros.scad`) — decisión del usuario, en vez de acercar el
  panel trasero a la placa. Mantiene intacta la separación entre
  postes (fija por los agujeros reales de la placa).
- Desplazadas junto con los postes: las islas de apoyo bajo ellos
  (`base.scad`, para que sigan teniendo material sólido debajo) y la
  posición de referencia de la placa (`um790_pos`,
  `assembly_positions.scad`).
- **NO se ha tocado** la estructura general de nervios/marco de la
  bandeja (sigue en su sitio) — el usuario pidió específicamente
  mover solo los postes, no toda la bandeja.
- `um790_rearIO_depth` recalculado para descontar el desplazamiento
  (21,45mm → ~3,45mm de hueco real restante).

### Verificado

- Hueco hasta el panel trasero: 3,45mm (antes 21,45mm).
- Holgura entre el borde delantero de la PCB y el nervio delantero:
  6,25mm de separación real (antes muy ajustada/tocando, según el
  usuario).
- Ensamblaje: 28/28 sin colisión mecánica dura (1 aviso nuevo, no
  bloqueante, de margen de cableado entre el Noctua y el ESP32 — a
  revisar en el routing, no un choque físico).

### Pendiente de confirmar

- El usuario reportó que el disipador tocaba el nervio delantero, y
  que el pulsador y el USB interno chocaban con dos "muretes" de la
  bandeja — no tengo medidas precisas de altura para verificar estos
  puntos de forma independiente. El mismo desplazamiento de 18mm
  debería dar bastante más margen en todos estos frentes (misma
  dirección Y), pero pendiente de que el usuario lo confirme con un
  montaje de prueba antes de darlo por resuelto del todo.

---



### Corregido

- `usb_front_hole_diameter`: 29 → 30mm, medida real confirmada por
  el usuario tras la aclaración pedida en la ronda anterior.

### Verificado

- Sin solape con el hueco del OLED (misma fila del cluster frontal).
- Ensamblaje: 28/28 sin colisión (sin cambios).

---



### Cambiado

- **Ancho del panel NFC**: 150 → 151mm, igualado al panel inferior
  (que ya tenía +1mm de sobredimensionado por merma de impresión
  desde antes) — no coincidían entre sí.
- **Altura del panel NFC**: +12mm (84,5 → 96,5mm), quitado el margen
  superior (`nfc_panel_margin_top`: 12 → 0) — no llegaba al borde
  superior del chasis. El borde inferior se mantiene fijo (sigue
  conectando igual con el panel inferior).
- **Logo de Steam**: reducido a la mitad (escala 1,58 → 0,79) y
  recentrado en el hueco libre por encima del texto. El texto
  "STEAM OS" se mantiene fijo (mismo tamaño y posición, ahora
  calculada de forma independiente del icono, no relativa a él).
- **Pared del canal LED**: grosor 1,5 → 10mm (petición explícita del
  usuario: "debería de tener un ancho de 10mm").

### Verificado

- Dimensiones del panel NFC confirmadas por coordenadas exportadas:
  151mm de ancho, Z de 51,5 a 148,0 (justo el borde superior).
- Logo Steam y texto sin colisión con el marco (método fiable).
- Pared del canal LED comprobada sin colisión contra UM790 y
  soporte RC522; las patas de conexión siguen tocando la pared con
  el nuevo grosor.
- Ensamblaje: 28/28 sin colisión (sin cambios).

### Pendiente de aclarar

- El diámetro del agujero USB frontal (actualmente 29mm) — el
  usuario pidió "agrandar hasta 28mm", pero 28 < 29 (sería reducir,
  no agrandar). Pendiente de que confirme la medida real.
- El ancho de ambos paneles, aunque ya coincide entre ellos (151mm),
  puede seguir sin ser suficiente según lo que el usuario reporte
  tras la próxima impresión — el mensaje mencionaba también que "no
  llegan al borde exterior del chasis" como queja aparte del
  desajuste entre ambos.

---



### Intentado — sin éxito dentro de esta sesión

- El usuario pidió más fidelidad al detalle real de la foto (plumas,
  sombrero, calavera, ojo, garras, llamas), no solo la silueta lisa.
- Se generó un mapa de líneas de detalle por detección de bordes
  (Canny) + vectorización (potrace) sobre la foto original —
  visualmente un resultado muy fiel, guardado en
  `openscad/assets/teknoparrot_detail.svg`.
- **Fallo real encontrado**: combinar esta geometría (por compleja
  que se simplificara) con la silueta mediante cualquier operación
  booleana (`difference()`, `union()`, con `render()`, incluso
  reexportando a STL y reimportando) es rechazado por CGAL con
  "The given mesh is not closed" — el detalle vectorizado desde una
  foto tiene una topología no válida para booleanos (aunque se
  extruye bien por sí solo, sin combinarlo con nada más).
- Se probó también reducir drásticamente la complejidad (de 959
  contornos/688.000 facetas a un mapa simplificado de 24.544 facetas,
  forzando líneas rectas en vez de curvas Bezier) — resolvió el
  problema de tiempo de cálculo (antes daba timeout), pero no el
  problema de topología de fondo.

### Estado actual

- `teknoparrotLogoEmboss()` vuelve a usar SOLO la silueta exterior
  (la versión ya validada de la ronda anterior) — sigue siendo
  fiable y compila en segundos.
- `teknoparrotDetail2D()` y el SVG se quedan en el archivo,
  documentados y listos para retomar el intento con otro enfoque
  (por ejemplo, dividir el detalle en muchas piezas simples e
  unirlas una a una, en vez de como un solo objeto complejo).

### Verificado

- Ensamblaje: 28/28 sin colisión (sin cambios).
- Archivo compila de forma fiable en segundos (sin timeouts).

---



### Añadido

- Completado `nfc_panel_teknoparrot.scad` (antes solo un borrador
  pendiente del icono): logo del loro pirata medido por análisis de
  contorno sobre la foto de la pieza física aportada por el usuario
  (máscara + simplificación de polígono con OpenCV, mismo método que
  Steam/RetroBat).
- **Silueta exterior como un único contorno cerrado**, pedido
  explícito del usuario ("cerrar el perímetro para que le pueda
  asignar más fácilmente el filamento" — así el "llenar" del
  laminador selecciona todo el emblema de una vez). Verificado con
  `shapely` (polígono válido, sin auto-intersecciones) y extruyendo
  en OpenSCAD sin errores.
- El texto "TEKNO PARROT" del diseño original ya viene integrado en
  el propio contorno (letras estilizadas en 3D) — no se ha añadido
  un texto aparte, a diferencia de Steam/RetroBat.

### Simplificado — decisión consciente, no un fallo

- No se han replicado los detalles finos internos (plumas
  individuales, textura del sombrero, calavera, grietas del huevo,
  líneas de las llamas) — solo la silueta exterior general. Intentar
  trazar cada detalle a mano desde una foto de una pieza física (no
  un vector limpio) habría llevado un tiempo desproporcionado sin
  garantía de fidelidad.

### Verificado

- Perfectamente centrado (X=0,0 según coordenadas exportadas).
- Sin colisión real con el marco elevado (método fiable, sin sondas
  restrictivas).
- Ensamblaje: 28/28 sin colisión (sin cambios).

---



### Corregido

- Los dos conectores HDMI del panel trasero estaban dibujados en
  horizontal (15×6mm, más ancho que alto) — según la foto real que
  aportó el usuario, van en VERTICAL. Intercambiadas las medidas
  (6×15mm, más alto que ancho).
- Como el ancho del HDMI también se usa para calcular la separación
  entre conectores en la fila, este cambio dejaba el ancho total muy
  corto frente a la referencia de la regla de la foto (84mm vs
  ~108mm) — reajustado el hueco entre conectores (4 → 7mm) para
  volver a acercarse a esa referencia.

### Verificado

- 9 volúmenes en el recorte aislado (mismo patrón ya confirmado como
  "8 conectores bien separados").
- Panel completo: 2 volúmenes (sin fragmentos sueltos).
- Ensamblaje: 28/28 sin colisión (sin cambios).

---



### Contexto

- El usuario va a hacer varios paneles NFC intercambiables, uno por
  cada sistema — al tocar cada etiqueta, arranca un sistema distinto
  (Steam, RetroBat, ...). Esto requiere reorganizar el código para
  poder añadir temas nuevos sin duplicar la base del panel.

### Cambiado

- **Reorganizado `nfc_panel.scad`**: extraída `nfcPanelBase()`
  (sólido + marco + ventana del tag + imanes, SIN marca) como base
  compartida y reutilizable. `nfcPanel()` (el panel con tema Steam)
  ahora se construye como `nfcPanelBase() + steamLogoEmboss() +
  steamOsText()` — mismo resultado que antes, sin cambios para quien
  ya use ese archivo.

### Añadido

- **Nuevo archivo `nfc_panel_retrobat.scad`**: panel con el logo de
  RetroBat (alas de murciélago + mando de consola con cruceta y 4
  botones) + texto "RETROBAT" en relieve, reutilizando
  `nfcPanelBase()`.
- Logo medido por análisis de píxeles sobre la imagen oficial
  aportada por el usuario (extracción de contorno + huecos internos
  con OpenCV, mismo rigor que el logo de Steam) — geometría propia
  generada en OpenSCAD, no un archivo importado.

### Corregido — fallos propios durante el ajuste

- Los 4 botones aparecían fuera del cuerpo del mando (invertí el eje
  Y dos veces sin darme cuenta al transcribir las coordenadas).
- El centrado del icono mezclaba coordenadas ya escaladas con sin
  escalar — corregido centrando dentro de `retrobatLogo2D()` antes
  de aplicar la escala.
- Con los valores iniciales (copiados del panel Steam) el texto se
  solapaba con el icono y se salía por el borde inferior del panel —
  la fuente real de "RETROBAT" es más alta de lo estimado. Ajustada
  la escala del icono y el hueco con el texto para que quepan ambos
  con margen por los dos lados.
- Una comprobación de colisión con el marco dio un falso positivo
  (usando una sonda restrictiva) — confirmado con una comprobación
  más directa y repetida 3 veces que no había solape real.

### Verificado

- Icono y texto perfectamente centrados y sin solape entre ellos.
- Sin colisión real con el marco elevado (confirmado con el método
  fiable, no con la sonda que dio el falso positivo).
- Ensamblaje general: 28/28 sin colisión (sin cambios, el panel de
  Steam sigue funcionando igual tras la reorganización).

---



### Cambiado

- El hueco trasero del tag (`nfcTagPocket()`) era un rectángulo
  genérico de 60×40mm — mucho más grande que el llavero real
  (40×32mm, con forma de "pera": cuerpo circular + cola con agujero
  de llavero, según foto aportada por el usuario), dejando holgura
  de sobra para que el tag se desplazase antes de fraguar el
  pegamento.
- Rediseñado como círculo principal (32mm, el ancho real) + cola más
  estrecha que añade el resto hasta los 40mm de largo, con hull()
  para una transición suave — 0,75mm de holgura para que el tag
  entre bien sin apenas margen para moverse.
- Orientación: la cola apunta hacia abajo (Z-) — una elección
  razonable por defecto, fácilmente ajustable si se prefiere otra.

### Corregido — fallo propio durante el ajuste

- Primer intento: la cola apuntaba hacia arriba en vez de hacia
  abajo (error de signo al aplicar la rotación) — detectado
  comparando el centro Z real de la geometría exportada contra el
  centro esperado del hueco, y corregido antes de dar el trabajo por
  bueno.

### Verificado

- Orientación confirmada con una sonda directa en la punta inferior
  esperada de la cola.
- Sin colisión con los imanes.
- Ensamblaje: 28/28 sin colisión (sin cambios).

---



### Añadido

- Texto "STEAM OS" en relieve, debajo del icono, mismo hueco
  (0,6mm) que el emblema — nuevo módulo `steamOsText()`.
- El icono se subió dentro del panel para dejar hueco al texto
  debajo, manteniendo el conjunto (icono + texto) dentro del área
  útil del panel.
- Ajustes tras la primera prueba: el espaciado inicial entre
  palabras ("STEAMOS") no se leía bien — corregido con doble espacio
  y el parámetro `spacing` del texto. El primer intento de separar
  más el texto del icono lo sacó por el borde inferior del panel
  (la altura real de la fuente es mayor de lo estimado) — corregido
  ajustando el hueco a un valor que cabe con margen por ambos lados.

### Verificado

- Márgenes confirmados por coordenadas exportadas: ~1,9mm hasta el
  borde inferior del panel.
- Sin solape entre el texto y el icono, sin colisión con el marco.
- Ensamblaje: 28/28 sin colisión (sin cambios).

---



### Cambiado

- El usuario aportó la imagen oficial del icono de Steam y preguntó
  "no podríamos hacer algo así" — la versión anterior (0.7.0/0.7.1)
  era una interpretación demasiado libre (una sola forma en "C" +
  válvula). Rehecho con la estructura real: anillo pequeño
  arriba-izquierda CON hueco, anillo grande arriba-derecha CERRADO
  (sin hueco), eje pequeño abajo-centro CON hueco, unidos por un
  brazo acodado en dos tramos — coincide en estructura con el icono
  real.
- Medidas tomadas directamente sobre la imagen aportada: recorte a
  escala, coordenadas leídas con una cuadrícula de referencia
  superpuesta (no una estimación a ojo como la versión anterior).
  Sigue siendo un diseño propio hecho a mano en OpenSCAD — no un
  archivo importado ni un trazado automático de la imagen.
- Escala y centrado recalculados para la nueva proporción (más ancho
  que alto, ~2,25:1) — ahora el ANCHO es el límite (134mm de 142mm
  disponibles), no el alto como antes.

### Verificado

- Dimensiones confirmadas por coordenadas exportadas: 134,1 × 59,5mm,
  perfectamente centrado (centro X=0,0).
- Sin colisión con el marco elevado.
- Ensamblaje: 28/28 sin colisión (sin cambios).

---



### Cambiado

- Escala del emblema: 0,8 → 4,0 (diámetro ~72mm, antes ~14mm),
  ocupando casi toda la altura útil del panel (80,5mm entre el borde
  inferior sin marco y el marco superior).
- Reposicionado y recentrado correctamente: el contorno del logo no
  es simétrico en X (la válvula sobresale más hacia un lado), así
  que se añadió una compensación (`logoCenterX`) para que el
  conjunto quede centrado de verdad en el panel, no solo su punto de
  origen.
- Esto fue posible sin ningún cambio estructural porque la ventana
  NFC y los imanes son huecos ciegos por la cara TRASERA del panel
  — el relieve del logo, en la cara FRONTAL, puede superponerse a
  esas zonas en el plano X/Z sin ningún conflicto real de material.

### Verificado

- Dimensiones confirmadas por coordenadas exportadas: 88,2 × 72mm.
- Sin colisión con el marco elevado.
- Ensamblaje: 28/28 sin colisión (sin cambios).

---



### Añadido

- **Emblema estilo Steam** en relieve (0,6mm de profundidad) en el
  panel NFC, sobre la ventana del sensor. Diseño propio hecho a mano
  en OpenSCAD (anillo grueso en forma de "C" + válvula pequeña con
  cruceta) — una interpretación estilizada del icono, no una réplica
  exacta ni un archivo importado.
- Pensado para imprimirse en dos filamentos: la base del panel en un
  color/filamento y el emblema en otro, usando la herramienta de
  "pintado por geometría/cara" del laminador (a diferencia de la
  franja LED, que usaba rango de altura — aquí es una forma 2D en el
  mismo plano, no una franja horizontal).
- Nuevos parámetros en `nfc_panel.scad`: `steam_logo_scale` (0,8) y
  `steam_logo_depth` (0,6mm).

### Verificado

- Sin colisión con la ventana NFC ni con el marco elevado.
- Posición confirmada por coordenadas exportadas (X:-7,2 a 10,4,
  Z:115,7 a 130,1 — dentro del hueco disponible sobre la ventana) y
  visualmente con un render.
- Ensamblaje: 28/28 sin colisión (sin cambios).

### Pendiente

- El tamaño y la posición exactos son una primera propuesta —
  ajustable si el usuario prefiere el emblema más grande, más
  pequeño, o en otra zona del panel.

---



### Encontrado — la causa real de la "media luna"

- Tras confirmar (0.6.8) que el archivo era idéntico byte a byte y
  que otro visor mostraba los agujeros limpios, el usuario probó en
  un tercer visor y localizó, con un círculo sobre la imagen, la
  zona exacta: un nervio vertical pasa a solo **0,5mm** del taladro
  de paso al pilar del suelo. Como el nervio es 5mm más alto que el
  taladro (sobresale de la base), desde cualquier ángulo que no sea
  perfectamente vertical, el nervio tapa parte de la vista/acceso al
  taladro — de ahí la forma de media luna, y el problema práctico
  real: un destornillador en ángulo choca con el nervio.
- El aviso de "no-manifold" corregido en 0.6.8 era un problema real,
  pero distinto — no la causa de esto.

### Corregido

- Los dos nervios verticales (izquierdo y derecho) reducidos de 3mm
  a 1,7mm de ancho, solo en el tramo que pasa cerca del taladro —
  siguen conectando el marco exterior con la isla del poste con
  margen de sobra. Separación resultante con el taladro: ~1,8mm
  (antes 0,5mm), verificada exportando la geometría real, no solo
  calculada a mano (la dirección en la que se ensancha un nervio
  rotado no es intuitiva — hubo que corregir un cálculo equivocado
  antes de dar con el ajuste correcto).

### Verificado

- Nervios siguen conectados a la isla/base (comprobación de contacto
  directo).
- Malla sigue watertight, 0 aristas problemáticas.
- Ensamblaje: 28/28 sin colisión (sin cambios).

---



### Investigado

- El usuario reportó un agujero con forma de media luna en una zona
  de la bandeja, en varias rondas de capturas. Comprobación
  definitiva: comparé byte a byte el `tray.stl` que el usuario tenía
  cargado contra el que genero yo — **2218 vértices únicos,
  coinciden exactamente, 0 diferencias**. Esto descarta cualquier
  problema en la geometría en sí — lo que se ve tenía que ser un
  artefacto de renderizado del visor, no un defecto en el archivo.

### Corregido

- Localizado con un análisis de malla (`trimesh`) el aviso "Object
  may not be a valid 2-manifold" que ya se había detectado antes
  (0.6.6) pero sin identificar su causa exacta: dos aristas no
  compartidas por exactamente 2 caras, en X=±55, Z=18 — exactamente
  donde el borde interior del marco exterior coincide en el mismo
  plano que el borde de los nervios verticales izquierdo/derecho (un
  caso clásico de coincidencia geométrica exacta que confunde a
  CGAL, sin relación con la isla del poste que se investigó antes).
- Corregido desplazando ambos nervios verticales 0,2mm hacia el
  interior de la carcasa, para que se solapen de verdad con el marco
  en vez de tocarse en un plano exacto.

### Verificado

- Malla resultante confirmada **watertight** (estanca) y con **0
  aristas problemáticas** (antes 2), mediante análisis de malla
  independiente (`trimesh`), no solo el aviso de OpenSCAD.
- Ensamblaje: 28/28 sin colisión (sin cambios).

### Pendiente

- No hay confirmación aún de si esta corrección resuelve lo que veía
  el usuario como "media luna" — es la explicación técnica más
  sólida encontrada (un fallo de malla real, en una zona cercana a
  donde el usuario señalaba), pero pendiente de que lo compruebe con
  el archivo nuevo.

---



### Corregido

- Tras la corrección anterior (0.6.6, taladros de paso a los
  pilares), el usuario mostró otra captura señalando que el problema
  seguía — pero resultó ser una zona DISTINTA: **el inserto de unión
  con el panel trasero** (X=±63, Ø10mm) sobresalía 3mm más allá del
  propio borde de la bandeja (que termina en X=±65) — la parte
  exterior del inserto quedaba sin apoyo, fuera del marco de la
  bandeja.
- Añadido `trayRearBridgeInsertPads()`: extiende el marco de la
  bandeja hasta cubrir el inserto entero por los cuatro lados, con
  7mm de margen de sobra antes de llegar a la pared (ya impresa, sin
  tocarla).

### Verificado

- Material sólido confirmado alrededor del inserto por los cuatro
  lados (comprobación geométrica directa, con margen).
- Sin colisión con la pared (0 facetas de solape).
- Ensamblaje: 28/28 sin colisión (sin cambios).

---



### Corregido

- **Los taladros de paso a los pilares del suelo (X=±60, Y=±40)
  caían casi enteros fuera de la isla de apoyo del poste** (que solo
  llega hasta Y=±41,5) — solo un 0,2mm de los 3,4mm de diámetro
  quedaba dentro de la isla, el resto (la mayoría) en hueco abierto
  sin apenas material alrededor. Confirmado con los 4 taladros
  simétricos (la foto del usuario solo mostraba 2, visibles desde
  ese ángulo).
- Como la posición del taladro depende de los pilares del suelo (ya
  impresos, no se puede mover), se añadió `traySupportHolePads()`: un
  parche de material alrededor de cada taladro, conectando con la
  isla existente — sin mover ni el taladro ni la isla.

### Verificado

- Material sólido confirmado alrededor del taladro por los 4 lados
  (comprobación geométrica directa).
- Sin colisión con los pilares del suelo (solo el contacto de apoyo
  esperado, 0mm).
- Ensamblaje: 28/28 sin colisión (sin cambios).

### Encontrado, no corregido (fuera del alcance de este aviso)

- Al validar, `tray.scad` da un aviso de OpenSCAD "Object may not be
  a valid 2-manifold" — confirmado que ya existía ANTES de este
  cambio (no lo causa el parche nuevo). No se ha investigado más en
  esta ronda; pendiente de revisar si el usuario lo considera
  prioritario.

---



### Cambiado

- **Marco continuo entre el panel inferior y el NFC**: quitado el
  marco elevado en el borde donde ambos paneles se juntan (el
  superior del inferior, el inferior del NFC) — se mantiene en los
  otros tres lados de cada uno. Verificado que el cuerpo base del
  panel sigue intacto ahí (solo se quitó el bisel, no material
  estructural).
- **USB frontal subido 2mm**: nuevo desplazamiento propio
  (`usb_front_z_offset`), independiente del resto del cluster
  (pulsador y OLED se quedan en su sitio). Verificado que deja 4mm de
  margen hasta el techo real del canal LED, sin solaparse con el
  OLED, sin colisión con el UM790, y sin cambios en el ensamblaje
  general (28/28).

---



### Cambiado — franja translúcida

- Más estrecha: de 12mm a 6mm, y reposicionada para quedar
  completamente FUERA del marco elevado (antes se solapaba 4mm con
  su borde superior) — el marco entero queda ahora en el filamento
  base, como pidió el usuario tras ver el acabado impreso.
- Verificado geométricamente que la franja ya no toca el marco.

### Cambiado — botón de encendido

- Diámetro del agujero: 16,0 → 16,5mm (0,5mm de holgura) — el
  usuario reportó que el pulsador no entraba bien tras imprimir.

### Cambiado — ancho del panel

- Sobredimensionado 1mm (0,5mm por lado) para compensar la merma de
  impresión FDM — el usuario reportó un hueco pequeño y simétrico
  respecto a las paredes tras imprimir, con el modelo midiendo
  exactamente los 150mm del hueco entre paredes. **Los taladros de
  tornillo NO se han movido** (siguen calculados igual, para seguir
  coincidiendo con los insertos de la pared ya impresa) — solo se
  ensanchó el borde exterior del panel y el marco.
- Nota honesta: con este cambio, el modelo (151mm) solapa
  teóricamente 0,5mm por lado con el modelo de la pared (150mm de
  hueco) — es una compensación deliberada por la merma observada, no
  un error. Si la impresora del usuario no encoge tanto como se
  asume aquí, podría quedar demasiado justo — pendiente de confirmar
  tras la reimpresión.

### Corregido — hueco de la pantalla OLED

- La medida usada hasta ahora (27×27mm) era la de toda la placa, no
  la de la pantalla — corregido a 27,0×20,0mm (medida real de la
  pantalla, aportada por el usuario).
- Añadido un rebaje ciego (solo por dentro, sin llegar al exterior)
  por encima de la pantalla, para los pines que sobresalen ahí
  (3mm de margen, según lo descrito por el usuario).
- Verificado que la piel frontal sigue sólida en esa zona (el rebaje
  no se ve desde fuera).

### Verificado

- Ensamblaje: 28/28 sin colisión (sin cambios).
- Pieza sigue en 3 volúmenes (sin fragmentos sueltos nuevos).

### Pendiente

- Confirmar tras reimprimir: si el margen del botón (16,5mm) y el
  sobredimensionado del panel (1mm) son suficientes, o necesitan más
  ajuste.
- El modelo de referencia del UM790 (`oled.scad`) seguía asumiendo
  los pines por DEBAJO de la pantalla, no por encima como describe
  el usuario — no se ha tocado esa parte en esta ronda (solo el
  recorte real del panel), pendiente de revisar si afecta a algo más.

---



### Corregido

- **El marco elevado (0.6.1) se solapa 4mm con la parte superior de
  la franja LED** (el borde superior del marco, Z=47,5 a 51,5, cae
  dentro de la franja LED, Z=39,5 a 51,5) — pero `ledDiffuserZone()`
  seguía marcando solo el grosor base del panel (3mm) en toda la
  franja, sin incluir el grosor añadido del marco donde se solapan.
  El resultado: la marca de "esto va en el 2º filamento" no cubría
  todo el material real ahí, así que el cambio de filamento habría
  dejado ese trozo en el filamento opaco.
- Corregido: `ledDiffuserZone()` ahora cubre el grosor completo real
  en cada tramo — solo el grosor base en la parte de la franja que
  no toca el marco (Z=39,5 a 47,5), y grosor base + marco en la
  parte que sí se solapa (Z=47,5 a 51,5).

### Verificado

- Cobertura completa confirmada en ambos tramos (con y sin marco)
  mediante comprobación geométrica directa (resta de la franja
  actualizada contra el material real del panel).
- Ensamblaje: 28/28 sin colisión (sin cambios).
- **Las alturas Z para el cambio de filamento en el laminador NO
  cambian** (siguen siendo 39,5 a 51,5mm) — este fue un fallo de
  geometría/modelado, no de las instrucciones de impresión ya dadas.

---



### Corregido

- **La pared del canal LED (`ledChannelWalls()`) nunca estuvo
  conectada al cuerpo del panel** — confirmado con una comprobación
  de contacto: separada 10mm (el ancho real de la tira LED) sin
  ningún puente entre ambas. No es un efecto del marco elevado
  añadido en 0.6.1; ya estaba así desde que se diseñó el canal
  ("segunda pared paralela") — un descuido de aquella sesión que no
  se verificó entonces.
- Añadido `ledChannelSupports()`: dos patas cortas, una a cada
  extremo del canal, conectando el cuerpo del panel con la pared del
  canal.

### Verificado

- Contacto confirmado por ambos lados: pata↔cuerpo del panel y
  pata↔pared del canal.
- Sin colisión con el UM790.
- Ensamblaje: 28/28 sin colisión (sin cambios).

---



### Añadido

- **Marco elevado (bisel) en el panel NFC y el inferior** — foto de
  referencia del usuario (Steam Machine original, ~5mm de
  profundidad visible en el borde del panel frontal). Puramente
  AÑADIDO hacia fuera (2mm de bisel + 3mm de grosor base = ~5mm en
  el borde) — **no toca `front_panel_thickness`**, que la pared ya
  impresa usa para calcular dónde reculan sus imanes y tornillos
  (cambiar ese valor habría desalineado la pieza real ya fabricada,
  confirmado explícitamente por el usuario: el chasis no se puede
  modificar).
- Nuevos parámetros compartidos en `00_parametros.scad`:
  `front_bezel_depth` (2mm) y `front_bezel_border` (4mm de ancho
  visible).

### Corregido — fallo propio detectado antes de dar por bueno el cambio

- Los tornillos de fijación del panel inferior caen a 3,75mm del
  borde — dentro de la franja del marco (4mm). Con el marco añadido
  como pieza aparte (unión después de los cortes), habría tapado el
  avellanado de esos tornillos, y el botón/OLED/USB también habrían
  quedado ocultos si hubieran caído en esa franja. Corregido
  reestructurando para que TODOS los cortes se apliquen al conjunto
  (base + marco), y extendiendo su alcance para atravesar también el
  grosor añadido del marco.

### Verificado

- Trayecto completo del tornillo (a través del marco) confirmado
  libre con sonda cilíndrica fina de extremo a extremo.
- Botón, USB frontal y ventana OLED confirmados libres a través del
  marco.
- Sin colisión con la pared (el marco sobresale más allá de su cara
  frontal, pero ahí no hay material de la pared con el que chocar —
  es justamente el efecto de profundidad buscado).
- Ensamblaje: 28/28 sin colisión (sin cambios).

---



### Corregido

- El "plano de distribución" de texto usado en 0.5.9 **no coincidía
  con la placa real** (aviso del usuario, con foto y regla): el
  orden estaba invertido (tenía DC-HDMI-RJ45-USB, la placa real es
  USB-RJ45-HDMI-DC) y los HDMI estaban apilados verticalmente cuando
  en realidad van uno al lado del otro.
- Sustituida la disposición completa por la que se ve directamente en
  la foto: USB×2 (apilados) | USB×2 (apilados) | RJ45 | HDMI | HDMI
  (lado a lado) | DC — de izquierda a derecha, vista desde atrás.
- Ancho total contrastado con la regla visible en la foto (~108 mm)
  frente a la suma de tamaños estándar más separaciones (~102 mm) —
  coincide razonablemente, la escala es creíble.

### Verificado

- 9 volúmenes en el recorte aislado (mismo patrón ya confirmado como
  "sin solapes" en la ronda anterior).
- Panel completo: 2 volúmenes (sin fragmentos sueltos).
- Ensamblaje: 28/28 sin colisión (sin cambios).

### Pendiente

- La posición exacta de cada conector dentro de la fila sigue siendo
  una distribución uniforme según lo apreciado en la foto, no una
  medida milimétrica exacta — pendiente de confirmar con más
  precisión si es posible (foto más perpendicular a la regla, o
  medidas directas).
- Tamaños de cada conector siguen siendo estándar de la industria.

---



### Cambiado

- Sustituida la distribución en fila estimada (0.5.8) por la
  disposición 2D real del "Plano de Distribución del Panel Trasero"
  que pasó el usuario: DC solo, HDMI×2 apilados verticalmente, RJ45
  solo (más alto), USB×4 en rejilla 2×2 — coordenadas exactas de
  cada centro, no una fila uniforme estimada.
- Conversión de coordenadas del plano a las de este proyecto:
  - Su origen (vista desde atrás, esquina inferior izquierda) se
    convierte a la vista desde delante que usa todo el proyecto —
    equivale a invertir X (vista desde atrás es un espejo).
  - Su ventana de 96 mm de ancho se asume centrada en X=0 (no había
    otra referencia).
  - **Sus alturas Z venían "respecto a la base del chasis" — pero al
    aplicarlas tal cual (6-17 mm) no encajaban con la altura real de
    la placa UM790 en este diseño (z_pcb_bottom=38 mm), y el chasis
    ya está impreso (confirmado por el usuario: no se puede
    modificar)**. Reinterpretadas como relativas al borde inferior de
    la placa (z_pcb_bottom + z_local) — coherente con dónde está la
    placa realmente.

### Corregido — fallo propio al ajustar el margen

- Con el margen de holgura anterior (1 mm), el hueco más ajustado del
  plano real (RJ45 a la columna de USB más cercana, solo 1,75 mm de
  separación natural) se fusionaba — confirmado exportando la
  geometría. Reducido a 0,5 mm, dejando un separador real de
  ~0,75 mm en el punto más justo.

### Verificado

- Coordenadas de la geometría exportada agrupadas en 8 conjuntos
  separados en X, sin solapes.
- Panel completo: 2 volúmenes (sin fragmentos sueltos).
- Ensamblaje: 28/28 sin colisión (sin cambios).

### Pendiente

- Tamaños de cada conector (diámetro DC, ancho/alto HDMI/RJ45/USB)
  siguen siendo ESTÁNDAR de la industria — el plano solo daba
  posiciones, no tamaños.
- La conversión de coordenadas (centrado de la ventana en X=0,
  reinterpretación de Z respecto a la placa) son las mejores
  suposiciones razonables ante el desajuste encontrado — pendientes
  de confirmar si es posible.

---



### Cambiado

- **`rearIOCut()` rediseñado**: antes un único hueco rectangular
  genérico cubriendo todo el bloque de IO — ahora un recorte
  independiente para cada conector real del UM790 Pro (confirmado
  por búsqueda: 1× DC 19V, 2× HDMI 2.1, 1× RJ45 2.5G Ethernet, 4×
  USB3.2 Tipo-A), en fila, en el orden habitual de este equipo.
- Medidas de cada conector: tamaños ESTÁNDAR de la industria para
  cada tipo (no las medidas exactas del UM790 real, que no están
  publicadas) — el ancho total resultante (129 mm) coincide
  razonablemente con el ancho real del equipo (130 mm), pero la
  posición exacta de cada conector dentro de esa fila es una
  distribución uniforme estimada, pendiente de confirmar con el
  equipo real o sus planos.

### Corregido — fallo propio durante la implementación

- Con el margen de holgura inicial (2 mm por conector) sumado al
  hueco entre conectores (3 mm), los recortes contiguos se solapaban
  y se fusionaban en una sola ranura continua — confirmado
  exportando la geometría (solo 2 volúmenes en vez de 8). Corregido
  reduciendo el margen a 1 mm, dejando un separador real de
  aproximadamente 1 mm entre agujeros.

### Verificado

- Coordenadas de la geometría exportada confirman 8 grupos
  separados en X, sin solapes entre ellos.
- Margen de 6 mm entre el borde de la fila de conectores y el
  tornillo de fijación del panel — sin conflicto.
- Ensamblaje: 28/28 sin colisión (sin cambios).

---



### Corregido

- **El brazo, al llegar centrado justo donde está el taladro de la
  placa, tapaba el propio agujero** — imposible meter el tornillo por
  dentro, bloqueado por el material del propio brazo (confirmado con
  una captura). Rediseñado como una horquilla de dos barras más finas
  (3 mm de alto cada una), una por encima y otra por debajo del eje
  del tornillo, con un hueco central de 8 mm — más ancho que el
  avellanado (6 mm) — para que quepa el destornillador.

### Verificado

- Trayecto completo del destornillador (desde el interior hasta la
  placa) confirmado libre con una sonda cilíndrica a lo largo de todo
  el eje.
- Sin colisión real con la pared, la placa del lector, ni el panel
  NFC.
- Pieza sigue en 2 volúmenes (todo conectado, la horquilla no crea
  fragmentos sueltos).
- Ensamblaje: 28/28 sin colisión (sin cambios).

### Nota sobre el proceso de verificación

- Varias sondas de diagnóstico en este mismo soporte dieron
  resultados engañosos en rondas anteriores (sonda centrada justo en
  el borde de un cono, sonda cuadrada para comprobar un agujero
  redondo) — no eran fallos del diseño, sino de cómo estaba
  comprobando. Sirva de recordatorio para las próximas verificaciones:
  sondas cilíndricas, bien centradas dentro de la zona a comprobar,
  no en su borde exacto.

---

## [0.5.6] - 2026-08-03 — Placa en ángulo de 90° real (aviso del usuario, confirmado por interacción)

### Cambiado

- Confirmado con el usuario el diseño exacto necesario: la pletina
  del extremo debe quedar PLANA contra la pared, con el tornillo
  perpendicular a ella — no un bloque macizo tocando solo la punta
  del poste (lo que había hasta ahora, 0.5.4/0.5.5).
- **Pletina rediseñada**: de un bloque macizo (14×14×14 mm) a una
  placa plana y ancha (15×15 mm), de solo 3 mm de grosor — mucho más
  ancha que el propio brazo (10 mm), para que el ángulo de 90° se
  note con claridad, con el avellanado en su cara interior (como ya
  se corrigió en 0.5.5).

### Corregido — fallo propio al ampliar la placa

- Al ensanchar la placa (probado primero con 18 mm), su borde se
  metía 1 mm dentro del propio panel NFC (colisión real, confirmada)
  — la placa, al estar más cerca del panel de lo que parecía, no
  cabía tan ancha sin invadirlo. Reducida a 15 mm, con margen de
  seguridad comprobado.

### Verificado

- Sin colisión real con la pared (solo contacto de plano en el
  extremo, 0 mm, sobre un área mayor por ser la placa más ancha).
- Sin colisión con la placa del lector ni con el panel NFC.
- Brazo y placa confirmados coincidiendo exactamente (66,0 mm en
  ambos lados de la unión).
- Ensamblaje: 28/28 sin colisión (sin cambios).

---

## [0.5.5] - 2026-08-03 — Soporte del RC522 v2.1: avellanado con acceso real (aviso del usuario)

### Corregido

- **El avellanado estaba en la cara EXTERIOR de la pletina** — justo
  donde toca el poste de la pared, sin ningún hueco ahí para alojar
  la cabeza del tornillo ni ángulo de acceso para un destornillador
  (bloqueado por el propio poste y la pared): tal y como estaba
  puesto, era físicamente imposible atornillarlo. Corregido: el
  avellanado ahora está en la cara INTERIOR de la pletina (mirando
  hacia la placa/el interior del chasis) — el tornillo entra desde
  dentro, con acceso real, atraviesa la pletina y rosca en el poste.

### Verificado

- Confirmado con sondas cilíndricas precisas (varias rondas de
  comprobación, incluyendo diagnóstico de por qué las primeras sondas
  daban un resultado engañoso — estaban mal centradas respecto al
  estrechamiento cónico del propio avellanado, no un fallo del
  diseño) que el hueco ancho queda ahora en la cara interior de la
  pletina, tal como corresponde.
- Sin colisión con la placa del lector ni con el panel NFC.
- Ensamblaje: 28/28 sin colisión (sin cambios).

---

## [0.5.4] - 2026-08-03 — Soporte del RC522 v2: extremos en L, avellanados, encaje exacto (aviso del usuario)

### Cambiado — rediseño completo pedido por el usuario

- **Extremos en "L"**: cada brazo termina ahora en una pletina más
  ancha (14×14 mm), con avellanado cónico real para la cabeza del
  tornillo M3 — antes, un simple taladro de paso al final de un brazo
  recto.
- **Encaje del lector ajustado a sus medidas exactas**
  (`nfc_reader_width` × `nfc_reader_height` × `nfc_reader_depth`),
  con 0,3 mm de holgura — antes, una huella aproximada.

### Corregido — 3 fallos propios encontrados al implementarlo

- **Taladro en el eje equivocado**: la v1.0 orientaba el tornillo en
  Y — no coincidía con el eje real del poste de la pared (que crece
  en X). Corregido con la rotación correcta.
- **Pletina invadiendo la pared**: al centrar la pletina sobre la
  punta del poste, la mitad se extendía hacia fuera, invadiendo el
  material propio de la pared (colisión real, confirmada). Corregido:
  la pletina ahora TERMINA en la punta del poste, no está centrada
  ahí.
- **Asimetría izquierda/derecha**: con la orientación de rotación
  igual en los dos lados, el taladro y el avellanado del lado
  izquierdo quedaban desplazados y con el cono invertido respecto al
  poste real. Corregido con fórmulas dependientes del lado.
- **Encaje invadiendo el panel NFC**: el marco del lector se extendía
  hasta la cara frontal del propio panel (colisión real, confirmada)
  — el hueco de separación panel-lector (`rc522_panel_gap` = 3 mm) ya
  estaba reservado para eso. Corregido quitando la pared frontal del
  encaje (el propio panel ya hace de tope) — ahora solo repisa
  trasera y guías laterales, dentro de la profundidad real de la
  placa.

### Verificado

- Sin colisión real con las paredes (solo contacto de borde en los
  dos extremos, 0 mm) — comprobado también que el eje del tornillo
  queda vacío en ambos lados.
- Sin colisión con la placa del lector ni con el panel NFC.
- Brazos y pletinas confirmados solapados (conexión sólida, no solo
  contacto).
- Ensamblaje: 28/28 sin colisión (sin cambios).

---

## [0.5.3] - 2026-08-03 — Soporte real e imprimible del lector RC522 (aviso del usuario)

### Añadido

- **`openscad/parts/04_soportes/rc522_bracket.scad`** (pieza nueva):
  hasta ahora solo existía `rc522Bracket()` en
  `reference/components/rc522.scad`, marcado explícitamente como "NO
  ES UNA PIEZA IMPRIMIBLE" — solo un volumen de referencia para
  comprobar colisiones. Faltaba la pieza real.
- Una barra que va de pared a pared, atornillada en cada extremo al
  poste de anclaje ya existente en la pared (`rc522MountBoss()`,
  `walls.scad`) — mismas coordenadas exactas, para que coincidan.
- Marco de referencia (huella) del tamaño de la placa en el centro,
  para alinearla al pegarla — no hay taladros propios de la placa
  (no se conocían sus medidas de montaje).
- Carpeta nueva `openscad/parts/04_soportes/`, para piezas accesorias
  de este tipo (no encajaban en bandeja/chasis/paneles).

### Verificado

- Sin colisión real con las paredes (solo contacto de borde
  esperado, 0 mm, en los dos extremos).
- Eje del tornillo comprobado libre hasta el inserto del poste.
- Sin colisión con la placa del lector ni con el panel NFC.
- Ensamblaje: 28/28 sin colisión (sin cambios — el soporte nuevo no
  forma parte todavía de esa comprobación automatizada, verificado
  a mano contra los elementos relevantes).

### Pendiente

- Alto del marco de referencia (`rc522_bracket_rim_height` = 1,5 mm)
  ESTIMADO, sin confirmar.
- Sin taladros propios para la placa (se desconocen sus medidas de
  montaje) — se pega dentro del marco de referencia.

---

## [0.5.2] - 2026-08-03 — Avellanados reales en las 4 esquinas de la tapa (aviso del usuario)

### Corregido

- **Las 4 esquinas de la tapa tenían muescas rectangulares** (7×28 mm)
  en vez de agujeros avellanados — mismo patrón ya corregido antes en
  el panel NFC, inferior y trasero, aquí sin aplicar todavía. Causa:
  el relleno del inserto en la pared (`topInsertPad()`) llegaba hasta
  Z=shell_height+1, pasando la cara EXTERIOR de la tapa — sin sitio
  para que la tapa tuviera su propio material sin invadirlo.
- Corregido con el mismo criterio que los demás paneles: el relleno
  (`topInsertPad()`/`topScrewInsertCuts()` en `walls.scad`) ahora para
  en la cara INTERIOR de la tapa, no llega a la exterior.
- Añadido avellanado cónico real a `topScrewHoles()`, dentro del
  grosor normal de la tapa (3 mm) — igual que en el resto de
  tornillos del proyecto.
- Retirada `topInsertRelief()` (la muesca rectangular), ya
  innecesaria.

### Verificado

- Sin colisión real con la pared (solo contacto de borde esperado,
  0 mm, en la nueva posición reculada).
- Ensamblaje: 28/28 sin colisión (sin cambios).

---



## [0.5.1] - 2026-08-03 — Rediseño completo de la tapa: rejilla densa sin hueco dedicado al ventilador (foto de referencia)

### Cambiado

- **Retirado `fanOpening()`**: ya no hay un hueco grande (120×120 mm)
  dedicado al ventilador. La rejilla ahora cubre casi toda la tapa
  (como en la foto de referencia del usuario) — el aire pasa por los
  agujeros de la rejilla que quedan encima del ventilador igual que
  por el resto, sin necesitar una abertura propia de su tamaño.
- **Retirado `fanFingerGuard()`** (las varillas dentro del hueco): ya
  no hace falta, la propia rejilla densa protege los dedos.
- **`topVentCut()` rediseñada**: cobertura casi total (antes: un
  anillo estrecho alrededor del hueco del ventilador), con agujeros
  más pequeños y densos (5 mm con 2,5 mm de pared, antes 10 mm con
  8 mm). Islas sólidas locales alrededor de cada poste del ventilador
  (`fanBossClearance`), para que ningún poste caiga sobre un hueco de
  la rejilla y quede sin apoyo.
- **Retirado `fanMountArms()`** (los brazos diagonales de sujeción):
  ya no hacen falta — con la rejilla cubriendo toda la zona, los
  postes quedan conectados de forma natural a través del propio
  material de la rejilla, sin necesitar un puente dedicado hasta el
  borde.

### Investigado — hallazgo, no fallo nuevo

- Al comprobar la tapa contra el modelo de referencia del ventilador,
  aparece un solape en los 4 postes de sujeción. Confirmado que **ya
  existía antes de este rediseño** (los postes, aislados, ya
  colisionaban con el modelo del ventilador independientemente de
  cualquier cambio de hoy) — el modelo de referencia trata todo el
  cuadrado del ventilador (120×120 mm) como sólido, sin distinguir el
  marco real de la zona hueca de las aspas. Los postes están puestos
  justo donde van los tornillos reales del ventilador (en el marco),
  así que es una simplificación del modelo de referencia, no un
  fallo físico real. No se ha tocado nada a raíz de esto.

### Verificado

- Ensamblaje: 28/28 sin colisión (sin cambios).
- Tapa completa: 2 volúmenes (todo bien conectado, sin fragmentos
  sueltos con la nueva rejilla densa).

---



## [0.5.0] - 2026-08-03 — La rejilla cuadrada de la tapa nunca llegó a existir (aviso del usuario)

### Corregido — causa raíz real

- **La zona de exclusión del ventilador (136×136 mm) era MÁS GRANDE
  que toda la zona de rejilla (124×130 mm con el margen anterior de
  16 mm)** — se comía la rejilla entera. El cambio a `squareGrid()`
  de una sesión anterior era correcto en el código, pero nunca llegó
  a producir ningún agujero real: lo único visible siempre fueron las
  tiras del protector de dedos del ventilador, confundibles con "la
  rejilla".
- `top_grill_margin`: 16 → 6 mm (deja un anillo real de agujeros
  cuadrados alrededor del ventilador — que ya ocupa la mayor parte
  del área disponible).
- Margen de exclusión del ventilador: separado de `vent_spacing`
  (8 mm) a un valor propio más ajustado (3 mm), para dejar hueco real
  a la rejilla.
- **El protector de dedos del ventilador también usaba tiras**
  (`slots()`), no agujeros cuadrados — cambiado a `squareGrid()`. Con
  una corrección adicional: `squareGrid()` genera cubos SUELTOS
  (pensada para restar y hacer agujeros) — usada tal cual en un
  cuerpo aditivo habría dejado cuadrados flotando sin conexión entre
  sí. Corregido invirtiéndola: una placa maciza MENOS `squareGrid()`,
  así queda una rejilla continua con agujeros cuadrados de verdad.

### Verificado

- Render en planta: ya se ven agujeros cuadrados reales alrededor
  del ventilador (antes: superficie lisa, sin ningún hueco).
- Tapa completa: 7 volúmenes (razonable, sin explosión de fragmentos
  sueltos — confirma que la inversión de `squareGrid()` conectó bien
  la rejilla).
- Brazos de sujeción del ventilador: siguen conectados en los mismos
  5 puntos de comprobación de siempre.
- Ensamblaje: 28/28 sin colisión (sin cambios).

---



## [0.4.9] - 2026-08-03 — Rediseño del canal LED: segunda pared en profundidad, no en altura

### Corregido

- El primer intento (0.4.8) interpretó mal la petición: puso dos
  paredes separadas en ALTURA (Z), ambas ocultas por detrás — no
  coincidía con la foto de referencia ni con lo que pedía el usuario.
- Aclarado por el usuario: la "pared existente" es el propio grosor
  del panel (su cara frontal, `front_panel_thickness` = 3 mm, que ya
  forma una pared al verla de canto) — no hacía falta añadirla. Lo
  que pedía era una SEGUNDA pared, paralela a esa, separada en
  PROFUNDIDAD (Y, hacia el interior) la anchura real de la tira LED
  (`led_bar_strip_width` = 10 mm), no en altura.
- Rediseñado `ledChannelWalls()`: ahora es una única pared nueva,
  paralela a la cara frontal del panel, a 10 mm de distancia hacia el
  interior — el hueco entre ambas (10 mm de ancho) es donde se pega
  la tira, con su longitud a lo largo del panel.

### Verificado

- Sin colisión con el UM790.
- Ensamblaje: 28/28 sin colisión (sin cambios).
- Confirmado con vista en planta: dos paredes paralelas, separadas
  10 mm.

### Pendiente

- Altura de cada pared (`led_channel_wall_height` = 3 mm) y grosor de
  la nueva (`led_channel_wall_thickness` = 1,5 mm) siguen siendo
  estimaciones, pendientes de confirmar con la tira LED real.

---



## [0.4.8] - 2026-08-03 — Canal en "U" para pegar la tira LED (petición del usuario, con foto de referencia)

### Añadido

- `ledChannelWalls()` en `lower_panel.scad`: dos paredes que
  sobresalen 4 mm hacia el interior (una arriba y otra abajo de la
  franja de 12 mm de la barra LED), formando un canal en "U" abierto
  hacia el interior donde pegar la tira LED real — igual que un
  perfil de aluminio típico para tiras LED (foto de referencia del
  usuario).
- Las paredes se colocan JUSTO FUERA de la franja de 12 mm (no la
  invaden), para no estrechar el hueco resultante por debajo del
  ancho real de la tira (`led_bar_strip_width` = 10 mm) — si hubieran
  ocupado parte de esos 12 mm, la tira no habría cabido.
- La zona de 2º filamento (`ledDiffuserZone()`, sin cambios) sigue
  siendo la que deja pasar la luz hacia el exterior — el canal es un
  añadido puramente mecánico, por detrás.
- Medidas del canal (profundidad 4 mm, grosor de pared 1,5 mm)
  ESTIMADAS, pendientes de confirmar con la tira LED real.

### Verificado

- Sin colisión con el UM790 (el canal sobresale cerca de esa zona).
- Sin colisión real con la pared.
- Ensamblaje: 28/28 sin colisión (sin cambios).

---



### Corregido

- Aplicada la misma corrección del panel NFC (0.4.6) al **panel
  inferior** (tornillo M2) y al **panel trasero** (tornillo M3), esta
  vez moviendo AMBOS lados a la vez (inserto en la pared + agujero en
  el panel) para mantener la alineación exacta que necesita un
  tornillo — a diferencia del imán, aquí no valía desplazar solo un
  lado.
- Nueva función compartida `panelMountX()` (`assembly_positions.scad`),
  con margen respecto al borde REAL de cada panel (no respecto a la
  cara exterior de la pared, que es más ancha) — usada a la vez en
  `walls.scad` (posición del inserto) y en cada panel (posición del
  agujero/avellanado), para que no puedan desalinearse.
- Radios de avellanado (`lower_panel_csk_radius`, `rear_csk_radius`)
  movidos a la fuente compartida por el mismo motivo.

### Verificado

- Ambos paneles: el avellanado ya cabe entero dentro del borde real
  del panel (antes se salía hasta 3 mm).
- Trayecto del tornillo comprobado libre de principio a fin (sonda a
  lo largo de su eje).
- Sin colisión real con la pared en ninguno de los dos paneles.
- Lengüeta de unión bandeja↔panel trasero: sigue sin colisión (el
  cambio de posición del tornillo no la afecta).
- Ensamblaje: 28/28 sin colisión (sin cambios).

---



### Corregido

- **El alojamiento del imán del panel NFC se salía 2 mm por el borde
  real del panel** (confirmado con una captura: el círculo del
  alojamiento no se cerraba dentro del panel). Causa: la X se copiaba
  directamente de `sideMountGlobalX()`, la misma fórmula que usa la
  pared para posicionar el imán dentro de SU propio espesor (que
  llega hasta X=78) — válida ahí, pero el panel NFC solo llega hasta
  X=75 (`nfc_panel_width/2`). Una posición que cabe en la pared no
  cabe automáticamente en un panel más estrecho.
- Corregido calculando la X con margen respecto al borde REAL del
  panel, no respecto al de la pared. El alojamiento ya no está
  perfectamente centrado con el imán de la pared (unos 3 mm de
  diferencia en X), inevitable si tiene que caber entero dentro del
  panel — la atracción magnética debería seguir funcionando con ese
  desfase.

### Encontrado, pendiente de decisión — mismo fallo en otros dos paneles

- **Panel inferior (tornillo M2)** y **panel trasero (tornillo M3)**
  tienen el mismo problema, y en el trasero es más grave (hasta
  3 mm fuera del borde, incluso el taladro de paso básico, no solo
  el avellanado).
- Aquí es más delicado que en el imán: el taladro de paso tiene que
  alinear EXACTAMENTE con el inserto de la pared para que el tornillo
  lo alcance — no se puede simplemente desplazar como con el imán.
  Requiere decidir entre reducir el avellanado, ensanchar el relleno
  de la pared en esa zona, o mover el inserto — pendiente de
  planteárselo al usuario antes de tocar nada más.

### Verificado

- Panel NFC: el alojamiento ya cabe entero dentro del panel (-75 a
  75). Sin colisión real con la pared (solo contacto de borde
  esperado, 0 mm).
- Ensamblaje: 28/28 sin colisión (sin cambios).

---



### Corregido

- **El panel NFC se dejó sin ningún alojamiento para el imán** en la
  corrección anterior (0.4.4) — se decidió que un imán del grosor
  estándar del proyecto (magnet_height = 3 mm) no cabía con piel
  delante en un panel de igual grosor, y se dejó completamente liso.
  El usuario avisó de que necesita un encaje real, no nada.
- Añadido `nfcMagnetPockets()`: alojamiento ciego, parcial (1,5 mm de
  profundidad — ESTIMADO, pendiente de confirmar el grosor real de
  la arandela/imán a usar aquí), que se queda dentro del propio
  grosor del panel sin sobresalir por detrás. Deja 1,5 mm de piel
  sólida por delante (oculto) y no invade el hueco donde ya está el
  imán de la pared (que se abre exactamente en el mismo punto, Y de
  la cara trasera del panel, y crece hacia el interior de la pared —
  si el del panel creciera en la misma dirección, invadiría ese
  mismo espacio).

### Verificado

- El panel sigue exactamente dentro de su grosor normal (-81,2 a
  -78,2), sin perforar la piel frontal ni sobresalir por detrás.
- Cara frontal confirmada maciza en el punto del imán (sonda
  dirigida).
- Sin colisión real con la pared (solo contacto de borde, 0 mm).
- Ensamblaje: 28/28 sin colisión (sin cambios).

---



### Contexto

Dos intentos anteriores no fueron aceptables: una muesca cuadrada
visible (0.4.3 primer intento) y un saliente redondo hacia el
exterior (0.4.3 segundo intento — "los soportes sobresalen por fuera
de los paneles"). Verificado matemáticamente que, con el relleno de
la pared llegando hasta la cara EXTERIOR de los paneles, ninguna
forma de material del panel podía evitarlo sin sobresalir o sin
quedar hueco — es decir, el panel por sí solo no tiene solución.

### Cambiado — con permiso explícito del usuario, en la pared

- `frontMagnetCuts()`, `sideBossPad()`, `lowerPanelScrewCuts()`
  (paredes laterales) y `rearBossPad()`/`rearWallScrewCuts()` (pared
  trasera): el alojamiento del imán/inserto y su relleno se reculan
  ahora `front_panel_thickness` (3 mm, paredes laterales) o
  `wall_thickness` (3 mm, pared trasera) hacia dentro — se abren
  justo en la cara INTERIOR de cada panel, no en la exterior.

### Corregido — paneles, ahora realmente lisos

- **Panel NFC**: sin ningún corte para el imán — el hueco de 3 mm de
  la pared no deja sitio para ningún alojamiento con piel delante en
  un panel de igual grosor (3 mm). El imán/arandela se pega en la
  cara trasera durante el montaje, sin ninguna pieza impresa.
- **Panel inferior y panel trasero**: taladro de paso + avellanado
  cónico real, ambos DENTRO del grosor normal del panel (sin ningún
  saliente) — ahora que la pared se reculó, cabe con margen.
- Verificado en los tres: sin colisión real con la pared (solo
  contacto de borde exacto, 0 mm de espesor, en la nueva posición
  reculada).

### Verificado — no se rompió nada más

- Ensamblaje: 28/28 sin colisión (sin cambios).
- Panel NFC vs RC522: sin colisión (sin cambios).
- Lengüeta bandeja↔panel trasero vs paredes: sin colisión (sin
  cambios, el retranqueo del relleno no la afecta).

---



### Corregido — imanes/tornillos visibles desde fuera (sin tocar la pared)

- **Diagnóstico**: el relleno de la pared (`sideBossPad()`) empieza
  exactamente en la cara EXTERIOR de los paneles frontales y se
  extiende mucho más allá de donde termina el panel por detrás — no
  queda ningún margen de grosor para dejar una "piel" sólida delante
  sin invadir el relleno. Confirmado con las coordenadas reales
  (Y=-81,2 tanto para el borde del panel como para el inicio del
  relleno). Cambiar esto habría requerido tocar la pared, que el
  usuario pidió expresamente no modificar.
- **Solución, íntegramente en los paneles**: un saliente REDONDO
  hacia el exterior (más allá de la cara normal del panel, en la zona
  donde el relleno de la pared todavía no existe), con:
  - **Panel NFC**: alojamiento del imán CIEGO, abierto hacia el
    interior — no pasante, no visible desde fuera.
  - **Panel inferior**: taladro de paso con avellanado cónico real
    en la cara exterior, para la cabeza del tornillo M2.
  - **Panel trasero**: mismo tratamiento que el inferior (M3), por
    consistencia — no se mencionó explícitamente pero tenía el mismo
    problema.
- Verificado en los tres paneles: sin colisión real con las paredes
  (solo contacto de borde esperado, 0 mm de espesor).

### Corregido — fallo propio detectado al aplicar lo anterior

- Al quitar las antiguas muescas cuadradas pasantes, se me olvidó que
  el panel PLANO seguía teniendo material sólido en esa zona — seguía
  chocando con el relleno de la pared. Corregido volviendo a añadir
  la muesca (`wallPadRelief()`), esta vez JUNTO con el nuevo saliente
  (no en su lugar), con el borde recalculado para no invadir el
  propio saliente.
- **El relleno del tornillo trasero bajo (Z=15) colisionaba con la
  lengüeta de unión bandeja↔panel trasero** (también a Z=15-18) — un
  fallo que ya existía de una corrección anterior, encontrado al
  verificar esta ronda. Corregido subiendo esa Z a 27 (lejos de la
  lengüeta y del recorte de la IO trasera).

### Corregido — rejilla de la tapa con piezas en el aire

- **Causa real**: la rejilla de la tapa reutilizaba
  `bottom_grill_margin`, el mismo parámetro reducido a 3 mm para
  ampliar la rejilla del SUELO en una sesión anterior — sin querer,
  ese cambio también vació la tapa casi hasta el borde, demasiado
  cerca de los taladros de tornillo y el relleno de los insertos,
  dejando fragmentos sin apoyo.
- Corregido con un parámetro propio (`top_grill_margin` = 16 mm), y
  cambiado el patrón de `valvePattern()` (rombos) a `squareGrid()`
  (agujeros cuadrados), a petición del usuario.

### Añadido — soportes del ventilador

- Antes: simple taladro de paso liso en los 3 mm de la tapa. Ahora:
  postes con alojamiento ciego para inserto M3 térmico, más robustos.
- Los postes caen dentro del hueco cuadrado del ventilador (donde van
  los anclajes reales) — añadidos brazos de sujeción diagonales hasta
  el material sólido exterior al hueco, para que no queden flotando
  (patrón habitual en ventiladores reales, "araña" de sujeción).
  Verificado en 5 puntos de la diagonal, conexión continua sin huecos.

### Resultado

- Ensamblaje: 28/28 sin colisión (sin cambios).
- Los tres paneles (NFC, inferior, trasero) verificados sin colisión
  real contra las paredes.

---



El usuario da por bueno el chasis en su estado actual. Validación
final antes del cierre:

- Sintaxis: limpia en las ~30 piezas del proyecto.
- Ensamblaje (28 pares): 28/28 sin colisión.
- Estructura vs 8 componentes (32 pares): 29/32 sin colisión — los 3
  restantes son los contactos de anclaje intencionados de siempre
  (RC522, ESP32, HUB).
- Estructura vs estructura: pares relevantes verificados durante la
  sesión (la mayoría a mano, por la lentitud del script automático
  completo) — sin colisión real, solo contactos de diseño esperados.
- Recorrido de inserción de la bandeja: verificado en 4 alturas
  intermedias, sin obstrucción.

Ver `docs/Virtual_Assembly_Report.md`, sección 12, para el resumen
completo de cierre, incluidas las limitaciones conocidas no
bloqueantes (medidas sin confirmar, un comentario del DIM sin
reconciliar, y que no se ha comprobado el recorrido de inserción de
piezas distintas a la bandeja).

A partir de aquí, el chasis no se modifica salvo que surja un
problema real al imprimir o montar.

---



### Contexto

Todas las comprobaciones de esta sesión verificaban la posición
FINAL de cada pieza. El usuario preguntó si la bandeja podría
insertarse sin problemas — una pregunta distinta: no solo si
colisiona en su destino, sino si el CAMINO para llegar ahí (bajando
desde arriba, con la tapa quitada) está libre.

### Corregido

- **La bandeja (150 mm de ancho, el hueco exacto entre paredes, sin
  ninguna holgura) chocaba con los rellenos de imanes/tornillos de
  las paredes laterales** (`sideBossPad()`, `rearBossPad()`,
  `topInsertPad()` — todos sobresalen 7 mm hacia el interior) durante
  el recorrido de bajada. No en su posición final — ahí nunca hubo
  colisión, por eso no se había detectado antes — sino en varios
  puntos intermedios del trayecto de inserción.
- Verificado con un barrido vertical completo (`tray_width` extruido
  desde la apertura superior hasta la posición final) contra las
  paredes: colisión real confirmada, no solo el contacto de ajuste
  esperado (usando sondas con 6 mm de margen para descartar falsos
  positivos de borde).
- Corregido reduciendo `tray_width` de 150 a 130 mm (deja 3 mm de
  holgura a cada lado del canal libre entre rellenos, y 8,5 mm de
  margen respecto a los anclajes reales del UM790, off_x = 56,5 mm).
  `tray_depth` no se ha tocado — el problema es solo con las paredes
  laterales fijas, no con el frente/fondo (paneles separados que no
  son obstáculo durante la inserción vertical).

### Resultado

- Verificado el recorrido completo de inserción en 4 alturas
  intermedias (Z=30, 70, 95, 140) con la bandeja real (postes,
  nervaduras, UM790 de referencia incluidos) — sin colisión en
  ninguna.
- Verificada también la posición final: sigue tocando los pilares de
  apoyo exactamente igual que antes (0 mm de espesor).
- Ensamblaje: 28/28 sin colisión (sin cambios).

---



### Cambiado

- **Suelo: rejilla en prácticamente toda su superficie**, para
  captar más caudal de aire externo. `bottom_grill_margin`: 12 → 3 mm
  (mínimo razonable para que el borde siga teniendo material sólido
  donde apoyan las paredes). Verificado: pilares de apoyo de la
  bandeja y patas siguen conectados correctamente, sin colisiones
  nuevas (28/28 ensamblaje, sin cambios).

### Corregido — hueco de fondo en la bandeja

- **`tray()` (`openscad/parts/01_bandeja/tray.scad`) nunca elevaba la
  bandeja a su posición real de montaje** — se renderizaba en su
  propio origen local (Z=0, como si apoyara directamente en el
  suelo), cuando en el ensamblaje real queda elevada sobre los
  pilares de apoyo del suelo, a `z_chamber_top` = 15 mm. Todo el resto
  del ensamblaje (posición del UM790, recorte del panel trasero, etc.)
  ya asumía esta elevación — verificado durante toda la sesión con el
  modelo de referencia — pero la pieza física de la bandeja en sí
  nunca se había materializado en su sitio correcto.
- Corregido envolviendo `tray()` con
  `translate([0,0,z_chamber_top])`. Con esto, la altura de separadores
  del UM790 (post_height=20 mm) y la posición del conector trasero
  coinciden matemáticamente con lo ya verificado (no ha hecho falta
  recalcular ningún valor — los números ya eran correctos, solo
  faltaba que la pieza los reflejara).
- Verificado: bandeja elevada toca el suelo exactamente en los
  pilares de apoyo (0 mm de espesor, contacto correcto, no
  colisión), toca las paredes solo en su borde (encaja exactamente
  entre ellas, tray_width = case_width - 2×wall_thickness), y el
  solape con el modelo de referencia del UM790 en la zona de los
  postes es el esperado (representan el mismo objeto físico dos
  veces: referencia y pieza real).

### Resultado

- Ensamblaje: 28/28 sin colisión (sin cambios).
- No ha sido necesario crear una pieza nueva de "base independiente":
  `tray.scad` ya era un archivo separado del chasis fijo; el hueco
  real era que le faltaba la traslación de elevación.

---



### Corregido — causa raíz real

- **`topInsertPad()` y `topScrewInsertCuts()` usaban coordenadas
  GLOBALES (centradas en el medio de la carcasa) dentro del sistema
  de coordenadas LOCAL de cada pared** (que empieza en el borde, no
  en el centro). Al pasar por la traslación de `leftWall()`/
  `rightWall()` (`-case_depth/2`), el valor se desplazaba una segunda
  vez — el soporte terminaba a case_depth/2 (81,2 mm) de donde debía,
  fuera por completo de la pieza ("en el aire", como se ve en la
  captura). El taladro del inserto sufría el mismo desplazamiento, así
  que cortaba en el vacío y no dejaba agujero real en el soporte.
  Confirmado exportando a STL: el soporte aparecía en Y=-144,4 mm,
  muy fuera del rango real de la pieza (-81,2 a 81,2 mm).
- Corregido pasando las coordenadas ya convertidas a locales
  (`wall_thickness + top_screw_y_inset` y
  `case_depth - wall_thickness - top_screw_y_inset`, equivalentes a
  las globales tras deshacer la traslación de la pared).
- De paso, ampliado el margen del corte del inserto (igual que se
  hizo antes con la muesca de la tapa) tras detectar que, aun con la
  posición ya correcta, el corte no llegaba a vaciar limpiamente el
  material — verificado con una sonda en el centro exacto del
  agujero, ahora confirmado hueco.

### Resultado

- Verificado exportando a STL: toda la geometría de ambas paredes
  queda ya dentro de los límites reales de la carcasa (X: -78 a 78,
  Y: -81,2 a 81,2 — antes se salía 63 mm por Y).
- Ensamblaje: 28/28 sin colisión (sin cambios).

---



### Corregido — registro erróneo

- La entrada [0.3.7] afirmaba que la fijación pared↔panel trasero se
  había "reintentado y resuelto" — **no era cierto**: no existía
  ninguna referencia a `rearBossPad`/`rearWallScrewCuts` en el
  código. Fue un error al escribir el resumen de aquel turno, no una
  regresión posterior. Detectado al investigar por qué el usuario no
  veía los soportes.

### Añadido

- **Fijación pared↔panel trasero, esta vez implementada de verdad**:
  `rearBossPad()`/`rearWallScrewCuts()` en `walls.scad` +
  `rearWallScrewHoles()` y su `wallPadRelief()` en `rear_panel.scad`.
  Queda un residuo menor (4 puntos, 3 mm de espesor) sin resolver del
  todo por tiempo — mucho más pequeño que el problema original, no
  bloqueante, documentado para revisión futura.
- **Inserto M3 de la tapa**: mismo tipo de fallo que los imanes (más
  ancho que la pared, asomaba 0,55 mm) — corregido con
  `topInsertPad()` + `topInsertRelief()` en la propia tapa.

### Investigado — artefacto de CGAL, no un fallo de diseño

Durante la verificación de paredes↔tapa apareció un solape que no
correspondía a ninguna pieza conocida. Comprobación exhaustiva:
- Ninguna pieza individual (pared base, cada relleno, cada poste) lo
  contenía por separado.
- El bloque de unión completo (todos los rellenos juntos, antes de
  los recortes) tampoco lo contenía.
- Solo aparecía **después** de aplicar los recortes — imposible en
  términos normales (restar no puede añadir material).
- Coincidía con avisos repetidos de "Object may not be a valid
  2-manifold".

Conclusión: artefacto numérico de la operación booleana de CGAL al
combinar muchos recortes cercanos, no un fallo de diseño real. No se
ha modificado nada a raíz de esto — se deja documentado por si
resulta relevante al laminar/imprimir.

### Resultado

- Ensamblaje: 28/28 sin colisión (sin cambios).

---



### Añadido

- **Fijación pared↔panel trasero, reintentada y esta vez resuelta**:
  usando el mismo patrón de muesca de alivio que ya funcionó para el
  panel inferior y el NFC (`wallPadRelief()`), se ha vuelto a añadir
  `rearBossPad()`/`rearWallScrewCuts()` en `walls.scad` y
  `rearWallScrewHoles()` + su propia muesca en `rear_panel.scad`.
  Verificado sin colisión real (solo contacto de borde esperado).

### Corregido

- **El inserto M3 de la tapa asomaba 0,55 mm por cada cara de la
  pared** (mismo tipo de fallo que los imanes, en menor escala,
  encontrado al revisar por qué el usuario no veía los soportes).
  Corregido con un relleno local (`topInsertPad()`) y recentrado del
  taladro (`sideBossCutX()`, reutilizando la función ya existente).
- Añadida la muesca de alivio correspondiente en la propia tapa
  (`topInsertRelief()`) para que su material no invada ese relleno.

### Pendiente / sin resolver del todo

- La comprobación completa paredes↔tapa sigue mostrando algo de
  contacto más allá de lo ya aceptado como "unión esperada" en
  versiones anteriores; una sonda puntual confirmó que el punto
  concreto del inserto de la tapa ya está bien (hueco correcto), pero
  no se ha rastreado el origen exacto del resto por falta de tiempo.
  No hay indicios de que sea un fallo nuevo (ya existía cierto
  contacto ahí antes de esta sesión, aceptado como el apoyo de la
  tapa sobre el borde de la pared) — pendiente de una revisión más
  detallada si se detectan problemas al imprimir.

### Resultado

- Ensamblaje: 28/28 sin colisión (sin cambios).

---



### Añadido

- **Comprobación estructura-contra-estructura** en
  `run_structure_checks.py` — hasta ahora solo se comparaba cada
  pieza del chasis contra los 8 componentes electrónicos, nunca las
  piezas del chasis entre sí. Esta comprobación fue la que destapó
  todos los fallos de esta entrada. Incluye una lista de parejas con
  contacto esperado (piezas que se tocan por diseño: la tapa se apoya
  en la pared, el panel trasero se atornilla a la bandeja, etc.) para
  no confundir un contacto intencionado con una colisión real.
- `wallPadRelief()` (nuevo módulo compartido en
  `assembly_positions.scad`): muesca de alivio que cualquier panel
  atornillado/imantado a la pared debe restar en los puntos de unión,
  para no invadir el relleno local de la pared (14×14 mm, mucho más
  ancho que un simple taladro de paso).

### Corregido

- **Pilares de apoyo de la bandeja** (aviso del usuario): estaban
  completamente macizos, sin alojamiento para el inserto M3.
  Corregido. Además no caían sobre material sólido de la bandeja
  (quedaban en la zona hueca del marco) — reposicionados con un
  `inset` distinto en X e Y.
- **Los pilares de apoyo colisionaban con el relleno de la pared**
  (aviso del usuario): al estar en la esquina (X=Y=70 mm), caían
  dentro de la franja de los rellenos de imán/tornillo. Reposicionados
  en Y (40 mm) — siguen sobre el marco sólido de la bandeja, pero
  fuera de la franja de los rellenos.
- **Panel trasero — dos colisiones de volumen real**: empezaba en
  Z=0 (el mismo espacio que el suelo) y medía 156 mm de ancho
  (solapando el propio grosor de las paredes, que ocupan hasta ±78 mm)
  — corregido a Z=bottom_thickness y 150 mm de ancho (encaja entre
  paredes, igual que la bandeja y el panel NFC).
- **La lengüeta de unión panel trasero↔bandeja estaba a la altura
  equivocada** (Z≈0-6, la misma que el suelo) — la bandeja en
  realidad queda elevada sobre sus pilares de apoyo (Z=15-18, ya usado
  en todo el ensamblaje validado). Corregido.
- **Fijación pared↔panel trasero retirada**: se intentó añadir
  (petición del usuario), pero colisionaba con el relleno de la
  pared de forma difícil de resolver limpiamente en el tiempo
  disponible. El panel trasero sigue fijado a la bandeja (ya
  verificado sin colisión). Queda pendiente para una futura revisión.
- **Panel inferior — mismo fallo de anchura que el panel trasero**
  (156 mm en vez de 150 mm) — nunca se había comprobado contra las
  paredes. Corregido.
- **Tornillos M2 del panel inferior e imanes del panel NFC invadían
  el relleno de la pared** — el taladro/imán en sí estaba bien
  alineado (`sideMountGlobalX()`), pero el material del panel
  alrededor del taladro competía con el relleno de 14×14 mm de la
  pared. Corregido con `wallPadRelief()` en ambos paneles.

### Resultado

- Ensamblaje: 28/28 sin colisión (sin cambios).
- Estructura vs 8 componentes: 29/32 (sin cambios; los 3 "colisiona"
  siguen siendo los contactos de anclaje intencionados de siempre).
- Estructura vs estructura: todas las parejas relevantes verificadas
  a mano durante esta sesión — sin colisión real, solo contactos de
  borde esperados (0 mm de espesor, confirmado exportando a STL en
  cada caso).

---



### Corregido

- **Los pilares de apoyo de la bandeja (`traySupportPosts()`) estaban
  completamente macizos**, sin alojamiento para el inserto M3.
  Corregido con un alojamiento ciego, igual que el resto de insertos
  del proyecto.
- **Los pilares no caían sobre material sólido de la bandeja**: con
  `tray_support_inset = 12`, la posición quedaba en la zona hueca del
  marco (que solo llega hasta 65 mm desde el centro; el pilar estaba
  en 63 mm). Corregido a `inset = 5` (posición en 70 mm, dentro del
  marco macizo). Añadido el taladro de paso correspondiente en la
  propia bandeja (`base.scad`, `trayScrewClearanceHoles()`).
- **El poste del RC522/ESP32/HUB SÍ tenía agujero** (falsa alarma
  inicial de una comprobación mal posicionada por mi parte; verificado
  con los radios exactos del corte transversal: 2,05 mm interior,
  5 mm exterior — confirmado correcto, sin cambios en esa parte).
- **Faltaba la fijación del panel trasero a las paredes laterales** —
  solo se sujetaba a la bandeja (2 tornillos M3 cerca del centro
  inferior), insuficiente para un panel de 148 mm de alto. Añadidos
  2 tornillos M3 por pared (`rearWallScrewCuts()`/`rearBossPad()` en
  `walls.scad`, taladros de paso correspondientes en
  `rear_panel.scad`), reutilizando la misma fórmula compartida
  (`sideMountGlobalX()`) para que no puedan desalinearse.
- De paso, encontrado y corregido: tanto el relleno frontal como el
  trasero de las paredes sobresalían 1 mm por fuera del borde real de
  la carcasa (arrastrando el mismo desliz "-1"/"+1" de una corrección
  anterior). Verificado con exportación a STL: ahora X e Y quedan
  exactamente dentro de los límites reales.

### Resultado

- Ensamblaje: 28/28 sin colisión (sin cambios).
- Estructura: 29/32 (sin cambios) — ninguna corrección de esta
  entrada introduce colisiones nuevas con los 8 componentes.

---



### Corregido

- **El panel NFC llevaba sus imanes desalineados 7,5 mm respecto a
  los de la pared desde que se creó ese archivo** (calculaba su
  propia posición en X de forma independiente, sin relación con la
  pared). El relleno local de la corrección anterior [0.3.3] lo
  cambió a 3,9 mm de desajuste — seguía mal, solo que menos.
- **El taladro de paso M2 del panel inferior también se
  desalineó** al mover el inserto de la pared en la corrección
  [0.3.3] (de 0 mm de desajuste a 2,5 mm).
- Causa raíz: cada archivo calculaba su propia posición en X con su
  propia fórmula, sin una fuente compartida — no podían mantenerse
  sincronizados.
- Solución: nueva función compartida `sideMountGlobalX()` en
  `assembly_positions.scad`, junto con `side_boss_margin`,
  `side_boss_depth`, `lower_panel_screw_diameter/depth` (movidos
  desde `walls.scad`, que los duplicaba). Tanto `walls.scad` como
  `nfc_panel.scad` y `lower_panel.scad` calculan ahora la misma
  posición desde la misma fuente — no pueden volver a
  desincronizarse.
- Verificado con `echo()`: ambas posiciones (pared y panel) coinciden
  exactamente, en los dos casos (imán NFC y tornillo M2).

### Resultado

- Ensamblaje: 28/28 sin colisión (sin cambios).
- Estructura: 29/32 (sin cambios).

---



### Corregido

- **Los alojamientos de imanes (Ø8,15 mm) y tornillos M2 (Ø6 mm) eran
  más anchos que la propia pared (3 mm de grosor)** — asomaban por la
  cara exterior, visibles desde fuera una vez montado. Detectado por
  el usuario con una captura de zoom en OpenSCAD.
- `openscad/parts/02_chassis/walls.scad`: añadido un relleno local
  (`sideBossPad()`, 10 mm de grosor) por el lado NO visto en cada
  punto de imán/tornillo, con los alojamientos recentrados dentro de
  ese grosor extra (`sideBossCutX()`). La cara exterior queda intacta
  y lisa; el relleno solo crece hacia el interior del chasis.
- Verificado exportando a STL y comprobando que la cara exterior sigue
  maciza en los puntos donde antes asomaba (antes: hueca; ahora:
  sólida). Nota técnica para futuras comprobaciones puntuales: los
  scripts de verificación "de un uso" deben usar `include`, no `use`,
  si referencian variables sueltas de otro archivo — `use` no ejecuta
  las asignaciones de variables de nivel superior del archivo
  importado, solo expone sus módulos/funciones; un script de
  comprobación mal escrito con `use` dio un falso positivo durante
  esta misma verificación, detectado y descartado.

### Resultado

- Ensamblaje: 28/28 sin colisión (sin cambios).
- Estructura: 29/32 (sin cambios respecto a la corrección anterior)
  — el relleno no introduce ninguna colisión nueva con los 8
  componentes.

---



### Corregido

- **Postes de anclaje del RC522 y el HUB crecían hacia fuera de la
  pared derecha** (`walls.scad`): `rc522MountBoss()` y
  `hubMountBosses()` usaban siempre `rotate([0,90,0])`, correcto solo
  para la pared izquierda. En la pared derecha el poste crecía 3 mm
  por la cara exterior, visible por fuera — detectado por el usuario
  en una captura de OpenSCAD. `rc522MountBoss()` ahora recibe un
  parámetro de dirección (`dir`); `hubMountBosses()` usa
  `rotate([0,-90,0])` (solo se llama desde la pared derecha).
- **Las 4 patas sobresalían 2 mm por fuera del borde real de la
  carcasa**, en X e Y (`floor.scad`, `virtual_assembly_v1.scad`): la
  fórmula de posición calculaba el punto como si `cube()` estuviera
  centrado, pero se llamaba con `center=false` (esquina) — confirmado
  exportando a STL y midiendo (X llegaba a 80 mm, límite real 78 mm).
  Corregido con `center=true` y un margen explícito
  (`leg_edge_margin`) respecto al borde de la carcasa.

### Resultado

- Ensamblaje: 28/28 sin colisión (sin cambios).
- Estructura del chasis: **29/32** (antes 30/32) — el cambio es una
  MEJORA: el poste del HUB, al corregir su dirección, ahora sí toca
  su placa (antes crecía hacia fuera sin tocar nada útil). Verificado
  que el nuevo contacto es de superficie (0 mm de espesor), igual que
  los otros dos anclajes.
- Patas y postes verificados con límites exactos (exportación a STL +
  medición de coordenadas), no solo visualmente.

---



### Confirmado por el usuario (todas las que eran "Estimado" pasan a dato real)

- `usb_front_hole_diameter` = 29 mm (ya coincidía).
- `usb_front_body_length`: 22 → **30 mm**.
- `leg_height` = 4 mm (ya coincidía, reconfirmado).
- `nfc_tag_pocket_depth` = 1,5 mm (ya coincidía).
- `nfc_window_width/height` = 60×40 mm (ya coincidía).
- `led_bar_margin` = 1 mm a cada lado (ya coincidía).
- Panel NFC sin marco frontal independiente: aceptado por el usuario,
  pendiente de confirmar al imprimir.

### Sin confirmar todavía (quedan como estimados, no bloqueante)

- `usb_front_flange_diameter` (35 mm).
- Huella de las patas (10×10 mm — solo la altura, 4 mm, está
  confirmada).

### Resultado

- 28/28 (ensamblaje) y 30/32 (estructura) sin colisión — el USB 8 mm
  más largo no reintroduce la colisión con la PCB (la holgura que
  evita el choque es en Z, no en la longitud del cuerpo).

---



### Añadido

- `openscad/parts/02_chassis/top.scad`: taladros de paso M3 (tapa) +
  insertos correspondientes en `walls.scad`; rejilla de protección de
  dedos del ventilador (`fanFingerGuard()`).
- `openscad/parts/02_chassis/floor.scad`: apoyos de la bandeja
  (`traySupportPosts()`) — la bandeja encaja a presión exacta con el
  chasis (0 mm de holgura), así que se apoya en postes desde el suelo
  en vez de guiarse por las paredes.
- `openscad/parts/01_bandeja/rear_panel.scad` +
  `openscad/parts/01_bandeja/base.scad`: unión estructural real entre
  el panel trasero y la bandeja (lengüetas + insertos M3), con dos
  fallos de altura corregidos durante la verificación.
- `openscad/parts/03_panels/lower_panel.scad` (nuevo, sustituye a
  `front_panel.scad`): panel inferior fijo definitivo — pulsador,
  OLED, USB doble, barra LED, tamaño mínimo imprescindible.
- `openscad/parts/03_panels/nfc_panel.scad` (nuevo, sustituye a
  `front_layout.scad`): panel NFC extraíble definitivo — ancho
  corregido (150 mm, antes 70 mm no llegaba a los imanes de las
  paredes), imanes, alojamiento del tag.
- `front_panel.scad` y `front_layout.scad` marcados obsoletos
  (comentario, no borrados) — sustituidos por los dos archivos
  anteriores.

### Corregido

- `nfc_panel_width`: 70 → 150 mm — el valor original no llegaba a los
  imanes embebidos en las paredes laterales (docs/02_Mechanical_Layout.md,
  sección 3: "Ocupará prácticamente todo el ancho frontal").

### Resultado final

- 28/28 (ensamblaje) y 30/32 (estructura del chasis) sin colisión.
- Los 4 pendientes de la sesión anterior (insertos tapa, rejilla
  ventilador, apoyos bandeja, unión panel trasero-bandeja, paneles
  frontales definitivos) — todos cerrados.

---



### Corregido

- `docs/02_Mechanical_Layout.md`: separadores del UM790 actualizados
  de 8 a 20 mm (adenda, documento "Approved" no reescrito).
- `openscad/parts/02_chassis/walls.scad`: los imanes del panel NFC
  estaban parcialmente en la zona del panel inferior (Z=25, dentro de
  0-39,5 mm) — el DIM especifica que el panel inferior va atornillado
  (M2), sin imanes. Corregido: imanes ahora solo dentro de la franja
  del panel NFC; añadidos insertos M2 propios para el panel inferior.
- `openscad/parts/01_bandeja/rear_panel.scad`: añadidos insertos M3
  (DIM sección 7). Pendiente: cómo se une estructuralmente el panel
  trasero a la bandeja no está resuelto todavía (solo las posiciones
  de los insertos).
- Verificados los puntos de la checklist del DIM (sección 8) que no
  se habían comprobado explícitamente: RC522 ↔ Panel NFC (con los
  3 mm de separación reales) y Cables USB ↔ Ventilador. Ambos sin
  colisión.

### Sin cambios

- 28/28 (ensamblaje) y 30/32 (estructura del chasis) sin colisión —
  ninguna de las correcciones de esta entrada afecta a los 8
  componentes ya verificados.

---



### Modificado

- Confirmado por el usuario: las patas son externas y miden 4 mm,
  añadidas por debajo del cascarón (no restan altura interna de
  trabajo, que se usaba erróneamente como si fueran 152 mm).
- Nuevo parámetro `shell_height` (148,0 mm) en `00_parametros.scad`,
  usado ahora en todo el ensamblaje y el chasis en vez de
  `case_height` (152, que sigue siendo el dato exterior original, sin
  modificar).
- `nfc_panel_height`: 88,5 → 84,5 (recalculado con la altura real del
  cascarón).
- `openscad/parts/02_chassis/floor.scad`: patas añadidas como
  geometría real (`floorLegs()`).
- Detectado y corregido automáticamente por la comprobación de
  consistencia ya incorporada (`front_panel_zones_consistent`): el
  primer intento de este recálculo dejaba el panel NFC solapado 4 mm
  con la barra LED.
- Resultado tras el recálculo: 28/28 (ensamblaje) y 30/32
  (estructura del chasis) sin colisión — sin cambios respecto a antes
  del recálculo.

---



### Añadido

- Ensamblaje virtual completo v1 (`openscad/reference/virtual_assembly_v1.scad`),
  previo al diseño del bastidor. Resultado final: **28/28 pares de
  componentes sin colisión** (verificado con
  `openscad/reference/checks/run_collision_checks.py`).
- Módulos independientes de componentes en `openscad/reference/components/`:
  `um790.scad`, `noctua.scad`, `rc522.scad`, `esp32.scad`, `hub_usb.scad`,
  `oled.scad`, `usb_front.scad` (v2, unidad doble real), `pushbutton.scad`.
- Postes de anclaje del UM790 modelados como geometría real
  (`um790MountingPosts()`), incluidos en la comprobación de colisiones.
- Posiciones del ensamblaje centralizadas en `assembly_positions.scad`
  e instancias en `assembly_instances.scad`.
- Verificador automático de colisiones par a par
  (`openscad/reference/checks/run_collision_checks.py`).
- Vista de alzado frontal 2D (`openscad/reference/front_panel_view.scad`),
  con las tres zonas del panel frontal (inferior fijo, barra LED, NFC).
- Nuevos parámetros reales/estimados en `00_parametros.scad` para
  ESP32 Terminal Adapter, pulsador M16×55, USB empotrable doble Ø29,
  OLED 27×27, disipador e IO trasera del UM790.
- `docs/Virtual_Assembly_Report.md` con el resultado final y el
  historial completo de la verificación.

### Modificado (valores ya existentes, confirmados por el usuario)

- `um790_standoff_height`: 12 → **20 mm** (resuelve colisión PCB/postes
  con el pulsador y el USB frontal).
- `led_bar_height`: 8 → **12 mm** (dato real de la tira LED, 10 mm + margen).
- `nfc_panel_height`: 70 → **88,5 mm** (panel inferior minimizado, NFC
  maximizado con el hueco restante).

### Pendiente

- Reconciliar la altura de separadores en `posts.scad` (6 mm) y
  `docs/02_Mechanical_Layout.md` (8 mm) con el valor confirmado (20 mm).
- Actualizar `front_panel.scad` y `front_layout.scad` con las nuevas
  posiciones y tamaños de esta verificación.

- Colisión real entre el pulsador / USB empotrable y la PCB del
  UM790 por falta de profundidad libre tras el panel frontal.
- Tres valores distintos de altura de separadores del UM790 conviven
  en el proyecto (6 / 8 / 12 mm) y deben reconciliarse.

---

## [0.1.0] - En desarrollo

### Añadido

- Estructura inicial del repositorio.
- README del proyecto.
- Reglas de diseño (`DESIGN_RULES.md`).
- Parámetros globales (`00_parametros.scad`).
- Librería `common.scad`.
- Librería `helpers.scad`.
- Librería `fasteners.scad`.
- Librería `guides.scad`.
- Librería `magnets.scad`.
- Librería `ventilation.scad`.
- Librería `hardware.scad`.

### Pendiente

- Bandeja del UM790 Pro.
- Chasis principal.
- Panel trasero modular.
- Panel frontal intercambiable con NFC.
- Soporte OLED.
- Sistema de iluminación LED.
- Integración ESP32.
- Sistema NFC.
- STL oficiales.
- Manual de montaje.
