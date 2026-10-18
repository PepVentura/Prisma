#!/usr/bin/env python3
"""Prisma — prepara el retrato animado (avatar 2,5D) a partir de las imágenes del generador.

Pon en una carpeta las imágenes con estos nombres (PNG o JPG; solo «base» es obligatoria):
    base            ojos abiertos, boca cerrada, expresión neutra
    ojos_cerrados   igual pero con los ojos cerrados
    boca_a, boca_e, boca_o, boca_i, boca_u      la boca diciendo esa vocal
    piensa          mirando arriba, pensativa
    sonrisa         sonrisa amplia (al escuchar)
    triste          apenada (cuando algo falla)
    fondo           (opcional) el decorado sin personaje: se recorta a la persona y se pone delante

    python3 prepara_retrato.py ~/retrato_nuevo            # crea ~/.config/prisma/retrato/
    python3 prepara_retrato.py ~/retrato_nuevo --salida OTRA_CARPETA

Para cada variante: la alinea con la base, localiza qué zona cambia (ojos, boca…), iguala el color
y recorta solo esa zona con bordes difuminados. Así el resto de la imagen es siempre la base y no
parpadea aunque el generador haya cambiado detalles mínimos. Escribe retrato.json con las capas y
una estimación de la cabeza y el cuello (para el balanceo); se pueden corregir a mano en el JSON.
Si una variante cambia mucho (otra postura, una mano…), se usa entera y se funde con la base.
Necesita numpy y Pillow (en Raspberry Pi OS: sudo apt install python3-numpy python3-pil) y, si hay
fondo aparte, rembg para recortar a la persona (pip install "rembg[cpu]" --break-system-packages;
la primera vez descarga un modelo de 180 MB).
"""
import argparse, json, os, sys
import numpy as np
from PIL import Image, ImageFilter

VARIANTES = ["ojos_cerrados", "boca_a", "boca_e", "boca_o", "boca_i", "boca_u", "piensa", "sonrisa", "triste"]
MAX_LADO = 1400          # la pantalla muestra el avatar a ≈410×510: no hace falta más resolución


def abre(carpeta, nombre):
    for ext in (".png", ".jpg", ".jpeg", ".webp"):
        f = os.path.join(carpeta, nombre + ext)
        if os.path.isfile(f):
            return Image.open(f).convert("RGB")
    return None


def gris(a):
    return a[..., 0] * 0.299 + a[..., 1] * 0.587 + a[..., 2] * 0.114


def desplazamiento(base, var):
    """Traslación entera que alinea var con base (correlación de fase)."""
    a, b = gris(base), gris(var)
    a, b = a - a.mean(), b - b.mean()
    v = np.hanning(a.shape[0])[:, None] * np.hanning(a.shape[1])[None, :]
    F = np.fft.fft2(a * v) * np.conj(np.fft.fft2(b * v))
    r = np.abs(np.fft.ifft2(F / (np.abs(F) + 1e-9)))
    dy, dx = np.unravel_index(np.argmax(r), r.shape)
    if dy > a.shape[0] // 2: dy -= a.shape[0]
    if dx > a.shape[1] // 2: dx -= a.shape[1]
    return int(dy), int(dx)


def mueve(a, dy, dx):
    return np.roll(np.roll(a, dy, axis=0), dx, axis=1)


def zonas(dif, paso):
    """Componentes conexas de la máscara reducida (sin scipy). Devuelve [(peso, y0, x0, y1, x1)]."""
    h, w = dif.shape
    marca = np.zeros((h, w), bool)
    sal = []
    for y in range(h):
        for x in range(w):
            if dif[y, x] <= 0 or marca[y, x]:
                continue
            pila, peso, y0, x0, y1, x1 = [(y, x)], 0.0, y, x, y, x
            marca[y, x] = True
            while pila:
                cy, cx = pila.pop()
                peso += dif[cy, cx]
                y0, x0, y1, x1 = min(y0, cy), min(x0, cx), max(y1, cy), max(x1, cx)
                for ny, nx in ((cy + 1, cx), (cy - 1, cx), (cy, cx + 1), (cy, cx - 1)):
                    if 0 <= ny < h and 0 <= nx < w and dif[ny, nx] > 0 and not marca[ny, nx]:
                        marca[ny, nx] = True
                        pila.append((ny, nx))
            sal.append((peso, y0 * paso, x0 * paso, (y1 + 1) * paso, (x1 + 1) * paso))
    return sorted(sal, reverse=True)


def solapa(a, b):
    return a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]


