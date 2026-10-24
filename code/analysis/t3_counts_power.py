#!/usr/bin/env python3
"""
t3_counts_power.py -- T3 del PI: conteos, cobertura y potencia con Saber 11 (2005-1 .. 2022-2).

Uso:  python3 -I /home/user/JMP/code/analysis/t3_counts_power.py

Insumos
  * /home/user/JMP/data/derived/saber11_slim.parquet          (9.293.650 filas; se leen 10 columnas)
  * /home/user/JMP/data/derived/t2_A_T1_muestra_T.csv          (452 municipios T, >=25 victimas PARA 1997-2006)

Salidas
  * /home/user/JMP/data/derived/t3_*.csv
  * /home/user/JMP/scoping/proposal/figs_t3_*.pdf

Bloques
  1. N evaluados por municipio de residencia x cohorte (1985-2005), T vs resto; ajuste del archivo truncado 2017-2.
  2. Coincidencia muni_res == muni_cole por periodo y en T.
  3. Edad al examen por cohorte; rezago (edad > 19) en T vs resto.
  4. ICC del score_z y MDE (80 % potencia, 5 %) para (a) T vs resto con errores agrupados por municipio y
     (b) contraste de ventanas de cohortes dentro de T (1995-2000 vs 2001-2005) con EF municipio + cohorte x dpto.
  5. Proxy de margen extensivo: indice de evaluados por cohorte (base 100) en T vs resto.
"""
import os, time, warnings
warnings.filterwarnings("ignore")
import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.parquet as pq
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

pd.set_option("display.width", 250); pd.set_option("display.max_columns", 60); pd.set_option("display.max_rows", 200)

PARQ = "/home/user/JMP/data/derived/saber11_slim.parquet"
TFILE = "/home/user/JMP/data/derived/t2_A_T1_muestra_T.csv"
DER = "/home/user/JMP/data/derived"
PROP = "/home/user/JMP/scoping/proposal"
os.makedirs(DER, exist_ok=True); os.makedirs(PROP, exist_ok=True)

COH0, COH1 = 1985, 2005          # cohortes del PI
FULL0, FULL1 = 1988, 2003        # cohortes observadas a las edades 16-19 completas (examenes 2005-2022)
W1 = (1995, 2000); W2 = (2001, 2005)
Z80 = 1.959964 + 0.841621        # z_{0.975} + z_{0.80}

BLUE, ORANGE, GREEN, YELLOW, GREY = "#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#8a8984"
plt.rcParams.update({
    "font.size": 7, "axes.titlesize": 8, "axes.labelsize": 7, "xtick.labelsize": 6.5, "ytick.labelsize": 6.5,
    "legend.fontsize": 6.5, "legend.frameon": False, "axes.spines.top": False, "axes.spines.right": False,
    "axes.linewidth": 0.6, "xtick.major.width": 0.5, "ytick.major.width": 0.5, "lines.linewidth": 1.2,
    "pdf.fonttype": 42, "figure.dpi": 150,
})

T0 = time.time()
def log(*a): print(f"[{time.time()-T0:6.1f}s]", *a, flush=True)
def pct(x, d=1): return f"{100*x:.{d}f}%"

# =====================================================================================
# 0. Carga
# =====================================================================================
tmun = pd.read_csv(TFILE, dtype={"muni": str})
T_SET = sorted(set(tmun["muni"]))
assert len(T_SET) == 452, len(T_SET)
exit_year = tmun.set_index("muni")["exit_year"]

cols = ["periodo", "year", "sem", "birth_year", "age_at_exam", "muni_res", "dpto_res", "muni_cole", "score_z", "flag_truncated_file"]
tb = pq.read_table(PARQ, columns=cols, read_dictionary=["periodo", "muni_res", "dpto_res", "muni_cole"])
# comparaciones en arrow (evita objetos python): coincidencia residencia = colegio y pertenencia a T
match = pc.equal(pc.cast(tb["muni_res"], pa.string()), pc.cast(tb["muni_cole"], pa.string()))
inT = pc.is_in(pc.cast(tb["muni_res"], pa.string()), value_set=pa.array(T_SET))
inT_cole = pc.is_in(pc.cast(tb["muni_cole"], pa.string()), value_set=pa.array(T_SET))
df = tb.to_pandas()
df["match"] = match.to_pandas()                       # NaN si falta alguno de los dos
df["inT"] = inT.to_pandas().fillna(False).astype(bool)
df["inT_cole"] = inT_cole.to_pandas().fillna(False).astype(bool)
del tb, match, inT, inT_cole
df["birth_year"] = df["birth_year"].astype("float32")
df["rezago"] = np.where(df["age_at_exam"].isna(), np.nan, (df["age_at_exam"] > 19).astype("float32"))
log(f"parquet leido: {len(df):,} filas, {df.memory_usage(deep=True).sum()/1e6:.0f} MB")
log("evaluados por grupo (todas las cohortes):", df["inT"].value_counts().to_dict(),
    "| muni_res NaN:", int(df["muni_res"].isna().sum()))

# Los grandes municipios estan en T: registrar para el memo
big = df[df["inT"]].groupby("muni_res", observed=True).size().sort_values(ascending=False).head(10)
log("Top-10 municipios T por evaluados:", big.to_dict())
share_T_all = df["inT"].mean()

# =====================================================================================
# 1. N por municipio de residencia x cohorte 1985-2005 (T vs resto), con ajuste de 2017-2
# =====================================================================================
coh = df[df["birth_year"].between(COH0, COH1) & df["muni_res"].notna()].copy()
coh["cohort"] = coh["birth_year"].astype("int16")
log(f"filas cohortes {COH0}-{COH1} con muni_res: {len(coh):,} ({pct(len(coh)/len(df))} del total)")

# 1a. composicion del archivo truncado 2017-2 frente a 2016-2 y 2018-2 (selectividad geografica)
chk = (df[df["periodo"].isin(["20162", "20172", "20182"])]
       .groupby("periodo", observed=True)
       .agg(N=("year", "size"), share_T=("inT", "mean"), n_munis=("muni_res", "nunique"), n_dptos=("dpto_res", "nunique"))
       .reset_index())
