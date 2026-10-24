#!/usr/bin/env python3
"""
t5_ruv_stayers.py -- T5 del PI: desplazamiento forzado (RUV, corte sep-2016) y muestra "stayer".

Uso:  python3 -I /home/user/JMP/code/analysis/t5_ruv_stayers.py

Insumos
  * data/raw/ruv/ruv_jngaravitoc/Reporte_Personas_Desplazados_por_Anio.xlsx   (RUV: año x municipio x expulsados/recibidos/declarados)
  * data/raw/poblacion/PANEL_CARACTERISTICAS_GENERALES_2024.dta             (Panel CEDE: pobl_tot DANE por municipio x año; README en la carpeta)
  * data/derived/cnmh_muni_month_victims.csv                                (CNMH: víctimas por municipio x mes x presunto responsable)
  * data/derived/t2_A_T1_muestra_T.csv                                      (452 municipios T, >=25 víctimas PARA 1997-2006)
  * data/derived/saber11_slim.parquet                                       (solo muni_res, para el peso de evaluados)

Salidas
  * data/derived/t5_ruv_expulsion_muni_anio.csv   expulsados por municipio x año 1997-2010 y acumulados
  * data/derived/t5_ruv_nacional_anual.csv        serie nacional 1984-2016 por tipo de víctima
  * data/derived/t5_poblacion_2005.csv            población 2005 por municipio y fuente del dato
  * data/derived/t5_muni_expulsion_dosis.csv      tabla maestra municipal: expulsión, población, tasa, dosis CNMH, T, stayer
  * data/derived/t5_correlaciones.csv             correlaciones tasa de expulsión vs dosis paramilitar
  * data/derived/t5_stayer_umbrales.csv           dosis retenida por umbral (5/10/15/20/30/50/100 %) y variantes
  * data/derived/t5_stayer_curva.csv              curva de retención de la dosis sobre una malla de umbrales
  * data/derived/t5_T_munis_expulsion.csv         los 451 municipios T con tasa y banderas stayer
  * data/derived/t5_top30_expulsion.csv           30 municipios con mayor expulsión acumulada (personas)
  * data/derived/t5_top30_tasa.csv                30 municipios con mayor tasa de expulsión acumulada
  * data/derived/t5_numeros_clave.json
  * scoping/proposal/fig6_desplazamiento_vs_dosis.pdf

Convenciones
  * Código DANE a 5 dígitos (el RUV trae 4 para dptos 05 y 08). Belén de Bajirá (27086, sin código DANE 2005) se funde en
    Riosucio, Chocó (27615) en RUV y CNMH. Códigos CNMH 'xx000', '00000' y 'EX*' (sin municipio) quedan fuera del
    denominador "con municipio válido" pero se reportan.
  * Expulsados = personas-evento del RUV (una persona desplazada dos veces cuenta dos), ambos tipos de víctima
    (conflicto armado + Sentencia C-280/Auto 119, estos últimos 1,3 % en 1997-2010); variante solo conflicto.
  * Población 2005 = pobl_tot DANE (proyecciones base Censo 2005, vía CEDE); si es 0 (municipios creados tras 2005) se usa
    retro_pobl_tot 2005 (base Censo 2018) o el primer año con población positiva.
  * Tasa de expulsión acumulada = expulsados 1997-2010 / población 2005. Stayer(u) = tasa < u.
"""
import os, re, json, time, warnings
warnings.filterwarnings("ignore")
import numpy as np
import pandas as pd
import pyarrow.parquet as pq
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
try:
    from scipy import stats as sps
except Exception:
    sps = None

pd.set_option("display.width", 250); pd.set_option("display.max_columns", 60); pd.set_option("display.max_rows", 200)

