#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
T2b — Verificación adversarial del perfil dosis-por-edad (Saber 11 × CNMH).

Ejecutar:  python3 -I /home/user/JMP/code/analysis/t2b_verify.py

Re-estima DE FORMA INDEPENDIENTE la especificación principal del RA B
(05b_T2b_perfil_dosis_primer_pase.md) partiendo de saber11_slim.parquet y de
cnmh_muni_month_victims.csv —sin leer ningún intermedio t2b_*— y la compara
coeficiente a coeficiente con t2b_coeficientes.csv (que sólo se usa para la tabla
comparativa). Después intenta romper el resultado:
  P1 sin municipios con post contaminado (Medellín, Córdoba, Urabá, Bajo Cauca, Nariño)
  P2 escala nueva (periodos >= 2014-2) frente a antigua (< 2014-2)
  P3 municipio del colegio (dosis + EF) en lugar de residencia; y submuestra coincidente
  P4 placebo pre-concepción: cohortes 1989+, ventana extra [-81,-46] (cohortes 1992+),
     placebo solo, y escala por 100
  P5 dosis de guerrilla (GUE) en lugar de paramilitar (PARA); y conjunta
  E1 errores agrupados por departamento (33 clusters, wild-cluster no; CR1)
  E2 EF cohorte×municipio + EF mes de nacimiento (sólo variación de mes dentro de año)
  E3 + dummies de edad entera al examen (truncación mecánica de 12-17 en el mes del examen)

Salidas: data/derived/t2b_verify_coefs.csv, t2b_verify_compare.csv,
         t2b_verify_fecheck.csv, t2b_verify_dosecheck.csv, t2b_verify_resumen.json,
         scoping/proposal/fig7_verificacion_adversarial.pdf