chk["periodo"] = chk["periodo"].astype(str)
chk.to_csv(f"{DER}/t3_trunc_20172_check.csv", index=False)
log("2017-2 truncado vs vecinos:\n" + chk.to_string(index=False))

# 1b. celdas muni x cohorte
cnt = (coh.groupby(["muni_res", "cohort"], observed=True)
       .agg(N=("year", "size"), N_edad_le19=("rezago", lambda s: float((s == 0).sum())),
            N_score=("score_z", "count"), mean_score_z=("score_z", "mean"), sd_score_z=("score_z", "std"),
            edad_media=("age_at_exam", "mean"))
       .reset_index())
cnt["N_edad_le19"] = cnt["N_edad_le19"].astype(int)

# contribucion de 2017-2 e imputacion a partir de 2016-2 (cohorte c-1) y 2018-2 (cohorte c+1): misma edad al examen
c4 = coh.groupby(["muni_res", "cohort", "year", "sem"], observed=True).size().rename("n").reset_index()
c172 = c4[(c4.year == 2017) & (c4["sem"] == 2)][["muni_res", "cohort", "n"]].rename(columns={"n": "N_20172"})
c162 = c4[(c4.year == 2016) & (c4["sem"] == 2)][["muni_res", "cohort", "n"]].copy(); c162["cohort"] += 1
c182 = c4[(c4.year == 2018) & (c4["sem"] == 2)][["muni_res", "cohort", "n"]].copy(); c182["cohort"] -= 1
imp = (c162.rename(columns={"n": "a"}).merge(c182.rename(columns={"n": "b"}), on=["muni_res", "cohort"], how="outer")
       .fillna(0.0))
imp["N_20172_imp"] = 0.5 * (imp["a"] + imp["b"])
imp = imp[imp["cohort"].between(COH0, COH1)][["muni_res", "cohort", "N_20172_imp"]]
cnt = cnt.merge(c172, on=["muni_res", "cohort"], how="left").merge(imp, on=["muni_res", "cohort"], how="left")
cnt[["N_20172", "N_20172_imp"]] = cnt[["N_20172", "N_20172_imp"]].fillna(0.0)
cnt["N_ajust"] = cnt["N"] - cnt["N_20172"] + cnt["N_20172_imp"]
log(f"2017-2: observado {cnt.N_20172.sum():,.0f} filas (cohortes {COH0}-{COH1}); imputado {cnt.N_20172_imp.sum():,.0f}")

# N por municipio del colegio (alternativa para cohortes pre 2012 si se dudara de la residencia)
cnt_cole = (df[df["birth_year"].between(COH0, COH1) & df["muni_cole"].notna()]
            .assign(cohort=lambda d: d["birth_year"].astype("int16"))
            .groupby(["muni_cole", "cohort"], observed=True).size().rename("N_cole").reset_index()
            .rename(columns={"muni_cole": "muni_res"}))
cnt["muni_res"] = cnt["muni_res"].astype(str); cnt_cole["muni_res"] = cnt_cole["muni_res"].astype(str)
cnt = cnt.merge(cnt_cole, on=["muni_res", "cohort"], how="outer")
cnt["N"] = cnt["N"].fillna(0).astype(int); cnt["N_cole"] = cnt["N_cole"].fillna(0).astype(int)
cnt["N_ajust"] = cnt["N_ajust"].fillna(0.0)
cnt["in_T"] = cnt["muni_res"].isin(T_SET)
cnt = cnt.rename(columns={"muni_res": "muni"})
cnt["exit_year"] = cnt["muni"].map(exit_year)
cnt = cnt.sort_values(["muni", "cohort"])
cnt.to_csv(f"{DER}/t3_N_muni_cohorte.csv", index=False)
log(f"t3_N_muni_cohorte.csv: {len(cnt):,} celdas, {cnt.muni.nunique()} municipios")

# 1c. resumen por cohorte
def _summ(g):
    gT, gC = g[g.in_T], g[~g.in_T]
    return pd.Series({
        "N_T": gT.N.sum(), "N_noT": gC.N.sum(), "share_T": gT.N.sum() / max(g.N.sum(), 1),
        "N_T_ajust_20172": gT.N_ajust.sum(), "N_noT_ajust_20172": gC.N_ajust.sum(),
        "N_T_edad_le19": gT.N_edad_le19.sum(), "N_noT_edad_le19": gC.N_edad_le19.sum(),
        "munis_T_con_evaluados": int((gT.N > 0).sum()), "munis_T_ge30": int((gT.N >= 30).sum()),
        "munis_T_ge100": int((gT.N >= 100).sum()), "munis_noT_con_evaluados": int((gC.N > 0).sum()),
        "munis_noT_ge30": int((gC.N >= 30).sum()),
        "mediana_N_muni_T": gT.N.median(), "p10_N_muni_T": gT.N.quantile(0.10),
    })
res = cnt.groupby("cohort").apply(_summ).reset_index()
for c in ["N_T", "N_noT", "N_T_edad_le19", "N_noT_edad_le19"]: res[c] = res[c].astype(int)
res["edad_min_observable"] = 2005 - res["cohort"]; res["edad_max_observable"] = 2022 - res["cohort"]
res["cobertura_16_19_completa"] = res["cohort"].between(FULL0, FULL1)
res["afectada_trunc_20172"] = res["cohort"].between(1999, 2001)
modal = coh.groupby("cohort")["year"].agg(lambda s: s.value_counts().idxmax()).rename("anio_examen_modal")
res = res.merge(modal.reset_index(), on="cohort", how="left")
res.to_csv(f"{DER}/t3_resumen_cohorte.csv", index=False)
log("Resumen por cohorte:\n" + res[["cohort", "N_T", "N_noT", "share_T", "N_T_ajust_20172", "munis_T_ge30", "munis_T_con_evaluados",
                                    "mediana_N_muni_T", "anio_examen_modal", "cobertura_16_19_completa"]].to_string(index=False))