ROOT = "/home/user/JMP"
RUV = f"{ROOT}/data/raw/ruv/ruv_jngaravitoc/Reporte_Personas_Desplazados_por_Anio.xlsx"
POB = f"{ROOT}/data/raw/poblacion/PANEL_CARACTERISTICAS_GENERALES_2024.dta"
CNMH = f"{ROOT}/data/derived/cnmh_muni_month_victims.csv"
TFILE = f"{ROOT}/data/derived/t2_A_T1_muestra_T.csv"
PARQ = f"{ROOT}/data/derived/saber11_slim.parquet"
DER = f"{ROOT}/data/derived"; PROP = f"{ROOT}/scoping/proposal"
os.makedirs(DER, exist_ok=True); os.makedirs(PROP, exist_ok=True)

Y0, Y1 = 1997, 2010            # ventana de expulsión del PI
D0, D1 = 1997, 2006            # ventana de dosis paramilitar
RECODE = {"27086": "27615"}    # Belén de Bajirá -> Riosucio (Chocó)
THRESH = [0.05, 0.10, 0.15, 0.20, 0.30, 0.50, 1.00]

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
def valid_code(s):
    s = pd.Index(s).astype(str)
    return np.array([bool(re.fullmatch(r"\d{5}", c)) and not c.endswith("000") for c in s])

KEY = {}

# =====================================================================================
# 1. RUV: expulsados por municipio x año 1997-2010 y acumulado
# =====================================================================================
ruv = pd.read_excel(RUV, dtype={"CODIGO DANE": str})
ruv.columns = ["tipo", "ano", "cod", "depto", "municipio", "expulsados", "recibidos", "declarados"]
ruv["muni"] = ruv["cod"].str.strip().str.zfill(5).replace(RECODE)
ruv["tipo_c"] = np.where(ruv["tipo"].str.contains("conflicto", case=False), "conflicto", "c280_auto119")
assert ruv.groupby(["tipo_c", "ano", "cod"]).size().max() == 1
log(f"RUV: {len(ruv):,} filas, {ruv.muni.nunique()} códigos, años {ruv.ano.min()}-{ruv.ano.max()}; "
    f"tipos: {ruv.tipo_c.value_counts().to_dict()}")

nac = ruv.pivot_table(index="ano", columns="tipo_c", values=["expulsados", "recibidos", "declarados"], aggfunc="sum", fill_value=0)
nac.columns = [f"{a}_{b}" for a, b in nac.columns]
nac["expulsados_total"] = nac.filter(like="expulsados_").sum(axis=1)
nac["recibidos_total"] = nac.filter(like="recibidos_").sum(axis=1)
nac.to_csv(f"{DER}/t5_ruv_nacional_anual.csv")

w = ruv[ruv.ano.between(Y0, Y1)]
names = (ruv.sort_values("ano").groupby("muni")[["depto", "municipio"]].last())
pan = w.pivot_table(index="muni", columns="ano", values="expulsados", aggfunc="sum", fill_value=0)
pan.columns = [f"exp_{int(c)}" for c in pan.columns]
pan["exp_9710"] = pan.sum(axis=1)
pan["exp_9706"] = pan[[f"exp_{y}" for y in range(D0, D1 + 1)]].sum(axis=1)
pan["exp_9710_conflicto"] = w[w.tipo_c == "conflicto"].groupby("muni")["expulsados"].sum().reindex(pan.index).fillna(0).astype(int)
pan["rec_9710"] = w.groupby("muni")["recibidos"].sum().reindex(pan.index).fillna(0).astype(int)
pan["exp_8596"] = ruv[ruv.ano.between(1985, 1996)].groupby("muni")["expulsados"].sum().reindex(pan.index).fillna(0).astype(int)
pan["exp_1116"] = ruv[ruv.ano.between(2011, 2016)].groupby("muni")["expulsados"].sum().reindex(pan.index).fillna(0).astype(int)
pan = names.join(pan, how="right").reset_index().sort_values("muni")
pan.to_csv(f"{DER}/t5_ruv_expulsion_muni_anio.csv", index=False)
KEY["ruv_exp_9710_total"] = int(pan.exp_9710.sum()); KEY["ruv_exp_9710_conflicto"] = int(pan.exp_9710_conflicto.sum())
KEY["ruv_exp_9706_total"] = int(pan.exp_9706.sum())
log(f"Expulsados {Y0}-{Y1}: {KEY['ruv_exp_9710_total']:,} (solo conflicto {KEY['ruv_exp_9710_conflicto']:,}); "
    f"{D0}-{D1}: {KEY['ruv_exp_9706_total']:,}; pico {nac.expulsados_total.loc[1997:2010].idxmax()} "
    f"({nac.expulsados_total.loc[1997:2010].max():,})")

