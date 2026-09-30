#!/usr/bin/env python3
"""
Simulación de graves de Prisma: DMA105-4 + DMA105-PR en la cámara acústica.

Modelo de parámetros concentrados (Thiele-Small) resuelto en frecuencia:
altavoz (eléctrico + mecánico) + radiador pasivo + compliancia de la caja con pérdidas.
Radiación en semiespacio (2π, aparato sobre una mesa), a 1 m.

Uso:  python3 tools/simulacion_audio.py [--vb 3.3]
Salida: tabla en consola + docs/img/audio_*.png
Requisitos: numpy, matplotlib
"""
import argparse
import os

import numpy as np

RHO, C = 1.18, 343.0

# --- Dayton DMA105-4 (hoja de datos de Dayton) -------------------------------
DRV = dict(Re=3.4, Le=0.3e-3, Fs=72.7, Qms=2.6, Qes=0.63, Mms=4.5e-3, Cms=1.06e-3,
           Bl=3.4, Sd=54.1e-4, Xmax=2.5e-3, Pmax=35.0, Rnom=4.0)
# --- Dayton DMA105-PR (hoja de datos de Dayton, sin masa añadida) -------------
PR = dict(Fs=37.9, Qms=7.8, Mms=29.3e-3, Cms=0.60e-3, Rms=0.90, Sd=54.1e-4, Xmax=9e-3)

QL = 7.0   # pérdidas de la caja (fugas); 7 es el valor típico para una caja bien sellada


def simulate(f, vb_l, added_g=0.0, volts=2.83, pr=True):
    """Devuelve SPL (dB), excursión altavoz (m), excursión PR (m) e impedancia (Ω)."""
    w = 2 * np.pi * f
    vb = vb_l * 1e-3
    cab = vb / (RHO * C ** 2)                       # compliancia acústica de la caja
    rmd = w_s = 2 * np.pi * DRV["Fs"]
    rmd = w_s * DRV["Mms"] / DRV["Qms"]             # pérdidas mecánicas del altavoz
    mmp = PR["Mms"] + added_g * 1e-3
    # frecuencia de sintonía aproximada para dimensionar las fugas
    kbox = PR["Sd"] ** 2 / cab
    fp = np.sqrt((1 / PR["Cms"] + kbox) / mmp) / (2 * np.pi)
    ral = QL / (2 * np.pi * fp * cab)               # resistencia acústica de fugas
    zbox = 1 / (1j * w * cab + 1 / ral)             # impedancia acústica de la caja

    ze = DRV["Re"] + 1j * w * DRV["Le"]
    zmd = 1j * w * DRV["Mms"] + rmd + 1 / (1j * w * DRV["Cms"]) + DRV["Bl"] ** 2 / ze
    zmp = 1j * w * mmp + PR["Rms"] + 1 / (1j * w * PR["Cms"])
    sd, sp = DRV["Sd"], PR["Sd"]

    # Incógnitas: velocidad del altavoz ud y del PR up (positivas hacia fuera).
    # Presión interior p = -zbox (sd ud + sp up); fuerza hacia fuera = p·S.
    a11 = zmd + zbox * sd * sd
    a12 = zbox * sd * sp
    a21 = zbox * sp * sd
    a22 = zmp + zbox * sp * sp
    fdrive = DRV["Bl"] * volts / ze
    if pr:
        det = a11 * a22 - a12 * a21
        ud = fdrive * a22 / det
        up = -fdrive * a21 / det
    else:  # caja cerrada de referencia (PR sustituido por una tapa rígida)
        ud = fdrive / a11
        up = np.zeros_like(ud)

    u_tot = sd * ud + sp * up
    p_far = 1j * w * RHO * u_tot / (2 * np.pi * 1.0)
    spl = 20 * np.log10(np.abs(p_far) / 20e-6)
    xd = np.abs(ud / (1j * w))
    xp = np.abs(up / (1j * w))
    i = (volts - DRV["Bl"] * ud) / ze
    zin = np.abs(volts / i)
    return spl, xd, xp, zin, fp


def f3(f, spl, ref_band=(300, 600)):
    ref = spl[(f >= ref_band[0]) & (f <= ref_band[1])].mean()
    below = np.where(spl < ref - 3)[0]
    below = below[f[below] < ref_band[0]]
    return f[below.max() + 1] if len(below) else f[0], ref