# 1d. tabla por municipio T (cohortes plenamente observadas)
full = cnt[cnt.in_T & cnt.cohort.between(FULL0, FULL1)]
tm = (full.groupby("muni").agg(N_total_1988_2003=("N", "sum"), N_mediana_cohorte=("N", "median"),
                                 N_min_cohorte=("N", "min"), cohortes_ge30=("N", lambda s: int((s >= 30).sum())),
                                 cohortes_ge100=("N", lambda s: int((s >= 100).sum())),
                                 score_z_medio=("mean_score_z", "mean"))
      .reset_index())
tm = tm.merge(tmun[["muni", "muni_name", "depto", "para_9706", "exit_year"]], on="muni", how="right").fillna({"N_total_1988_2003": 0})
tm = tm.sort_values("N_total_1988_2003", ascending=False)
tm.to_csv(f"{DER}/t3_T_munis_N.csv", index=False)
nT16 = int((tm["cohortes_ge30"] == (FULL1 - FULL0 + 1)).sum())
log(f"Municipios T con >=30 evaluados en TODAS las cohortes {FULL0}-{FULL1}: {nT16}/452; "
    f"con N total >= 500: {int((tm.N_total_1988_2003 >= 500).sum())}; sin evaluados: {int((tm.N_total_1988_2003 == 0).sum())}")
log("Municipios T con menos evaluados:\n" + tm.tail(8)[["muni", "muni_name", "depto", "para_9706", "N_total_1988_2003"]].to_string(index=False))

# =====================================================================================
# 2. Coincidencia muni_res == muni_cole
# =====================================================================================
both = df[df["match"].notna()].copy()
both["match"] = both["match"].astype(float)
mp = (both.groupby("periodo", observed=True)
      .agg(N_ambos=("match", "size"), tasa=("match", "mean"),
           tasa_T=("match", lambda s: s[both.loc[s.index, "inT"]].mean()),
           tasa_noT=("match", lambda s: s[~both.loc[s.index, "inT"]].mean()),
           tasa_coleT=("match", lambda s: s[both.loc[s.index, "inT_cole"]].mean()))
      .reset_index())
mp["periodo"] = mp["periodo"].astype(str)
mp["N_total"] = df.groupby("periodo", observed=True).size().values
mp["share_ambos"] = mp["N_ambos"] / mp["N_total"]
mp.to_csv(f"{DER}/t3_coincidencia_periodo.csv", index=False)
log("Coincidencia por periodo:\n" + mp[["periodo", "N_total", "share_ambos", "tasa", "tasa_T", "tasa_noT", "tasa_coleT"]].to_string(index=False))

# resumen: total, cohortes 1985-2005, por calendario, y destino de los no coincidentes en T
bc = both[both["birth_year"].between(COH0, COH1)]
rows = []
def addrow(nombre, d):
    rows.append({"muestra": nombre, "N": len(d), "tasa": d.match.mean(),
                 "tasa_T": d.match[d.inT].mean(), "tasa_noT": d.match[~d.inT].mean(),
                 "tasa_coleT": d.match[d.inT_cole].mean(),
                 "share_res_T_entre_cole_T": d.inT[d.inT_cole].mean(),
                 "no_coinc_T_que_van_a_otro_T": d.inT_cole[d.inT & (d.match == 0)].mean(),
                 "no_coinc_T_que_van_a_noT": 1 - d.inT_cole[d.inT & (d.match == 0)].mean()})
addrow("todos los periodos", both)
addrow(f"cohortes {COH0}-{COH1}", bc)
addrow("2005-1 a 2012-1", both[both.year.lt(2012) | ((both.year == 2012) & (both["sem"] == 1))])
addrow("2012-2 a 2022-2", both[both.year.gt(2012) | ((both.year == 2012) & (both["sem"] == 2))])
addrow("calendario A (sem 2)", both[both["sem"] == 2]); addrow("calendario B (sem 1)", both[both["sem"] == 1])
mres = pd.DataFrame(rows); mres.to_csv(f"{DER}/t3_coincidencia_resumen.csv", index=False)
log("Coincidencia resumen:\n" + mres.to_string(index=False))
del both, bc

# =====================================================================================
# 3. Edad al examen por cohorte; rezago (> 19) en T vs resto
# =====================================================================================
ag = coh[coh["age_at_exam"].notna()]
def _ages(s):
    q = s.quantile([0.10, 0.25, 0.50, 0.75, 0.90])
    return pd.Series({"N": len(s), "edad_media": s.mean(), "p10": q[0.10], "p25": q[0.25], "p50": q[0.50],
                      "p75": q[0.75], "p90": q[0.90], "share_gt19": (s > 19).mean(), "share_ge21": (s >= 21).mean(),
                      "share_lt16": (s < 16).mean()})
age_tab = ag.groupby(["cohort", "inT"])["age_at_exam"].apply(_ages).unstack().reset_index()
age_tab["grupo"] = np.where(age_tab["inT"], "T", "resto"); age_tab = age_tab.drop(columns="inT")
age_tab["N"] = age_tab["N"].astype(int)
age_tab.to_csv(f"{DER}/t3_edad_cohorte.csv", index=False)
fullage = ag[ag.cohort.between(FULL0, FULL1)]
rez_T = fullage.loc[fullage.inT, "rezago"].mean(); rez_C = fullage.loc[~fullage.inT, "rezago"].mean()
# rezago por municipio T (cohortes plenas) para ver la dispersion
rez_m = fullage[fullage.inT].groupby("muni_res", observed=True)["rezago"].agg(["mean", "size"])
rez_m = rez_m[rez_m["size"] >= 100]
log(f"Rezago (edad>19) cohortes {FULL0}-{FULL1}: T {pct(rez_T)} vs resto {pct(rez_C)}; "
    f"por municipio T (n>=100): mediana {pct(rez_m['mean'].median())}, p90 {pct(rez_m['mean'].quantile(.9))}")
log("Edad por cohorte (T):\n" + age_tab[age_tab.grupo == "T"][["cohort", "N", "edad_media", "p10", "p50", "p90", "share_gt19"]].to_string(index=False))