# =====================================================================================
# 2. Población 2005 (DANE vía Panel CEDE)
# =====================================================================================
cede = pd.read_stata(POB, columns=["codmpio", "coddepto", "ano", "pobl_tot", "retro_pobl_tot", "municipio", "depto"],
                     convert_categoricals=False)
cede["muni"] = cede.codmpio.astype(int).astype(str).str.zfill(5)
cede["ano"] = cede.ano.astype(int)
p05 = cede[cede.ano == 2005].set_index("muni")
pop = pd.DataFrame({"depto_cede": p05.depto, "municipio_cede": p05.municipio,
                    "pobl_tot_2005": p05.pobl_tot.astype(float), "retro_pobl_tot_2005": p05.retro_pobl_tot.astype(float)})
pop["pop2005"] = pop.pobl_tot_2005.where(pop.pobl_tot_2005 > 0)
pop["pop_src"] = np.where(pop.pop2005.notna(), "pobl_tot_2005", "")
m = pop.pop2005.isna() & (pop.retro_pobl_tot_2005 > 0)
pop.loc[m, "pop2005"] = pop.loc[m, "retro_pobl_tot_2005"]; pop.loc[m, "pop_src"] = "retro_pobl_tot_2005"
for mu in pop.index[pop.pop2005.isna()]:
    s = cede[(cede.muni == mu) & (cede.pobl_tot > 0)].sort_values("ano")
    if len(s):
        pop.loc[mu, "pop2005"] = float(s.pobl_tot.iloc[0]); pop.loc[mu, "pop_src"] = f"pobl_tot_{int(s.ano.iloc[0])}"
pop.index.name = "muni"
pop.reset_index().to_csv(f"{DER}/t5_poblacion_2005.csv", index=False)
KEY["pop2005_total"] = float(pop.pop2005.sum()); KEY["pop2005_n_munis"] = int(pop.pop2005.notna().sum())
KEY["pop2005_src"] = pop.pop_src.value_counts().to_dict()
log(f"Población 2005: {KEY['pop2005_total']:,.0f} en {KEY['pop2005_n_munis']} municipios; fuentes {KEY['pop2005_src']}; "
    f"retro 2005 total {pop.retro_pobl_tot_2005.sum():,.0f}")

# =====================================================================================
# 3. CNMH: dosis paramilitar 1997-2006 por municipio
# =====================================================================================
cn = pd.read_csv(CNMH, dtype={"muni": str})
cn["muni"] = cn.muni.replace(RECODE)
dose = cn[cn.year.between(D0, D1)].groupby("muni")[["PARA", "GUE", "EST", "POSD", "NI"]].sum()
dose["TOT"] = dose.sum(axis=1)
dose_valid = valid_code(dose.index)
KEY["para_9706_all"] = int(dose.PARA.sum()); KEY["para_9706_valid_muni"] = int(dose.PARA[dose_valid].sum())
KEY["para_9706_sin_municipio"] = int(dose.PARA[~dose_valid].sum())
log(f"CNMH PARA {D0}-{D1}: {KEY['para_9706_all']:,} víctimas; con municipio válido {KEY['para_9706_valid_muni']:,} "
    f"({KEY['para_9706_sin_municipio']} sin municipio/exterior); municipios con PARA>0: {(dose.PARA[dose_valid]>0).sum()}")

T = pd.read_csv(TFILE, dtype={"muni": str})
T["muni"] = T.muni.replace(RECODE)
T = T[valid_code(T.muni)]
KEY["n_T"] = int(T.muni.nunique())
log(f"T efectivo: {KEY['n_T']} municipios (excluido 47000 'SIN INFORMACION')")

