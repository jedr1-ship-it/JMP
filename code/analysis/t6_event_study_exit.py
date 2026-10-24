#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
T6 (prueba 1) — Event study de cohortes relativas a la salida (y a la entrada) paramilitar municipal.

Ejecutar:  python3 -I /home/user/JMP/code/analysis/t6_event_study_exit.py

Unidad: evaluado (score_z y composición) y celda municipio T × cohorte de nacimiento (log N). Cohortes 1988-2003,
calendario A (sem = 2), sin 2017-2 (archivo truncado). Tiempo relativo k = cohorte − año de salida del municipio.
Reglas de salida: (i) anual con umbral absoluto (último año 1996-2006 con ≥ 3 víctimas PARA; `exit_year` de T1),
(ii) mensual con umbral absoluto (último mes ≤ dic-2006 cuyo acumulado de 12 meses es ≥ 3), (iii) mensual con regla
relativa del 5 % (`exit_ym` de T1, desaconsejada por 02). Ventana k ∈ [−12, +4] con extremos agrupados, referencia k = −1.
EF municipio y cohorte × departamento (y versión con EF periodo × edad al examen); errores agrupados por municipio (CR1).
Muestra T (451 municipios) sin municipios con población 2005 ≥ 500.000 (7 ciudades) y con ellos.
Event study de entrada: k_e = cohorte − año de entrada, municipios con entrada limpia (≥ 24 meses sin PARA antes de la entrada).

Salidas: data/derived/t6_es_coefs.csv, t6_es_counts_k.csv, t6_es_rules_muni.csv, t6_es_cells.csv, t6_es_fe_check.csv,
         t6_es_resumen.json; scoping/proposal/fig8_event_study_salida.pdf