# =====================================================================================
# 4. ICC y MDE
# =====================================================================================
def icc_anova(y, g):
    """ICC (estimador ANOVA de un factor) de y con grupos g (codigos enteros)."""
    y = np.asarray(y, dtype=np.float64); g = np.asarray(g)
    N = len(y); gm = y.mean()
    ng = np.bincount(g); keep = ng > 0; G = int(keep.sum())
    sg = np.bincount(g, weights=y); mg = np.where(ng > 0, sg / np.maximum(ng, 1), 0.0)
    ssb = float((ng * (mg - gm) ** 2).sum()); ssw = float(((y - mg[g]) ** 2).sum())
    msb = ssb / (G - 1); msw = ssw / (N - G)
    n0 = (N - (ng ** 2).sum() / N) / (G - 1)
    return (msb - msw) / (msb + (n0 - 1) * msw), G, N / G, n0

def demean_fe(y, f1, f2, tol=1e-9, maxit=500):
    """Residuo de y respecto a dos conjuntos de efectos fijos (proyecciones alternantes)."""
    r = y.astype(np.float64).copy()
    for it in range(maxit):
        r_old = r.copy()
        m1 = np.bincount(f1, weights=r) / np.bincount(f1); r -= m1[f1]
        m2 = np.bincount(f2, weights=r) / np.bincount(f2); r -= m2[f2]
        if np.max(np.abs(r - r_old)) < tol: break
    return r, it + 1

def mde_two_groups(sig2, n1, m1, n2, m2, rho):
    """MDE (80 %, 5 %) de la diferencia de medias entre dos grupos con efecto de diseno de Moulton/Kish."""
    v = sig2 * ((1 + (m1 - 1) * rho) / n1 + (1 + (m2 - 1) * rho) / n2)
    return Z80 * np.sqrt(v)

pw = coh[coh["score_z"].notna()].copy()
pw["mcode"] = pw["muni_res"].cat.codes.astype(np.int64)
sig2_all = float(pw["score_z"].var())
icc_rows, mde_rows = [], []

# 4a. ICC por municipio (bruta y neta de EF de cohorte) en varias muestras
for nombre, d in [(f"todas, cohortes {COH0}-{COH1}", pw), (f"T, cohortes {COH0}-{COH1}", pw[pw.inT]),
                  (f"resto, cohortes {COH0}-{COH1}", pw[~pw.inT]), (f"todas, cohortes {FULL0}-{FULL1}", pw[pw.cohort.between(FULL0, FULL1)])]:
    codes = pd.factorize(d["mcode"])[0]
    r_raw, G, mbar, n0 = icc_anova(d["score_z"].values, codes)
    ydm = d["score_z"].values - d.groupby("cohort")["score_z"].transform("mean").values
    r_c, _, _, _ = icc_anova(ydm, codes)
    icc_rows.append({"muestra": nombre, "nivel": "municipio de residencia", "N": len(d), "G": G, "tam_medio": mbar,
                     "var_score": float(d["score_z"].var()), "ICC_bruta": r_raw, "ICC_neta_EF_cohorte": r_c})
    log(f"ICC {nombre}: N={len(d):,} G={G} m={mbar:.0f} var={d['score_z'].var():.3f} ICC bruta={r_raw:.4f} neta cohorte={r_c:.4f}")

rho_m = icc_rows[0]["ICC_neta_EF_cohorte"]; rho_m_raw = icc_rows[0]["ICC_bruta"]

# 4b. MDE (a): tratados vs no tratados, errores agrupados por municipio
def grp_stats(d):
    G = d["mcode"].nunique(); N = len(d); return N, G, N / G
for nombre, d, nco in [(f"cohortes {COH0}-{COH1} (acumuladas)", pw, COH1 - COH0 + 1),
                       (f"cohortes {FULL0}-{FULL1} (acumuladas)", pw[pw.cohort.between(FULL0, FULL1)], FULL1 - FULL0 + 1)]:
    NT, GT, mT = grp_stats(d[d.inT]); NC, GC, mC = grp_stats(d[~d.inT])
    s2 = float(d["score_z"].var())
    for rho_lab, rho in [("ICC neta de cohorte", rho_m), ("ICC bruta", rho_m_raw)]:
        mde = mde_two_groups(s2, NT, mT, NC, mC, rho)
        mde1 = mde_two_groups(s2, NT / nco, mT / nco, NC / nco, mC / nco, rho)   # una sola cohorte
        mde_rows.append({"contraste": "(a) T vs resto, cluster municipio", "muestra": nombre, "rho_usada": rho_lab, "rho": rho,
                         "sigma2": s2, "N1": NT, "G1": GT, "m1": mT, "N2": NC, "G2": GC, "m2": mC,
                         "MDE_acumulado": mde, "MDE_una_cohorte": mde1,
                         "MDE_limite_solo_clusters": Z80 * np.sqrt(s2 * rho * (1 / GT + 1 / GC))})
        log(f"MDE (a) {nombre} [{rho_lab} rho={rho:.4f}]: NT={NT:,} GT={GT} mT={mT:.0f} | NC={NC:,} GC={GC} mC={mC:.0f} "
            f"-> MDE={mde:.4f} DE (una cohorte: {mde1:.4f}; limite solo clusters: {Z80*np.sqrt(s2*rho*(1/GT+1/GC)):.4f})")