# Saber 11: evaluados por municipio de residencia (peso para la muestra)
sab = pq.read_table(PARQ, columns=["muni_res"]).column("muni_res").to_pandas().dropna().astype(str).str.zfill(5)
n_sab = sab.replace(RECODE).value_counts().rename("n_saber_0522")
del sab
log(f"Saber 11: {int(n_sab.sum()):,} evaluados con municipio de residencia en {len(n_sab)} códigos")

# =====================================================================================
# 4. Tabla maestra y correlaciones
# =====================================================================================
M = pop[["depto_cede", "municipio_cede", "pop2005", "pop_src", "retro_pobl_tot_2005"]].copy()
M = M.join(pan.set_index("muni")[["exp_9710", "exp_9706", "exp_9710_conflicto", "rec_9710", "exp_8596", "exp_1116"]], how="left")
M = M.join(dose[["PARA", "GUE", "EST", "POSD", "NI", "TOT"]].rename(columns=lambda c: f"{c}_9706"), how="left")
M = M.join(n_sab, how="left")
for c in [c for c in M.columns if c.startswith(("exp_", "rec_")) or c.endswith("_9706") or c.startswith("n_saber")]:
    M[c] = M[c].fillna(0).astype(int)
M["in_T"] = M.index.isin(T.muni)
M = M.join(T.set_index("muni")[["exit_year", "entry_year", "para_9706"]].rename(columns={"para_9706": "para_9706_T1"}), how="left")
# La dosis de T1 (para_9706) incluye víctimas con año pero sin mes; el panel municipio x mes las excluye. Brecha pequeña:
gapT = M.loc[M.in_T, "para_9706_T1"].sum() / M.loc[M.in_T, "PARA_9706"].sum() - 1
KEY["dosis_T1_vs_panel_mensual_gap"] = float(gapT)
KEY["dosis_T1_sum_T"] = int(M.loc[M.in_T, "para_9706_T1"].sum()); KEY["dosis_panel_sum_T"] = int(M.loc[M.in_T, "PARA_9706"].sum())
log(f"Dosis en T: T1 (con víctimas sin mes) {KEY['dosis_T1_sum_T']:,} vs panel mensual {KEY['dosis_panel_sum_T']:,} (brecha {pct(gapT,2)}); "
    f"se usa el panel mensual para todo el universo")
assert abs(gapT) < 0.03, "dosis T1 vs panel mensual difieren más de 3%"
M["rate_9710"] = M.exp_9710 / M.pop2005
M["rate_9706"] = M.exp_9706 / M.pop2005
M["rate_9710_conflicto"] = M.exp_9710_conflicto / M.pop2005
M["rate_9710_retro"] = M.exp_9710 / M.retro_pobl_tot_2005.where(M.retro_pobl_tot_2005 > 0)
M["para_per_1000"] = M.PARA_9706 / M.pop2005 * 1000
M["rec_rate_9710"] = M.rec_9710 / M.pop2005
for u in THRESH:
    M[f"stayer_{int(round(u*100)):03d}"] = M.rate_9710 < u
M.index.name = "muni"
# cobertura: dosis/expulsados fuera del universo CEDE
lost_dose = dose.PARA[dose_valid & ~dose.index.isin(M.index)].sum()
lost_exp = pan.loc[~pan.muni.isin(M.index), "exp_9710"].sum()
KEY["para_valid_fuera_universo"] = int(lost_dose); KEY["exp_9710_fuera_universo"] = int(lost_exp)
log(f"Universo: {len(M)} municipios; dosis PARA con municipio válido fuera del universo: {lost_dose}; expulsados fuera: {lost_exp}")
M.reset_index().to_csv(f"{DER}/t5_muni_expulsion_dosis.csv", index=False)