def region(base, var, evita=()):
    """Rectángulo (y0, x0, y1, x1) de la zona que cambia de verdad entre base y variante.
    evita: zonas ya conocidas que no cuentan (p. ej. los ojos cerrados en las imágenes de la boca)."""
    paso = 8
    d = np.abs(gris(base) - gris(var))
    d = np.asarray(Image.fromarray(np.clip(d, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(3))).astype(np.float32)
    h, w = d.shape
    p = d[: h // paso * paso, : w // paso * paso].reshape(h // paso, paso, w // paso, paso).mean(axis=(1, 3))
    umbral = max(12.0, np.percentile(p, 99) * 0.35)
    comps = [c for c in zonas(np.where(p > umbral, p, 0), paso) if not any(solapa(c[1:], e) for e in evita)]
    if not comps:
        return None
    _, y0, x0, y1, x1 = comps[0]
    alto = y1 - y0
    for peso, a0, b0, a1, b1 in comps[1:]:       # el otro ojo, la otra comisura…
        if peso < comps[0][0] * 0.25:
            break
        cy = (a0 + a1) / 2
        if y0 - alto <= cy <= y1 + alto and abs((b0 + b1) / 2 - (x0 + x1) / 2) < w * 0.35:
            y0, x0, y1, x1 = min(y0, a0), min(x0, b0), max(y1, a1), max(x1, b1)
    m = int(max(y1 - y0, x1 - x0) * 0.22) + 6
    return max(0, y0 - m), max(0, x0 - m), min(h, y1 + m), min(w, x1 + m)


def recorta(base, var, r):
    """Parche RGBA con bordes difuminados y el color igualado a la base en el borde."""
    y0, x0, y1, x1 = r
    pb, pv = base[y0:y1, x0:x1].astype(np.float32), var[y0:y1, x0:x1].astype(np.float32)
    h, w = pb.shape[:2]
    borde = max(4, int(min(h, w) * 0.22))
    yy, xx = np.mgrid[0:h, 0:w]
    dist = np.minimum.reduce([yy, xx, h - 1 - yy, w - 1 - xx]).astype(np.float32)
    alfa = np.clip(dist / borde, 0, 1)
    alfa = alfa * alfa * (3 - 2 * alfa)                      # suavizado
    anillo = dist < borde
    pv += (pb[anillo].mean(axis=0) - pv[anillo].mean(axis=0))   # misma luz y tono que la base
    rgba = np.dstack([np.clip(pv, 0, 255), alfa * 255]).astype(np.uint8)
    return Image.fromarray(rgba, "RGBA")


def recortador():
    try:
        from rembg import new_session, remove
    except ImportError:
        sys.exit('Para usar un fondo aparte hace falta rembg:  pip install "rembg[cpu]" --break-system-packages')
    sesion = new_session("isnet-general-use")
    return lambda img: np.asarray(remove(img, session=sesion, only_mask=True).convert("L")).astype(np.float32) / 255


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("carpeta")
    ap.add_argument("--salida", default=os.path.expanduser("~/.config/prisma/retrato"))
    a = ap.parse_args()

    base = abre(a.carpeta, "base")
    if base is None:
        sys.exit("Falta la imagen «base» (base.png o base.jpg) en " + a.carpeta)
    escala = min(1.0, MAX_LADO / max(base.size))
    if escala < 1:
        base = base.resize((round(base.width * escala), round(base.height * escala)), Image.LANCZOS)
    W, H = base.size
    nb = np.asarray(base)
    os.makedirs(a.salida, exist_ok=True)
    anterior = {}
    fj = os.path.join(a.salida, "retrato.json")
    if os.path.isfile(fj):
        with open(fj) as f:
            anterior = json.load(f)

    fondo = abre(a.carpeta, "fondo")
    mascara = recortador() if fondo else None
    if fondo:
        e = min(1.0, MAX_LADO / max(fondo.size))
        if e < 1:
            fondo = fondo.resize((round(fondo.width * e), round(fondo.height * e)), Image.LANCZOS)
        fondo.save(os.path.join(a.salida, "fondo.jpg"), quality=88)
        m = mascara(base)
        Image.fromarray(np.dstack([nb, m * 255]).astype(np.uint8), "RGBA").save(os.path.join(a.salida, "base.png"))
        nombre_base = "base.png"
        print("  base: persona recortada del fondo")
    else:
        base.save(os.path.join(a.salida, "base.jpg"), quality=90)
        nombre_base = "base.jpg"

    capas, conocidas = {}, []
    for n in VARIANTES:
        v = abre(a.carpeta, n)
        if v is None:
            continue
        if v.size != base.size:
            v = v.resize(base.size, Image.LANCZOS)
        nv = np.asarray(v).astype(np.float32)
        dy, dx = desplazamiento(nb.astype(np.float32), nv)
        if abs(dy) > H * 0.1 or abs(dx) > W * 0.1:
            dy = dx = 0
        nv = mueve(nv, dy, dx)
        if n.startswith("boca_") and conocidas:
            # La boca: siempre la misma ventana bajo los ojos (nariz → barbilla). Al abrirla, el generador
            # suele retocar también la barbilla y el cuello, y eso no debe convertirla en otra postura
            oy0, ox0, oy1, ox1 = conocidas[0]
            ancho = ox1 - ox0
            cx, cy = (ox0 + ox1) / 2, (oy0 + oy1) / 2
            r = (int(oy1 - ancho * 0.04), int(cx - ancho * 0.42), int(min(H, cy + ancho * 0.9)), int(cx + ancho * 0.42))
        else:
            r = region(nb.astype(np.float32), nv, conocidas if n.startswith("boca_") else ())
        if r is None:
            print(f"  {n}: no se aprecia ningún cambio respecto a la base; se omite")
            continue
        y0, x0, y1, x1 = r
        if (y1 - y0) * (x1 - x0) > 0.1 * W * H and not n.startswith("boca_"):
            # Cambia la postura: la variante entera (recortada si hay fondo) sustituye a la base con un fundido
            img = Image.fromarray(np.clip(nv, 0, 255).astype(np.uint8))
            al = mascara(img) if mascara else np.ones((H, W), np.float32)
            ys, xs = np.nonzero(al > 0.02)
            y0, y1, x0, x1 = (int(ys.min()), int(ys.max()) + 1, int(xs.min()), int(xs.max()) + 1) if len(ys) else (0, H, 0, W)
            rgba = np.dstack([np.asarray(img), al * 255]).astype(np.uint8)[y0:y1, x0:x1]
            Image.fromarray(rgba, "RGBA").save(os.path.join(a.salida, n + ".png"))
            capas[n] = {"archivo": n + ".png", "x": x0, "y": y0, "w": x1 - x0, "h": y1 - y0, "sustituye": True}
            print(f"  {n}: cambia la postura; se usa entera ({x1 - x0}×{y1 - y0}) con fundido")
            continue
        recorta(nb, nv, r).save(os.path.join(a.salida, n + ".png"))
        capas[n] = {"archivo": n + ".png", "x": x0, "y": y0, "w": x1 - x0, "h": y1 - y0}
        if n == "ojos_cerrados":
            conocidas.append(r)
        print(f"  {n}: zona {x1 - x0}×{y1 - y0} en ({x0}, {y0}), desplazada ({dx}, {dy})")

    # Cabeza y cuello a partir de ojos y boca (corregibles a mano en retrato.json)
    ojos = capas.get("ojos_cerrados")
    boca = next((capas[k] for k in ("boca_a", "boca_o", "boca_e", "boca_i", "boca_u") if k in capas), None)
    if ojos and boca:
        ox, oy = ojos["x"] + ojos["w"] / 2, ojos["y"] + ojos["h"] / 2
        by = boca["y"] + boca["h"] * 0.3        # la ventana de la boca baja hasta la barbilla
        d = max(by - oy, H * 0.04)
        cabeza = {"x": round(ox), "y": round(oy + d * 0.15), "r": round(d * 2.6)}
        cuello_y = round(by + d * 1.0)
    else:
        cabeza = {"x": W // 2, "y": round(H * 0.42), "r": round(H * 0.22)}
        cuello_y = round(H * 0.62)
    datos = {
        "ancho": W, "alto": H, "base": nombre_base,
        "cabeza": anterior.get("cabeza", cabeza),
        "cuello_y": anterior.get("cuello_y", cuello_y),
        "centro": anterior.get("centro", {"x": cabeza["x"], "y": round(cabeza["y"] + cabeza["r"] * 0.55)}),
        "zoom": anterior.get("zoom", 1.0),
        "capas": capas,
    }
    if fondo:
        datos["fondo"] = anterior.get("fondo") or {"archivo": "fondo.jpg", "ancho": fondo.width, "alto": fondo.height,
                                                   "centro": {"x": fondo.width // 2, "y": fondo.height // 2}}
    with open(fj, "w") as f:
        json.dump(datos, f, indent=1, ensure_ascii=False)
    print(f"Listo: {len(capas)} capas en {a.salida}. Recarga la pantalla (F5) para verlo.")
    if not any(k.startswith("boca_") for k in capas):
        print("Aviso: sin imágenes de boca no moverá los labios.")


if __name__ == "__main__":
    main()