# 4c. MDE (b): contraste de ventanas de cohortes dentro de T, EF municipio + cohorte x dpto
tw = pw[pw.inT & pw.cohort.between(W1[0], W2[1]) & pw["dpto_res"].notna()].copy()
f_m = pd.factorize(tw["mcode"])[0]
f_cd = pd.factorize(tw["cohort"].astype(str) + "_" + tw["dpto_res"].astype(str))[0]
resid, nit = demean_fe(tw["score_z"].values, f_m, f_cd)
tw["resid"] = resid
sig2_w = float(np.var(resid))
cell = pd.factorize(tw["mcode"].astype(str) + "_" + tw["cohort"].astype(str))[0]
rho_mc, Gc, mc_bar, _ = icc_anova(resid, cell)
# ICC de celda de los residuos con solo EF de municipio (sin absorber choques cohorte x dpto)
resid_m = tw["score_z"].values - tw.groupby("mcode")["score_z"].transform("mean").values
rho_mc_m, _, _, _ = icc_anova(resid_m, cell)
icc_rows.append({"muestra": f"T, cohortes {W1[0]}-{W2[1]}, residuo EF muni + cohorte x dpto", "nivel": "celda municipio x cohorte",
                 "N": len(tw), "G": Gc, "tam_medio": mc_bar, "var_score": sig2_w, "ICC_bruta": rho_mc, "ICC_neta_EF_cohorte": np.nan})
icc_rows.append({"muestra": f"T, cohortes {W1[0]}-{W2[1]}, residuo solo EF muni", "nivel": "celda municipio x cohorte",
                 "N": len(tw), "G": Gc, "tam_medio": mc_bar, "var_score": float(np.var(resid_m)), "ICC_bruta": rho_mc_m, "ICC_neta_EF_cohorte": np.nan})
log(f"Residualizacion T {W1[0]}-{W2[1]}: N={len(tw):,}, {nit} iteraciones, var resid={sig2_w:.4f} (bruta {tw.score_z.var():.4f}); "
    f"ICC celda muni x cohorte: {rho_mc:.4f} (solo EF muni: {rho_mc_m:.4f}); celdas={Gc}, tam medio={mc_bar:.0f}")

d1 = tw[tw.cohort.between(*W1)]; d2 = tw[tw.cohort.between(*W2)]
def cell_stats(d):
    N = len(d); C = (d["mcode"].astype(str) + "_" + d["cohort"].astype(str)).nunique(); return N, C, N / C
N1, C1, m1 = cell_stats(d1); N2, C2, m2 = cell_stats(d2)
for lab, rho, s2 in [("Moulton celda muni x cohorte (resid. EF muni + cohorte x dpto)", rho_mc, sig2_w),
                     ("Moulton celda muni x cohorte (resid. solo EF muni)", rho_mc_m, float(np.var(resid_m))),
                     ("iid dentro de municipio (cota inferior)", 0.0, sig2_w)]:
    mde = mde_two_groups(s2, N1, m1, N2, m2, rho)
    mde_rows.append({"contraste": f"(b) T: cohortes {W1[0]}-{W1[1]} vs {W2[0]}-{W2[1]}", "muestra": "T, EF municipio + cohorte x dpto",
                     "rho_usada": lab, "rho": rho, "sigma2": s2, "N1": N1, "G1": C1, "m1": m1, "N2": N2, "G2": C2, "m2": m2,
                     "MDE_acumulado": mde, "MDE_una_cohorte": np.nan, "MDE_limite_solo_clusters": Z80 * np.sqrt(s2 * rho * (1 / C1 + 1 / C2))})
    log(f"MDE (b) [{lab}]: N1={N1:,} celdas={C1} m1={m1:.0f} | N2={N2:,} celdas={C2} m2={m2:.0f} -> MDE={mde:.4f} DE")

# 4d. comprobacion empirica: regresion dentro de T con EF municipio, dummy ventana 2001-05, errores agrupados por municipio
x = (tw["cohort"] >= W2[0]).astype(float).values
xd = x - tw.groupby("mcode")[["cohort"]].transform(lambda s: (s >= W2[0]).mean()).values[:, 0]
yd = tw["score_z"].values - tw.groupby("mcode")["score_z"].transform("mean").values
sxx = float((xd ** 2).sum()); beta = float((xd * yd).sum() / sxx); e = yd - beta * xd
sc = pd.Series(xd * e).groupby(f_m).sum().values
se_cl = np.sqrt((sc ** 2).sum()) / sxx
G_cl = len(sc); se_cl *= np.sqrt(G_cl / (G_cl - 1) * (len(e) - 1) / (len(e) - 2))
mde_rows.append({"contraste": f"(b) T: cohortes {W1[0]}-{W1[1]} vs {W2[0]}-{W2[1]}", "muestra": "regresion EF municipio, cluster municipio (comprobacion)",
                 "rho_usada": "SE empirico agrupado por municipio", "rho": np.nan, "sigma2": float(np.var(e)), "N1": N1, "G1": G_cl, "m1": np.nan,
                 "N2": N2, "G2": G_cl, "m2": np.nan, "MDE_acumulado": Z80 * se_cl, "MDE_una_cohorte": np.nan, "MDE_limite_solo_clusters": np.nan})
log(f"Regresion EF muni, dummy {W2[0]}-{W2[1]}: beta={beta:.4f}, SE cluster muni={se_cl:.4f} (G={G_cl}) -> MDE={Z80*se_cl:.4f} DE")

# 4e. extra: placebo 'nacidas tras la salida municipal' vs nacidas 1-6 anios antes de la salida, dentro de T
tp = pw[pw.inT].copy(); tp["exit"] = tp["muni_res"].astype(str).map(exit_year).astype(float)
post = tp[tp.cohort > tp.exit]; pre = tp[(tp.cohort <= tp.exit - 1) & (tp.cohort >= tp.exit - 6)]
Np, Cp, mp_ = cell_stats(post); Nq, Cq, mq = cell_stats(pre)
mde_pl = mde_two_groups(sig2_w, Np, mp_, Nq, mq, rho_mc)
mde_rows.append({"contraste": "(b') T: nacidas tras la salida municipal vs nacidas 1-6 anios antes", "muestra": f"T, cohortes {COH0}-{COH1}",
                 "rho_usada": "Moulton celda muni x cohorte (resid. EF muni + cohorte x dpto)", "rho": rho_mc, "sigma2": sig2_w,
                 "N1": Np, "G1": Cp, "m1": mp_, "N2": Nq, "G2": Cq, "m2": mq, "MDE_acumulado": mde_pl, "MDE_una_cohorte": np.nan,
                 "MDE_limite_solo_clusters": Z80 * np.sqrt(sig2_w * rho_mc * (1 / Cp + 1 / Cq))})
