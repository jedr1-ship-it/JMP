#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
T2b — Primer pase del perfil dosis-por-edad (Saber 11 x CNMH paramilitar).

Ejecutar:  python3 -I /home/user/JMP/code/analysis/t2b_dose_profile_saber11.py [--build-only] [--rebuild] [--figure-only]

Construye, para cada evaluado de las cohortes 1985-2005 con mes de nacimiento,
municipio de residencia y score_z, la dosis paramilitar (PARA del panel CNMH
municipio x mes, masacres + asesinatos selectivos) en ventanas de edad relativas al
mes de nacimiento, y estima
    score_z = sum_a beta_a * dosis_a + sexo + EF municipio + EF cohorte x departamento,
errores agrupados por municipio. Los EF se absorben por demeaning alternado
(proyecciones alternantes) y se verifica contra una regresion con dummies.

Salidas:
  data/derived/t2b_dose_individual_sample.parquet
  data/derived/t2b_coeficientes.csv, t2b_tests.csv, t2b_descriptivos.csv,
  data/derived/t2b_within_corr.csv, t2b_fe_check.csv, t2b_resumen.json
  scoping/proposal/fig5_perfil_dosis_edad_saber11.pdf
"""
import os, sys, time, json, warnings
import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from scipy import stats as sps

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

warnings.filterwarnings("ignore", category=FutureWarning)
T0 = time.time()
def log(msg):
    print(f"[{time.time()-T0:7.1f}s] {msg}", flush=True)

ROOT = "/home/user/JMP"
F_SABER = f"{ROOT}/data/derived/saber11_slim.parquet"
F_CNMH = f"{ROOT}/data/derived/cnmh_muni_month_victims.csv"
F_T = f"{ROOT}/data/derived/t2_A_T1_muestra_T.csv"
OUT_D = f"{ROOT}/data/derived"
OUT_P = f"{ROOT}/scoping/proposal"
F_IND = f"{OUT_D}/t2b_dose_individual_sample.parquet"
F_FIG = f"{OUT_P}/fig5_perfil_dosis_edad_saber11.pdf"
os.makedirs(OUT_D, exist_ok=True); os.makedirs(OUT_P, exist_ok=True)

BUILD_ONLY = "--build-only" in sys.argv
FIGURE_ONLY = "--figure-only" in sys.argv
REBUILD = "--rebuild" in sys.argv

COH_LO, COH_HI = 1985, 2005
# ventanas en meses relativos al mes de nacimiento (ambos extremos inclusive)
WINDOWS = [
    ("preconc", -45, -10, "Pre-conc.\n−45 a −10"),
    ("inutero", -9, -1, "In utero\n−9 a −1"),
    ("a0_2", 0, 35, "0-2 años\n0 a 35"),
    ("a3_5", 36, 71, "3-5 años\n36 a 71"),
    ("a6_11", 72, 143, "6-11 años\n72 a 143"),
    ("a12_17", 144, 215, "12-17 años\n144 a examen"),
]
WKEYS = [w[0] for w in WINDOWS]
WLAB = {w[0]: w[3] for w in WINDOWS}
CORE4 = ["inutero", "a0_2", "a3_5", "a6_11"]
SCALES = {"log": "log(1+víctimas)", "p100": "víctimas por 100 evaluados de la celda municipio×cohorte",
          "p100f": "víctimas por 100 evaluados (denominador fijo: media municipal de la celda, cohortes 1990-2003)",
          "p100w": "víctimas por 100 evaluados de la celda, winsorizada en el p99 de cada ventana"}
COL = {"blue": "#2a78d6", "orange": "#eb6834", "green": "#1baf7a", "yellow": "#eda100", "gray": "#8a8984"}

# ----------------------------------------------------------------------------
# 1. Construccion de la muestra individual con dosis
# ----------------------------------------------------------------------------
def build_sample():
    log("Leyendo Saber 11 (columnas seleccionadas, cohortes 1985-2005)")
    cols = ["periodo", "year", "sem", "consecutivo", "birth_year", "birth_month", "muni_res", "dpto_res",
            "sexo", "score_z", "math_z", "lang_z", "flag_truncated_file"]
    tab = pq.read_table(F_SABER, columns=cols,
                        filters=[("birth_year", ">=", COH_LO), ("birth_year", "<=", COH_HI)])
    df = tab.to_pandas(); del tab
    n0 = len(df)
    log(f"  filas cohortes {COH_LO}-{COH_HI}: {n0:,}")
    flow = {"cohortes_1985_2005": n0}
    df = df[df.birth_month.notna()]; flow["con_mes_nacimiento"] = len(df)
    df = df[df.muni_res.notna()]; flow["con_muni_res"] = len(df)
    df = df[df.score_z.notna()]; flow["con_score_z"] = len(df)
    df = df[df.sexo.isin(["F", "M"])]; flow["con_sexo"] = len(df)
    df = df.reset_index(drop=True)
    log(f"  muestra analitica: {len(df):,}  flujo={flow}")

    # tipos compactos
    df["birth_year"] = df.birth_year.astype(np.int16)
    df["birth_month"] = df.birth_month.astype(np.int8)
    df["year"] = df.year.astype(np.int16); df["sem"] = df["sem"].astype(np.int8)
    df["female"] = (df.sexo == "F").astype(np.int8)
    dp = df.dpto_res.astype(object)
    miss_dp = dp.isna()
    dp[miss_dp] = df.muni_res[miss_dp].str[:2]
    df["dpto_res"] = dp.astype(str)
    df["birth_ym"] = (df.birth_year.astype(np.int32) * 12 + df.birth_month.astype(np.int32) - 1).astype(np.int32)
    # mes aproximado del examen: 15-mar (sem 1) / 15-ago (sem 2), como en el codebook
    df["exam_ym"] = (df.year.astype(np.int32) * 12 + np.where(df["sem"].values == 1, 2, 7)).astype(np.int32)
    for c in ["score_z", "math_z", "lang_z"]:
        df[c] = df[c].astype(np.float32)

    # ---- panel CNMH: acumulado mensual por municipio ----
    log("Panel CNMH: acumulado mensual PARA por municipio")
    p = pd.read_csv(F_CNMH, dtype={"muni": str}, usecols=["muni", "ym", "PARA"])
    YM0 = int(p.ym.min()); YM1 = int(p.ym.max()); TN = YM1 - YM0 + 1
    munis_p = np.sort(p.muni.unique())
    midx = {m: i for i, m in enumerate(munis_p)}
    NP = len(munis_p)
    A = np.zeros((NP + 1, TN), dtype=np.float64)       # fila NP = municipio sin victimas registradas
    np.add.at(A, (p.muni.map(midx).values, (p.ym - YM0).values), p.PARA.values.astype(np.float64))
    Cp = np.zeros((NP + 1, TN + 1), dtype=np.float64)
    Cp[:, 1:] = np.cumsum(A, axis=1)                  # Cp[m,k] = suma de meses [0, k-1]
    log(f"  panel {YM0//12}-{YM0%12+1:02d} a {YM1//12}-{YM1%12+1:02d} ({TN} meses), {NP} municipios, PARA total {int(A.sum()):,}")

    m_idx = df.muni_res.map(midx).fillna(NP).astype(np.int32).values
    df["muni_in_panel"] = (m_idx < NP).astype(np.int8)
    b_idx = (df.birth_ym.values - YM0).astype(np.int64)
    e_idx = (df.exam_ym.values - YM0).astype(np.int64)

    def window_sum(lo, hi):
        start = b_idx + lo
        end = np.minimum(b_idx + hi, e_idx)            # truncada en el mes del examen
        s = np.clip(start, 0, TN); e1 = np.clip(end + 1, 0, TN)
        d = Cp[m_idx, e1] - Cp[m_idx, s]
        obs = np.clip(np.minimum(end, TN - 1) - np.maximum(start, 0) + 1, 0, None)   # meses observados en el panel
        return np.maximum(d, 0), obs

    for key, lo, hi, _ in WINDOWS:
        d, obs = window_sum(lo, hi)
        df[f"v_{key}"] = d.astype(np.int32)
        df[f"mobs_{key}"] = obs.astype(np.int16)
    log("  dosis por ventana calculadas (vectorizado)")

    # ---- denominadores: evaluados por celda municipio x cohorte ----
    cell = df.groupby(["muni_res", "birth_year"], observed=True).size().rename("n_cell").reset_index()
    fixed = (cell[(cell.birth_year >= 1990) & (cell.birth_year <= 2003)]
             .groupby("muni_res").n_cell.mean().rename("n_muni_fixed"))
    fixed_all = cell.groupby("muni_res").n_cell.mean().rename("n_muni_fixed_all")
    df = df.merge(cell, on=["muni_res", "birth_year"], how="left")
    df = df.merge(fixed, on="muni_res", how="left").merge(fixed_all, on="muni_res", how="left")
    df["n_muni_fixed"] = df.n_muni_fixed.fillna(df.n_muni_fixed_all).astype(np.float32)
    df = df.drop(columns=["n_muni_fixed_all"])
    df["n_cell"] = df.n_cell.astype(np.int32)
    for key in WKEYS:
        v = df[f"v_{key}"].values.astype(np.float64)
        df[f"log_{key}"] = np.log1p(v).astype(np.float32)
        df[f"p100_{key}"] = (100.0 * v / df.n_cell.values).astype(np.float32)
        df[f"p100f_{key}"] = (100.0 * v / df.n_muni_fixed.values).astype(np.float32)
    # variante winsorizada de (ii): tope en el percentil 99 de cada ventana (muestra completa)
    caps = {}
    for key in WKEYS:
        cap = float(np.quantile(df[f"p100_{key}"].values, 0.99)); caps[key] = cap
        df[f"p100w_{key}"] = np.minimum(df[f"p100_{key}"].values, cap).astype(np.float32)

    # ---- muestra T y mes de salida ----
    T = pd.read_csv(F_T, dtype={"muni": str})
    T = T[T.muni != "00000"]
    rel = T[(T.exit_month_assigned) & (~T.exit_month_censored) & (~T.exit_month_unreliable)]
    df["in_T"] = df.muni_res.isin(set(T.muni)).astype(np.int8)
    ex = df.muni_res.map(rel.set_index("muni").exit_ym)
    df["exit_ym"] = ex.astype("float32")
    df["in_T431"] = ex.notna().astype(np.int8)
    df["born_after_exit"] = ((df.birth_ym >= ex + 12) & ex.notna()).astype(np.int8)
    df["months_birth_minus_exit"] = (df.birth_ym - ex).astype("float32")
    top5 = set(T.sort_values("para_9706", ascending=False).muni.head(5))
    df["top5_dose_muni"] = df.muni_res.isin(top5).astype(np.int8)
    log(f"  en T: {int(df.in_T.sum()):,} ({df.in_T.mean():.1%}); en T431: {int(df.in_T431.sum()):,}; "
        f"nacidos >=12 m tras la salida: {int(df.born_after_exit.sum()):,}; top5={sorted(top5)}")

    meta = {"flow": flow, "panel": {"ym0": YM0, "ym1": YM1, "n_muni_panel": NP, "para_total": int(A.sum())},
            "n_T_munis": int(T.muni.nunique()), "n_T431_munis": int(rel.muni.nunique()), "top5_dose_munis": sorted(top5),
            "n_muni_res_not_in_panel": int((df.muni_in_panel == 0).sum()),
            "n_muni_res_codes_not_in_panel": int(df.loc[df.muni_in_panel == 0, "muni_res"].nunique()),
            "n_dpto_res_imputado": int(miss_dp.sum()), "p100_winsor_caps_p99": caps}
    df = df.drop(columns=["sexo"])
    log("Guardando parquet individual")
    pq.write_table(pa.Table.from_pandas(df, preserve_index=False), F_IND, compression="zstd")
    with open(f"{OUT_D}/t2b_build_meta.json", "w") as fh:
        json.dump(meta, fh, indent=1, ensure_ascii=False)
    return df, meta

# ----------------------------------------------------------------------------
# 2. Econometria: demeaning alternado de dos vias + OLS con errores agrupados
# ----------------------------------------------------------------------------
def two_way_demean(M, g1, g2, tol=1e-9, maxit=1000):
    """Proyecciones alternantes sobre dos conjuntos de EF. M: (N,K) float64, g1/g2 codigos 0..n-1."""
    n1, n2 = g1.max() + 1, g2.max() + 1
    c1 = np.bincount(g1, minlength=n1).astype(np.float64)
    c2 = np.bincount(g2, minlength=n2).astype(np.float64)
    M = np.array(M, dtype=np.float64, order="F", copy=True)
    K = M.shape[1]
    scale = np.maximum(M.std(axis=0), 1e-12)
    for it in range(1, maxit + 1):
        dmax = 0.0
        for g, c, n in ((g1, c1, n1), (g2, c2, n2)):
            for k in range(K):
                mu = np.bincount(g, weights=M[:, k], minlength=n) / c
                M[:, k] -= mu[g]
                dmax = max(dmax, np.abs(mu).max() / scale[k])
        if dmax < tol:
            break
    # verificacion: medias por grupo tras converger
    chk = 0.0
    for g, c, n in ((g1, c1, n1), (g2, c2, n2)):
        for k in range(K):
            mu = np.bincount(g, weights=M[:, k], minlength=n) / c
            chk = max(chk, np.abs(mu).max() / scale[k])
    return M, it, chk, int(n1), int(n2)

def ols_cluster(y, X, cl):
    """OLS sin constante (datos demeaned) con varianza agrupada (CR1)."""
    N, K = X.shape
    G = cl.max() + 1
    XtX = X.T @ X
    XtX_inv = np.linalg.inv(XtX)
    beta = XtX_inv @ (X.T @ y)
    e = y - X @ beta
    Sg = np.column_stack([np.bincount(cl, weights=X[:, k] * e, minlength=G) for k in range(K)])
    meat = Sg.T @ Sg
    adj = (G / (G - 1.0)) * ((N - 1.0) / (N - K))
    V = adj * XtX_inv @ meat @ XtX_inv
    r2w = 1.0 - (e @ e) / (y @ y)
    return beta, V, r2w

def wald_eq(beta, V, i, j):
    d = beta[i] - beta[j]
    v = V[i, i] + V[j, j] - 2 * V[i, j]
    stat = d * d / v
    return d, np.sqrt(v), stat, sps.chi2.sf(stat, 1)

def run_block(D, mask, sample, outcomes, scales, specs, extra=None, note=""):
    """Demean una vez todas las columnas necesarias y estima cada (outcome, escala, spec)."""
    extra = extra or []
    idx = np.flatnonzero(mask)
    g1 = np.unique(D["muni_code"].values[idx], return_inverse=True)[1].astype(np.int64)
    g2 = np.unique(D["cohdep_code"].values[idx], return_inverse=True)[1].astype(np.int64)
    colnames = list(outcomes) + ["female"] + [f"{s}_{w}" for s in scales for w in WKEYS] + extra
    M = np.column_stack([D[c].values[idx].astype(np.float64) for c in colnames])
    ci = {c: k for k, c in enumerate(colnames)}
    t1 = time.time()
    Md, it, chk, n1, n2 = two_way_demean(M, g1, g2)
    del M
    N = len(idx)
    log(f"  [{sample}] N={N:,} muni={n1} cohorte×dpto={n2} demeaning: {it} iter, max|media grupo|/sd={chk:.1e}, {time.time()-t1:.0f}s")
    fe_rows = [{"sample": sample, "note": note, "N": N, "n_muni_fe": n1, "n_cohdep_fe": n2, "iter": it, "max_abs_group_mean_rel": chk}]
    within_sd = Md.std(axis=0)
    coef_rows, test_rows = [], []
    for y in outcomes:
        for s in scales:
            for spec_name, wins, use_extra in specs:
                xcols = [f"{s}_{w}" for w in wins] + ["female"] + (extra if use_extra else [])
                X = Md[:, [ci[c] for c in xcols]]
                beta, V, r2w = ols_cluster(Md[:, ci[y]], X, g1)
                se = np.sqrt(np.diag(V))
                for k, c in enumerate(xcols):
                    term = c[len(s) + 1:] if c.startswith(s + "_") else c
                    coef_rows.append({"sample": sample, "outcome": y, "scale": s, "spec": spec_name, "term": term,
                                      "beta": beta[k], "se": se[k], "ci_lo": beta[k] - 1.96 * se[k], "ci_hi": beta[k] + 1.96 * se[k],
                                      "t": beta[k] / se[k], "p": 2 * sps.norm.sf(abs(beta[k] / se[k])),
                                      "within_sd_x": within_sd[ci[c]], "beta_x_within_sd": beta[k] * within_sd[ci[c]],
                                      "N": N, "n_clusters": n1, "n_cohdep_fe": n2, "r2_within": r2w, "note": note})
                if "a0_2" in wins and "a3_5" in wins:
                    i, j = xcols.index(f"{s}_a0_2"), xcols.index(f"{s}_a3_5")
                    d, sd, stat, pv = wald_eq(beta, V, i, j)
                    test_rows.append({"sample": sample, "outcome": y, "scale": s, "spec": spec_name, "test": "b(0-2) = b(3-5)",
                                      "diff": d, "se_diff": sd, "chi2": stat, "p": pv, "N": N, "note": note})
                if "preconc" in wins:
                    k = xcols.index(f"{s}_preconc")
                    test_rows.append({"sample": sample, "outcome": y, "scale": s, "spec": spec_name, "test": "placebo b(pre-concepción) = 0",
                                      "diff": beta[k], "se_diff": se[k], "chi2": (beta[k] / se[k]) ** 2,
                                      "p": 2 * sps.norm.sf(abs(beta[k] / se[k])), "N": N, "note": note})
    # correlaciones within de las dosis (escala log) para el bloque principal
    corr = None
    if "log" in scales:
        cols_log = [ci[f"log_{w}"] for w in WKEYS]
        corr = pd.DataFrame(np.corrcoef(Md[:, cols_log].T), index=WKEYS, columns=WKEYS)
        corr.insert(0, "sample", sample)
    return coef_rows, test_rows, fe_rows, corr

def fe_check_with_dummies(D):
    """Verifica el demeaning contra OLS con dummies (statsmodels) en una submuestra de 3 departamentos."""
    import statsmodels.api as sm
    rng = np.random.default_rng(20261024)
    sel = np.flatnonzero(D.dpto_res.isin(["05", "20", "54"]).values)
    sel = np.sort(rng.choice(sel, size=min(80000, len(sel)), replace=False))
    sub = D.iloc[sel]
    g1 = np.unique(sub.muni_code.values, return_inverse=True)[1]
    g2 = np.unique(sub.cohdep_code.values, return_inverse=True)[1]
    xcols = [f"log_{w}" for w in WKEYS] + ["female"]
    M = np.column_stack([sub[c].values.astype(np.float64) for c in ["score_z"] + xcols])
    Md, it, chk, n1, n2 = two_way_demean(M, g1, g2)
    b_dm, V_dm, _ = ols_cluster(Md[:, 0], Md[:, 1:], g1)
    # dummies explicitas
    # dummies de municipio (todas: absorben la constante) + cohorte×dpto sin una cohorte por departamento (rango completo)
    D1 = pd.get_dummies(pd.Series(g1), drop_first=False).values.astype(np.float64)
    cd = pd.DataFrame({"g2": g2, "dp": sub.dpto_res.values})
    drop = set(cd.groupby("dp").g2.min().values)
    keep = [c for c in range(g2.max() + 1) if c not in drop]
    D2 = pd.get_dummies(pd.Series(g2)).reindex(columns=keep).values.astype(np.float64)
    Xd = np.column_stack([M[:, 1:], D1, D2])
    assert np.linalg.matrix_rank(Xd.T @ Xd) == Xd.shape[1], "diseño con dummies no es de rango completo"
    res = sm.OLS(M[:, 0], Xd).fit()
    b_dum = res.params[:len(xcols)]
    res_cl = sm.OLS(M[:, 0], Xd).fit(cov_type="cluster", cov_kwds={"groups": g1})
    se_dum = res_cl.bse[:len(xcols)]
    out = pd.DataFrame({"term": xcols, "beta_demean": b_dm, "beta_dummies": b_dum, "abs_diff_beta": np.abs(b_dm - b_dum),
                        "se_demean_CR1": np.sqrt(np.diag(V_dm)), "se_dummies_cluster_sm": se_dum})
    out["N_sub"] = len(sub); out["n_muni"] = n1; out["n_cohdep"] = n2
    return out

# ----------------------------------------------------------------------------
# 3. Figura
# ----------------------------------------------------------------------------
def make_figure(coef, tests, Ns):
    plt.rcParams.update({"font.size": 7, "axes.titlesize": 7.5, "axes.labelsize": 6.8, "xtick.labelsize": 6.3,
                         "ytick.labelsize": 6.3, "legend.fontsize": 6.5, "pdf.fonttype": 42, "axes.spines.top": False,
                         "axes.spines.right": False, "axes.linewidth": 0.6, "xtick.major.width": 0.5, "ytick.major.width": 0.5})
    fig, axes = plt.subplots(2, 2, figsize=(7.2, 5.2), sharex=True, sharey="row")
    xpos = np.arange(len(WKEYS))
    rows = [("log", "Escala (i): log(1 + víctimas PARA)\nβ (DE de score_z) por unidad"),
            ("p100", "Escala (ii): víctimas PARA por 100 evaluados\nβ (DE de score_z) por unidad")]
    colsamp = [("all", "Todos los municipios"), ("T", "Muestra T (452 municipios)")]
    for r, (s, slab) in enumerate(rows):
        for c, (smp, clab) in enumerate(colsamp):
            ax = axes[r, c]
            ax.axhline(0, color=COL["gray"], lw=0.6, zorder=1)
            for spec, color, mk, off, lab, fill in [("main6", COL["blue"], "o", -0.09, "6 ventanas (principal)", True),
                                                   ("core4", COL["orange"], "s", 0.13, "4 ventanas (in utero a 6-11)", False)]:
                d = coef[(coef["sample"] == smp) & (coef.scale == s) & (coef.spec == spec) & (coef.outcome == "score_z")
                         & (coef.term.isin(WKEYS)) & (coef.note == "")].set_index("term")
                xs = np.array([WKEYS.index(t) for t in d.index]) + off
                ax.errorbar(xs, d.beta.values, yerr=1.96 * d.se.values, fmt=mk, ms=3.2, color=color, ecolor=color,
                            elinewidth=0.8, capsize=1.5, lw=0.9, mfc=color if fill else "white", mew=0.9,
                            ls="-" if spec == "main6" else "none", label=lab, zorder=3)
            tt = tests[(tests["sample"] == smp) & (tests.scale == s) & (tests.spec == "main6") & (tests.outcome == "score_z")
                       & (tests.note == "") & (tests.test.str.startswith("b(0-2)"))]
            if len(tt):
                ax.text(0.98, 0.03, f"H0: β(0-2) = β(3-5), p = {tt.p.iloc[0]:.2f}", transform=ax.transAxes, ha="right", va="bottom",
                        fontsize=6, color="#333333")
            if r == 0:
                ax.set_title(f"{clab}, N = {Ns[smp]:,}".replace(",", "."), loc="left")
            if c == 0:
                ax.set_ylabel(slab)
            ax.set_xticks(xpos); ax.set_xticklabels([WLAB[w] for w in WKEYS])
            ax.grid(axis="y", color="#e5e5e5", lw=0.4, zorder=0)
            ax.margins(x=0.06)
    axes[0, 0].legend(loc="upper right", frameon=False, ncol=1)
    fig.suptitle("Perfil dosis-por-edad: β por ventana de edad (IC 95 %, errores agrupados por municipio)\n"
                 "score_z ~ Σ β_a·dosis_a + sexo + EF municipio + EF cohorte×departamento; cohortes 1985-2005; Saber 11 2005-1 a 2022-2",
                 fontsize=7, x=0.01, ha="left", y=0.995)
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    fig.savefig(F_FIG)
    plt.close(fig)
    log(f"Figura guardada: {F_FIG}")

# ----------------------------------------------------------------------------
# 4. Main
# ----------------------------------------------------------------------------
def main():
    if FIGURE_ONLY:
        coef = pd.read_csv(f"{OUT_D}/t2b_coeficientes.csv"); tests = pd.read_csv(f"{OUT_D}/t2b_tests.csv")
        coef["note"] = coef.note.fillna(""); tests["note"] = tests.note.fillna("")
        Ns = coef.groupby("sample").N.max().to_dict()
        make_figure(coef, tests, Ns); return
    if os.path.exists(F_IND) and not REBUILD:
        log(f"Leyendo muestra individual existente: {F_IND}")
        D = pd.read_parquet(F_IND)
        with open(f"{OUT_D}/t2b_build_meta.json") as fh:
            meta = json.load(fh)
    else:
        D, meta = build_sample()
    if BUILD_ONLY:
        log("--build-only: fin"); return

    D["muni_code"] = pd.factorize(D.muni_res)[0].astype(np.int32)
    D["cohdep_code"] = pd.factorize(D.birth_year.astype(str) + "_" + D.dpto_res)[0].astype(np.int32)
    allm = np.ones(len(D), dtype=bool)
    inT = D.in_T.values == 1
    inT431 = D.in_T431.values == 1
    ml = D.math_z.notna().values & D.lang_z.notna().values
    coh89 = D.birth_year.values >= 1989
    notop5 = D.top5_dose_muni.values == 0

    # ---- descriptivos ----
    log("Descriptivos")
    desc = []
    for smp, m in [("all", allm), ("T", inT), ("T431", inT431)]:
        S = D[m]
        base = {"sample": smp, "N": len(S), "n_muni": S.muni_res.nunique(), "n_cohdep": S.cohdep_code.nunique(),
                "share_female": S.female.mean(), "share_born_after_exit": S.born_after_exit.mean(),
                "n_cell_median": S.n_cell.median(), "n_cell_p10": S.n_cell.quantile(.1)}
        for w in WKEYS:
            v = S[f"v_{w}"]
            base.update({f"{w}_share_pos": (v > 0).mean(), f"{w}_mean": v.mean(), f"{w}_p50": v.median(), f"{w}_p90": v.quantile(.9),
                         f"{w}_p99": v.quantile(.99), f"{w}_max": v.max(), f"{w}_mean_log": S[f"log_{w}"].mean(),
                         f"{w}_mean_p100": S[f"p100_{w}"].mean(), f"{w}_p99_p100": S[f"p100_{w}"].quantile(.99),
                         f"{w}_max_p100": S[f"p100_{w}"].max(), f"{w}_share_window_fully_observed": (S[f"mobs_{w}"] == (dict((k, hi - lo + 1) for k, lo, hi, _ in WINDOWS)[w])).mean()})
        desc.append(base)
    desc = pd.DataFrame(desc)
    desc.to_csv(f"{OUT_D}/t2b_descriptivos.csv", index=False)
    Ns = {"all": int(allm.sum()), "T": int(inT.sum()), "T431": int(inT431.sum())}

    # ---- verificacion EF con dummies ----
    log("Verificacion del demeaning contra dummies (submuestra)")
    fechk = fe_check_with_dummies(D)
    fechk.to_csv(f"{OUT_D}/t2b_fe_check_dummies.csv", index=False)
    log(f"  max |beta_demean - beta_dummies| = {fechk.abs_diff_beta.max():.2e}")

    # ---- regresiones ----
    SPECS_MAIN = [("main6", WKEYS, False), ("core4", CORE4, False)]
    SPECS_EXIT = SPECS_MAIN + [("main6_exit", WKEYS, True), ("core4_exit", CORE4, True)]
    coef, tests, fe, corrs = [], [], [], []
    def add(res):
        c, t, f, cr = res
        coef.extend(c); tests.extend(t); fe.extend(f)
        if cr is not None: corrs.append(cr)

    log("Bloque (a) todos los municipios, score_z")
    add(run_block(D, allm, "all", ["score_z"], ["log", "p100", "p100f", "p100w"], SPECS_MAIN))
    log("Bloque (e) todos, math_z y lang_z")
    add(run_block(D, allm & ml, "all", ["math_z", "lang_z"], ["log", "p100"], SPECS_MAIN))
    log("Bloque (b) muestra T, score_z")
    add(run_block(D, inT, "T", ["score_z"], ["log", "p100", "p100f", "p100w"], SPECS_MAIN))
    log("Bloque (e) T, math_z y lang_z")
    add(run_block(D, inT & ml, "T", ["math_z", "lang_z"], ["log", "p100"], SPECS_MAIN))
    log("Bloque (f) T431 con 'nacido tras la salida'")
    add(run_block(D, inT431, "T431", ["score_z"], ["log", "p100"], SPECS_EXIT, extra=["born_after_exit"]))
    add(run_block(D, inT431 & ml, "T431", ["math_z", "lang_z"], ["log"], [("main6_exit", WKEYS, True)], extra=["born_after_exit"]))
    log("Robustez: cohortes 1989-2005 (ventana pre-concepcion observada por completo)")
    add(run_block(D, allm & coh89, "all", ["score_z"], ["log", "p100"], [("main6", WKEYS, False)], note="cohortes 1989-2005"))
    add(run_block(D, inT & coh89, "T", ["score_z"], ["log", "p100"], [("main6", WKEYS, False)], note="cohortes 1989-2005"))
    log("Robustez: sin los 5 municipios de mayor dosis")
    add(run_block(D, allm & notop5, "all", ["score_z"], ["log", "p100"], [("main6", WKEYS, False)], note="sin top-5 dosis"))
    add(run_block(D, inT & notop5, "T", ["score_z"], ["log", "p100"], [("main6", WKEYS, False)], note="sin top-5 dosis"))

    coef = pd.DataFrame(coef); tests = pd.DataFrame(tests); fe = pd.DataFrame(fe)
    coef.to_csv(f"{OUT_D}/t2b_coeficientes.csv", index=False)
    tests.to_csv(f"{OUT_D}/t2b_tests.csv", index=False)
    fe.to_csv(f"{OUT_D}/t2b_fe_check.csv", index=False)
    pd.concat(corrs).to_csv(f"{OUT_D}/t2b_within_corr.csv")

    # tabla compacta para el memo: principal (6 ventanas), score_z, por muestra x escala
    main = coef[(coef.spec == "main6") & (coef.outcome == "score_z") & (coef.note == "") & (coef["sample"].isin(["all", "T"]))]
    piv = main.pivot_table(index="term", columns=["sample", "scale"], values=["beta", "se"]).reindex(WKEYS + ["female"])
    piv.to_csv(f"{OUT_D}/t2b_tabla_principal.csv")

    make_figure(coef, tests, Ns)
    summary = {"meta": meta, "N": Ns, "fe_check_max_abs_diff": float(fechk.abs_diff_beta.max()),
               "fe_demean_max_group_mean": float(fe.max_abs_group_mean_rel.max())}
    with open(f"{OUT_D}/t2b_resumen.json", "w") as fh:
        json.dump(summary, fh, indent=1, ensure_ascii=False, default=float)
    log("Fin")

if __name__ == "__main__":
    main()