# descriptivos de la tasa
desc = {}
for name, sub in [("todos", M), ("T", M[M.in_T]), ("no_T", M[~M.in_T])]:
    r = sub.rate_9710
    desc[name] = {"n": int(len(sub)), "mediana": float(r.median()), "p25": float(r.quantile(.25)), "p75": float(r.quantile(.75)),
                  "media_pond_dosis": float(np.average(r, weights=sub.PARA_9706)) if sub.PARA_9706.sum() > 0 else np.nan,
                  "media_pond_pob": float(np.average(r, weights=sub.pop2005)),
                  "share_ge_10": float((r >= .10).mean()), "share_ge_30": float((r >= .30).mean()), "share_gt_100": float((r > 1).mean())}
KEY["tasa_desc"] = desc
log("Tasa acumulada 1997-2010:", {k: {kk: (round(vv, 3) if isinstance(vv, float) else vv) for kk, vv in v.items()} for k, v in desc.items()})

def corr_row(sub, x, y, label, sample):
    d = sub[[x, y]].replace([np.inf, -np.inf], np.nan).dropna()
    out = {"muestra": sample, "x": x, "y": y, "n": len(d), "pearson": d[x].corr(d[y]), "spearman": d[x].corr(d[y], method="spearman")}
    if sps is not None and len(d) > 3:
        out["p_pearson"] = sps.pearsonr(d[x], d[y])[1]; out["p_spearman"] = sps.spearmanr(d[x], d[y])[1]
    out["nota"] = label
    return out

M["log_rate_9710"] = np.log1p(100 * M.rate_9710)
M["log_PARA"] = np.log1p(M.PARA_9706)
M["log_para_per_1000"] = np.log1p(M.para_per_1000)
rows = []
for sname, sub in [("todos (1122)", M), ("T (451)", M[M.in_T]), ("PARA>0", M[M.PARA_9706 > 0])]:
    rows.append(corr_row(sub, "PARA_9706", "rate_9710", "víctimas PARA 1997-2006 vs tasa de expulsión 1997-2010", sname))
    rows.append(corr_row(sub, "para_per_1000", "rate_9710", "víctimas PARA por 1.000 hab. vs tasa", sname))
    rows.append(corr_row(sub, "log_PARA", "log_rate_9710", "log1p víctimas vs log1p tasa (%)", sname))
    rows.append(corr_row(sub, "log_para_per_1000", "log_rate_9710", "log1p víctimas/1.000 vs log1p tasa (%)", sname))
    rows.append(corr_row(sub, "GUE_9706", "rate_9710", "víctimas guerrilla 1997-2006 vs tasa (comparación)", sname))
    rows.append(corr_row(sub, "PARA_9706", "rate_9706", "víctimas PARA vs tasa 1997-2006", sname))
CORR = pd.DataFrame(rows)
CORR.to_csv(f"{DER}/t5_correlaciones.csv", index=False)
print(CORR.round(3).to_string())
KEY["corr"] = {f"{r.muestra}|{r.x}|{r.y}": {"pearson": round(r.pearson, 3), "spearman": round(r.spearman, 3), "n": int(r.n)} for r in CORR.itertuples()}

# =====================================================================================
# 5. Muestra stayer por umbral
# =====================================================================================
def retention(rate, u, sub=M):
    s = sub[rate] < u
    sT = s & sub.in_T
    return {
        "n_munis": int(s.sum()), "n_T": int(sT.sum()),
        "share_munis": float(s.mean()), "share_T_munis": float(sT.sum() / sub.in_T.sum()),
        "share_pob": float(sub.pop2005[s].sum() / sub.pop2005.sum()),
        "share_saber": float(sub.n_saber_0522[s].sum() / sub.n_saber_0522.sum()),
        "para_dentro": int(sub.PARA_9706[s].sum()),
        "share_dosis_PARA": float(sub.PARA_9706[s].sum() / KEY["para_9706_valid_muni"]),
        "share_dosis_PARA_total": float(sub.PARA_9706[s].sum() / KEY["para_9706_all"]),
        "share_dosis_PARA_en_T": float(sub.PARA_9706[sT].sum() / sub.PARA_9706[sub.in_T].sum()),
        "share_dosis_GUE": float(sub.GUE_9706[s].sum() / sub.GUE_9706.sum()),
        "share_dosis_TOT": float(sub.TOT_9706[s].sum() / sub.TOT_9706.sum()),
    }