def max_clean_power(f, vb, added):
    """Potencia máxima sin superar Xmax del altavoz ni del PR (por encima de 40 Hz)."""
    band = f >= 40
    spl1, xd, xp, _, _ = simulate(f, vb, added, volts=np.sqrt(1 * DRV["Rnom"]))
    ratio = max((xd[band] / DRV["Xmax"]).max(), (xp[band] / PR["Xmax"]).max())
    p = min(1 / ratio ** 2, DRV["Pmax"])
    return p


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--vb", type=float, default=3.3, help="volumen neto en litros")
    args = ap.parse_args()
    f = np.logspace(np.log10(20), np.log10(1000), 600)

    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    outdir = os.path.join(root, "docs", "img")
    os.makedirs(outdir, exist_ok=True)

    cases = [("Caja cerrada (sin PR)", None), ("PR sin masa", 0.0), ("PR +10 g", 10.0), ("PR +20 g", 20.0)]
    print(f"Volumen neto: {args.vb:.2f} L · 2,83 V · 1 m · semiespacio\n")
    print(f"{'Caso':24s} {'Sintonía':>9s} {'F3':>7s} {'Pot. máx.':>10s} {'SPL máx. 100 Hz':>16s}")
    results = {}
    for name, added in cases:
        pr = added is not None
        spl, xd, xp, zin, fp = simulate(f, args.vb, added or 0.0, pr=pr)
        f3v, ref = f3(f, spl)
        if pr:
            pmax = max_clean_power(f, args.vb, added)
        else:
            _, xd1, _, _, _ = simulate(f, args.vb, 0, volts=np.sqrt(DRV["Rnom"]), pr=False)
            pmax = min(1 / ((xd1[f >= 40] / DRV["Xmax"]).max()) ** 2, DRV["Pmax"])
        spl_p, xd_p, xp_p, _, _ = simulate(f, args.vb, added or 0.0, volts=np.sqrt(pmax * DRV["Rnom"]), pr=pr)
        i100 = np.argmin(abs(f - 100))
        results[name] = dict(spl=spl, xd=xd_p, xp=xp_p, zin=zin, fp=fp if pr else None,
                             f3=f3v, pmax=pmax, spl_p=spl_p)
        tune = f"{fp:6.1f} Hz" if pr else "      —  "
        print(f"{name:24s} {tune:>9s} {f3v:5.0f} Hz {pmax:7.1f} W {spl_p[i100]:12.1f} dB")

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("\n(matplotlib no instalado: sin gráficas)")
        return

    colors = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100"]   # paleta validada (dataviz)
    ink, muted, grid = "#1f1f1e", "#6b6a64", "#e4e3dc"

    def style(ax, ylabel):
        ax.set_xscale("log")
        ax.set_xlim(20, 1000)
        ax.set_xticks([20, 30, 50, 100, 200, 500, 1000])
        ax.set_xticklabels(["20", "30", "50", "100", "200", "500", "1k"])
        ax.set_xlabel("Frecuencia (Hz)", color=muted)
        ax.set_ylabel(ylabel, color=muted)
        ax.grid(True, which="major", color=grid, lw=0.8)
        ax.tick_params(colors=muted)
        for s in ax.spines.values():
            s.set_visible(False)

    # 1. Respuesta a 2,83 V
    fig, ax = plt.subplots(figsize=(9, 5), dpi=130)
    for (name, _), col in zip(cases, colors):
        r = results[name]
        ax.plot(f, r["spl"], color=col, lw=2, label=f"{name} — F3 {r['f3']:.0f} Hz")
    style(ax, "SPL a 2,83 V / 1 m (dB)")
    ax.set_ylim(60, 95)
    ax.set_title(f"Respuesta en graves · cámara de {args.vb:.1f} L", color=ink, loc="left", fontsize=13)
    ax.legend(frameon=False, loc="lower right", labelcolor=ink)
    fig.tight_layout()
    fig.savefig(os.path.join(outdir, "audio_respuesta.png"))

    # 2. Excursión del PR y del altavoz a potencia máxima limpia (caso recomendado)
    rec = "PR +10 g"
    r = results[rec]
    fig, ax = plt.subplots(figsize=(9, 5), dpi=130)
    ax.plot(f, r["xd"] * 1e3, color=colors[0], lw=2, label="Altavoz DMA105-4")
    ax.plot(f, r["xp"] * 1e3, color=colors[1], lw=2, label="Radiador DMA105-PR")
    ax.axhline(DRV["Xmax"] * 1e3, color=colors[0], lw=1, ls="--")
    ax.axhline(PR["Xmax"] * 1e3, color=colors[1], lw=1, ls="--")
    ax.text(900, DRV["Xmax"] * 1e3 + 0.2, "Xmax altavoz 2,5 mm", color=ink, ha="right", fontsize=9)
    ax.text(900, PR["Xmax"] * 1e3 + 0.2, "Xmax radiador 9 mm", color=ink, ha="right", fontsize=9)
    style(ax, "Excursión (mm, pico)")
    ax.set_ylim(0, 11)
    ax.set_title(f"Excursión con {rec} a {r['pmax']:.0f} W", color=ink, loc="left", fontsize=13)
    ax.legend(frameon=False, loc="upper right", labelcolor=ink, bbox_to_anchor=(1, 0.8))
    fig.tight_layout()
    fig.savefig(os.path.join(outdir, "audio_excursion.png"))
    print(f"\nGráficas en {os.path.relpath(outdir, root)}/audio_respuesta.png y audio_excursion.png")


if __name__ == "__main__":
    main()
