#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
T6 (prueba 2) — Perfil dosis-por-edad per cápita, ventanas fijas, controles por perpetrador y dos relojes (víctimas y expulsiones).

Ejecutar:  python3 -I /home/user/JMP/code/analysis/t6_percapita_profile.py

Réplica de T2b con: dosis = víctimas por 1.000 habitantes (población 2005, Panel CEDE; alternativa winsorizada en el p99 de la
muestra de estimación); ventanas de longitud FIJA relativas al mes de nacimiento, sin truncar en el examen (pre-concepción
[−45, −10], in utero [−9, −1], 0-2 [0, 35], 3-5 [36, 71], 6-11 [72, 143], 12-17 [144, 215]); cohortes 1988-2003; calendario A;
sin 2017-2; EF municipio + cohorte × departamento + periodo × edad al examen (entera); muestra T (451) sin municipios ≥ 500.000
habitantes (y con ellos); errores agrupados por municipio (CR1). Relojes: PARA (principal), GUE y EST (controles), POSD (placebo)
del panel CNMH mensual; expulsiones RUV (anual, repartidas uniformemente entre los 12 meses del año) por 1.000 habitantes.
Columnas: PARA sola; PARA + GUE + EST; GUE sola; POSD sola; PARA + GUE + EST + POSD; PARA + RUV (dos relojes); RUV sola;
PARA + RUV + GUE + EST. Placebo pre-concepción en cada columna y reloj. A nivel de celda municipio × cohorte (sin ponderar):
correlación residual entre ventanas y entre relojes, VIF y varianza residual tras EF municipio + cohorte × dpto.

Salidas: data/derived/t6_pc_coefs.csv, t6_pc_tests.csv, t6_pc_descriptivos.csv, t6_pc_within_corr_cells.csv, t6_pc_resid_var_cells.csv,
         t6_dos_relojes_coefs.csv, t6_dos_relojes_corr.csv, t6_pc_resumen.json; scoping/proposal/fig9_perfil_percapita.pdf