"""
import os, sys, json, time, warnings
import numpy as np
import pandas as pd
import pyarrow.parquet as pq
from scipy import stats as sps
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

warnings.filterwarnings("ignore")
T0 = time.time()
def log(msg): print(f"[{time.time()-T0:7.1f}s] {msg}", flush=True)

ROOT = "/home/user/JMP"
F_SABER = f"{ROOT}/data/derived/saber11_slim.parquet"
F_CNMH = f"{ROOT}/data/derived/cnmh_muni_month_victims.csv"
F_T = f"{ROOT}/data/derived/t2_A_T1_muestra_T.csv"
F_POP = f"{ROOT}/data/derived/t5_poblacion_2005.csv"
OUT_D = f"{ROOT}/data/derived"; OUT_P = f"{ROOT}/scoping/proposal"
F_FIG = f"{OUT_P}/fig8_event_study_salida.pdf"

COH_LO, COH_HI = 1988, 2003
K_LO, K_HI, K_REF = -12, 4, -1          # salida (años)
KE_LO, KE_HI, KE_REF = -8, 6, -1        # entrada (años)
KS_LO, KS_HI, KS_REF = -24, 8, -1       # salida (semestres de nacimiento)
KP_LO, KP_HI, KP_REF = -10, 4, -1       # pico (años)
BIG_POP = 500_000
NON_MUNI = {"00000", "47000"}
COLOR, GRAY = "#1f4e79", "#8a8984"

# ----------------------------------------------------------------------------------------------------------
# Econometría: proyecciones alternantes (k vías, con pesos opcionales) y OLS con errores agrupados CR1
# ----------------------------------------------------------------------------------------------------------
def demean(M, groups, w=None, tol=1e-9, maxit=600):
    """Absorbe los EF de `groups` (lista de vectores de códigos 0..n-1) por proyecciones alternantes.
    M: (N,K). w: pesos (None = 1). Devuelve M demeaned, iteraciones y máx |media de grupo| / sd."""
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

def ols_cluster(y, X, cl, w=None):
    """OLS (sin constante; datos demeaned), opcionalmente ponderado, con varianza agrupada CR1."""
    N, K = X.shape
    G = int(cl.max()) + 1
    if w is None:
        Xw, yw = X, y
    else:
        sw = np.sqrt(w); Xw = X * sw[:, None]; yw = y * sw
    XtX_inv = np.linalg.inv(Xw.T @ Xw)
    beta = XtX_inv @ (Xw.T @ yw)
    e = yw - Xw @ beta
    Sg = np.column_stack([np.bincount(cl, weights=Xw[:, k] * e, minlength=G) for k in range(K)])
    V = (G / (G - 1.0)) * ((N - 1.0) / (N - K)) * XtX_inv @ (Sg.T @ Sg) @ XtX_inv
    return beta, V, 1.0 - (e @ e) / (yw @ yw)

def codes(a):
    return np.unique(np.asarray(a), return_inverse=True)[1].astype(np.int64)

def event_dummies(k, lo, hi, ref):
    """k ya acotado a [lo, hi]. Devuelve matriz de dummies (una por valor != ref) y lista de valores."""
    vals = [v for v in range(lo, hi + 1) if v != ref]
    return np.column_stack([(k == v).astype(np.float64) for v in vals]), vals

def run_es(D, mask, kcol, lo, hi, ref, outcomes, fe_cols, w=None, cluster="muni_code", label="", note="", extra_rows=None):
    """Event study: outcomes ~ dummies(k) + female (si está) + EF(fe_cols). Devuelve filas de coeficientes."""
    idx = np.flatnonzero(mask)
    k = np.clip(D[kcol].values[idx].astype(int), lo, hi)
    Xd, vals = event_dummies(k, lo, hi, ref)
    xnames = [f"k{v:+d}" for v in vals]
    if "female" in D.columns and "female" not in outcomes:
        Xd = np.column_stack([Xd, D["female"].values[idx].astype(np.float64)]); xnames.append("female")
    Y = np.column_stack([D[o].values[idx].astype(np.float64) for o in outcomes])
    groups = [codes(D[c].values[idx]) for c in fe_cols]
    cl = codes(D[cluster].values[idx])
    ww = None if w is None else D[w].values[idx].astype(np.float64)
    M, it, chk = demean(np.column_stack([Y, Xd]), groups, w=ww)
    nY = len(outcomes)
    Xm = M[:, nY:]
    rows = []
    for j, o in enumerate(outcomes):
        beta, V, r2 = ols_cluster(M[:, j], Xm, cl, w=ww)
        se = np.sqrt(np.diag(V))
        for i, nm in enumerate(xnames):
            rows.append({"label": label, "note": note, "outcome": o, "term": nm,
                         "k": int(nm[1:]) if nm.startswith("k") else np.nan,
                         "beta": beta[i], "se": se[i], "ci_lo": beta[i] - 1.96 * se[i], "ci_hi": beta[i] + 1.96 * se[i],
                         "p": 2 * sps.norm.sf(abs(beta[i] / se[i])), "N": len(idx), "n_clusters": int(cl.max()) + 1,
                         "fe": "+".join(fe_cols), "weighted": w is not None, "r2_within": r2, "demean_iter": it, "demean_chk": chk})
        rows.append({"label": label, "note": note, "outcome": o, "term": f"k{ref:+d}", "k": ref, "beta": 0.0, "se": 0.0,
                     "ci_lo": 0.0, "ci_hi": 0.0, "p": np.nan, "N": len(idx), "n_clusters": int(cl.max()) + 1,
                     "fe": "+".join(fe_cols), "weighted": w is not None, "r2_within": r2, "demean_iter": it, "demean_chk": chk})
    log(f"  [{label}{(' | ' + note) if note else ''}] N={len(idx):,} clusters={int(cl.max())+1} FE={fe_cols} iter={it} chk={chk:.1e}")
    return rows

def joint_pre_test(rows, label, outcome, kmax=-8):
    """Wald conjunto de los coeficientes k <= kmax (pretendencias) no está en las filas: se calcula aparte."""
    pass

# ----------------------------------------------------------------------------------------------------------
# 1. Reglas de salida/entrada por municipio
# ----------------------------------------------------------------------------------------------------------
def build_rules():
    T = pd.read_csv(F_T, dtype={"muni": str})
    T = T[~T.muni.isin(NON_MUNI)].copy()
    assert len(T) == 451, len(T)
    pop = pd.read_csv(F_POP, dtype={"muni": str})[["muni", "municipio_cede", "pop2005"]]
    T = T.merge(pop, on="muni", how="left")
    assert T.pop2005.notna().all()
    T["big"] = T.pop2005 >= BIG_POP
    # panel mensual PARA para los municipios T
    p = pd.read_csv(F_CNMH, dtype={"muni": str}, usecols=["muni", "ym", "PARA"])
    YM0, YM1 = int(p.ym.min()), int(p.ym.max()); TN = YM1 - YM0 + 1
    munis = T.muni.tolist(); mi = {m: i for i, m in enumerate(munis)}
    pT = p[p.muni.isin(mi)]
    P = np.zeros((len(munis), TN))
    np.add.at(P, (pT.muni.map(mi).values, (pT.ym - YM0).values), pT.PARA.values.astype(float))
    # (ii) salida mensual absoluta: último mes t <= dic-2006 con suma PARA[t-11..t] >= 3
    roll = np.column_stack([P[:, max(0, j - 11):j + 1].sum(axis=1) for j in range(TN)])
    jmax = 2006 * 12 + 11 - YM0
    ok = roll[:, :jmax + 1] >= 3
    last = np.where(ok.any(axis=1), ok.shape[1] - 1 - np.argmax(ok[:, ::-1], axis=1), -1)
    T["exit_abs12_ym"] = np.where(last >= 0, YM0 + last, np.nan)
    T["exit_abs12_year"] = T.exit_abs12_ym // 12
    assert T.exit_abs12_ym.notna().all()
    # (iii) regla del 5 % (T1): exit_ym, sólo municipios con mes asignado
    T["exit_5pct_year"] = np.where(T.exit_month_assigned, T.exit_ym // 12, np.nan)
    # entrada limpia: >= 24 meses consecutivos sin PARA antes de enero del año de entrada (y entrada >= 1997)
    j_entry = (T.entry_year.values * 12 - YM0).astype(int)
    pre24 = np.array([P[i, max(0, j - 24):j].sum() for i, j in enumerate(j_entry)])
    T["para_24m_pre_entry"] = pre24
    T["clean_entry"] = (T.entry_year >= 1997) & (pre24 == 0)
    T["clean_entry_strict"] = T.clean_entry & (T.pre_para_88_95 < 3)
    T["clean_entry_broad"] = (T.entry_year >= 1997) & (T.pre_para_88_95 < 3)      # definición de 01 ("~120 limpios")
    # víctimas PARA en los 12 meses posteriores a cada regla (control de calidad de la regla)
    def after12(ym):
        j = (ym - YM0).astype(int)
        return np.array([P[i, j[i] + 1:j[i] + 13].sum() for i in range(len(j))])
    T["para_12m_after_exit_year"] = after12((T.exit_year.values * 12 + 11))
    T["para_12m_after_abs12"] = after12(T.exit_abs12_ym.values)
    T["para_12m_after_5pct"] = np.where(T.exit_month_assigned, after12(np.where(T.exit_month_assigned, T.exit_ym, YM0).astype(int)), np.nan)
    T["exit_abs12_minus_exit_year"] = T.exit_abs12_year - T.exit_year
    # pico: año de máximo de víctimas PARA en 1997-2006 (empates: el primero)
    j97 = 1997 * 12 - YM0
    ann = np.column_stack([P[:, j97 + 12 * y: j97 + 12 * (y + 1)].sum(axis=1) for y in range(10)])
    T["peak_year"] = 1997 + np.argmax(ann, axis=1)
    T["peak_para"] = ann.max(axis=1)
    T["peak_share_9706"] = ann.max(axis=1) / np.maximum(ann.sum(axis=1), 1)
    keep = ["muni", "muni_name", "depto", "pop2005", "big", "para_9706", "entry_year", "exit_year", "exit_abs12_ym", "exit_abs12_year",
            "exit_abs12_minus_exit_year", "exit_ym", "exit_5pct_year", "exit_month_assigned", "pre_para_88_95", "para_24m_pre_entry",
            "peak_year", "peak_para", "peak_share_9706", "clean_entry", "clean_entry_strict", "clean_entry_broad", "para_12m_after_exit_year", "para_12m_after_abs12", "para_12m_after_5pct"]
    T = T[keep]
    T.to_csv(f"{OUT_D}/t6_es_rules_muni.csv", index=False)
    log(f"Reglas: T={len(T)}; grandes (≥{BIG_POP:,}): {int(T.big.sum())} {sorted(T[T.big].muni_name)}; "
        f"salida abs12 = salida anual: {(T.exit_abs12_minus_exit_year == 0).mean():.1%}; "
        f"entrada limpia (24 m sin PARA, entrada ≥ 1997): {int(T.clean_entry.sum())} (estricta, <3 en 1988-95: {int(T.clean_entry_strict.sum())}; amplia de 01, entrada ≥ 1997 y <3 en 1988-95: {int(T.clean_entry_broad.sum())})")
    log(f"  salida abs12 por año: {T.exit_abs12_year.value_counts().sort_index().to_dict()}")
    log(f"  pico por año: {T.peak_year.value_counts().sort_index().to_dict()}; share del pico en la dosis 97-06, mediana {T.peak_share_9706.median():.2f}")
    log(f"  víctimas PARA en los 12 meses tras la salida, mediana (p90): anual {T.para_12m_after_exit_year.median():.0f} ({T.para_12m_after_exit_year.quantile(.9):.0f}); "
        f"abs12 {T.para_12m_after_abs12.median():.0f} ({T.para_12m_after_abs12.quantile(.9):.0f}); 5 % {T.para_12m_after_5pct.median():.0f} ({T.para_12m_after_5pct.quantile(.9):.0f})")
    return T

# ----------------------------------------------------------------------------------------------------------
# 2. Muestra individual
# ----------------------------------------------------------------------------------------------------------
def build_sample(T):
    cols = ["periodo", "year", "sem", "birth_year", "birth_month", "age_at_exam", "muni_res", "dpto_res", "cole_naturaleza",
            "sexo", "estrato", "educ_madre", "score_z", "flag_truncated_file"]
    df = pq.read_table(F_SABER, columns=cols, filters=[("birth_year", ">=", COH_LO), ("birth_year", "<=", COH_HI)]).to_pandas()
    flow = {"cohortes_1988_2003": len(df)}
    df = df[df.muni_res.isin(set(T.muni))]; flow["en_T_451"] = len(df)
    df = df[df["sem"] == 2]; flow["calendario_A"] = len(df)
    df = df[~df.flag_truncated_file]; flow["sin_2017_2"] = len(df)
    df = df[df.score_z.notna() & df.sexo.isin(["F", "M"]) & df.age_at_exam.notna()]; flow["con_score_sexo_edad"] = len(df)
    df = df.reset_index(drop=True)
    log(f"Muestra individual: {flow}")
    df["female"] = (df.sexo == "F").astype(np.int8)
    df["no_oficial"] = (df.cole_naturaleza == "no oficial").astype(np.float32)
    df.loc[df.cole_naturaleza.isna(), "no_oficial"] = np.nan
    df["rezago"] = (df.age_at_exam > 19).astype(np.float32)
    df["age_int"] = np.floor(df.age_at_exam).astype(np.int16)
    df["per_age"] = df.periodo.astype(str) + "_" + df.age_int.astype(str)
    dp = df.dpto_res.astype(object); m = dp.isna(); dp[m] = df.muni_res[m].str[:2]; df["dpto_res"] = dp.astype(str)
    df["cohdep"] = df.birth_year.astype(str) + "_" + df.dpto_res
    # educación de la madre <= primaria (texto 2009-2+; códigos ICFES 2008-1..2009-1: 9 prim. inc., 10 prim. compl., 0 ninguno; 99 no sabe)
    low = {"Ninguno", "Primaria incompleta", "Primaria completa", "9", "10", "0"}
    miss = {"No sabe", "No Aplica", "99", "7", "4"}
    em = df.educ_madre.astype(object)
    df["educ_le_prim"] = np.where(em.isna() | em.isin(miss), np.nan, em.isin(low).astype(float)).astype(np.float32)
    es = df.estrato.astype("float")
    df["estrato_12"] = np.where(es.isna() | (es == 0), np.nan, (es <= 2).astype(float)).astype(np.float32)
    df["birth_ym"] = (df.birth_year.astype(int) * 12 + df.birth_month.astype(int) - 1).astype(np.int32)
    Ti = T.set_index("muni")
    for c in ["exit_year", "exit_abs12_ym", "exit_5pct_year", "entry_year", "peak_year", "big", "clean_entry", "clean_entry_broad"]:
        df[c] = df.muni_res.map(Ti[c])
    df["k_peak"] = (df.birth_year - df.peak_year).astype(int)
    df["k_exit"] = (df.birth_year - df.exit_year).astype(int)
    df["k_exit5"] = (df.birth_year - df.exit_5pct_year)
    df["k_exit_sem"] = np.floor((df.birth_ym - df.exit_abs12_ym) / 6.0)
    df["k_entry"] = (df.birth_year - df.entry_year).astype(int)
    df["muni_code"] = pd.factorize(df.muni_res)[0]
    df = df.drop(columns=["sexo", "cole_naturaleza", "educ_madre", "estrato", "periodo", "flag_truncated_file"])
    return df, flow

# ----------------------------------------------------------------------------------------------------------
# 3. Celdas municipio × cohorte
# ----------------------------------------------------------------------------------------------------------
def build_cells(df, T):
    g = df.groupby(["muni_res", "birth_year"], observed=True)
    cells = g.agg(N=("score_z", "size"), mean_score=("score_z", "mean"), female=("female", "mean"), no_oficial=("no_oficial", "mean"),
                  rezago=("rezago", "mean"), educ_le_prim=("educ_le_prim", "mean"), estrato_12=("estrato_12", "mean"),
                  n_educ=("educ_le_prim", "count"), n_estrato=("estrato_12", "count")).reset_index()
    # imputación 2017-2 (como T3): 0,5 × [N(c−1, 2016-2) + N(c+1, 2018-2)] para la misma edad al examen
    a = df[df.year == 2016].groupby(["muni_res", "birth_year"]).size().rename("a").reset_index(); a["birth_year"] += 1
    b = df[df.year == 2018].groupby(["muni_res", "birth_year"]).size().rename("b").reset_index(); b["birth_year"] -= 1
    imp = a.merge(b, on=["muni_res", "birth_year"], how="outer").fillna(0)
    imp["N_imp_20172"] = 0.5 * (imp.a + imp.b)
    cells = cells.merge(imp[["muni_res", "birth_year", "N_imp_20172"]], on=["muni_res", "birth_year"], how="left")
    cells["N_imp_20172"] = cells.N_imp_20172.fillna(0.0)
    cells["N_adj"] = cells.N + cells.N_imp_20172
    cells["logN"] = np.log(cells.N); cells["logN_adj"] = np.log(cells.N_adj)
    Ti = T.set_index("muni")
    for c in ["depto", "exit_year", "exit_5pct_year", "entry_year", "peak_year", "big", "clean_entry", "clean_entry_broad", "pop2005"]:
        cells[c] = cells.muni_res.map(Ti[c])
    cells["k_peak"] = cells.birth_year - cells.peak_year
    cells["dpto"] = cells.muni_res.str[:2]
    cells["cohdep"] = cells.birth_year.astype(str) + "_" + cells.dpto
    cells["k_exit"] = cells.birth_year - cells.exit_year
    cells["k_exit5"] = cells.birth_year - cells.exit_5pct_year
    cells["k_entry"] = cells.birth_year - cells.entry_year
    cells["muni_code"] = pd.factorize(cells.muni_res)[0]
    full = T.shape[0] * (COH_HI - COH_LO + 1)
    log(f"Celdas municipio × cohorte con evaluados: {len(cells):,} de {full:,} posibles; N mediana {cells.N.median():.0f}, p10 {cells.N.quantile(.1):.0f}")
    cells.to_csv(f"{OUT_D}/t6_es_cells.csv", index=False)
    return cells

# ----------------------------------------------------------------------------------------------------------
# 4. Figura
# ----------------------------------------------------------------------------------------------------------
def make_figure(coef, counts):
    plt.rcParams.update({"font.family": "serif", "font.size": 8, "axes.titlesize": 8.5, "axes.labelsize": 8, "xtick.labelsize": 7,
                         "ytick.labelsize": 7, "legend.fontsize": 7, "pdf.fonttype": 42, "axes.spines.top": False,
                         "axes.spines.right": False, "axes.linewidth": 0.6, "xtick.major.width": 0.5, "ytick.major.width": 0.5})
    def panel(ax, lab_main, lab_gray, outcome, title, ylabel, lo, hi, ref, gray_label="con ciudades ≥ 500 mil", main_label="sin ciudades ≥ 500 mil"):
        ax.axhline(0, color="#bbbbbb", lw=0.6, zorder=1); ax.axvline(ref + 0.5, color="#bbbbbb", lw=0.6, ls=":", zorder=1)
        for lab, col, off, name, z in [(lab_gray, GRAY, 0.15, gray_label, 2), (lab_main, COLOR, -0.15, main_label, 3)]:
            if lab is None: continue
            d = coef[(coef.label == lab) & (coef.outcome == outcome) & coef.k.notna()].sort_values("k")
            if len(d) == 0: continue
            ax.errorbar(d.k + off, d.beta, yerr=1.96 * d.se, fmt="o", ms=2.6, color=col, ecolor=col, elinewidth=0.7, capsize=0,
                        lw=0.8, ls="-", label=name, zorder=z)
        ax.set_xlim(lo - 0.7, hi + 0.7); ax.set_xticks(range(lo, hi + 1))
        ax.set_xticklabels([("≤" if v == lo else "≥" if v == hi else "") + str(v) for v in range(lo, hi + 1)])
        ax.set_title(title, loc="left"); ax.set_ylabel(ylabel)
    with PdfPages(F_FIG) as pdf:
        for page, (ev, lo, hi, ref, xlab) in enumerate([("exit", K_LO, K_HI, K_REF, "k = cohorte − año de salida (ref. k = −1)"),
                                                      ("entry", KE_LO, KE_HI, KE_REF, "k = cohorte − año de entrada (ref. k = −1)"),
                                                      ("peak", KP_LO, KP_HI, KP_REF, "k = cohorte − año del pico (ref. k = −1)")]):
            fig, axes = plt.subplots(1, 3, figsize=(8, 4.5))
            main = f"{ev}_nobig"; big = f"{ev}_all"
            panel(axes[0], main, big, "score_z", "(a) score_z (individual)", "β (DE de score_z)", lo, hi, ref)
            # EF periodo × edad como línea sin marcadores
            d = coef[(coef.label == f"{ev}_nobig_perage") & (coef.outcome == "score_z") & coef.k.notna()].sort_values("k")
            if len(d): axes[0].plot(d.k - 0.15, d.beta, color=COLOR, lw=0.8, ls="--", label="+ EF periodo × edad", zorder=4)
            panel(axes[1], main, big, "logN", "(b) log N de la celda", "β (log puntos)", lo, hi, ref)
            # composición: sin ciudades, cuatro indicadores, mismo color, marcadores distintos
            ax = axes[2]; ax.axhline(0, color="#bbbbbb", lw=0.6, zorder=1); ax.axvline(ref + 0.5, color="#bbbbbb", lw=0.6, ls=":", zorder=1)
            for o, mk, off, nm, fc in [("educ_le_prim", "o", -0.22, "madre ≤ primaria", COLOR), ("estrato_12", "s", -0.07, "estrato 1-2", "white"),
                                       ("no_oficial", "^", 0.08, "colegio no oficial", COLOR), ("rezago", "D", 0.23, "rezago (> 19 años)", "white")]:
                d = coef[(coef.label == main) & (coef.outcome == o) & coef.k.notna()].sort_values("k")
                if len(d) == 0: continue
                ax.errorbar(d.k + off, d.beta, yerr=1.96 * d.se, fmt=mk, ms=2.6, color=COLOR, mfc=fc, mew=0.7, ecolor=COLOR, elinewidth=0.5,
                            capsize=0, ls="none", label=nm, zorder=3)
            ax.set_xlim(lo - 0.7, hi + 0.7); ax.set_xticks(range(lo, hi + 1))
            ax.set_xticklabels([("≤" if v == lo else "≥" if v == hi else "") + str(v) for v in range(lo, hi + 1)])
            ax.set_title("(c) composición, sin ciudades ≥ 500 mil", loc="left"); ax.set_ylabel("β (puntos de proporción)")
            for a in axes: a.set_xlabel(xlab); a.tick_params(axis="x", labelsize=6)
            axes[0].legend(frameon=False, loc="lower left"); axes[2].legend(frameon=False, loc="lower left", ncol=1)
            ct = counts[(counts.event == ev) & (counts.sample == "nobig")]
            ttl = {"exit": "Salida paramilitar (último año con ≥ 3 víctimas PARA), muestra T",
                   "entry": "Entrada paramilitar (primer año con ≥ 3 víctimas PARA), municipios con entrada limpia",
                   "peak": "Pico paramilitar (año de máximo de víctimas PARA 1997-2006), muestra T"}[ev]
            fig.suptitle(f"{ttl}. Cohortes 1988-2003, calendario A, sin 2017-2; EF municipio y cohorte × dpto.; IC 95 %, cluster municipio. "
                         f"N = {int(ct.N.sum()):,} evaluados, {int(ct.cells.sum()):,} celdas".replace(",", "."), fontsize=7, x=0.01, ha="left", y=0.995)
            fig.tight_layout(rect=(0, 0, 1, 0.95))
            pdf.savefig(fig); plt.close(fig)
    log(f"Figura: {F_FIG}")

# ----------------------------------------------------------------------------------------------------------
# 5. Main
# ----------------------------------------------------------------------------------------------------------
def main():
    T = build_rules()
    df, flow = build_sample(T)
    cells = build_cells(df, T)
    big = df.big.values.astype(bool); cbig = cells.big.values.astype(bool)
    coef, counts = [], []

    # ---- conteos por k ----
    def add_counts(frame, kcol, lo, hi, ev, sample, note=""):
        k = np.clip(frame[kcol].values.astype(float), lo, hi)
        g = pd.DataFrame({"k": k, "N": frame["N"].values if "N" in frame else 1, "muni": frame.muni_res.values}).groupby("k")
        out = g.agg(cells=("N", "size"), N=("N", "sum"), munis=("muni", "nunique")).reset_index()
        out["event"] = ev; out["sample"] = sample; out["note"] = note
        counts.append(out)
    for ev, kcol, lo, hi in [("exit", "k_exit", K_LO, K_HI), ("exit5", "k_exit5", K_LO, K_HI), ("entry", "k_entry", KE_LO, KE_HI),
                             ("peak", "k_peak", KP_LO, KP_HI)]:
        base = cells[cells.k_exit5.notna()] if ev == "exit5" else (cells[cells.clean_entry.astype(bool)] if ev == "entry" else cells)
        add_counts(base[~base.big.astype(bool)], kcol, lo, hi, ev, "nobig")
        add_counts(base, kcol, lo, hi, ev, "all")
    cb = cells[cells.clean_entry_broad.astype(bool)]
    add_counts(cb[~cb.big.astype(bool)], "k_entry", KE_LO, KE_HI, "entry_broad", "nobig"); add_counts(cb, "k_entry", KE_LO, KE_HI, "entry_broad", "all")

    IND = ["score_z", "female", "no_oficial", "rezago"]
    # ---- (A) salida, regla anual absoluta ----
    log("(A) Salida, regla anual absoluta: individual")
    coef += run_es(df, ~big, "k_exit", K_LO, K_HI, K_REF, IND, ["muni_code", "cohdep"], label="exit_nobig")
    coef += run_es(df, ~big & df.educ_le_prim.notna().values, "k_exit", K_LO, K_HI, K_REF, ["educ_le_prim"], ["muni_code", "cohdep"], label="exit_nobig")
    coef += run_es(df, ~big & df.estrato_12.notna().values, "k_exit", K_LO, K_HI, K_REF, ["estrato_12"], ["muni_code", "cohdep"], label="exit_nobig")
    coef += run_es(df, ~big, "k_exit", K_LO, K_HI, K_REF, ["score_z"], ["muni_code", "cohdep", "per_age"], label="exit_nobig_perage")
    coef += run_es(df, np.ones(len(df), bool), "k_exit", K_LO, K_HI, K_REF, IND, ["muni_code", "cohdep"], label="exit_all")
    coef += run_es(df, df.educ_le_prim.notna().values, "k_exit", K_LO, K_HI, K_REF, ["educ_le_prim"], ["muni_code", "cohdep"], label="exit_all")
    coef += run_es(df, df.estrato_12.notna().values, "k_exit", K_LO, K_HI, K_REF, ["estrato_12"], ["muni_code", "cohdep"], label="exit_all")
    coef += run_es(df, np.ones(len(df), bool), "k_exit", K_LO, K_HI, K_REF, ["score_z"], ["muni_code", "cohdep", "per_age"], label="exit_all_perage")
    log("(A) Salida: celdas (log N)")
    coef += run_es(cells, ~cbig, "k_exit", K_LO, K_HI, K_REF, ["logN", "logN_adj"], ["muni_code", "cohdep"], label="exit_nobig")
    coef += run_es(cells, ~cbig & ~cells.birth_year.between(1999, 2001).values, "k_exit", K_LO, K_HI, K_REF, ["logN"], ["muni_code", "cohdep"],
                   label="exit_nobig", note="sin cohortes 1999-2001")
    coef += run_es(cells, ~cbig, "k_exit", K_LO, K_HI, K_REF, ["logN"], ["muni_code", "cohdep"], w="N", label="exit_nobig", note="ponderado por N")
    coef += run_es(cells, np.ones(len(cells), bool), "k_exit", K_LO, K_HI, K_REF, ["logN", "logN_adj"], ["muni_code", "cohdep"], label="exit_all")
    # ---- (B) salida, regla del 5 % (año del mes de salida), municipios con mes asignado ----
    log("(B) Salida, regla del 5 %")
    m5 = df.k_exit5.notna().values; c5 = cells.k_exit5.notna().values
    coef += run_es(df, ~big & m5, "k_exit5", K_LO, K_HI, K_REF, ["score_z"], ["muni_code", "cohdep"], label="exit5_nobig")
    coef += run_es(cells, ~cbig & c5, "k_exit5", K_LO, K_HI, K_REF, ["logN"], ["muni_code", "cohdep"], label="exit5_nobig")
    coef += run_es(df, m5, "k_exit5", K_LO, K_HI, K_REF, ["score_z"], ["muni_code", "cohdep"], label="exit5_all")
    # ---- (C) salida mensual absoluta, semestres de nacimiento ----
    log("(C) Salida mensual absoluta (acumulado 12 m ≥ 3), semestre de nacimiento")
    coef += run_es(df, ~big, "k_exit_sem", KS_LO, KS_HI, KS_REF, ["score_z", "rezago", "no_oficial"], ["muni_code", "cohdep"], label="exitsem_nobig")
    # ---- (D) entrada, municipios con entrada limpia ----
    log("(D) Entrada limpia")
    ce = df.clean_entry.values.astype(bool); cce = cells.clean_entry.values.astype(bool)
    coef += run_es(df, ce & ~big, "k_entry", KE_LO, KE_HI, KE_REF, IND, ["muni_code", "cohdep"], label="entry_nobig")
    coef += run_es(df, ce & ~big & df.educ_le_prim.notna().values, "k_entry", KE_LO, KE_HI, KE_REF, ["educ_le_prim"], ["muni_code", "cohdep"], label="entry_nobig")
    coef += run_es(df, ce & ~big & df.estrato_12.notna().values, "k_entry", KE_LO, KE_HI, KE_REF, ["estrato_12"], ["muni_code", "cohdep"], label="entry_nobig")
    coef += run_es(df, ce & ~big, "k_entry", KE_LO, KE_HI, KE_REF, ["score_z"], ["muni_code", "cohdep", "per_age"], label="entry_nobig_perage")
    coef += run_es(cells, cce & ~cbig, "k_entry", KE_LO, KE_HI, KE_REF, ["logN", "logN_adj"], ["muni_code", "cohdep"], label="entry_nobig")
    coef += run_es(df, ce, "k_entry", KE_LO, KE_HI, KE_REF, ["score_z"], ["muni_code", "cohdep"], label="entry_all")
    coef += run_es(cells, cce, "k_entry", KE_LO, KE_HI, KE_REF, ["logN"], ["muni_code", "cohdep"], label="entry_all")
    # ---- (E) entrada limpia amplia (definición de 01: entrada ≥ 1997 y < 3 PARA en 1988-95) y todos los T con entrada ≥ 1997 ----
    cb_i = df.clean_entry_broad.values.astype(bool); cb_c = cells.clean_entry_broad.values.astype(bool)
    coef += run_es(df, cb_i & ~big, "k_entry", KE_LO, KE_HI, KE_REF, IND, ["muni_code", "cohdep"], label="entry_broad_nobig")
    coef += run_es(df, cb_i & ~big & df.educ_le_prim.notna().values, "k_entry", KE_LO, KE_HI, KE_REF, ["educ_le_prim"], ["muni_code", "cohdep"], label="entry_broad_nobig")
    coef += run_es(df, cb_i & ~big, "k_entry", KE_LO, KE_HI, KE_REF, ["score_z"], ["muni_code", "cohdep", "per_age"], label="entry_broad_nobig_perage")
    coef += run_es(cells, cb_c & ~cbig, "k_entry", KE_LO, KE_HI, KE_REF, ["logN"], ["muni_code", "cohdep"], label="entry_broad_nobig")
    coef += run_es(df, ~big & (df.entry_year.values >= 1997), "k_entry", KE_LO, KE_HI, KE_REF, ["score_z"], ["muni_code", "cohdep"],
                   label="entry_nobig", note="todos los T con entrada ≥ 1997")

    # ---- (F) pico municipal (año de máximo PARA 1997-2006) ----
    log("(F) Pico municipal")
    coef += run_es(df, ~big, "k_peak", KP_LO, KP_HI, KP_REF, IND, ["muni_code", "cohdep"], label="peak_nobig")
    coef += run_es(df, ~big & df.educ_le_prim.notna().values, "k_peak", KP_LO, KP_HI, KP_REF, ["educ_le_prim"], ["muni_code", "cohdep"], label="peak_nobig")
    coef += run_es(df, ~big & df.estrato_12.notna().values, "k_peak", KP_LO, KP_HI, KP_REF, ["estrato_12"], ["muni_code", "cohdep"], label="peak_nobig")
    coef += run_es(df, ~big, "k_peak", KP_LO, KP_HI, KP_REF, ["score_z"], ["muni_code", "cohdep", "per_age"], label="peak_nobig_perage")
    coef += run_es(cells, ~cbig, "k_peak", KP_LO, KP_HI, KP_REF, ["logN", "logN_adj"], ["muni_code", "cohdep"], label="peak_nobig")
    coef += run_es(df, np.ones(len(df), bool), "k_peak", KP_LO, KP_HI, KP_REF, ["score_z"], ["muni_code", "cohdep"], label="peak_all")
    coef += run_es(cells, np.ones(len(cells), bool), "k_peak", KP_LO, KP_HI, KP_REF, ["logN"], ["muni_code", "cohdep"], label="peak_all")

    coef = pd.DataFrame(coef); counts = pd.concat(counts, ignore_index=True)
    coef.to_csv(f"{OUT_D}/t6_es_coefs.csv", index=False)
    counts.to_csv(f"{OUT_D}/t6_es_counts_k.csv", index=False)

    # ---- tests conjuntos: pretendencias (k <= -8) y post (k >= +1), por re-estimación con matriz V ----
    log("Tests conjuntos (Wald, CR1)")
    tests = []
    def wald_block(D, mask, kcol, lo, hi, ref, outcome, fe_cols, label, w=None, blocks=None):
        idx = np.flatnonzero(mask)
        k = np.clip(D[kcol].values[idx].astype(int), lo, hi)
        Xd, vals = event_dummies(k, lo, hi, ref)
        if "female" in D.columns and outcome != "female":
            Xd = np.column_stack([Xd, D["female"].values[idx].astype(np.float64)])
        groups = [codes(D[c].values[idx]) for c in fe_cols]; cl = codes(D["muni_code"].values[idx])
        ww = None if w is None else D[w].values[idx].astype(np.float64)
        M, it, chk = demean(np.column_stack([D[outcome].values[idx].astype(np.float64), Xd]), groups, w=ww)
        beta, V, _ = ols_cluster(M[:, 0], M[:, 1:], cl, w=ww)
        for bname, sel in blocks:
            ii = [i for i, v in enumerate(vals) if sel(v)]
            if not ii: continue
            b = beta[ii]; Vb = V[np.ix_(ii, ii)]
            stat = float(b @ np.linalg.solve(Vb, b)); p = sps.chi2.sf(stat, len(ii))
            tests.append({"label": label, "outcome": outcome, "block": bname, "n_coefs": len(ii), "chi2": stat, "p": p,
                          "mean_beta": float(b.mean()), "N": len(idx), "n_clusters": int(cl.max()) + 1})
    blocks_exit = [("pre: k ≤ −8", lambda v: v <= -8), ("k ∈ [−7, −2]", lambda v: -7 <= v <= -2), ("post: k ≥ 0", lambda v: v >= 0), ("post: k ≥ +1", lambda v: v >= 1)]
    blocks_entry = [("pre: k ≤ −3", lambda v: v <= -3), ("post: k ≥ 0", lambda v: v >= 0)]
    for o in ["score_z", "no_oficial", "rezago", "female"]:
        wald_block(df, ~big, "k_exit", K_LO, K_HI, K_REF, o, ["muni_code", "cohdep"], "exit_nobig", blocks=blocks_exit)
    wald_block(df, ~big & df.educ_le_prim.notna().values, "k_exit", K_LO, K_HI, K_REF, "educ_le_prim", ["muni_code", "cohdep"], "exit_nobig", blocks=blocks_exit)
    wald_block(df, ~big & df.estrato_12.notna().values, "k_exit", K_LO, K_HI, K_REF, "estrato_12", ["muni_code", "cohdep"], "exit_nobig", blocks=blocks_exit)
    wald_block(cells, ~cbig, "k_exit", K_LO, K_HI, K_REF, "logN", ["muni_code", "cohdep"], "exit_nobig", blocks=blocks_exit)
    wald_block(df, np.ones(len(df), bool), "k_exit", K_LO, K_HI, K_REF, "score_z", ["muni_code", "cohdep"], "exit_all", blocks=blocks_exit)
    wald_block(cells, np.ones(len(cells), bool), "k_exit", K_LO, K_HI, K_REF, "logN", ["muni_code", "cohdep"], "exit_all", blocks=blocks_exit)
    for o in ["score_z", "no_oficial", "rezago"]:
        wald_block(df, ce & ~big, "k_entry", KE_LO, KE_HI, KE_REF, o, ["muni_code", "cohdep"], "entry_nobig", blocks=blocks_entry)
    wald_block(cells, cce & ~cbig, "k_entry", KE_LO, KE_HI, KE_REF, "logN", ["muni_code", "cohdep"], "entry_nobig", blocks=blocks_entry)
    for o in ["score_z", "no_oficial", "rezago"]:
        wald_block(df, cb_i & ~big, "k_entry", KE_LO, KE_HI, KE_REF, o, ["muni_code", "cohdep"], "entry_broad_nobig", blocks=blocks_entry)
    wald_block(cells, cb_c & ~cbig, "k_entry", KE_LO, KE_HI, KE_REF, "logN", ["muni_code", "cohdep"], "entry_broad_nobig", blocks=blocks_entry)
    blocks_peak = [("pre: k ≤ −5", lambda v: v <= -5), ("k ∈ [−4, −2]", lambda v: -4 <= v <= -2), ("post: k ≥ 0", lambda v: v >= 0)]
    for o in ["score_z", "no_oficial", "rezago"]:
        wald_block(df, ~big, "k_peak", KP_LO, KP_HI, KP_REF, o, ["muni_code", "cohdep"], "peak_nobig", blocks=blocks_peak)
    wald_block(df, ~big & df.educ_le_prim.notna().values, "k_peak", KP_LO, KP_HI, KP_REF, "educ_le_prim", ["muni_code", "cohdep"], "peak_nobig", blocks=blocks_peak)
    wald_block(cells, ~cbig, "k_peak", KP_LO, KP_HI, KP_REF, "logN", ["muni_code", "cohdep"], "peak_nobig", blocks=blocks_peak)
    tests = pd.DataFrame(tests); tests.to_csv(f"{OUT_D}/t6_es_tests.csv", index=False)
    print(tests.round(4).to_string())

    # ---- verificación del demeaning con dummies (submuestra) ----
    import statsmodels.api as sm
    rng = np.random.default_rng(20261024)
    sel = np.flatnonzero(~big & df.dpto_res.isin(["20", "47", "70"]).values)
    sel = np.sort(rng.choice(sel, size=min(60000, len(sel)), replace=False))
    sub = df.iloc[sel]
    k = np.clip(sub.k_exit.values, K_LO, K_HI); Xd, vals = event_dummies(k, K_LO, K_HI, K_REF)
    Xd = np.column_stack([Xd, sub.female.values.astype(float)])
    g1, g2 = codes(sub.muni_code.values), codes(sub.cohdep.values)
    M, it, chk = demean(np.column_stack([sub.score_z.values.astype(float), Xd]), [g1, g2])
    b_dm, V_dm, _ = ols_cluster(M[:, 0], M[:, 1:], g1)
    D1 = pd.get_dummies(pd.Series(g1)).values.astype(float)
    cd = pd.DataFrame({"g2": g2, "dp": sub.dpto_res.values}); drop = set(cd.groupby("dp").g2.min().values)
    D2 = pd.get_dummies(pd.Series(g2)).reindex(columns=[c for c in range(g2.max() + 1) if c not in drop]).values.astype(float)
    X = np.column_stack([Xd, D1, D2]); keepc = [i for i in range(X.shape[1]) if X[:, i].std() > 0]
    X = X[:, keepc]
    res = sm.OLS(sub.score_z.values.astype(float), X).fit(cov_type="cluster", cov_kwds={"groups": g1})
    nb = Xd.shape[1]
    fechk = pd.DataFrame({"term": [f"k{v:+d}" for v in vals] + ["female"], "beta_demean": b_dm, "beta_dummies": res.params[:nb],
                          "se_demean_CR1": np.sqrt(np.diag(V_dm)), "se_dummies_sm": res.bse[:nb]})
    fechk["abs_diff_beta"] = (fechk.beta_demean - fechk.beta_dummies).abs(); fechk["N_sub"] = len(sub)
    fechk.to_csv(f"{OUT_D}/t6_es_fe_check.csv", index=False)
    log(f"Verificación EF con dummies (N={len(sub):,}): max |Δβ| = {fechk.abs_diff_beta.max():.2e}")

    make_figure(coef, counts)
    summ = {"flow": flow, "n_T": int(len(T)), "n_big": int(T.big.sum()), "big": sorted(T[T.big].muni_name.tolist()),
            "n_clean_entry": int(T.clean_entry.sum()), "n_clean_entry_strict": int(T.clean_entry_strict.sum()), "n_clean_entry_broad": int(T.clean_entry_broad.sum()),
            "exit_abs12_eq_exit_year_share": float((T.exit_abs12_minus_exit_year == 0).mean()),
            "n_cells": int(len(cells)), "fe_check_max_abs_diff": float(fechk.abs_diff_beta.max()),
            "demean_max_chk": float(coef.demean_chk.max())}
    with open(f"{OUT_D}/t6_es_resumen.json", "w") as fh: json.dump(summ, fh, indent=1, ensure_ascii=False)
    # resumen en consola
    for lab in ["exit_nobig", "exit_all", "exit_nobig_perage", "exit5_nobig", "entry_nobig", "entry_broad_nobig", "peak_nobig"]:
        d = coef[(coef.label == lab) & (coef.note == "") & coef.k.notna()]
        if len(d) == 0: continue
        print(f"\n== {lab} ==")
        print(d.pivot_table(index="k", columns="outcome", values="beta").round(4).to_string())
        print(d.pivot_table(index="k", columns="outcome", values="se").round(4).to_string())
    print(counts.pivot_table(index="k", columns=["event", "sample"], values=["cells", "N"], aggfunc="sum").to_string())
    log("Fin")

if __name__ == "__main__":
    main()