log(f"Placebo post-salida: N_post={Np:,} celdas={Cp} | N_pre={Nq:,} celdas={Cq} -> MDE={mde_pl:.4f} DE; municipios con post: {post.muni_res.nunique()}")

# 4g. MDE empirico para regresores anclados a la salida municipal (variacion muni x cohorte, como en el diseno):
#     EF municipio + cohorte x dpto, errores agrupados por municipio. MDE = 2.8 * SE(beta).
def fe_cluster_mde(y, x, f1, f2, cl):
    yr, _ = demean_fe(y, f1, f2); xr, _ = demean_fe(x, f1, f2)
    sxx = float((xr ** 2).sum()); beta = float((xr * yr).sum() / sxx); e = yr - beta * xr
    sc = np.bincount(cl, weights=xr * e); G = int((np.bincount(cl) > 0).sum())
    se = np.sqrt((sc ** 2).sum()) / sxx * np.sqrt(G / (G - 1))
    return beta, se, Z80 * se, float(np.var(xr) / np.var(x)), G

te = pw[pw.inT & pw.cohort.between(FULL0, COH1) & pw["dpto_res"].notna()].copy()
te["exit"] = te["muni_res"].astype(str).map(exit_year).astype(float)
g_m = pd.factorize(te["mcode"])[0]
g_cd = pd.factorize(te["cohort"].astype(str) + "_" + te["dpto_res"].astype(str))[0]
yv = te["score_z"].values.astype(np.float64)
regs = [
    ("1[c >= salida-2]: expuestas a lo sumo in utero/0-2 (vs expuestas tambien a 3+)", (te["cohort"] >= te["exit"] - 2).astype(float).values),
    ("1[c > salida]: nacidas tras la salida municipal (placebo bajo H2)", (te["cohort"] > te["exit"]).astype(float).values),
    ("1[salida-5 <= c <= salida-3]: expuestas 0-2 y 3-5 pero no 6+ (vs resto)", te["cohort"].between(te["exit"] - 5, te["exit"] - 3).astype(float).values),
]
for lab, xv in regs:
    beta, se, mde_e, shx, G = fe_cluster_mde(yv, xv, g_m, g_cd, g_m)
    n1 = int(xv.sum()); c1 = int((te.loc[xv == 1, "mcode"].astype(str) + "_" + te.loc[xv == 1, "cohort"].astype(str)).nunique())
    mde_rows.append({"contraste": f"(b'') T: {lab}", "muestra": f"T, cohortes {FULL0}-{COH1}, EF municipio + cohorte x dpto, cluster municipio",
                     "rho_usada": "SE empirico agrupado por municipio", "rho": np.nan, "sigma2": np.nan, "N1": n1, "G1": c1,
                     "m1": shx, "N2": len(te) - n1, "G2": G, "m2": np.nan, "MDE_acumulado": mde_e, "MDE_una_cohorte": np.nan,
                     "MDE_limite_solo_clusters": np.nan})
    log(f"Regresion anclada a la salida [{lab}]: N1={n1:,} celdas1={c1} beta={beta:.4f} SE={se:.4f} (G={G}, var residual de X / var X = {shx:.3f}) -> MDE={mde_e:.4f} DE")
# el mismo contraste de ventanas 1995-2000 vs 2001-2005 con cluster municipio pero solo EF municipio ya esta en 4d.

# 4f. MDE por tamano de celda tipico: cuantos municipios T aportan celdas con >=30 y el MDE de un contraste 'una celda vs una celda' tipico
icc = pd.DataFrame(icc_rows); icc.to_csv(f"{DER}/t3_icc.csv", index=False)
mde = pd.DataFrame(mde_rows)
mde["nota"] = np.where(mde["contraste"].str.startswith("(b'')"), "N1/G1 = obs y celdas con X=1; m1 = var residual de X / var X; G2 = clusters (municipios)", "")
mde.to_csv(f"{DER}/t3_potencia.csv", index=False)
log("Tabla de potencia:\n" + mde[["contraste", "muestra", "rho_usada", "rho", "N1", "G1", "N2", "G2", "MDE_acumulado", "MDE_una_cohorte"]].to_string(index=False))

# =====================================================================================
# 5. Proxy de margen extensivo: indice de evaluados por cohorte, T vs resto
# =====================================================================================
ext = cnt.groupby(["in_T", "cohort"]).agg(N=("N", "sum"), N_ajust=("N_ajust", "sum"), N_le19=("N_edad_le19", "sum")).reset_index()
ext["grupo"] = np.where(ext["in_T"], "T", "resto")
def _index(d, col, b0, b1):
    base = d.loc[d.cohort.between(b0, b1), col].mean(); return 100 * d[col] / base
parts = []
for g, d in ext.groupby("grupo"):
    d = d.sort_values("cohort").copy()
    d["idx_1985_1990"] = _index(d, "N", 1985, 1990)
    d["idx_ajust_1985_1990"] = _index(d, "N_ajust", 1985, 1990)
    d["idx_1988_1992"] = _index(d, "N", 1988, 1992)
    d["idx_ajust_1988_1992"] = _index(d, "N_ajust", 1988, 1992)
    d["idx_le19_1989_1993"] = _index(d, "N_le19", 1989, 1993)
    parts.append(d)
ext = pd.concat(parts)
wide = ext.pivot(index="cohort", columns="grupo", values=["idx_1985_1990", "idx_ajust_1985_1990", "idx_1988_1992", "idx_ajust_1988_1992", "idx_le19_1989_1993"])
ratio = pd.DataFrame({"cohort": wide.index,
                      "ratio_T_resto_1985_1990": wide[("idx_1985_1990", "T")].values / wide[("idx_1985_1990", "resto")].values,
                      "ratio_T_resto_ajust_1985_1990": wide[("idx_ajust_1985_1990", "T")].values / wide[("idx_ajust_1985_1990", "resto")].values,
                      "ratio_T_resto_ajust_1988_1992": wide[("idx_ajust_1988_1992", "T")].values / wide[("idx_ajust_1988_1992", "resto")].values,
                      "ratio_T_resto_le19_1989_1993": wide[("idx_le19_1989_1993", "T")].values / wide[("idx_le19_1989_1993", "resto")].values})