rows = []
for var, rate in [("principal: exp 1997-2010 / pob 2005", "rate_9710"),
                  ("ventana de dosis: exp 1997-2006 / pob 2005", "rate_9706"),
                  ("solo víctimas de conflicto armado", "rate_9710_conflicto"),
                  ("pob 2005 retroproyectada (base 2018)", "rate_9710_retro")]:
    for u in THRESH:
        rows.append({"variante": var, "tasa": rate, "umbral": u, **retention(rate, u)})
# variante sin Medellín (la ciudad con más dosis) para ver la dependencia
sub2 = M.drop(index="05001")
for u in THRESH:
    r = retention("rate_9710", u, sub2)
    r["share_dosis_PARA"] = sub2.PARA_9706[sub2.rate_9710 < u].sum() / sub2.PARA_9706[valid_code(sub2.index)].sum()
    rows.append({"variante": "principal sin Medellín (dosis sin Medellín)", "tasa": "rate_9710", "umbral": u, **r})
UMB = pd.DataFrame(rows)
UMB.to_csv(f"{DER}/t5_stayer_umbrales.csv", index=False)
print(UMB[UMB.variante.str.startswith("principal:")].round(3).to_string())

grid = np.round(np.exp(np.linspace(np.log(0.005), np.log(5), 120)), 4)
CUR = pd.DataFrame([{"umbral": u, **retention("rate_9710", u)} for u in grid])
CUR.to_csv(f"{DER}/t5_stayer_curva.csv", index=False)

# umbral al que se alcanzan 30 % y 50 % de la dosis
def thr_for(share):
    ok = CUR[CUR.share_dosis_PARA >= share]
    return float(ok.umbral.iloc[0]) if len(ok) else np.nan
KEY["umbral_para_30pct_dosis"] = thr_for(.30); KEY["umbral_para_50pct_dosis"] = thr_for(.50); KEY["umbral_para_15pct_dosis"] = thr_for(.15)

main10 = retention("rate_9710", .10); main05 = retention("rate_9710", .05); main20 = retention("rate_9710", .20); main30 = retention("rate_9710", .30)
KEY["stayer"] = {"05": main05, "10": main10, "20": main20, "30": main30}
r10 = main10["share_dosis_PARA"]
KEY["share_dosis_T1_en_T_stayer10"] = float(M.para_9706_T1[M.in_T & M.stayer_010].sum() / M.para_9706_T1[M.in_T].sum())
KEY["veredicto"] = "APROBADO" if r10 >= .30 else ("LETAL" if r10 < .15 else "ZONA GRIS")
log(f"Stayer <10%: {main10['n_munis']} municipios ({main10['n_T']} T), retiene {pct(r10)} de la dosis PARA "
    f"(denominador con municipio válido), {pct(main10['share_dosis_PARA_en_T'])} de la dosis en T, {pct(main10['share_pob'])} de la población, "
    f"{pct(main10['share_saber'])} de los evaluados -> {KEY['veredicto']}")

# T con banderas
TT = M[M.in_T].sort_values("PARA_9706", ascending=False).reset_index()
TT = TT[["muni", "municipio_cede", "depto_cede", "pop2005", "exp_9710", "exp_9706", "rate_9710", "rate_9706", "PARA_9706", "para_per_1000",
         "GUE_9706", "exit_year", "entry_year", "n_saber_0522"] + [c for c in TT.columns if c.startswith("stayer_")]]