"""
import os, sys, time, json, warnings
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
def log(m): print(f"[{time.time()-T0:7.1f}s] {m}", flush=True)

ROOT = "/home/user/JMP"
F_SABER = f"{ROOT}/data/derived/saber11_slim.parquet"
F_CNMH = f"{ROOT}/data/derived/cnmh_muni_month_victims.csv"
F_T = f"{ROOT}/data/derived/t2_A_T1_muestra_T.csv"
F_RA = f"{ROOT}/data/derived/t2b_coeficientes.csv"   # sólo para la tabla comparativa
OUT_D = f"{ROOT}/data/derived"; OUT_P = f"{ROOT}/scoping/proposal"
os.makedirs(f"{ROOT}/code/analysis", exist_ok=True)
F_FIG = f"{OUT_P}/fig7_verificacion_adversarial.pdf"

COH_LO, COH_HI = 1985, 2005
WIN = {"preconc": (-45, -10), "inutero": (-9, -1), "a0_2": (0, 35), "a3_5": (36, 71),
       "a6_11": (72, 143), "a12_17": (144, 215)}
WIN_X = {"preconc2": (-81, -46)}          # placebo adicional, más lejano
WK = list(WIN)
LAB = {"preconc2": "Pre-conc. 2\n−81 a −46", "preconc": "Pre-conc.\n−45 a −10", "inutero": "In utero",
       "a0_2": "0-2", "a3_5": "3-5", "a6_11": "6-11", "a12_17": "12-17\n(a examen)"}
COL = {"blue": "#2a78d6", "orange": "#eb6834", "green": "#1baf7a", "yellow": "#eda100", "gray": "#8a8984"}
# municipios con post contaminado (carta del PI, P4)
EXCL_MUNI = {"05001", "05837", "05045", "05147", "05172", "05490",
             "05154", "05790", "05120", "05250", "05895", "05495"}
EXCL_DPTO = {"23", "52"}

# ----------------------------------------------------------------------------- figura
def make_figure(res, ra):
    plt.rcParams.update({"font.size": 7, "axes.titlesize": 7.3, "axes.labelsize": 6.8, "xtick.labelsize": 6.2,
                         "ytick.labelsize": 6.2, "legend.fontsize": 6.0, "pdf.fonttype": 42, "axes.spines.top": False,
                         "axes.spines.right": False, "axes.linewidth": 0.6, "xtick.major.width": 0.5, "ytick.major.width": 0.5})
    XL = {"preconc2": "pre2", "preconc": "pre", "inutero": "iu", "a0_2": "0-2", "a3_5": "3-5", "a6_11": "6-11", "a12_17": "12-17"}
    def get(block, scale, spec="main", dose=None):
        d = res[(res.block == block) & (res.scale == scale) & (res.spec == spec) & (res.term.isin(WK + ["preconc2"]))]
        if dose: d = d[d.dose == dose]
        return d.set_index("term")
    def panel(ax, series, title, mult, wins=WK):
        ax.axhline(0, color=COL["gray"], lw=0.6, zorder=1)
        offs = np.linspace(-0.2, 0.2, len(series)) if len(series) > 1 else [0.0]
        for (lab, d, color), off, mk in zip(series, offs, ["o", "s", "^", "D"]):
            d = d.reindex(wins).dropna(subset=["beta"])
            xs = np.array([wins.index(t) for t in d.index]) + off
            ax.errorbar(xs, mult * d.beta.values, yerr=mult * 1.96 * d.se.values, fmt=mk, ms=2.8, color=color, ecolor=color,
                        elinewidth=0.7, capsize=1.3, lw=0.8, ls="-", mfc=color, mew=0.7, label=lab, zorder=3)
        ax.set_xticks(range(len(wins))); ax.set_xticklabels([XL[w] for w in wins])
        ax.set_title(title, loc="left", pad=20)
        ax.legend(loc="lower left", bbox_to_anchor=(-0.02, 1.0), ncol=2, frameon=False, handletextpad=0.3,
                  columnspacing=0.9, borderaxespad=0.0)
        ax.grid(axis="y", color="#e5e5e5", lw=0.4, zorder=0); ax.margins(x=0.08)
    raT = ra[ra["sample"] == "T"].set_index("term")
    with PdfPages(F_FIG) as pdf:
        for scale, slab, mult, ylab in [("log", "log(1 + víctimas)", 1.0, "β (DE de score_z) por unidad de log(1 + víctimas)"),
                                        ("p100", "víctimas por 100 evaluados de la celda municipio × cohorte", 1000.0,
                                         "β × 1.000 (DE de score_z) por unidad de dosis")]:
            fig, axes = plt.subplots(2, 3, figsize=(7.8, 5.6))
            rT = raT[raT.scale == scale]
            panel(axes[0, 0], [("RA B", rT, COL["blue"]), ("re-estimación", get("R0_T", scale), COL["orange"])], "(a) Réplica, muestra T", mult)
            panel(axes[0, 1], [("T", get("R0_T", scale), COL["blue"]), ("sin post contaminado", get("P1_T_sin_contaminados", scale), COL["orange"])],
                  "(b) P1: sin municipios de post contaminado", mult)
            panel(axes[0, 2], [("antigua (< 2014-2)", get("P2_T_escala_antigua_pre2014-2", scale), COL["blue"]),
                               ("nueva (≥ 2014-2)", get("P2_T_escala_nueva_2014-2+", scale), COL["orange"])], "(c) P2: escala del examen", mult)
            panel(axes[1, 0], [("residencia", get("R0_T", scale), COL["blue"]), ("colegio", get("P3_T_muni_colegio", scale), COL["orange"]),
                               ("res = colegio", get("P3_T_res_igual_cole", scale), COL["green"])], "(d) P3: municipio del colegio", mult)
            panel(axes[1, 1], [("cohortes 1985-2005", get("R0_T", scale), COL["blue"]), ("1989+", get("P4_T_coh1989+", scale), COL["orange"]),
                               ("1992+, con pre2", get("P4_T_coh1992+_preconc2", scale), COL["green"])], "(e) P4: placebos pre-concepción", mult,
                  wins=["preconc2"] + WK)
            panel(axes[1, 2], [("PARA", get("P5_T_GUE", scale, "main"), COL["blue"]), ("GUE", get("P5_T_GUE", scale, "main_GUE"), COL["orange"]),
                               ("PARA | GUE", get("P5_T_GUE", scale, "joint_PARA_GUE", dose="PARA"), COL["green"])], "(f) P5: perpetrador", mult)
            for ax in axes[:, 0]: ax.set_ylabel(ylab)
            fig.suptitle(f"Verificación adversarial del perfil dosis-por-edad — dosis en {slab}\n"
                         "score_z ~ Σ β_a·dosis_a + mujer + EF municipio + EF cohorte×departamento; cohortes 1985-2005; muestra T; IC 95 %, EE agrupados por municipio.\n"
                         "Ventanas en meses desde el nacimiento: pre2 = −81..−46, pre = −45..−10 (pre-concepción), iu = in utero (−9..−1), "
                         "0-2, 3-5, 6-11, 12-17 (truncada en el mes del examen).", fontsize=6.6, x=0.01, ha="left", y=0.998)
            fig.tight_layout(rect=(0, 0, 1, 0.945), h_pad=1.6, w_pad=1.0); pdf.savefig(fig); plt.close(fig)
    log(f"Figura: {F_FIG}")


if "--figure-only" in sys.argv:
    _res = pd.read_csv(f"{OUT_D}/t2b_verify_coefs.csv")
    _ra = pd.read_csv(F_RA); _ra["note"] = _ra.note.fillna("")
    _ra = _ra[(_ra.spec == "main6") & (_ra.outcome == "score_z") & (_ra.note == "") & (_ra["sample"].isin(["all", "T"]))]
    make_figure(_res, _ra); sys.exit(0)

# ----------------------------------------------------------------------------- CNMH
log("CNMH: matriz municipio × mes (acumulados) para PARA y GUE")
pan = pd.read_csv(F_CNMH, dtype={"muni": str}, usecols=["muni", "ym", "PARA", "GUE"])
YM0, YM1 = int(pan.ym.min()), int(pan.ym.max()); TN = YM1 - YM0 + 1
PM = np.sort(pan.muni.unique()); PMI = pd.Series(np.arange(len(PM)), index=PM); NPM = len(PM)
CUM = {}
for perp in ["PARA", "GUE"]:
    A = np.zeros((NPM + 1, TN))                      # última fila: municipio ausente del panel (0 víctimas)
    np.add.at(A, (PMI[pan.muni].values, pan.ym.values - YM0), pan[perp].values.astype(float))
    C = np.zeros((NPM + 1, TN + 1)); C[:, 1:] = np.cumsum(A, axis=1)
    CUM[perp] = C
    log(f"  {perp}: total {int(A.sum()):,}; panel {YM0//12}-{YM0%12+1:02d} a {YM1//12}-{YM1%12+1:02d}, {NPM} municipios")

def dose(perp, mrow, b_ym, e_ym, lo, hi):
    """Víctimas en [b+lo, min(b+hi, e)] (meses, inclusive), 0 fuera del panel."""
    C = CUM[perp]
    s = b_ym + lo
    t = np.minimum(b_ym + hi, e_ym)
    sc = np.clip(s - YM0, 0, TN); tc = np.clip(t - YM0 + 1, 0, TN)
    out = C[mrow, tc] - C[mrow, sc]
    out[t < s] = 0.0
    return np.maximum(out, 0.0)

# ----------------------------------------------------------------------------- Saber 11
log("Saber 11: lectura por columnas, cohortes 1985-2005")
cols = ["periodo", "year", "sem", "birth_year", "birth_month", "muni_res", "dpto_res", "muni_cole", "sexo", "score_z"]
tab = pq.read_table(F_SABER, columns=cols, filters=[("birth_year", ">=", COH_LO), ("birth_year", "<=", COH_HI)])
df = tab.to_pandas(strings_to_categorical=True); del tab
flow = {"cohortes_1985_2005": len(df)}
df = df[df.birth_month.notna()]; flow["con_mes"] = len(df)
df = df[df.muni_res.notna()]; flow["con_muni_res"] = len(df)
df = df[df.score_z.notna()]; flow["con_score"] = len(df)
df = df[df.sexo.isin(["F", "M"])]; flow["con_sexo"] = len(df)
df = df.reset_index(drop=True)
N = len(df); log(f"  muestra analítica N = {N:,}  {flow}")
df["female"] = (df.sexo == "F").astype(np.int8)
df["muni_res"] = df.muni_res.cat.remove_unused_categories()
df["b_ym"] = (df.birth_year.astype(np.int32) * 12 + df.birth_month.astype(np.int32) - 1).astype(np.int32)
df["e_ym"] = (df.year.astype(np.int32) * 12 + np.where(df["sem"].values == 1, 2, 7)).astype(np.int32)   # 15-mar / 15-ago
df["per"] = df.periodo.astype(str).astype(np.int32)
df["age_int"] = ((df.e_ym - df.b_ym) // 12).astype(np.int16)
# departamento: dos primeros dígitos del código de residencia (nested por construcción)
mr_cats = df.muni_res.cat.categories
df["dpto"] = pd.Series(np.asarray(mr_cats.str[:2])[df.muni_res.cat.codes.values], dtype="category")
n_dp_diff = int((df.dpto.astype(str) != df.dpto_res.astype(str)).sum())
log(f"  dpto (muni_res[:2]) difiere de dpto_res en {n_dp_diff:,} filas")

# filas del panel para residencia y colegio
def panel_row(cat_series):
    cats = cat_series.cat.categories
    rows = PMI.reindex(cats).fillna(NPM).astype(np.int64).values
    r = rows[cat_series.cat.codes.values]
    r[cat_series.cat.codes.values < 0] = NPM
    return r
mrow_res = panel_row(df.muni_res)
log(f"  muni_res fuera del panel CNMH: {int((mrow_res == NPM).sum()):,} filas")

# dosis (PARA y GUE) por ventana, residencia
b = df.b_ym.values; e = df.e_ym.values
for perp in ["PARA", "GUE"]:
    for w, (lo, hi) in {**WIN, **WIN_X}.items():
        df[f"v{perp}_{w}"] = dose(perp, mrow_res, b, e, lo, hi).astype(np.float32)
# dosis PARA por municipio del colegio
has_cole = df.muni_cole.notna().values
mrow_cole = panel_row(df.muni_cole)
for w, (lo, hi) in WIN.items():
    df[f"vCOLE_{w}"] = dose("PARA", mrow_cole, b, e, lo, hi).astype(np.float32)
log("  dosis calculadas")

# --- verificación de la dosis contra sumas directas del panel (30 individuos al azar)
rng = np.random.default_rng(7)
chk_rows = []
for i in rng.choice(N, 30, replace=False):
    m = str(df.muni_res.iloc[i]); bi = int(b[i]); ei = int(e[i])
    sub = pan[pan.muni == m]
    for perp in ["PARA", "GUE"]:
        for w, (lo, hi) in {**WIN, **WIN_X}.items():
            direct = float(sub[(sub.ym >= bi + lo) & (sub.ym <= min(bi + hi, ei))][perp].sum())
            chk_rows.append({"i": int(i), "muni": m, "perp": perp, "win": w, "direct": direct,
                             "vectorized": float(df[f"v{perp}_{w}"].iloc[i])})
chk = pd.DataFrame(chk_rows); chk["diff"] = chk.direct - chk.vectorized
chk.to_csv(f"{OUT_D}/t2b_verify_dosecheck.csv", index=False)
log(f"  verificación dosis: {len(chk)} celdas, max |dif| = {chk['diff'].abs().max():.0f}")
assert chk["diff"].abs().max() == 0

# --- denominadores por 100 evaluados (celda municipio × cohorte, muestra analítica)
cell = df.groupby(["muni_res", "birth_year"], observed=True).size().rename("n_cell")
df = df.join(cell, on=["muni_res", "birth_year"]); df["n_cell"] = df.n_cell.astype(np.float32)
cell_c = df[has_cole].groupby(["muni_cole", "birth_year"], observed=True).size().rename("n_cell_cole")
df = df.join(cell_c, on=["muni_cole", "birth_year"]); df["n_cell_cole"] = df.n_cell_cole.astype(np.float32)

# --- muestra T
Tdf = pd.read_csv(F_T, dtype={"muni": str})
Tset = set(Tdf.muni) - {"00000"}
inT = df.muni_res.isin(Tset).values
inT_cole = df.muni_cole.isin(Tset).values & has_cole
log(f"  T: {len(Tset)} códigos; en T por residencia {int(inT.sum()):,} ({inT.mean():.1%}), "
    f"{df.muni_res[inT].nunique()} municipios; por colegio {int(inT_cole.sum()):,}")

# ----------------------------------------------------------------------------- econometría
def absorb(M, groups, tol=1e-10, maxit=3000):
    """Proyecciones alternantes sobre los conjuntos de EF en `groups` (códigos 0..n-1)."""
    M = M if (isinstance(M, np.ndarray) and M.flags.f_contiguous and M.dtype == np.float64) else np.asfortranarray(np.asarray(M, dtype=np.float64))
    K = M.shape[1]
    sd = M.std(axis=0); sd[sd == 0] = 1.0
    cnts = [np.bincount(g).astype(np.float64) for g in groups]
    for it in range(1, maxit + 1):
        dmax = 0.0
        for g, c in zip(groups, cnts):
            for k in range(K):
                mu = np.bincount(g, weights=M[:, k]) / c
                M[:, k] -= mu[g]
                dmax = max(dmax, float(np.abs(mu).max() / sd[k]))
        if dmax < tol:
            break
    return M, it, dmax

def ols_cl(y, X, cl):
    n, k = X.shape
    XtXi = np.linalg.inv(X.T @ X)
    beta = XtXi @ (X.T @ y)
    u = y - X @ beta
    G = int(cl.max()) + 1
    S = np.column_stack([np.bincount(cl, weights=X[:, j] * u, minlength=G) for j in range(k)])
    V = XtXi @ (S.T @ S) @ XtXi * (G / (G - 1.0)) * ((n - 1.0) / (n - k))
    return beta, np.sqrt(np.diag(V)), V, G, 1.0 - (u @ u) / (y @ y)

def codes(*arrs):
    """Código entero 0..n-1 de la combinación de arrays (radix mixto sobre códigos factorizados)."""
    key = np.zeros(len(arrs[0]), dtype=np.int64)
    for a in arrs:
        c = pd.factorize(np.asarray(a))[0].astype(np.int64)
        key = key * (c.max() + 1) + c
    return pd.factorize(key)[0].astype(np.int64)

ROWS = []
def run_block(name, mask, fe_groups, dose_prefix, note="", cluster=None, scales=("log", "p100"),
              wins=WK, denom="n_cell", extra_specs=None, extra_dose=None, age_dummies=False):
    """Demean una vez y estima score_z ~ Σ dosis_a + female para cada escala.
    fe_groups: lista de arrays (ya en la máscara). cluster: array (en la máscara) o None = primer grupo."""
    idx = np.flatnonzero(mask)
    groups = [codes(g) for g in fe_groups]
    cl = groups[0] if cluster is None else codes(cluster)
    colnames = ["score_z", "female"] + [f"{s}:{pref}:{w}" for s in scales for pref in ([dose_prefix] + (extra_dose or [])) for w in wins]
    age_cols = []
    if age_dummies:
        age = np.minimum(df.age_int.values[idx], 25)
        age_cols = [f"age_{a}" for a in sorted(set(age.tolist())) if a != 17]
        colnames += age_cols
    M = np.empty((len(idx), len(colnames)), dtype=np.float64, order="F")
    M[:, 0] = df.score_z.values[idx]; M[:, 1] = df.female.values[idx]
    den = df[denom].values[idx].astype(np.float64)
    k = 2
    for s in scales:
        for pref in ([dose_prefix] + (extra_dose or [])):
            for w in wins:
                v = df[f"v{pref}_{w}"].values[idx].astype(np.float64)
                M[:, k] = np.log1p(v) if s == "log" else 100.0 * v / den
                k += 1
    for c in age_cols:
        M[:, k] = (age == int(c.split("_")[1])).astype(np.float64); k += 1
    t1 = time.time()
    Md, it, dmax = absorb(M, groups); del M
    n = len(idx)
    log(f"  [{name}] N={n:,} EF={[int(g.max()+1) for g in groups]} clusters={int(cl.max()+1)} "
        f"demeaning {it} it, max|media grupo|/sd={dmax:.1e}, {time.time()-t1:.0f}s")
    ci = {c: k for k, c in enumerate(colnames)}
    y = Md[:, 0]
    specs = []
    for s in scales:
        specs.append((s, "main", [f"{s}:{dose_prefix}:{w}" for w in wins] + ["female"] + age_cols))
        if extra_dose:
            for pref in extra_dose:
                specs.append((s, f"main_{pref}", [f"{s}:{pref}:{w}" for w in wins] + ["female"]))
            specs.append((s, "joint_" + "_".join([dose_prefix] + extra_dose),
                          [f"{s}:{p}:{w}" for p in [dose_prefix] + extra_dose for w in wins] + ["female"]))
        for sp_name, sp_wins in (extra_specs or []):
            specs.append((s, sp_name, [f"{s}:{dose_prefix}:{w}" for w in sp_wins] + ["female"]))
    for s, sp, xc in specs:
        X = Md[:, [ci[c] for c in xc]]
        beta, se, V, G, r2 = ols_cl(y, X, cl)
        for k, c in enumerate(xc):
            parts = c.split(":")
            term = parts[-1]; pref = parts[1] if len(parts) == 3 else ""
            ROWS.append({"block": name, "note": note, "scale": s, "spec": sp, "dose": pref, "term": term,
                         "beta": beta[k], "se": se[k], "t": beta[k] / se[k],
                         "p": 2 * sps.norm.sf(abs(beta[k] / se[k])), "N": n, "G": G, "r2_within": r2,
                         "within_sd_x": Md[:, ci[c]].std()})
        pd.DataFrame(ROWS).to_csv(f"{OUT_D}/t2b_verify_coefs.csv", index=False)
        if f"{s}:{dose_prefix}:a0_2" in xc and f"{s}:{dose_prefix}:a3_5" in xc:
            i, j = xc.index(f"{s}:{dose_prefix}:a0_2"), xc.index(f"{s}:{dose_prefix}:a3_5")
            d = beta[i] - beta[j]; v = V[i, i] + V[j, j] - 2 * V[i, j]
            ROWS.append({"block": name, "note": note, "scale": s, "spec": sp, "dose": dose_prefix, "term": "test_b02_eq_b35",
                         "beta": d, "se": np.sqrt(v), "t": d / np.sqrt(v), "p": sps.chi2.sf(d * d / v, 1),
                         "N": n, "G": G, "r2_within": r2, "within_sd_x": np.nan})
    return Md, ci, groups, cl

# grupos base
g_muni = df.muni_res.cat.codes.values.astype(np.int64)
g_cd = codes(df.birth_year.values, df.dpto.cat.codes.values)
allm = np.ones(N, dtype=bool)

# ---- cross-check de la absorción de EF contra linearmodels.AbsorbingLS (submuestra 400k)
log("Cross-check absorción EF vs linearmodels.AbsorbingLS (submuestra aleatoria)")
try:
    from linearmodels.iv.absorbing import AbsorbingLS
    sel = np.sort(rng.choice(N, 400_000, replace=False))
    sub = df.iloc[sel]
    Xs = pd.DataFrame({f"log_{w}": np.log1p(sub[f"vPARA_{w}"].values.astype(float)) for w in WK})
    Xs["female"] = sub.female.values.astype(float)
    ab = pd.DataFrame({"muni": pd.Categorical(sub.muni_res.astype(str).values),
                       "cd": pd.Categorical((sub.birth_year.astype(str) + "_" + sub.dpto.astype(str)).values)})
    res = AbsorbingLS(sub.score_z.values.astype(float), Xs, absorb=ab).fit(
        cov_type="clustered", clusters=pd.Series(pd.factorize(sub.muni_res.astype(str).values)[0]))
    # mi rutina en la misma submuestra
    Mx = np.column_stack([sub.score_z.values.astype(float)] + [Xs[c].values for c in Xs.columns])
    gs = [codes(sub.muni_res.cat.codes.values), codes(sub.birth_year.values, sub.dpto.cat.codes.values)]
    Mdx, it, dmax = absorb(Mx, gs)
    bmine, semine, _, _, _ = ols_cl(Mdx[:, 0], Mdx[:, 1:], gs[0])
    fechk = pd.DataFrame({"term": list(Xs.columns), "beta_mine": bmine, "beta_linearmodels": res.params.values,
                          "se_mine_CR1": semine, "se_linearmodels_cl": res.std_errors.values})
    fechk["abs_diff_beta"] = (fechk.beta_mine - fechk.beta_linearmodels).abs()
    fechk["ratio_se"] = fechk.se_mine_CR1 / fechk.se_linearmodels_cl
    fechk.to_csv(f"{OUT_D}/t2b_verify_fecheck.csv", index=False)
    log(f"  max |Δβ| = {fechk.abs_diff_beta.max():.2e}; ratio EE (mío/linearmodels) {fechk.ratio_se.min():.4f}-{fechk.ratio_se.max():.4f}")
except Exception as ex:
    log(f"  linearmodels no disponible o falló: {ex}")

# ---- R0: réplica
log("R0 réplica: todos")
Md_all, ci_all, gr_all, cl_all = run_block("R0_all", allm, [g_muni, g_cd], "PARA", extra_specs=[("placebo_only", ["preconc"]), ("core4", ["inutero", "a0_2", "a3_5", "a6_11"])])
# E1: cluster por departamento, reutilizando el demeaning
g_dp = df.dpto.cat.codes.values.astype(np.int64)
for s in ("log", "p100"):
    xc = [f"{s}:PARA:{w}" for w in WK] + ["female"]
    X = Md_all[:, [ci_all[c] for c in xc]]
    beta, se, V, G, r2 = ols_cl(Md_all[:, 0], X, codes(g_dp))
    for k, c in enumerate(xc):
        ROWS.append({"block": "E1_all_cluster_dpto", "note": "cluster departamento", "scale": s, "spec": "main", "dose": "PARA",
                     "term": c.split(":")[-1], "beta": beta[k], "se": se[k], "t": beta[k] / se[k],
                     "p": 2 * sps.norm.sf(abs(beta[k] / se[k])), "N": N, "G": G, "r2_within": r2, "within_sd_x": np.nan})
del Md_all
log("R0 réplica: T")
Md_T, ci_T, gr_T, cl_T = run_block("R0_T", inT, [g_muni[inT], g_cd[inT]], "PARA", extra_specs=[("placebo_only", ["preconc"]), ("core4", ["inutero", "a0_2", "a3_5", "a6_11"])])
for s in ("log", "p100"):
    xc = [f"{s}:PARA:{w}" for w in WK] + ["female"]
    X = Md_T[:, [ci_T[c] for c in xc]]
    beta, se, V, G, r2 = ols_cl(Md_T[:, 0], X, codes(g_dp[inT]))
    for k, c in enumerate(xc):
        ROWS.append({"block": "E1_T_cluster_dpto", "note": "cluster departamento", "scale": s, "spec": "main", "dose": "PARA",
                     "term": c.split(":")[-1], "beta": beta[k], "se": se[k], "t": beta[k] / se[k],
                     "p": 2 * sps.norm.sf(abs(beta[k] / se[k])), "N": int(inT.sum()), "G": G, "r2_within": r2, "within_sd_x": np.nan})
del Md_T

# ---- P1: sin municipios con post contaminado
excl = df.muni_res.isin(EXCL_MUNI).values | df.dpto.isin(EXCL_DPTO).values
log(f"P1 exclusión post contaminado: {int(excl.sum()):,} filas, {df.muni_res[excl].nunique()} municipios")
m = allm & ~excl; run_block("P1_all_sin_contaminados", m, [g_muni[m], g_cd[m]], "PARA", note="sin Medellín, Córdoba, Urabá, Bajo Cauca, Nariño")
m = inT & ~excl; run_block("P1_T_sin_contaminados", m, [g_muni[m], g_cd[m]], "PARA", note="sin Medellín, Córdoba, Urabá, Bajo Cauca, Nariño")

# ---- P2: escala nueva vs antigua
new = df.per.values >= 20142
for nm, mm in [("P2_T_escala_nueva_2014-2+", inT & new), ("P2_T_escala_antigua_pre2014-2", inT & ~new)]:
    coh = df.birth_year.values[mm]
    log(f"{nm}: cohortes {coh.min()}-{coh.max()}, p10-p90 {np.percentile(coh,10):.0f}-{np.percentile(coh,90):.0f}")
    run_block(nm, mm, [g_muni[mm], g_cd[mm]], "PARA", note=f"cohortes {coh.min()}-{coh.max()}")

# ---- P3: municipio del colegio
g_cole = df.muni_cole.cat.codes.values.astype(np.int64)
cole_cats = df.muni_cole.cat.categories
dpto_cole = np.asarray(cole_cats.str[:2])[np.maximum(g_cole, 0)]
g_cd_cole = codes(df.birth_year.values, dpto_cole)
m = inT_cole & df.n_cell_cole.notna().values
log(f"P3 colegio: en T por colegio {int(m.sum()):,}")
run_block("P3_T_muni_colegio", m, [g_cole[m], g_cd_cole[m]], "COLE", note="dosis y EF por municipio del colegio", denom="n_cell_cole")
coinc = has_cole & (df.muni_res.astype(str).values == df.muni_cole.astype(str).values)
m = inT & coinc
log(f"P3 coincidentes res==cole en T: {int(m.sum()):,} ({m.sum()/inT.sum():.1%} de T)")
run_block("P3_T_res_igual_cole", m, [g_muni[m], g_cd[m]], "PARA", note="submuestra muni_res == muni_cole")
m = inT & has_cole & ~coinc
log(f"P3 no coincidentes en T: {int(m.sum()):,}")
run_block("P3_T_res_distinto_cole", m, [g_muni[m], g_cd[m]], "PARA", note="submuestra muni_res != muni_cole (dosis por residencia)")

# ---- P4: placebo
m = inT & (df.birth_year.values >= 1989)
run_block("P4_T_coh1989+", m, [g_muni[m], g_cd[m]], "PARA", note="pre-concepción observada por completo")
m = inT & (df.birth_year.values >= 1992)
run_block("P4_T_coh1992+_preconc2", m, [g_muni[m], g_cd[m]], "PARA", note="añade ventana [-81,-46]", wins=["preconc2"] + WK)

# ---- P5: guerrilla
run_block("P5_all_GUE", allm, [g_muni, g_cd], "PARA", note="PARA vs GUE y conjunta", extra_dose=["GUE"])
run_block("P5_T_GUE", inT, [g_muni[inT], g_cd[inT]], "PARA", note="PARA vs GUE y conjunta", extra_dose=["GUE"])

# ---- E2: EF cohorte×municipio + mes de nacimiento
g_cm = codes(df.birth_year.values, g_muni)
g_bm = df.birth_month.values.astype(np.int64) - 1
run_block("E2_T_EF_cohorte_x_muni", inT, [g_cm[inT], g_bm[inT]], "PARA", note="EF cohorte×municipio + mes de nacimiento; cluster municipio", cluster=g_muni[inT])

# ---- E3: + dummies de edad entera al examen (10..25+, ref. 17): truncación mecánica de 12-17
run_block("E3_T_dummies_edad_examen", inT, [g_muni[inT], g_cd[inT]], "PARA", note="+ dummies de edad entera al examen (ref. 17)", age_dummies=True)

# ----------------------------------------------------------------------------- salida
res = pd.DataFrame(ROWS)
res.to_csv(f"{OUT_D}/t2b_verify_coefs.csv", index=False)

# comparación coeficiente a coeficiente con el RA B
ra = pd.read_csv(F_RA); ra["note"] = ra.note.fillna("")
ra = ra[(ra.spec == "main6") & (ra.outcome == "score_z") & (ra.note == "") & (ra["sample"].isin(["all", "T"])) & (ra.scale.isin(["log", "p100"]))]
mine = res[(res.block.isin(["R0_all", "R0_T"])) & (res.spec == "main")].copy()
mine["sample"] = mine.block.map({"R0_all": "all", "R0_T": "T"})
cmp = mine.merge(ra[["sample", "scale", "term", "beta", "se", "N", "n_clusters"]], on=["sample", "scale", "term"], suffixes=("_mine", "_RA"))
cmp["diff_beta"] = cmp.beta_mine - cmp.beta_RA
cmp["diff_beta_in_se"] = cmp.diff_beta / cmp.se_RA
cmp["ratio_se"] = cmp.se_mine / cmp.se_RA
cmp = cmp[["sample", "scale", "term", "beta_RA", "beta_mine", "diff_beta", "diff_beta_in_se", "se_RA", "se_mine", "ratio_se", "N_RA", "N_mine", "n_clusters", "G"]]
cmp.to_csv(f"{OUT_D}/t2b_verify_compare.csv", index=False)
log("Comparación con el RA B (β y EE):")
print(cmp.to_string(float_format=lambda x: f"{x:.5f}"))

summary = {"flow": flow, "N": {"all": int(N), "T": int(inT.sum()), "T_cole": int(inT_cole.sum())},
           "n_muni_all": int(df.muni_res.nunique()), "n_muni_T": int(df.muni_res[inT].nunique()),
           "n_dpto_diff": n_dp_diff, "excl_rows": int(excl.sum()), "excl_munis": int(df.muni_res[excl].nunique()),
           "max_abs_diff_beta_vs_RA": float(cmp.diff_beta.abs().max()),
           "max_abs_diff_beta_in_se_vs_RA": float(cmp.diff_beta_in_se.abs().max()),
           "dose_check_max_abs_diff": float(chk["diff"].abs().max())}
with open(f"{OUT_D}/t2b_verify_resumen.json", "w") as fh:
    json.dump(summary, fh, indent=1, ensure_ascii=False, default=float)

make_figure(res, ra)
log("Fin")