ext = ext.drop(columns="in_T").merge(ratio, on="cohort", how="left")
ext.to_csv(f"{DER}/t3_margen_extensivo.csv", index=False)
log("Margen extensivo (indices):\n" + ext[["grupo", "cohort", "N", "N_ajust", "idx_1985_1990", "idx_ajust_1988_1992", "idx_le19_1989_1993", "ratio_T_resto_ajust_1988_1992"]].to_string(index=False))

# =====================================================================================
# Figuras
# =====================================================================================
def shade_trunc(ax):
    ax.axvspan(1998.5, 2001.5, color=GREY, alpha=0.12, lw=0)

# Fig 1: margen extensivo
eT = ext[ext.grupo == "T"].sort_values("cohort"); eC = ext[ext.grupo == "resto"].sort_values("cohort")
fig, axs = plt.subplots(1, 3, figsize=(7.5, 2.5))
ax = axs[0]
ax.plot(eT.cohort, eT.idx_1985_1990, color=BLUE, label="T (452 municipios)")
ax.plot(eC.cohort, eC.idx_1985_1990, color=ORANGE, label="resto")
ax.plot(eT.cohort, eT.idx_ajust_1985_1990, color=BLUE, ls="--", lw=0.9, label="T, 2017-2 imputado")
ax.plot(eC.cohort, eC.idx_ajust_1985_1990, color=ORANGE, ls="--", lw=0.9, label="resto, 2017-2 imputado")
shade_trunc(ax); ax.axhline(100, color=GREY, lw=0.5, ls=":")
ax.set_title("A. Índice, base 1985-90 = 100"); ax.set_xlabel("Cohorte de nacimiento"); ax.set_ylabel("Índice")
ax.legend(loc="lower right")
ax = axs[1]
ax.plot(eT.cohort, eT.idx_ajust_1988_1992, color=BLUE, label="T")
ax.plot(eC.cohort, eC.idx_ajust_1988_1992, color=ORANGE, label="resto")
ax.plot(eT.cohort, eT.idx_le19_1989_1993, color=BLUE, ls=":", lw=1.0, label="T, edad ≤ 19")
ax.plot(eC.cohort, eC.idx_le19_1989_1993, color=ORANGE, ls=":", lw=1.0, label="resto, edad ≤ 19")
shade_trunc(ax); ax.axhline(100, color=GREY, lw=0.5, ls=":")
ax.set_title("B. Índice, base 1988-92 = 100"); ax.set_xlabel("Cohorte de nacimiento")
ax.legend(loc="lower right", handlelength=1.6)
ax = axs[2]
ax.plot(ratio.cohort, ratio.ratio_T_resto_ajust_1988_1992, color=GREEN, label="base 1988-92, 2017-2 imputado")
ax.plot(ratio.cohort, ratio.ratio_T_resto_le19_1989_1993, color=GREEN, ls=":", label="solo edad ≤ 19, base 1989-93")
shade_trunc(ax); ax.axhline(1, color=GREY, lw=0.5, ls=":")
ax.set_title("C. Cociente índice T / índice resto"); ax.set_xlabel("Cohorte de nacimiento"); ax.set_ylabel("Cociente")
ax.legend(loc="lower right", handlelength=1.6)
for a in axs: a.set_xlim(COH0 - 0.5, COH1 + 0.5)
fig.text(0.005, 0.005, "Franja gris: cohortes 1999-2001, afectadas por el archivo truncado 2017-2 (73 mil de ~550 mil filas). Series de edad ≤ 19: base 1989-93.\n"
         "Cohortes 1985-1987 solo se observan a edades ≥ 18-20 (primer examen disponible: 2005-1).", fontsize=5.5, color=GREY, va="bottom")
fig.tight_layout(rect=(0, 0.06, 1, 1)); fig.savefig(f"{PROP}/figs_t3_margen_extensivo.pdf"); plt.close(fig)

# Fig 2: edad y rezago
aT = age_tab[age_tab.grupo == "T"].sort_values("cohort"); aC = age_tab[age_tab.grupo == "resto"].sort_values("cohort")
fig, axs = plt.subplots(1, 2, figsize=(5.6, 2.3))
ax = axs[0]
ax.plot(aT.cohort, aT.share_gt19, color=BLUE, label="T"); ax.plot(aC.cohort, aC.share_gt19, color=ORANGE, label="resto")
ax.axvspan(COH0 - 0.5, FULL0 - 0.5, color=GREY, alpha=0.12, lw=0); ax.axvspan(FULL1 + 0.5, COH1 + 0.5, color=GREY, alpha=0.12, lw=0)
ax.set_title("A. Fracción con edad al examen > 19 (rezago)"); ax.set_xlabel("Cohorte de nacimiento"); ax.set_ylabel("Fracción")
ax.set_ylim(0, 1); ax.legend(loc="upper right")
ax = axs[1]
ax.plot(aT.cohort, aT.p50, color=BLUE, label="T, mediana"); ax.plot(aC.cohort, aC.p50, color=ORANGE, label="resto, mediana")
ax.fill_between(aT.cohort, aT.p10, aT.p90, color=BLUE, alpha=0.12, lw=0, label="T, p10-p90")
ax.fill_between(aC.cohort, aC.p10, aC.p90, color=ORANGE, alpha=0.12, lw=0, label="resto, p10-p90")
ax.axvspan(COH0 - 0.5, FULL0 - 0.5, color=GREY, alpha=0.12, lw=0); ax.axvspan(FULL1 + 0.5, COH1 + 0.5, color=GREY, alpha=0.12, lw=0)
ax.set_title("B. Edad al examen por cohorte"); ax.set_xlabel("Cohorte de nacimiento"); ax.set_ylabel("Años"); ax.legend(loc="upper right")
for a in axs: a.set_xlim(COH0 - 0.5, COH1 + 0.5)
fig.text(0.005, 0.005, "Franjas grises: cohortes sin cobertura completa de las edades 16-19 (exámenes 2005-1 a 2022-2); su rezago está truncado por construcción.",
         fontsize=5.5, color=GREY)