TT["share_dosis_T_acum"] = TT.PARA_9706.cumsum() / TT.PARA_9706.sum()
TT.to_csv(f"{DER}/t5_T_munis_expulsion.csv", index=False)
# dosis de T que se pierde, por municipio (los 15 mayores)
lostT = TT[~TT.stayer_010].head(15)[["muni", "municipio_cede", "depto_cede", "PARA_9706", "rate_9710", "pop2005"]]
print("Mayores dosis de T fuera de la muestra stayer <10%:\n", lostT.round(3).to_string())
KEY["T_fuera_stayer10_top"] = lostT.to_dict("records")
inT = TT[TT.stayer_010].head(15)[["muni", "municipio_cede", "depto_cede", "PARA_9706", "rate_9710", "pop2005"]]
print("Mayores dosis dentro de la muestra stayer <10%:\n", inT.round(3).to_string())
KEY["T_dentro_stayer10_top"] = inT.to_dict("records")

# =====================================================================================
# 6. Top 30 por expulsión acumulada (personas) y por tasa
# =====================================================================================
cols = ["muni", "municipio_cede", "depto_cede", "exp_9710", "pop2005", "rate_9710", "PARA_9706", "para_per_1000", "GUE_9706", "TOT_9706",
        "in_T", "entry_year", "exit_year", "rec_9710", "exp_8596", "exp_1116"]
top_exp = M.reset_index().sort_values("exp_9710", ascending=False).head(30)[cols].reset_index(drop=True)
top_exp.index = top_exp.index + 1; top_exp.index.name = "rank"
top_exp.to_csv(f"{DER}/t5_top30_expulsion.csv")
top_rate = M.reset_index().sort_values("rate_9710", ascending=False).head(30)[cols].reset_index(drop=True)
top_rate.index = top_rate.index + 1; top_rate.index.name = "rank"
top_rate.to_csv(f"{DER}/t5_top30_tasa.csv")
print("Top 30 por expulsión acumulada:\n", top_exp.round(3).to_string())
KEY["top30_exp_share_exp"] = float(top_exp.exp_9710.sum() / M.exp_9710.sum())
KEY["top30_exp_share_dosis"] = float(top_exp.PARA_9706.sum() / KEY["para_9706_valid_muni"])
KEY["top30_exp_n_T"] = int(top_exp.in_T.sum())
KEY["top30_exp_n_stayer10"] = int((top_exp.rate_9710 < .10).sum())
log(f"Top 30 expulsión: {pct(KEY['top30_exp_share_exp'])} de los expulsados, {pct(KEY['top30_exp_share_dosis'])} de la dosis PARA, "
    f"{KEY['top30_exp_n_T']} en T, {KEY['top30_exp_n_stayer10']} con tasa <10%")

# =====================================================================================
# 7. Figura 6
# =====================================================================================
fig, axes = plt.subplots(1, 3, figsize=(7.4, 2.55))
P = M[(M.PARA_9706 > 0) & (M.exp_9710 > 0)].copy()
n_drop = len(M) - len(P)
for ax, xcol, xlab in [(axes[0], "PARA_9706", "Víctimas paramilitares 1997-2006 (CNMH)"),
                       (axes[1], "para_per_1000", "Víctimas paramilitares por 1.000 hab. (2005)")]:
    nt = P[~P.in_T]; t = P[P.in_T]
    ax.scatter(nt[xcol], 100 * nt.rate_9710, s=5, c=GREY, alpha=.45, linewidths=0, label=f"resto (n={len(nt)})")
    ax.scatter(t[xcol], 100 * t.rate_9710, s=6, c=BLUE, alpha=.7, linewidths=0, label=f"T, ≥25 víctimas (n={len(t)})")
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.axhline(10, color=ORANGE, lw=.8, ls="--"); ax.text(ax.get_xlim()[0] * 1.15, 10 * 1.12, "umbral stayer 10 %", color=ORANGE, fontsize=6, va="bottom")
    ax.axhline(100, color=GREY, lw=.5, ls=":")
    ax.set_xlabel(xlab); ax.grid(True, which="major", lw=.3, color="#dddddd", alpha=.8)
    rho = P[[xcol, "rate_9710"]].corr(method="spearman").iloc[0, 1]; rhoT = t[[xcol, "rate_9710"]].corr(method="spearman").iloc[0, 1]
    ax.text(.02, .97, f"Spearman ρ = {rho:.2f} (T: {rhoT:.2f})", transform=ax.transAxes, va="top", fontsize=6.5, color="#333333")
    for mu in ["05001", "54001", "20001", "47189", "54810", "70204", "27615"]:
        if mu in P.index:
            ax.annotate(P.loc[mu, "municipio_cede"], (P.loc[mu, xcol], 100 * P.loc[mu, "rate_9710"]), fontsize=5.2, color="#333333",
                        xytext=(3, 2), textcoords="offset points")