"""
import os, sys, json, time, warnings
import numpy as np
import pandas as pd
import pyarrow.parquet as pq
from scipy import stats as sps
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

warnings.filterwarnings("ignore")
T0 = time.time()
def log(msg): print(f"[{time.time()-T0:7.1f}s] {msg}", flush=True)

ROOT = "/home/user/JMP"
F_SABER = f"{ROOT}/data/derived/saber11_slim.parquet"
F_CNMH = f"{ROOT}/data/derived/cnmh_muni_month_victims.csv"
F_T = f"{ROOT}/data/derived/t2_A_T1_muestra_T.csv"
F_POP = f"{ROOT}/data/derived/t5_poblacion_2005.csv"
F_RUV = f"{ROOT}/data/raw/ruv/ruv_jngaravitoc/Reporte_Personas_Desplazados_por_Anio.xlsx"
OUT_D = f"{ROOT}/data/derived"; OUT_P = f"{ROOT}/scoping/proposal"
F_FIG = f"{OUT_P}/fig9_perfil_percapita.pdf"

COH_LO, COH_HI = 1988, 2003
BIG_POP = 500_000
NON_MUNI = {"00000", "47000"}
RECODE = {"27086": "27615"}     # Belén de Bajirá -> Riosucio (como en T5)
WINDOWS = [("preconc", -45, -10, "Pre-conc.\n[−45, −10]"), ("inutero", -9, -1, "In utero\n[−9, −1]"), ("a0_2", 0, 35, "0-2\n[0, 35]"),
           ("a3_5", 36, 71, "3-5\n[36, 71]"), ("a6_11", 72, 143, "6-11\n[72, 143]"), ("a12_17", 144, 215, "12-17\n[144, 215]")]
WKEYS = [w[0] for w in WINDOWS]; WLAB = {w[0]: w[3] for w in WINDOWS}
CLOCKS = ["PARA", "GUE", "EST", "POSD", "RUV"]
COLOR, GRAY = "#1f4e79", "#8a8984"

# ---------------------------------------------------------------- econometría (idéntica a t6_event_study_exit.py)
def demean(M, groups, w=None, tol=1e-9, maxit=600):
    M = np.array(M, dtype=np.float64, order="F", copy=True)
    K = M.shape[1]
    w = np.ones(M.shape[0]) if w is None else np.asarray(w, dtype=np.float64)
    gs = [(g, np.bincount(g, weights=w)) for g in groups]
    scale = np.maximum(M.std(axis=0), 1e-12)
    it = 0
    for it in range(1, maxit + 1):
        dmax = 0.0
        for g, c in gs:
            for k in range(K):
                mu = np.bincount(g, weights=w * M[:, k], minlength=len(c)) / c
                M[:, k] -= mu[g]
                dmax = max(dmax, np.abs(mu).max() / scale[k])
        if dmax < tol: break
    chk = 0.0
    for g, c in gs:
        for k in range(K):
            mu = np.bincount(g, weights=w * M[:, k], minlength=len(c)) / c
            chk = max(chk, np.abs(mu).max() / scale[k])
    return M, it, chk

def ols_cluster(y, X, cl):
    N, K = X.shape; G = int(cl.max()) + 1
    XtX_inv = np.linalg.inv(X.T @ X); beta = XtX_inv @ (X.T @ y); e = y - X @ beta
    Sg = np.column_stack([np.bincount(cl, weights=X[:, k] * e, minlength=G) for k in range(K)])
    V = (G / (G - 1.0)) * ((N - 1.0) / (N - K)) * XtX_inv @ (Sg.T @ Sg) @ XtX_inv
    return beta, V, 1.0 - (e @ e) / (y @ y)

def codes(a): return np.unique(np.asarray(a), return_inverse=True)[1].astype(np.int64)

# ---------------------------------------------------------------- 1. paneles mensuales por reloj (municipios T)
def build_panels(T):
    p = pd.read_csv(F_CNMH, dtype={"muni": str}, usecols=["muni", "ym", "PARA", "GUE", "EST", "POSD"])
    p["muni"] = p.muni.replace(RECODE)
    YM0, YM1 = int(p.ym.min()), int(p.ym.max()); TN = YM1 - YM0 + 1
    munis = T.muni.tolist(); mi = {m: i for i, m in enumerate(munis)}
    pT = p[p.muni.isin(mi)]
    P = {}
    for c in ["PARA", "GUE", "EST", "POSD"]:
        A = np.zeros((len(munis), TN))
        np.add.at(A, (pT.muni.map(mi).values, (pT.ym - YM0).values), pT[c].values.astype(float))
        P[c] = A
    # RUV: expulsados por municipio × año (ambos tipos de víctima, como T5), repartidos uniformemente en los 12 meses del año
    ruv = pd.read_excel(F_RUV, dtype={"CODIGO DANE": str})
    ruv.columns = ["tipo", "ano", "cod", "depto", "municipio", "expulsados", "recibidos", "declarados"]
    ruv["muni"] = ruv.cod.str.strip().str.zfill(5).replace(RECODE); ruv["ano"] = ruv.ano.astype(int)
    ry = ruv[ruv.muni.isin(mi)].groupby(["muni", "ano"]).expulsados.sum()
    A = np.zeros((len(munis), TN))
    for (m, y), v in ry.items():
        j0 = y * 12 - YM0
        if 0 <= j0 and j0 + 12 <= TN: A[mi[m], j0:j0 + 12] = v / 12.0
        elif j0 < TN and j0 + 12 > 0: A[mi[m], max(j0, 0):min(j0 + 12, TN)] = v / 12.0
    P["RUV"] = A
    Y0, Y1 = int(ruv.ano.min()), int(ruv.ano.max())
    log(f"Paneles: CNMH {YM0//12}-{YM0%12+1:02d} a {YM1//12}-{YM1%12+1:02d} ({TN} meses); RUV años {Y0}-{Y1}, expulsados en T 1997-2010: "
        f"{int(ry[[y in range(1997, 2011) for _, y in ry.index]].sum()):,}; totales en T: " + ", ".join(f"{c} {P[c].sum():,.0f}" for c in CLOCKS))
    cum = {c: np.concatenate([np.zeros((len(munis), 1)), np.cumsum(P[c], axis=1)], axis=1) for c in CLOCKS}
    return P, cum, mi, YM0, TN

# ---------------------------------------------------------------- 2. muestra individual con dosis
def build_sample(T, cum, mi, YM0, TN):
    cols = ["periodo", "year", "sem", "birth_year", "birth_month", "age_at_exam", "muni_res", "dpto_res", "sexo", "score_z", "flag_truncated_file"]
    df = pq.read_table(F_SABER, columns=cols, filters=[("birth_year", ">=", COH_LO), ("birth_year", "<=", COH_HI)]).to_pandas()
    flow = {"cohortes_1988_2003": len(df)}
    df["muni_res"] = df.muni_res.replace(RECODE)
    df = df[df.muni_res.isin(mi)]; flow["en_T_451"] = len(df)
    df = df[df["sem"] == 2]; flow["calendario_A"] = len(df)
    df = df[~df.flag_truncated_file]; flow["sin_2017_2"] = len(df)
    df = df[df.score_z.notna() & df.sexo.isin(["F", "M"]) & df.age_at_exam.notna() & df.birth_month.notna()]; flow["con_score_sexo_edad"] = len(df)
    df = df.reset_index(drop=True)
    log(f"Muestra individual: {flow}")
    df["female"] = (df.sexo == "F").astype(np.int8)
    df["age_int"] = np.floor(df.age_at_exam).astype(np.int16)
    df["per_age"] = df.periodo.astype(str) + "_" + df.age_int.astype(str)
    dp = df.dpto_res.astype(object); m = dp.isna(); dp[m] = df.muni_res[m].str[:2]; df["dpto_res"] = dp.astype(str)
    df["cohdep"] = df.birth_year.astype(str) + "_" + df.dpto_res
    df["birth_ym"] = (df.birth_year.astype(int) * 12 + df.birth_month.astype(int) - 1).astype(np.int32)
    df["exam_ym"] = (df.year.astype(int) * 12 + 7).astype(np.int32)
    Ti = T.set_index("muni")
    df["pop2005"] = df.muni_res.map(Ti.pop2005).astype(float); df["big"] = df.muni_res.map(Ti.big).astype(bool)
    midx = df.muni_res.map(mi).values.astype(int)
    b = (df.birth_ym.values - YM0).astype(int)
    for key, lo, hi, _ in WINDOWS:
        s = np.clip(b + lo, 0, TN); e1 = np.clip(b + hi + 1, 0, TN)
        df[f"mobs_{key}"] = (e1 - s).astype(np.int16)                     # meses de la ventana dentro del panel
        df[f"exam_in_{key}"] = ((df.exam_ym.values - df.birth_ym.values) <= hi).astype(np.int8)   # examen antes del fin de la ventana
        for c in CLOCKS:
            v = cum[c][midx, e1] - cum[c][midx, s]
            df[f"{c}_{key}"] = (1000.0 * v / df.pop2005.values).astype(np.float32)   # por 1.000 habitantes de 2005
    df["muni_code"] = pd.factorize(df.muni_res)[0]
    df = df.drop(columns=["sexo", "periodo", "flag_truncated_file"])
    return df, flow

# ---------------------------------------------------------------- 3. estimación por bloques
def run_block(D, mask, sample, scale_cols, specs, fe_cols, note=""):
    """Demean una vez todas las columnas (score_z, female, dosis) y estima cada spec (lista de columnas X)."""
    idx = np.flatnonzero(mask)
    allx = sorted({c for _, xs in specs for c in xs})
    names = ["score_z", "female"] + allx
    M = np.column_stack([D[c].values[idx].astype(np.float64) for c in names]); ci = {c: i for i, c in enumerate(names)}
    groups = [codes(D[c].values[idx]) for c in fe_cols]; cl = codes(D["muni_code"].values[idx])
    t1 = time.time(); Md, it, chk = demean(M, groups); del M
    sd_w = Md.std(axis=0)
    log(f"  [{sample}{(' | ' + note) if note else ''}] N={len(idx):,} clusters={int(cl.max())+1} FE={fe_cols} iter={it} chk={chk:.1e} ({time.time()-t1:.0f}s)")
    rows, tests = [], []
    for spec, xs in specs:
        xcols = xs + ["female"]
        X = Md[:, [ci[c] for c in xcols]]
        beta, V, r2 = ols_cluster(Md[:, ci["score_z"]], X, cl); se = np.sqrt(np.diag(V))
        for i, c in enumerate(xcols):
            clock, win = (c.split("_", 1) if c != "female" else ("", "female"))
            win = win.replace("w_", "") if win.startswith("w_") else win
            rows.append({"sample": sample, "note": note, "fe": "+".join(fe_cols), "spec": spec, "clock": clock, "window": win, "term": c,
                         "beta": beta[i], "se": se[i], "ci_lo": beta[i] - 1.96 * se[i], "ci_hi": beta[i] + 1.96 * se[i],
                         "p": 2 * sps.norm.sf(abs(beta[i] / se[i])), "within_sd_x": sd_w[ci[c]], "beta_x_within_sd": beta[i] * sd_w[ci[c]],
                         "N": len(idx), "n_clusters": int(cl.max()) + 1, "r2_within": r2, "demean_iter": it, "demean_chk": chk})
        # tests: placebo pre-concepción por reloj; igualdad 0-2 = 3-5 por reloj; conjunto postnatal = 0
        for clock in sorted({c.split("_", 1)[0] for c in xs}):
            pre = [c for c in xs if c.split("_", 1)[0] == clock and c.endswith("preconc")]
            if pre:
                i = xcols.index(pre[0])
                tests.append({"sample": sample, "note": note, "fe": "+".join(fe_cols), "spec": spec, "clock": clock, "test": "placebo pre-concepción = 0",
                              "stat": beta[i] / se[i], "p": 2 * sps.norm.sf(abs(beta[i] / se[i])), "N": len(idx)})
            a, b_ = [c for c in xs if c.split("_", 1)[0] == clock and c.endswith("a0_2")], [c for c in xs if c.split("_", 1)[0] == clock and c.endswith("a3_5")]
            if a and b_:
                i, j = xcols.index(a[0]), xcols.index(b_[0]); d = beta[i] - beta[j]; v = V[i, i] + V[j, j] - 2 * V[i, j]
                tests.append({"sample": sample, "note": note, "fe": "+".join(fe_cols), "spec": spec, "clock": clock, "test": "β(0-2) = β(3-5)",
                              "stat": d / np.sqrt(v), "p": 2 * sps.norm.sf(abs(d / np.sqrt(v))), "N": len(idx)})
            post = [xcols.index(c) for c in xs if c.split("_", 1)[0] == clock and not c.endswith("preconc")]
            if post:
                bb = beta[post]; VV = V[np.ix_(post, post)]; st = float(bb @ np.linalg.solve(VV, bb))
                tests.append({"sample": sample, "note": note, "fe": "+".join(fe_cols), "spec": spec, "clock": clock, "test": "conjunto in utero..12-17 = 0",
                              "stat": st, "p": sps.chi2.sf(st, len(post)), "N": len(idx)})
    return rows, tests

# ---------------------------------------------------------------- 4. celdas: correlaciones within, VIF, varianza residual
def cell_diagnostics(df, mask, sample):
    S = df[mask]
    dcols = [f"{c}_{w}" for c in CLOCKS for w in WKEYS]
    cells = S.groupby(["muni_res", "birth_year"], observed=True)[dcols].mean().reset_index()
    cells["N"] = S.groupby(["muni_res", "birth_year"], observed=True).size().values
    cells["cohdep"] = cells.birth_year.astype(str) + "_" + cells.muni_res.str[:2]
    g = [codes(cells.muni_res.values), codes(cells.cohdep.values)]
    M = cells[dcols].values.astype(float)
    Md, it, chk = demean(M, g)
    raw_var = M.var(axis=0); res_var = Md.var(axis=0)
    rv = pd.DataFrame({"sample": sample, "term": dcols, "clock": [c.split("_", 1)[0] for c in dcols], "window": [c.split("_", 1)[1] for c in dcols],
                       "n_cells": len(cells), "mean": M.mean(axis=0), "sd_raw": np.sqrt(raw_var), "sd_resid": np.sqrt(res_var),
                       "var_resid_share": res_var / np.where(raw_var > 0, raw_var, np.nan), "share_pos": (M > 0).mean(axis=0)})
    C = pd.DataFrame(np.corrcoef(Md.T), index=dcols, columns=dcols); C.insert(0, "sample", sample)
    # dos relojes: ρ(V_a, E_a) residual por ventana, VIF pareado y VIF en el conjunto de 12 regresores
    rows = []
    iV = [dcols.index(f"PARA_{w}") for w in WKEYS]; iE = [dcols.index(f"RUV_{w}") for w in WKEYS]
    X12 = Md[:, iV + iE]; X12 = X12 / X12.std(axis=0)
    R = np.corrcoef(X12.T); vif12 = np.diag(np.linalg.inv(R))
    XV = Md[:, iV] / Md[:, iV].std(axis=0); vifV = np.diag(np.linalg.inv(np.corrcoef(XV.T)))
    for j, w in enumerate(WKEYS):
        rho = np.corrcoef(Md[:, iV[j]], Md[:, iE[j]])[0, 1]
        rho_raw = np.corrcoef(M[:, iV[j]], M[:, iE[j]])[0, 1]
        rho_g = np.corrcoef(Md[:, iV[j]], Md[:, dcols.index(f"GUE_{w}")])[0, 1]
        rows.append({"sample": sample, "window": w, "n_cells": len(cells), "corr_raw_V_E": rho_raw, "corr_resid_V_E": rho, "vif_pair_V_E": 1 / (1 - rho ** 2),
                     "vif_V_in_12": vif12[j], "vif_E_in_12": vif12[6 + j], "vif_V_in_6_PARA": vifV[j], "corr_resid_V_GUE": rho_g,
                     "veredicto_PI": "aprobado (ρ < 0,7)" if abs(rho) < 0.7 else ("gris (0,7-0,8)" if abs(rho) < 0.8 else "letal (> 0,8)")})
    two = pd.DataFrame(rows)
    log(f"  celdas [{sample}]: {len(cells):,}; demean iter={it} chk={chk:.1e}; ρ resid V/E por ventana: "
        + ", ".join(f"{r.window} {r.corr_resid_V_E:.2f}" for r in two.itertuples()))
    return rv, C, two, cells

# ---------------------------------------------------------------- 5. figura
def make_figure(coef, two):
    plt.rcParams.update({"font.family": "serif", "font.size": 8, "axes.titlesize": 8.5, "axes.labelsize": 8, "xtick.labelsize": 6.5,
                         "ytick.labelsize": 7, "legend.fontsize": 6.8, "pdf.fonttype": 42, "axes.spines.top": False,
                         "axes.spines.right": False, "axes.linewidth": 0.6, "xtick.major.width": 0.5, "ytick.major.width": 0.5})
    fig, axes = plt.subplots(1, 3, figsize=(8, 4.5))
    xpos = np.arange(len(WKEYS))
    def series(ax, sample, spec, clock, scale, off, color, mk, fc, ls, label, note=""):
        d = coef[(coef["sample"] == sample) & (coef.spec == spec) & (coef.clock == clock) & (coef.note == note) & (coef.scale == scale)
                 & (coef.fe == "muni_code+cohdep+per_age") & coef.window.isin(WKEYS)].set_index("window").reindex(WKEYS)
        if d.beta.isna().all(): return
        ax.errorbar(xpos + off, d.beta_x_within_sd, yerr=1.96 * d.se * d.within_sd_x, fmt=mk, ms=3, color=color, mfc=fc, mew=0.8, ecolor=color,
                    elinewidth=0.7, capsize=0, ls=ls, lw=0.8, label=label, zorder=3)
    for ax in axes:
        ax.axhline(0, color="#bbbbbb", lw=0.6, zorder=1); ax.set_xticks(xpos); ax.set_xticklabels([WLAB[w] for w in WKEYS]); ax.margins(x=0.08)
    ax = axes[0]
    series(ax, "nobig", "PARA", "PARA", "pc", -0.2, COLOR, "o", COLOR, "-", "PARA sola")
    series(ax, "nobig", "PARA+GUE+EST", "PARA", "pc", 0.0, COLOR, "s", "white", "--", "PARA, con GUE y EST")
    series(ax, "nobig", "GUE", "GUE", "pc", 0.2, GRAY, "^", GRAY, "-", "GUE sola")
    ax.set_title("(a) Perpetrador: PARA frente a GUE", loc="left"); ax.set_ylabel("β × DE within de la dosis (DE de score_z)")
    ax = axes[1]
    series(ax, "nobig", "PARA", "PARA", "pc", -0.2, COLOR, "o", COLOR, "-", "sin ciudades ≥ 500 mil")
    series(ax, "nobig", "PARA", "PARA", "pcw", 0.0, COLOR, "s", "white", "--", "ídem, winsorizada p99")
    series(ax, "all", "PARA", "PARA", "pc", 0.2, GRAY, "o", GRAY, "-", "con ciudades ≥ 500 mil")
    ax.set_title("(b) PARA sola: muestra y escala", loc="left")
    ax = axes[2]
    series(ax, "nobig", "PARA+RUV", "PARA", "pc", -0.15, COLOR, "o", COLOR, "-", "víctimas PARA (V_a)")
    series(ax, "nobig", "PARA+RUV", "RUV", "pc", 0.15, COLOR, "D", "white", "--", "expulsiones RUV (E_a)")
    series(ax, "nobig", "RUV", "RUV", "pc", 0.3, GRAY, "D", GRAY, ":", "RUV sola")
    ax.set_title("(c) Dos relojes: V_a y E_a conjuntas", loc="left")
    t = two[two["sample"] == "nobig"].set_index("window").reindex(WKEYS)
    ax.text(0.02, 0.02, "ρ resid. V/E por ventana: " + " ".join(f"{r:.2f}" for r in t.corr_resid_V_E), transform=ax.transAxes, fontsize=6, va="bottom")
    for ax in axes: ax.legend(frameon=False, loc="upper left")
    N = int(coef[(coef["sample"] == "nobig") & (coef.scale == "pc")].N.max()); G = int(coef[(coef["sample"] == "nobig")].n_clusters.max())
    fig.suptitle(f"Perfil dosis-por-edad per cápita (víctimas o expulsados por 1.000 hab. 2005), ventanas fijas, cohortes 1988-2003, calendario A, sin 2017-2. "
                 f"EF municipio, cohorte × dpto., periodo × edad; IC 95 %, cluster municipio. Muestra T sin ciudades: N = {N:,}, {G} municipios".replace(",", "."),
                 fontsize=6.8, x=0.01, ha="left", y=0.995)
    fig.tight_layout(rect=(0, 0, 1, 0.95)); fig.savefig(F_FIG); plt.close(fig)
    log(f"Figura: {F_FIG}")

# ---------------------------------------------------------------- 6. main
def main():
    T = pd.read_csv(F_T, dtype={"muni": str}); T = T[~T.muni.isin(NON_MUNI)].copy(); T["muni"] = T.muni.replace(RECODE)
    pop = pd.read_csv(F_POP, dtype={"muni": str})[["muni", "pop2005"]]
    T = T.merge(pop, on="muni", how="left"); assert T.pop2005.notna().all() and len(T) == 451
    T["big"] = T.pop2005 >= BIG_POP
    P, cum, mi, YM0, TN = build_panels(T)
    df, flow = build_sample(T, cum, mi, YM0, TN)
    big = df.big.values
    nobig = ~big
    # winsorización p99 (muestra de estimación sin ciudades) para PARA, GUE y RUV
    caps = {}
    for c in ["PARA", "GUE", "RUV"]:
        for w in WKEYS:
            cap = float(np.quantile(df.loc[nobig, f"{c}_{w}"].values, 0.99)); caps[f"{c}_{w}"] = cap
            df[f"{c}_w_{w}"] = np.minimum(df[f"{c}_{w}"].values, cap).astype(np.float32)
    # descriptivos
    desc = []
    for smp, m in [("nobig", nobig), ("all", np.ones(len(df), bool))]:
        S = df[m]
        base = {"sample": smp, "N": len(S), "n_muni": S.muni_res.nunique(), "share_female": S.female.mean()}
        for c in CLOCKS:
            for w in WKEYS:
                v = S[f"{c}_{w}"]
                base.update({f"{c}_{w}_mean": v.mean(), f"{c}_{w}_sd": v.std(), f"{c}_{w}_p50": v.median(), f"{c}_{w}_p99": v.quantile(.99),
                             f"{c}_{w}_share_pos": (v > 0).mean()})
        for w in WKEYS:
            base[f"{w}_share_fully_in_panel"] = (S[f"mobs_{w}"] == dict((k, hi - lo + 1) for k, lo, hi, _ in WINDOWS)[w]).mean()
            base[f"{w}_share_exam_before_window_end"] = S[f"exam_in_{w}"].mean()
        desc.append(base)
    pd.DataFrame(desc).to_csv(f"{OUT_D}/t6_pc_descriptivos.csv", index=False)
    d0 = desc[0]
    log("Descriptivos (sin ciudades): " + "; ".join(f"{c} 0-2 media {d0[f'{c}_a0_2_mean']:.2f}/1.000 (sd {d0[f'{c}_a0_2_sd']:.2f})" for c in CLOCKS))
    log("  12-17 observada por completo en el panel: {:.1%}; examen antes del fin de 12-17: {:.1%}; pre-conc. completa: {:.1%}".format(
        d0["a12_17_share_fully_in_panel"], d0["a12_17_share_exam_before_window_end"], d0["preconc_share_fully_in_panel"]))

    V = lambda c, ws=WKEYS: [f"{c}_{w}" for w in ws]
    Vw = lambda c: [f"{c}_w_{w}" for w in WKEYS]
    SPECS_PC = [("PARA", V("PARA")), ("PARA+GUE+EST", V("PARA") + V("GUE") + V("EST")), ("GUE", V("GUE")), ("POSD", V("POSD")),
                ("PARA+GUE+EST+POSD", V("PARA") + V("GUE") + V("EST") + V("POSD")), ("PARA+RUV", V("PARA") + V("RUV")), ("RUV", V("RUV")),
                ("PARA+RUV+GUE+EST", V("PARA") + V("RUV") + V("GUE") + V("EST")), ("EST", V("EST"))]
    SPECS_W = [("PARA", Vw("PARA")), ("PARA+GUE+EST", Vw("PARA") + Vw("GUE") + V("EST")), ("GUE", Vw("GUE")), ("PARA+RUV", Vw("PARA") + Vw("RUV"))]
    FE3 = ["muni_code", "cohdep", "per_age"]; FE2 = ["muni_code", "cohdep"]
    coef, tests = [], []
    def add(res, scale):
        r, t = res
        for x in r: x["scale"] = scale
        for x in t: x["scale"] = scale
        coef.extend(r); tests.extend(t)
    log("Bloque 1: T sin ciudades, per cápita, EF 3 vías")
    add(run_block(df, nobig, "nobig", None, SPECS_PC, FE3), "pc")
    log("Bloque 2: T sin ciudades, per cápita winsorizada p99, EF 3 vías")
    add(run_block(df, nobig, "nobig", None, SPECS_W, FE3), "pcw")
    log("Bloque 3: T sin ciudades, per cápita, EF 2 vías (comparable con T2b)")
    add(run_block(df, nobig, "nobig", None, [s for s in SPECS_PC if s[0] in ("PARA", "PARA+GUE+EST", "GUE", "PARA+RUV")], FE2), "pc")
    log("Bloque 4: T con ciudades, per cápita, EF 3 vías")
    add(run_block(df, np.ones(len(df), bool), "all", None, [s for s in SPECS_PC if s[0] in ("PARA", "PARA+GUE+EST", "GUE", "PARA+RUV", "RUV")], FE3), "pc")
    log("Bloque 5: robustez, cohortes 1989-2003 (pre-concepción observada por completo), sin ciudades")
    add(run_block(df, nobig & (df.birth_year.values >= 1989), "nobig", None, [("PARA", V("PARA")), ("PARA+RUV", V("PARA") + V("RUV"))], FE3,
                  note="cohortes 1989-2003"), "pc")
    coef = pd.DataFrame(coef); tests = pd.DataFrame(tests)
    coef.to_csv(f"{OUT_D}/t6_pc_coefs.csv", index=False); tests.to_csv(f"{OUT_D}/t6_pc_tests.csv", index=False)
    coef[coef.spec.str.contains("RUV")].to_csv(f"{OUT_D}/t6_dos_relojes_coefs.csv", index=False)

    log("Diagnósticos de celda (correlaciones within, VIF, varianza residual)")
    rvs, Cs, twos = [], [], []
    for smp, m in [("nobig", nobig), ("all", np.ones(len(df), bool))]:
        rv, C, two, cells = cell_diagnostics(df, m, smp)
        rvs.append(rv); Cs.append(C); twos.append(two)
    rv = pd.concat(rvs); C = pd.concat(Cs); two = pd.concat(twos)
    rv.to_csv(f"{OUT_D}/t6_pc_resid_var_cells.csv", index=False); C.to_csv(f"{OUT_D}/t6_pc_within_corr_cells.csv")
    two.to_csv(f"{OUT_D}/t6_dos_relojes_corr.csv", index=False)

    make_figure(coef, two)
    # resumen en consola
    pd.set_option("display.width", 250)
    main = coef[(coef["sample"] == "nobig") & (coef.fe == "muni_code+cohdep+per_age") & (coef.note == "") & coef.window.isin(WKEYS)]
    for sc in ["pc", "pcw"]:
        print(f"\n== β por unidad (1 por 1.000 hab.), sin ciudades, escala {sc} ==")
        print(main[main.scale == sc].pivot_table(index="window", columns=["spec", "clock"], values="beta").reindex(WKEYS).round(4).to_string())
        print(main[main.scale == sc].pivot_table(index="window", columns=["spec", "clock"], values="se").reindex(WKEYS).round(4).to_string())
    print("\n== β × DE within, sin ciudades, pc ==")
    print(main[main.scale == "pc"].pivot_table(index="window", columns=["spec", "clock"], values="beta_x_within_sd").reindex(WKEYS).round(4).to_string())
    print(tests[(tests["sample"] == "nobig") & (tests.note == "")].round(4).to_string())
    print(two.round(3).to_string())
    print(rv[rv["sample"] == "nobig"].round(3).to_string())
    summ = {"flow": flow, "n_big": int(T.big.sum()), "winsor_caps_p99": caps, "demean_max_chk": float(coef.demean_chk.max()),
            "ruv_monthly_rule": "expulsados RUV por municipio × año repartidos uniformemente entre los 12 meses del año (1/12 por mes)"}
    with open(f"{OUT_D}/t6_pc_resumen.json", "w") as fh: json.dump(summ, fh, indent=1, ensure_ascii=False)
    log("Fin")

if __name__ == "__main__":
    main()