fig.tight_layout(rect=(0, 0.03, 1, 1)); fig.savefig(f"{PROP}/figs_t3_edad_rezago.pdf"); plt.close(fig)

# Fig 3: coincidencia residencia = colegio por periodo
mp2 = mp.copy(); mp2["t"] = mp2.periodo.str[:4].astype(int) + np.where(mp2.periodo.str[4] == "2", 0.5, 0.0)
fig, ax = plt.subplots(figsize=(5.0, 2.6))
s2 = mp2[mp2.periodo.str[4] == "2"]; s1 = mp2[mp2.periodo.str[4] == "1"]
ax.plot(s2.t, s2.tasa_T, color=BLUE, marker="o", ms=2.5, label="T, calendario A (sem 2)")
ax.plot(s2.t, s2.tasa_noT, color=ORANGE, marker="o", ms=2.5, label="resto, calendario A")
ax.plot(s1.t, s1.tasa_T, color=BLUE, marker="s", ms=2.5, ls="--", lw=0.8, label="T, calendario B (sem 1)")
ax.plot(s1.t, s1.tasa_noT, color=ORANGE, marker="s", ms=2.5, ls="--", lw=0.8, label="resto, calendario B")
ax.set_ylim(0.4, 1.0); ax.set_xlabel("Año del examen"); ax.set_ylabel("Fracción muni_res = muni_cole")
ax.set_xticks(range(2005, 2023, 2))
ax.legend(loc="lower center", bbox_to_anchor=(0.5, 1.0), ncol=2, handlelength=2.2)
ax.axvline(2017.5, color=GREY, lw=0.5, ls=":"); ax.text(2017.6, 0.76, "2017-2 truncado", fontsize=5.5, color=GREY)
fig.tight_layout(); fig.savefig(f"{PROP}/figs_t3_coincidencia.pdf"); plt.close(fig)

# Fig 4: N por cohorte en T y numero de municipios T con >= 30
fig, axs = plt.subplots(1, 2, figsize=(5.8, 2.5))
ax = axs[0]
ax.bar(res.cohort, res.N_T / 1e3, color=BLUE, width=0.8, label="T, observado")
ax.plot(res.cohort, res.N_T_ajust_20172 / 1e3, color=GREY, lw=0.8, ls="--", marker=".", ms=3, label="T, 2017-2 imputado")
ax.plot(res.cohort, res.N_T_edad_le19 / 1e3, color=GREEN, lw=0.9, ls=":", label="T, edad ≤ 19")
ax.set_title("A. Evaluados por cohorte en T (miles)", pad=14); ax.set_xlabel("Cohorte de nacimiento"); ax.set_ylabel("Miles")
ax.legend(loc="lower center", bbox_to_anchor=(0.5, 0.985), ncol=3, handlelength=1.5, columnspacing=0.8)
ax = axs[1]
ax.plot(res.cohort, res.munis_T_ge30, color=BLUE, marker="o", ms=2.5, label="≥ 30 evaluados")
ax.plot(res.cohort, res.munis_T_ge100, color=GREEN, marker="o", ms=2.5, label="≥ 100 evaluados")
ax.plot(res.cohort, res.munis_T_con_evaluados, color=GREY, lw=0.8, ls="--", label="≥ 1 evaluado")
ax.axhline(452, color=GREY, lw=0.5, ls=":"); ax.text(COH0, 456, "452 municipios T", fontsize=5.5, color=GREY)
ax.set_ylim(0, 480); ax.set_title("B. Municipios T por tamaño de celda", pad=14); ax.set_xlabel("Cohorte de nacimiento"); ax.set_ylabel("Municipios")
ax.legend(loc="lower right")
for a in axs: a.set_xlim(COH0 - 0.6, COH1 + 0.6)
fig.tight_layout(); fig.savefig(f"{PROP}/figs_t3_N_cohorte_T.pdf"); plt.close(fig)

# =====================================================================================
# Numeros clave para el memo (json)
# =====================================================================================
import json
rf = res[res.cohort.between(FULL0, FULL1)]
key = {
    "share_T_todos_los_evaluados": share_T_all,
    "N_cohortes_1985_2005": int(len(coh)), "N_T_1985_2005": int(res.N_T.sum()), "N_noT_1985_2005": int(res.N_noT.sum()),
    "N_T_1988_2003": int(rf.N_T.sum()), "N_noT_1988_2003": int(rf.N_noT.sum()),
    "N_T_por_cohorte_1988_2003_media": float(rf.N_T.mean()), "munis_T_ge30_1988_2003_min_max": [int(rf.munis_T_ge30.min()), int(rf.munis_T_ge30.max())],
    "munis_T_ge30_todas_cohortes_1988_2003": nT16, "munis_T_sin_evaluados": int((tm.N_total_1988_2003 == 0).sum()),
    "mediana_N_muni_T_por_cohorte_1988_2003": float(rf.mediana_N_muni_T.median()),
    "coincidencia": mres.set_index("muestra")[["tasa", "tasa_T", "tasa_noT"]].to_dict("index"),
    "rezago_T_1988_2003": rez_T, "rezago_resto_1988_2003": rez_C,
    "icc": icc[["muestra", "ICC_bruta", "ICC_neta_EF_cohorte"]].to_dict("records"),
    "mde": mde[["contraste", "rho_usada", "MDE_acumulado", "MDE_una_cohorte"]].to_dict("records"),
    "placebo_munis_con_post": int(post.muni_res.nunique()),
    "ratio_T_resto_ajust_1988_1992": ratio.set_index("cohort")["ratio_T_resto_ajust_1988_1992"].round(3).to_dict(),
    "trunc_20172": chk.to_dict("records"),
}
with open(f"{DER}/t3_numeros_clave.json", "w") as f: json.dump(key, f, indent=1, default=float)
log("Listo.")