axes[0].set_ylabel("Expulsados 1997-2010 / población 2005 (%)")
axes[0].set_title("a. Dosis en víctimas", loc="left"); axes[1].set_title("b. Dosis per cápita", loc="left")
axes[0].legend(loc="lower right", markerscale=1.6, handletextpad=.2)
axes[1].set_yticklabels([])

ax = axes[2]
ax.plot(100 * CUR.umbral, 100 * CUR.share_dosis_PARA, color=BLUE, label="dosis PARA retenida")
ax.plot(100 * CUR.umbral, 100 * CUR.share_T_munis, color=GREEN, lw=1, label="municipios T retenidos")
ax.plot(100 * CUR.umbral, 100 * CUR.share_saber, color=GREY, lw=1, label="evaluados Saber 11 retenidos")
ax.set_xscale("log"); ax.set_xlim(0.5, 500); ax.set_ylim(0, 100)
ax.axvline(10, color=ORANGE, lw=.8, ls="--")
ax.axhline(30, color="#555555", lw=.5, ls=":"); ax.axhline(15, color="#555555", lw=.5, ls=":")
ax.text(0.55, 31, "≥30 %: aprobado", fontsize=5.8, color="#555555", va="bottom")
ax.text(0.55, 16, "<15 %: letal", fontsize=5.8, color="#555555", va="bottom")
for u in [.05, .10, .20, .30]:
    y = 100 * CUR.share_dosis_PARA[(CUR.umbral - u).abs().idxmin()]
    yy = 100 * retention("rate_9710", u)["share_dosis_PARA"]
    ax.plot([100 * u], [yy], marker="o", ms=3.2, color=BLUE, mec="white", mew=.6)
    ax.annotate(f"{yy:.0f} %", (100 * u, yy), xytext=(4, -3), textcoords="offset points", fontsize=5.8, color="#333333")
ax.set_xlabel("Umbral de expulsión acumulada (% de la población 2005, escala log)")
ax.set_ylabel("% retenido en la muestra stayer")
ax.set_title("c. Retención por umbral", loc="left")
ax.legend(loc="lower right", handlelength=1.6)
ax.grid(True, which="major", lw=.3, color="#dddddd", alpha=.8)
fig.suptitle(f"Desplazamiento (RUV 2016) y dosis paramilitar: {len(M)} municipios; {n_drop} sin dosis o sin expulsión no aparecen en a-b",
             fontsize=7, x=0.01, ha="left", y=0.995)
fig.tight_layout(w_pad=1.2)
fig.savefig(f"{PROP}/fig6_desplazamiento_vs_dosis.pdf")
plt.close(fig)
log("fig6 guardada")

# =====================================================================================
# 8. Números clave
# =====================================================================================
KEY["n_universo"] = int(len(M)); KEY["n_scatter"] = int(len(P))
KEY["share_exp_9710_en_T"] = float(M.exp_9710[M.in_T].sum() / M.exp_9710.sum())
KEY["share_pop_en_T"] = float(M.pop2005[M.in_T].sum() / M.pop2005.sum())
KEY["ratio_exp_9710_pop"] = float(M.exp_9710.sum() / M.pop2005.sum())
with open(f"{DER}/t5_numeros_clave.json", "w") as f:
    json.dump(KEY, f, indent=1, ensure_ascii=False, default=lambda o: float(o) if isinstance(o, (np.floating,)) else int(o))
log("VEREDICTO:", KEY["veredicto"], "| dosis retenida stayer<10%:", pct(r10))
