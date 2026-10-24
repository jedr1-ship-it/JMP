#!/usr/bin/env python3
"""
t2_A.py -- Tareas T1 (replicacion del PI) y T2 (test de identificacion del perfil de edad).

Uso:  python3 -I /home/user/JMP/code/exploration/t2_A.py

Insumos
  * /home/user/JMP/data/raw/cnmh_omc_202503/CMasacres_202503.xlsx
  * /home/user/JMP/data/raw/cnmh_omc_202503/CAsesionatosSelectivos_202503.xlsx
  * /home/user/JMP/data/derived/cnmh_muni_month_victims.csv   (panel muni x mes, solo casos con Mes>=1)

Salidas
  * /home/user/JMP/data/derived/t2_A_*.csv
  * /home/user/JMP/scoping/proposal/t2_A_resultados.md

Implementacion propia (no copia el script del PI). Para T1(a)-(c) se usan los agregados anuales
de los archivos crudos (incluyen casos con Mes=0, como hizo el PI). Para T1(d) y T2 se usa el panel
mensual derivado, previa verificacion de que coincide con una reagregacion propia de los crudos.
Los efectos fijos de dos vias se absorben por demeaning iterado (proyecciones alternantes) con
criterio de convergencia explicito, y se contrastan con una regresion con dummies (lstsq).
"""
import sys, time, warnings
warnings.filterwarnings("ignore")
import numpy as np
import pandas as pd

pd.set_option("display.width", 250); pd.set_option("display.max_rows", 500); pd.set_option("display.max_columns", 60)

RAW = "/home/user/JMP/data/raw/cnmh_omc_202503"
DER = "/home/user/JMP/data/derived"
PANEL = f"{DER}/cnmh_muni_month_victims.csv"
OUT_MD = "/home/user/JMP/scoping/proposal/t2_A_resultados.md"
PFX = f"{DER}/t2_A_"

T0 = time.time()
def log(*a):
    print(f"[{time.time()-T0:6.1f}s]", *a, flush=True)
def pct(x): return f"{100*x:.1f}%"

# =====================================================================================
# 0. Carga de los crudos (MA + AS) con clasificacion de responsable identica a la del panel
# =====================================================================================
PARA_LABELS = {"GRUPO PARAMILITAR", "AGENTE DEL ESTADO - GRUPO PARAMILITAR"}
POSD_LABELS = {"GRUPO POSDESMOVILIZACIÓN", "AGENTE DEL ESTADO - GRUPO POSDESMOVILIZACIÓN"}

def classify(resp: str) -> str:
    if resp in PARA_LABELS: return "PARA"
    if resp in POSD_LABELS: return "POSD"
    if resp == "GUERRILLA": return "GUE"
    if resp == "AGENTE DEL ESTADO": return "EST"
    return "NI"

def load_raw(path: str, mod: str) -> pd.DataFrame:
    keep = ["ID Caso", "Año", "Mes", "Código DANE de Municipio", "Municipio", "Departamento",
            "Presunto Responsable", "Total de Víctimas del Caso"]
    df = pd.read_excel(path, sheet_name=0, usecols=keep)
    df = df.rename(columns={"Año": "year", "Mes": "month", "Código DANE de Municipio": "muni",
                            "Municipio": "muni_name", "Departamento": "depto",
                            "Presunto Responsable": "resp", "Total de Víctimas del Caso": "vic"})
    df["year"] = pd.to_numeric(df["year"], errors="coerce")
    df["month"] = pd.to_numeric(df["month"], errors="coerce").fillna(0).astype(int)
    df["vic"] = pd.to_numeric(df["vic"], errors="coerce")
    df["muni"] = df["muni"].astype(str).str.strip().str.replace(r"\.0$", "", regex=True).str.zfill(5)
    df["grp"] = df["resp"].astype(str).map(classify)
    df["mod"] = mod
    return df

log("Leyendo crudos ...")
raw = pd.concat([load_raw(f"{RAW}/CMasacres_202503.xlsx", "MA"),
                 load_raw(f"{RAW}/CAsesionatosSelectivos_202503.xlsx", "AS")], ignore_index=True)
log(f"casos MA+AS: {len(raw):,}; victimas NaN: {raw.vic.isna().sum()}; victimas <=0: {(raw.vic<=0).sum()}")
assert raw.vic.isna().sum() == 0 and (raw.vic <= 0).sum() == 0, "revisar Total de Victimas"
raw = raw[raw.year.between(1985, 2015)].copy()
raw["year"] = raw["year"].astype(int)
raw["is_num_code"] = raw["muni"].str.fullmatch(r"\d{5}")
raw["is_real_muni"] = raw["is_num_code"] & (raw["muni"] != "00000")
log(f"casos 1985-2015: {len(raw):,}; codigos no numericos: {sorted(raw.loc[~raw.is_num_code,'muni'].unique())}; "
    f"codigo 00000 (sin informacion): {(raw.muni=='00000').sum()} casos")
muni_info = (raw[raw.is_real_muni].drop_duplicates("muni").set_index("muni")[["muni_name", "depto"]])
assert raw[raw.is_real_muni].groupby("muni")["depto"].nunique().max() == 1

# =====================================================================================
# 0b. Verificacion del panel mensual derivado contra una reagregacion propia de los crudos
# =====================================================================================
panel = pd.read_csv(PANEL, dtype={"muni": str})
panel["muni"] = panel["muni"].str.zfill(5)
GRPS = ["PARA", "POSD", "GUE", "EST", "NI"]
for g in GRPS:
    if g not in panel.columns: panel[g] = 0
mine = raw[raw.month.between(1, 12)].copy()
mine["ym"] = mine.year * 12 + mine.month - 1
mine = mine.pivot_table(index=["muni", "ym"], columns="grp", values="vic", aggfunc="sum", fill_value=0).reset_index()
for g in GRPS:
    if g not in mine.columns: mine[g] = 0
chk = panel[["muni", "ym"] + GRPS].merge(mine[["muni", "ym"] + GRPS], on=["muni", "ym"], how="outer",
                                           suffixes=("_panel", "_mine"), indicator=True)
assert (chk["_merge"] == "both").all(), "filas muni-mes distintas entre panel y reagregacion propia"
maxdiff = max(float((chk[f"{g}_panel"] - chk[f"{g}_mine"]).abs().max()) for g in GRPS)
assert maxdiff == 0, f"panel derivado != reagregacion propia (max diff {maxdiff})"
log(f"Panel derivado verificado: {len(panel):,} filas muni-mes, identico a la reagregacion propia (Mes>=1).")
log(f"  ym rango: {panel.ym.min()} ({panel.year.min()}-{panel.month.min():02d}) .. {panel.ym.max()} ({panel.year.max()}-{panel.month.max():02d})")

# =====================================================================================
# T1 (a): muestra T = municipios con >=25 victimas paramilitares (MA+AS) en 1997-2006
# =====================================================================================
ann = (raw.groupby(["muni", "year", "grp"])["vic"].sum().unstack("grp", fill_value=0).reset_index())
for g in GRPS:
    if g not in ann.columns: ann[g] = 0
ann["TOT"] = ann[GRPS].sum(axis=1)
# rejilla completa muni x ano (1985-2015) para que los ceros existan
munis_all = sorted(ann.muni.unique()); years_all = list(range(1985, 2016))
grid = pd.MultiIndex.from_product([munis_all, years_all], names=["muni", "year"]).to_frame(index=False)
ann = grid.merge(ann, on=["muni", "year"], how="left").fillna(0)
for g in GRPS + ["TOT"]: ann[g] = ann[g].astype(int)

w9706 = ann[ann.year.between(1997, 2006)]
ptot_all = w9706.groupby("muni")["PARA"].sum()                      # incluye 00000 y codigos extranjeros
real = ptot_all.index.to_series().str.fullmatch(r"\d{5}") & (ptot_all.index != "00000")
ptot = ptot_all[real]
T = ptot[ptot >= 25].index.tolist()
n_T = len(T)
para_9706_total_all = int(ptot_all.sum()); para_9706_total_real = int(ptot.sum()); para_9706_T = int(ptot[T].sum())
share_T = para_9706_T / para_9706_total_all
share_T_real = para_9706_T / para_9706_total_real
n_T_PI_filter = int((ptot_all[ptot_all.index.to_series().str.fullmatch(r"\d{5}")] >= 25).sum())  # filtro \d{5} (incluye 00000)
code0_para = int(ptot_all.get("00000", 0))
# sensibilidad: solo casos con mes (lo que ve el panel mensual)
pm = panel[panel.year.between(1997, 2006)].groupby("muni")["PARA"].sum()
pm = pm[pm.index.to_series().str.fullmatch(r"\d{5}") & (pm.index != "00000")]
n_T_dated = int((pm >= 25).sum())
T_dated = set(pm[pm >= 25].index)
log(f"T1(a): municipios con >=25 victimas PARA 1997-2006: {n_T} (PI: 453). "
    f"Con filtro \\d{{5}} del PI (incluye 00000, que tiene {code0_para} victimas PARA): {n_T_PI_filter}. "
    f"Solo casos con mes (panel): {n_T_dated} (interseccion con T: {len(T_dated & set(T))}).")
log(f"       victimas PARA 1997-2006 en T: {para_9706_T:,} de {para_9706_total_all:,} ({100*share_T:.1f}%); "
    f"sobre municipios reales {para_9706_total_real:,} ({100*share_T_real:.1f}%)")
thr_tab = pd.DataFrame({"umbral": [1, 10, 25, 50, 100, 250],
                        "n_munis": [int((ptot >= k).sum()) for k in [1, 10, 25, 50, 100, 250]],
                        "share_victimas_PARA_9706": [float(ptot[ptot >= k].sum() / ptot.sum()) for k in [1, 10, 25, 50, 100, 250]]})

# =====================================================================================
# T1 (b): entrada / salida anual (primer / ultimo ano 1996-2006 con >=3 victimas PARA), duracion
# =====================================================================================
aT = ann[ann.muni.isin(T)].copy()
act = aT[aT.year.between(1996, 2006) & (aT.PARA >= 3)]
entry = act.groupby("muni")["year"].min().rename("entry_year")
exit_ = act.groupby("muni")["year"].max().rename("exit_year")
Tdf = pd.DataFrame(index=pd.Index(T, name="muni")).join(muni_info).join(ptot.rename("para_9706")).join(entry).join(exit_)
assert Tdf.entry_year.notna().all(), "en T siempre hay >=1 ano con >=3 (25 victimas en 11 anos)"
Tdf["duration_years"] = Tdf.exit_year - Tdf.entry_year + 1
Tdf["pre_para_88_95"] = aT[aT.year.between(1988, 1995)].groupby("muni")["PARA"].sum()
exit_counts = Tdf.exit_year.value_counts().sort_index()
entry_counts = Tdf.entry_year.value_counts().sort_index()
med_dur = float(Tdf.duration_years.median())
q_dur = Tdf.duration_years.quantile([.1, .25, .5, .75, .9])
log(f"T1(b): salida anual: {exit_counts.to_dict()} (PI: 2003:52, 2004:93, 2005:216, 2006:64)")
log(f"       entrada anual: {entry_counts.to_dict()}")
log(f"       duracion mediana: {med_dur:.0f} anos (PI: 9); cuartiles {q_dur[.25]:.0f}-{q_dur[.75]:.0f}; "
    f"con PARA>=3 en 1988-95: {int((Tdf.pre_para_88_95>=3).sum())} ({100*(Tdf.pre_para_88_95>=3).mean():.0f}%)")

# =====================================================================================
# T1 (c): ratio de victimas TOTALES (todos los perpetradores) 2007-2010 / 2000-2002 en T
# =====================================================================================
serT = aT.groupby("year")[GRPS + ["TOT"]].sum()
serN = ann[ann.muni.isin(ptot.index)].groupby("year")[GRPS + ["TOT"]].sum()
m0002_T = serT.loc[2000:2002, "TOT"].mean(); m0710_T = serT.loc[2007:2010, "TOT"].mean()
ratio_T = float(m0710_T / m0002_T)
m0002_N = serN.loc[2000:2002, "TOT"].mean(); m0710_N = serN.loc[2007:2010, "TOT"].mean()
ratio_N = float(m0710_N / m0002_N)
ratio_T_sum = float(serT.loc[2007:2010, "TOT"].sum() / serT.loc[2000:2002, "TOT"].sum())
log(f"T1(c): T: TOT medio 2000-02 = {m0002_T:,.0f}/ano, 2007-10 = {m0710_T:,.0f}/ano, ratio = {ratio_T:.3f} (PI: 0,12; 15.226 -> 1.856). "
    f"Nacional: {m0002_N:,.0f} -> {m0710_N:,.0f}, ratio {ratio_N:.3f}")

# =====================================================================================
# T1 (d): mes de salida municipal = primer mes a partir del cual las victimas PARA restantes
#         hasta dic-2006 son <=5% del total municipal 1996-2006 (panel mensual, solo Mes>=1)
# =====================================================================================
YM0, YM1 = 1985 * 12, 2015 * 12 + 11
NM = YM1 - YM0 + 1
pT = panel[panel.muni.isin(T)]
mi = {m: i for i, m in enumerate(T)}
P = np.zeros((n_T, NM))                       # matriz muni x mes de victimas PARA (fechadas)
np.add.at(P, (pT.muni.map(mi).to_numpy(), (pT.ym - YM0).to_numpy()), pT.PARA.to_numpy(dtype=float))
j96, j06 = 1996 * 12 - YM0, 2006 * 12 + 11 - YM0
Pw = P[:, j96:j06 + 1]                        # ene-1996 .. dic-2006 (132 meses)
S_dated = Pw.sum(axis=1)
remaining = Pw[:, ::-1].cumsum(axis=1)[:, ::-1]    # remaining[:, k] = suma desde el mes k hasta dic-2006
ok = remaining <= 0.05 * S_dated[:, None]
first_ok = np.where(ok.any(axis=1), ok.argmax(axis=1), Pw.shape[1])   # 132 => no hay salida antes de 2007
exit_ym = 1996 * 12 + first_ok
Tdf["para_9606_all"] = aT[aT.year.between(1996, 2006)].groupby("muni")["PARA"].sum()
Tdf["para_9606_dated"] = pd.Series(S_dated, index=T)
Tdf["undated_share_9606"] = 1 - Tdf.para_9606_dated / Tdf.para_9606_all
Tdf["exit_ym"] = pd.Series(exit_ym, index=T)
Tdf["exit_month_year"] = Tdf.exit_ym // 12
Tdf["exit_month_month"] = Tdf.exit_ym % 12 + 1
Tdf["exit_month_label"] = Tdf.exit_month_year.astype(str) + "-" + Tdf.exit_month_month.map(lambda m: f"{m:02d}")
Tdf["exit_month_censored"] = Tdf.exit_ym > 2006 * 12 + 11            # el ultimo 5% cae en dic-2006 o nunca se alcanza
Tdf["exit_month_unreliable"] = Tdf.undated_share_9606 > 0.05           # >5% de la dosis 1996-2006 sin mes
Tdf["exit_month_assigned"] = ~Tdf.exit_month_censored & ~Tdf.exit_month_unreliable
Tdf.loc[Tdf.exit_month_censored, "exit_month_label"] = ">=2007-01 (censurado)"
sem = np.where(Tdf.exit_month_month <= 6, "S1", "S2")
Tdf["exit_semester"] = Tdf.exit_month_year.astype(str) + "-" + sem
Tdf.loc[Tdf.exit_month_censored, "exit_semester"] = ">=2007 (censurado)"
Tdf.loc[Tdf.exit_month_year < 2002, "exit_semester"] = "<2002"

def sem_table(df):
    order = ["<2002"] + [f"{y}-S{s}" for y in range(2002, 2007) for s in (1, 2)] + [">=2007 (censurado)"]
    vc = df.exit_semester.value_counts()
    out = pd.DataFrame({"semestre": order, "n_munis": [int(vc.get(k, 0)) for k in order]})
    out["share_munis"] = out.n_munis / out.n_munis.sum()
    out["victimas_PARA_9706"] = [int(df.loc[df.exit_semester == k, "para_9706"].sum()) for k in order]
    out["share_victimas_PARA_9706"] = out.victimas_PARA_9706 / df.para_9706.sum()
    return out
sem_all = sem_table(Tdf)
sem_rel = sem_table(Tdf[~Tdf.exit_month_unreliable])
n_assigned = int(Tdf.exit_month_assigned.sum())
cov_assigned_T = float(Tdf.loc[Tdf.exit_month_assigned, "para_9706"].sum() / Tdf.para_9706.sum())
cov_assigned_all = float(Tdf.loc[Tdf.exit_month_assigned, "para_9706"].sum() / para_9706_total_all)
cov_notcens_all = float(Tdf.loc[~Tdf.exit_month_censored, "para_9706"].sum() / para_9706_total_all)
Tdf["exit_month_minus_exit_year"] = Tdf.exit_month_year - Tdf.exit_year
diff_tab = Tdf.loc[~Tdf.exit_month_censored, "exit_month_minus_exit_year"].value_counts().sort_index()
big = Tdf.para_9706.idxmax(); ex_big = int(Tdf.loc[big, "exit_ym"])
post12_big = int(P[mi[big], ex_big - YM0: ex_big - YM0 + 12].sum())
share_le1 = float((Tdf.loc[~Tdf.exit_month_censored, "exit_month_minus_exit_year"].abs() <= 1).mean())
log(f"T1(d): municipio de mayor dosis {muni_info.loc[big,'muni_name']}: mes de salida {Tdf.loc[big,'exit_month_label']}, "
    f"{post12_big} victimas PARA fechadas en los 12 meses siguientes; |ano mes salida - ano salida anual| <= 1 en {pct(share_le1)} de T")
log(f"T1(d): mes de salida asignado (no censurado y <=5% de dosis sin mes) en {n_assigned}/{n_T} municipios; "
    f"censurados (>5% de la dosis en dic-06 o nunca): {int(Tdf.exit_month_censored.sum())}; "
    f"con >5% sin mes: {int(Tdf.exit_month_unreliable.sum())}")
log(f"       cobertura: {100*cov_assigned_all:.1f}% de las victimas PARA 1997-2006 (todas) / {100*cov_assigned_T:.1f}% de las de T; "
    f"sin exigir el criterio de mes faltante: {100*cov_notcens_all:.1f}%")
log("       distribucion por semestre (todos los T):\n" + sem_all.to_string(index=False))
log("       ano del mes de salida - ano de salida anual (>=3):\n" + diff_tab.to_string())

# =====================================================================================
# T2: dosis por ventana de edad, municipio x cohorte (nacimiento en julio de c), c = 1988..2008
# =====================================================================================
COHORTS = list(range(1988, 2009))
WINDOWS = {"inutero": (-9, -1), "d02": (0, 35), "d35": (36, 71), "d611": (72, 143)}
WLAB = {"inutero": "in utero (-9..-1)", "d02": "0-2 (0..35)", "d35": "3-5 (36..71)", "d611": "6-11 (72..143)"}
C = P.cumsum(axis=1)                                  # suma acumulada por fila
def window_sum(lo_rel, hi_rel, b):
    """Suma de P entre b+lo_rel y b+hi_rel (indices absolutos ym); NaN si la ventana sale de 1985-2015."""
    lo, hi = b + lo_rel - YM0, b + hi_rel - YM0
    if lo < 0 or hi > NM - 1:
        return np.full(n_T, np.nan)
    return C[:, hi] - (C[:, lo - 1] if lo > 0 else 0.0)
rows = []
for c in COHORTS:
    b = c * 12 + 6                                    # julio de c (ym = year*12 + month-1)
    d = {w: window_sum(lo, hi, b) for w, (lo, hi) in WINDOWS.items()}
    rows.append(pd.DataFrame({"muni": T, "cohort": c, **d}))
cells = pd.concat(rows, ignore_index=True)
cells = cells.merge(Tdf[["depto", "entry_year", "exit_year", "exit_ym", "exit_month_assigned"]], left_on="muni", right_index=True)
cells["birth_ym"] = cells.cohort * 12 + 6
cells["born_after_exit_year"] = cells.cohort > cells.exit_year
cells["born_after_exit_month"] = cells.exit_month_assigned & (cells.birth_ym > cells.exit_ym)
n_cells = len(cells)
miss = cells[list(WINDOWS)].isna().groupby(cells.cohort).any()
log(f"T2: celdas muni x cohorte: {n_cells:,} ({n_T} munis x {len(COHORTS)} cohortes); "
    f"ventanas faltantes por salir de 1985-2015: " +
    "; ".join(f"{w}: cohortes {sorted(miss.index[miss[w]].tolist())}" for w in WINDOWS if miss[w].any()))

# (1) correlacion bruta 0-2 / 3-5
both = cells[["d02", "d35"]].dropna()
corr_raw_02_35 = float(np.corrcoef(both.d02, both.d35)[0, 1])
log(f"T2(1): corr bruta dosis 0-2 vs 3-5 (n={len(both):,}): {corr_raw_02_35:.3f}")

# (2) residualizacion con EF de dos vias por demeaning iterado
def demean_2way(x, g1, g2, tol=1e-11, maxit=5000):
    """Proyecciones alternantes sobre los complementos de los EF g1 y g2. Devuelve residuo, iteraciones y
    la mayor media de grupo residual (criterio de convergencia)."""
    r = x.astype(float).copy()
    n1, n2 = np.bincount(g1), np.bincount(g2)
    scale = max(r.std(), 1e-12)
    for it in range(1, maxit + 1):
        r -= (np.bincount(g1, weights=r, minlength=len(n1)) / n1)[g1]
        r -= (np.bincount(g2, weights=r, minlength=len(n2)) / n2)[g2]
        gap = max(np.abs(np.bincount(g1, weights=r, minlength=len(n1)) / n1).max(),
                  np.abs(np.bincount(g2, weights=r, minlength=len(n2)) / n2).max())
        if gap < tol * scale:
            return r, it, gap
    return r, it, gap

def residualize(df, win, spec):
    """spec = 'muni+cohort_x_depto' o 'muni+cohort'. Residualiza df[win] en su propia muestra no faltante."""
    s = df[df[win].notna()].copy()
    g1 = pd.factorize(s.muni)[0]
    g2 = pd.factorize(s.cohort.astype(str) + "|" + s.depto)[0] if spec == "muni+cohort_x_depto" else pd.factorize(s.cohort)[0]
    r, it, gap = demean_2way(s[win].to_numpy(), g1, g2)
    return pd.Series(r, index=s.index), it, gap

def dummy_resid(df, win, spec):
    """Verificacion: residuo de la regresion con dummies (lstsq, rango deficiente tolerado)."""
    s = df[df[win].notna()]
    D1 = pd.get_dummies(s.muni, dtype=float)
    key = (s.cohort.astype(str) + "|" + s.depto) if spec == "muni+cohort_x_depto" else s.cohort.astype(str)
    D2 = pd.get_dummies(key, dtype=float)
    X = np.hstack([D1.to_numpy(), D2.to_numpy()])
    beta = np.linalg.lstsq(X, s[win].to_numpy(dtype=float), rcond=None)[0]
    return pd.Series(s[win].to_numpy() - X @ beta, index=s.index)

SPECS = {"muni+cohort_x_depto": "EF municipio + EF cohorte x departamento",
         "muni+cohort": "EF municipio + EF cohorte (sin interaccion)"}
TOP10 = Tdf.para_9706.sort_values(ascending=False).head(10).index.tolist()
SAMPLES = {"A_1988_2008": ("cohortes 1988-2008, cada ventana en su muestra no faltante", cells),
           "D_1988_2008_sin_top10": ("cohortes 1988-2008 sin los 10 municipios de mayor dosis 1997-2006", cells[~cells.muni.isin(TOP10)]),
           "B_1988_2003_balanced": ("cohortes 1988-2003, las cuatro ventanas observadas", cells[cells.cohort <= 2003]),
           "C_1995_2008": ("cohortes 1995-2008 (Saber 11 2012-2025 a los 17)", cells[cells.cohort >= 1995])}
TRANSFORMS = {"levels": lambda x: x, "log1p": np.log1p}

summary_rows, conv_rows, resid_store = [], [], {}
for sname, (sdesc, sdf) in SAMPLES.items():
    for tname, tf in TRANSFORMS.items():
        base = sdf.copy()
        for w in WINDOWS: base[w] = tf(base[w])
        for spec in SPECS:
            res = pd.DataFrame(index=base.index)
            for w in WINDOWS:
                r, it, gap = residualize(base, w, spec)
                res[w] = r
                conv_rows.append({"sample": sname, "transform": tname, "spec": spec, "window": w, "n": int(r.notna().sum()),
                                  "iterations": it, "max_group_mean_after": gap})
                if sname == "A_1988_2008" and tname == "levels":           # contraste con dummies solo en la muestra principal
                    rd = dummy_resid(base, w, spec)
                    conv_rows[-1]["max_abs_diff_vs_dummies"] = float((r - rd).abs().max())
            resid_store[(sname, tname, spec)] = res
            row = {"sample": sname, "sample_desc": sdesc, "transform": tname, "spec": spec, "n_cells": len(base)}
            for w in WINDOWS:
                m = base[w].notna()
                row[f"n_{w}"] = int(m.sum())
                row[f"var_raw_{w}"] = float(base.loc[m, w].var(ddof=1))
                row[f"var_resid_{w}"] = float(res.loc[m, w].var(ddof=1))
                row[f"var_resid_share_{w}"] = row[f"var_resid_{w}"] / row[f"var_raw_{w}"] if row[f"var_raw_{w}"] > 0 else np.nan
            for a, b_ in [("inutero", "d02"), ("d02", "d35"), ("d35", "d611")]:
                m = base[a].notna() & base[b_].notna()
                row[f"corr_raw_{a}_{b_}"] = float(np.corrcoef(base.loc[m, a], base.loc[m, b_])[0, 1])
                row[f"corr_resid_{a}_{b_}"] = float(np.corrcoef(res.loc[m, a], res.loc[m, b_])[0, 1])
                row[f"n_pair_{a}_{b_}"] = int(m.sum())
            # (5) colinealidad conjunta: VIF y numero de condicion de la matriz de dosis residualizadas
            for wset, lab in [(["inutero", "d02", "d35", "d611"], "4w"), (["inutero", "d02", "d35"], "3w")]:
                m = res[wset].notna().all(axis=1)
                R = res.loc[m, wset].to_numpy()
                Z = (R - R.mean(0)) / R.std(0, ddof=1)
                row[f"cond_number_{lab}"] = float(np.linalg.cond(Z))
                row[f"n_{lab}"] = int(m.sum())
                for j, w in enumerate(wset):
                    others = np.delete(Z, j, axis=1)
                    bhat = np.linalg.lstsq(np.column_stack([np.ones(len(Z)), others]), Z[:, j], rcond=None)[0]
                    e = Z[:, j] - np.column_stack([np.ones(len(Z)), others]) @ bhat
                    r2 = 1 - e.var() / Z[:, j].var()
                    row[f"vif_{lab}_{w}"] = float(1 / (1 - r2)) if r2 < 1 else np.inf
            summary_rows.append(row)
summary = pd.DataFrame(summary_rows)
conv = pd.DataFrame(conv_rows)
assert (conv.iterations < 5000).all(), "demeaning no convergio"
# concentracion de la variacion residual (principal, niveles) por municipio
R0 = resid_store[("A_1988_2008", "levels", "muni+cohort_x_depto")]
conc_rows = []
for w in WINDOWS:
    ss = (R0[w] ** 2).groupby(cells.muni).sum().sort_values(ascending=False); tot = ss.sum()
    conc_rows.append({"window": w, "top1_muni": ss.index[0], "top1_name": muni_info.loc[ss.index[0], "muni_name"],
                      "share_ss_top1": ss.iloc[0] / tot, "share_ss_top5": ss.head(5).sum() / tot, "share_ss_top10": ss.head(10).sum() / tot,
                      "top5": ", ".join(muni_info.loc[i, "muni_name"] for i in ss.index[:5])})
conc = pd.DataFrame(conc_rows)
log("T2: concentracion de la suma de cuadrados residual por municipio (principal, niveles):\n" + conc.round(3).to_string(index=False))
log("T2(2): convergencia del demeaning iterado (muestra principal, niveles):\n" +
    conv[(conv["sample"] == "A_1988_2008") & (conv["transform"] == "levels")].to_string(index=False))

MAIN = summary[(summary["sample"] == "A_1988_2008") & (summary["transform"] == "levels") & (summary.spec == "muni+cohort_x_depto")].iloc[0]
ALT = summary[(summary["sample"] == "A_1988_2008") & (summary["transform"] == "levels") & (summary.spec == "muni+cohort")].iloc[0]
show_cols = ["sample", "transform", "spec"] + [f"var_resid_share_{w}" for w in WINDOWS] + \
            ["corr_resid_inutero_d02", "corr_resid_d02_d35", "corr_resid_d35_d611", "cond_number_4w", "cond_number_3w"]
log("T2(2)/(5)/(6): resumen por muestra x transformacion x especificacion:\n" + summary[show_cols].round(3).to_string(index=False))

# (3) celdas con dosis 0-2 > 0 y dosis 3-5 = 0
m23 = cells.d02.notna() & cells.d35.notna()
c02pos_35zero = int(((cells.d02 > 0) & (cells.d35 == 0) & m23).sum())
share_02pos_35zero = c02pos_35zero / int(m23.sum())
c02zero_35pos = int(((cells.d02 == 0) & (cells.d35 > 0) & m23).sum())
c_bothzero = int(((cells.d02 == 0) & (cells.d35 == 0) & m23).sum())
by_cohort_0235 = cells[m23].groupby("cohort").apply(
    lambda g: pd.Series({"n": len(g), "d02pos_d35zero": int(((g.d02 > 0) & (g.d35 == 0)).sum()),
                         "d02zero_d35pos": int(((g.d02 == 0) & (g.d35 > 0)).sum()), "both_zero": int(((g.d02 == 0) & (g.d35 == 0)).sum()),
                         "both_pos": int(((g.d02 > 0) & (g.d35 > 0)).sum()),
                         "mean_d02": g.d02.mean(), "mean_d35": g.d35.mean(), "mean_inutero": g.inutero.mean(),
                         "mean_d611": g.d611.mean()}), include_groups=False).reset_index()
log(f"T2(3): celdas con dosis 0-2 > 0 y 3-5 = 0: {c02pos_35zero:,} de {int(m23.sum()):,} ({100*share_02pos_35zero:.1f}%); "
    f"0-2 = 0 y 3-5 > 0: {c02zero_35pos:,}; ambas 0: {c_bothzero:,}")
log("       por cohorte:\n" + by_cohort_0235.round(1).to_string(index=False))

# (4) celdas 'nacido tras la salida'
n_after_year = int(cells.born_after_exit_year.sum())
n_after_month = int(cells.born_after_exit_month.sum())
n_after_year_le2008 = n_after_year
munis_with_after = int(cells[cells.born_after_exit_year].muni.nunique())
after_by_cohort = cells.groupby("cohort")["born_after_exit_year"].sum().astype(int)
log(f"T2(4): celdas con cohorte > ano de salida anual: {n_after_year:,} ({100*n_after_year/n_cells:.1f}% de las celdas; "
    f"{munis_with_after} municipios); con nacimiento (jul-c) posterior al mes de salida asignado: {n_after_month:,}")
log("       por cohorte: " + ", ".join(f"{c}:{v}" for c, v in after_by_cohort.items() if v > 0))

# contribucion de deptos con un solo municipio en T (celdas absorbidas por cohorte x depto)
dcount = Tdf.groupby("depto").size().sort_values(ascending=False)
single = dcount[dcount == 1]
log(f"       departamentos en T: {len(dcount)}; con un solo municipio en T (dosis absorbida por EF cohorte x depto): {len(single)} "
    f"({', '.join(single.index)})")

# =====================================================================================
# Veredicto frente a los umbrales del PI
# =====================================================================================
cr = MAIN["corr_resid_d02_d35"]; vs02 = MAIN["var_resid_share_d02"]; vs35 = MAIN["var_resid_share_d35"]
def verdict(cr, vs):
    if cr > 0.8 or vs < 0.10: return "LETAL"
    if cr < 0.7 and vs > 0.20: return "APROBADO"
    return "ZONA GRIS"
v_main = verdict(cr, min(vs02, vs35))
verdict_txt = (f"{v_main}: corr residual 0-2/3-5 = {cr:.3f} (aprobado <0,7; letal >0,8); varianza residual 0-2 = {100*vs02:.1f}% "
               f"y 3-5 = {100*vs35:.1f}% de la bruta (aprobado >20%; letal <10%). "
               f"Spec alternativa (EF muni + cohorte): corr = {ALT['corr_resid_d02_d35']:.3f}, var resid 0-2 = {100*ALT['var_resid_share_d02']:.1f}%, "
               f"3-5 = {100*ALT['var_resid_share_d35']:.1f}%.")
D = summary[(summary["sample"] == "D_1988_2008_sin_top10") & (summary["transform"] == "levels") & (summary.spec == "muni+cohort_x_depto")].iloc[0]
LG = summary[(summary["sample"] == "A_1988_2008") & (summary["transform"] == "log1p") & (summary.spec == "muni+cohort_x_depto")].iloc[0]
c02 = conc[conc.window == "d02"].iloc[0]
verdict_txt += (f" Matices: {pct(c02.share_ss_top1)} de la suma de cuadrados residual de la dosis 0-2 proviene de {c02.top1_name} y {pct(c02.share_ss_top5)} de cinco municipios; "
                f"sin los 10 municipios de mayor dosis (niveles): var resid 0-2 = {pct(D.var_resid_share_d02)}, 3-5 = {pct(D.var_resid_share_d35)}, corr = {D.corr_resid_d02_d35:.3f} "
                f"({verdict(D.corr_resid_d02_d35, min(D.var_resid_share_d02, D.var_resid_share_d35))}); con dosis log1p: var resid 0-2 = {pct(LG.var_resid_share_d02)}, "
                f"3-5 = {pct(LG.var_resid_share_d35)}, corr = {LG.corr_resid_d02_d35:.3f} ({verdict(LG.corr_resid_d02_d35, min(LG.var_resid_share_d02, LG.var_resid_share_d35))}).")
log("VEREDICTO T2: " + verdict_txt)

# =====================================================================================
# Salidas CSV
# =====================================================================================
Tdf.reset_index().to_csv(PFX + "T1_muestra_T.csv", index=False)
thr_tab.to_csv(PFX + "T1a_umbrales.csv", index=False)
pd.DataFrame({"exit_year": exit_counts.index, "n_munis": exit_counts.values,
              "PI": [{2003: 52, 2004: 93, 2005: 216, 2006: 64}.get(int(y), np.nan) for y in exit_counts.index]}).to_csv(PFX + "T1b_salida_anual.csv", index=False)
pd.DataFrame({"entry_year": entry_counts.index, "n_munis": entry_counts.values}).to_csv(PFX + "T1b_entrada_anual.csv", index=False)
Tdf.duration_years.value_counts().sort_index().rename_axis("duration_years").reset_index(name="n_munis").to_csv(PFX + "T1b_duracion.csv", index=False)
pd.concat([serT.add_prefix("T_"), serN.add_prefix("nat_")], axis=1).loc[1985:2015].to_csv(PFX + "T1c_series_anuales.csv")
sem_all.assign(muestra="todos los T (mes calculado solo con casos fechados)").to_csv(PFX + "T1d_salida_mensual_semestre.csv", index=False)
sem_rel.assign(muestra="T con <=5% de la dosis 1996-2006 sin mes").to_csv(PFX + "T1d_salida_mensual_semestre_fiables.csv", index=False)
Tdf.exit_month_label.value_counts().sort_index().rename_axis("exit_month").reset_index(name="n_munis").to_csv(PFX + "T1d_salida_mensual_mes.csv", index=False)
cells_out = cells.copy()
for w in WINDOWS: cells_out[f"res_{w}"] = resid_store[("A_1988_2008", "levels", "muni+cohort_x_depto")][w]
for w in WINDOWS: cells_out[f"res_alt_{w}"] = resid_store[("A_1988_2008", "levels", "muni+cohort")][w]
cells_out.to_csv(PFX + "T2_celdas_muni_cohorte.csv", index=False)
summary.to_csv(PFX + "T2_resumen_especificaciones.csv", index=False)
conv.to_csv(PFX + "T2_convergencia_demeaning.csv", index=False)
by_cohort_0235.to_csv(PFX + "T2_celdas_por_cohorte.csv", index=False)
conc.to_csv(PFX + "T2_concentracion_residual.csv", index=False)
# matrices de correlacion residual completas (muestra principal, ambas specs)
cm = []
for spec in SPECS:
    R = resid_store[("A_1988_2008", "levels", spec)]
    cmat = R.corr(min_periods=10).round(4); cmat.index.name = "window"
    cm.append(cmat.assign(spec=spec).reset_index())
pd.concat(cm).to_csv(PFX + "T2_matrices_corr_residual.csv", index=False)

# =====================================================================================
# Resumen markdown
# =====================================================================================
L = []
L.append("# T1/T2 — Replicación del PI y test de identificación del perfil de edad (t2_A)\n")
L.append(f"Script: `code/exploration/t2_A.py` (implementación propia; ejecutado {time.strftime('%Y-%m-%d %H:%M')}). "
         "Fuente: CNMH-OMC corte mar-2025, masacres + asesinatos selectivos. PARA = 'GRUPO PARAMILITAR' + "
         "'AGENTE DEL ESTADO - GRUPO PARAMILITAR' (idéntico, en estos archivos, a la regla `contains('PARAMILITAR')` del PI). "
         "T1(a)-(c) usan agregados anuales de los crudos (incluyen casos con Mes=0, ~1% de las víctimas); T1(d) y T2 usan el panel "
         f"mensual derivado, verificado celda a celda contra una reagregación propia ({len(panel):,} filas muni-mes, diferencia máxima 0).\n")
L.append("## T1. Replicación\n")
L.append(f"**(a)** Municipios con ≥25 víctimas paramilitares 1997-2006: **{n_T}** (PI: 453). Concentran **{pct(share_T)}** de las víctimas "
         f"paramilitares 1997-2006 ({para_9706_T:,} de {para_9706_total_all:,}; PI: 94%). "
         f"Con el filtro `\\d{{5}}` del PI, que no excluye el código 00000 ('SIN INFORMACION', {code0_para} víctimas PARA 1997-2006), "
         f"salen {n_T_PI_filter}. Usando solo casos con mes (lo que ve el panel mensual) salen {n_T_dated}.\n")
L.append("| Umbral | Municipios | Share víctimas PARA 97-06 |\n|---|---|---|")
for _, r in thr_tab.iterrows(): L.append(f"| ≥{int(r.umbral)} | {int(r.n_munis)} | {pct(r.share_victimas_PARA_9706)} |")
L.append("")
L.append(f"**(b)** Entrada = primer año 1996-2006 con ≥3 víctimas PARA; salida = último. Distribución de salida: "
         + ", ".join(f"{int(y)}: {int(n)}" for y, n in exit_counts.items())
         + " (PI: 2003: 52, 2004: 93, 2005: 216, 2006: 64). Entrada: "
         + ", ".join(f"{int(y)}: {int(n)}" for y, n in entry_counts.items())
         + f". Duración mediana **{med_dur:.0f} años** (PI: 9); p10/p25/p75/p90 = {q_dur[.1]:.0f}/{q_dur[.25]:.0f}/{q_dur[.75]:.0f}/{q_dur[.9]:.0f}. "
         f"{int((Tdf.pre_para_88_95>=3).sum())} municipios ({pct((Tdf.pre_para_88_95>=3).mean())}) ya tenían ≥3 víctimas PARA en 1988-95 (PI: 73%).\n")
L.append(f"**(c)** Víctimas totales (todos los perpetradores) en T: media anual 2000-02 = {m0002_T:,.0f}, 2007-10 = {m0710_T:,.0f}, "
         f"**ratio = {ratio_T:.3f}** (PI: 0,12 con 15.226 → 1.856). Nacional: {m0002_N:,.0f} → {m0710_N:,.0f}, ratio {ratio_N:.3f}.\n")
L.append(f"**(d) Mes de salida** (nuevo): primer mes m tal que las víctimas PARA fechadas desde m hasta dic-2006 son ≤5% del total "
         f"municipal fechado 1996-2006. Se calcula solo con casos con Mes≥1; se marca *no fiable* si >5% de la dosis PARA 1996-2006 del "
         f"municipio carece de mes ({int(Tdf.exit_month_unreliable.sum())} municipios) y *censurado* si el último 5% cae en dic-2006 "
         f"({int(Tdf.exit_month_censored.sum())} municipios). Mes asignado en **{n_assigned}/{n_T}** municipios, que concentran "
         f"**{pct(cov_assigned_all)}** de las víctimas PARA 1997-2006 (criterio del PI: ≥80%); {pct(cov_assigned_T)} de las de T. "
         f"Sin la exclusión por mes faltante: {pct(cov_notcens_all)}.\n")
L.append("| Semestre de salida | Municipios (todos T) | Share munis | Share víctimas PARA 97-06 (T) | Municipios (≤5% sin mes) |\n|---|---|---|---|---|")
for (_, r), (_, r2) in zip(sem_all.iterrows(), sem_rel.iterrows()):
    L.append(f"| {r.semestre} | {int(r.n_munis)} | {pct(r.share_munis)} | {pct(r.share_victimas_PARA_9706)} | {int(r2.n_munis)} |")
L.append("")
L.append("Año del mes de salida menos año de salida anual (≥3): " + ", ".join(f"{int(k):+d}: {int(v)}" for k, v in diff_tab.items()) +
         ". El criterio del 5% suele adelantar la salida respecto al 'último año con ≥3' porque la cola de 1-2 víctimas/año ya es <5% "
         "en municipios con dosis grande.\n")
L.append("## T2. Test de identificación del perfil de edad\n")
L.append(f"Panel: {n_T} municipios de T × 21 cohortes (1988-2008, nacimiento en julio) = {n_cells:,} celdas. Dosis = víctimas PARA fechadas "
         "del panel mensual en las ventanas in utero (−9..−1), 0-2 (0..35), 3-5 (36..71) y 6-11 (72..143 meses). La ventana 6-11 sale de "
         "1985-2015 para las cohortes 2004-2008 (faltante); las otras tres están completas. Por construcción del CNMH no hay víctimas "
         "PARA después de 2006 (pasan a 'posdesmovilización'), así que las cohortes 2007-2008 tienen dosis cero en todas las ventanas.\n")
L.append(f"**(1)** Correlación bruta 0-2/3-5 (n = {len(both):,}): **{corr_raw_02_35:.3f}**.\n")
L.append("**(2)** Residualización con EF de municipio y EF cohorte × departamento (demeaning iterado; converge en "
         f"{int(conv[(conv['sample']=='A_1988_2008')&(conv["transform"]=='levels')&(conv.spec=='muni+cohort_x_depto')].iterations.max())} iteración(es) "
         f"con media de grupo residual máxima {conv[(conv['sample']=='A_1988_2008')&(conv["transform"]=='levels')].max_group_mean_after.max():.1e}; "
         f"diferencia máxima frente a la regresión con dummies {conv[(conv['sample']=='A_1988_2008')&(conv["transform"]=='levels')].max_abs_diff_vs_dummies.max():.1e}). "
         "Una sola pasada es exacta porque el panel es balanceado dentro de cada departamento (todos los municipios tienen las 21 cohortes y la "
         "falta de 6-11 depende solo de la cohorte); el criterio de convergencia se evalúa igualmente y el residuo coincide con el de la regresión con dummies. "
         "Cada ventana se residualiza en su propia muestra no faltante; las correlaciones usan celdas con ambas ventanas.\n")
L.append("| Muestra | Transf. | Especificación | var res. in utero | var res. 0-2 | var res. 3-5 | var res. 6-11 | ρ in utero/0-2 | ρ 0-2/3-5 | ρ 3-5/6-11 | cond. 4w | cond. 3w |\n|---|---|---|---|---|---|---|---|---|---|---|---|")
for _, r in summary.iterrows():
    L.append(f"| {r['sample']} | {r["transform"]} | {r.spec} | {pct(r.var_resid_share_inutero)} | {pct(r.var_resid_share_d02)} | {pct(r.var_resid_share_d35)} | "
             f"{pct(r.var_resid_share_d611)} | {r.corr_resid_inutero_d02:.3f} | {r.corr_resid_d02_d35:.3f} | {r.corr_resid_d35_d611:.3f} | "
             f"{r.cond_number_4w:.1f} | {r.cond_number_3w:.1f} |")
L.append("")
L.append(f"Principal (A, niveles, muni + cohorte×depto): varianza residual como fracción de la bruta: in utero {pct(MAIN.var_resid_share_inutero)}, "
         f"0-2 **{pct(MAIN.var_resid_share_d02)}**, 3-5 **{pct(MAIN.var_resid_share_d35)}**, 6-11 {pct(MAIN.var_resid_share_d611)}. "
         f"Correlaciones residuales: in utero/0-2 = {MAIN.corr_resid_inutero_d02:.3f}, **0-2/3-5 = {MAIN.corr_resid_d02_d35:.3f}**, "
         f"3-5/6-11 = {MAIN.corr_resid_d35_d611:.3f}.\n")
L.append("**Concentración de la variación identificadora** (principal, niveles): " + "; ".join(
    f"{WLAB[r.window]}: {pct(r.share_ss_top1)} de la suma de cuadrados residual en {r.top1_name}, {pct(r.share_ss_top5)} en cinco municipios ({r.top5})"
    for _, r in conc.iterrows()) + ". Por eso se añaden la muestra D (sin los 10 municipios de mayor dosis 1997-2006: " +
    ", ".join(muni_info.loc[m, "muni_name"] for m in TOP10) + ") y la transformación log1p, que muestran qué variación queda para el municipio típico.\n")
L.append(f"**(3)** Celdas con dosis 0-2 > 0 y 3-5 = 0: **{c02pos_35zero:,} de {int(m23.sum()):,} ({pct(share_02pos_35zero)})**; "
         f"0-2 = 0 y 3-5 > 0: {c02zero_35pos:,}; ambas cero: {c_bothzero:,}. Por cohorte (véase `t2_A_T2_celdas_por_cohorte.csv`): "
         + ", ".join(f"{int(r.cohort)}: {int(r.d02pos_d35zero)}" for _, r in by_cohort_0235.iterrows() if r.d02pos_d35zero > 0) + ".\n")
L.append(f"**(4)** Celdas 'nacido tras la salida' (cohorte > año de salida anual): **{n_after_year:,}** ({pct(n_after_year/n_cells)} de las celdas, "
         f"{munis_with_after} municipios); por cohorte: " + ", ".join(f"{c}: {v}" for c, v in after_by_cohort.items() if v > 0) +
         f". Con el mes de salida asignado (nacimiento en jul-c posterior al mes de salida): {n_after_month:,}.\n")
L.append(f"**(5)** Colinealidad conjunta de las dosis residualizadas (principal): número de condición de la matriz estandarizada = "
         f"{MAIN.cond_number_4w:.2f} con las cuatro ventanas (n = {int(MAIN.n_4w):,}, cohortes 1988-2003) y {MAIN.cond_number_3w:.2f} con tres "
         f"(n = {int(MAIN.n_3w):,}). VIF (4 ventanas): in utero {MAIN.vif_4w_inutero:.2f}, 0-2 {MAIN.vif_4w_d02:.2f}, 3-5 {MAIN.vif_4w_d35:.2f}, "
         f"6-11 {MAIN.vif_4w_d611:.2f}; (3 ventanas): in utero {MAIN.vif_3w_inutero:.2f}, 0-2 {MAIN.vif_3w_d02:.2f}, 3-5 {MAIN.vif_3w_d35:.2f}.\n")
L.append(f"**(6)** Especificación alternativa (EF municipio + EF cohorte, sin interacción con departamento): var residual 0-2 {pct(ALT.var_resid_share_d02)}, "
         f"3-5 {pct(ALT.var_resid_share_d35)}; ρ 0-2/3-5 = {ALT.corr_resid_d02_d35:.3f}; cond. 4w {ALT.cond_number_4w:.2f}. "
         f"Departamentos en T: {len(dcount)}, de los cuales {len(single)} tienen un solo municipio en T ({', '.join(single.index)}): en la "
         "especificación principal sus celdas quedan absorbidas por el EF cohorte × departamento (residuo exactamente cero), lo que reduce la "
         "varianza residual respecto a la alternativa; la alternativa deja en el residuo la variación entre departamentos dentro de cohorte, "
         "que es justamente la que el PI quiere no usar.\n")
L.append(f"## Veredicto frente a los umbrales del PI\n\n**{verdict_txt}**\n")
L.append("## Caveats\n")
L.append("- Dosis en niveles (víctimas), no per cápita ni por 100.000: no hay población municipal en el repositorio. La fila `log1p` muestra la "
         "sensibilidad a las colas (Medellín, etc.).")
L.append("- Las ventanas usan solo casos con mes; ~1% de las víctimas (Mes=0) no entran en la dosis. El mes de salida se marca no fiable si "
         "ese 1% se concentra en un municipio (>5% de su dosis).")
L.append("- La correlación residual 0-2/3-5 en A incluye las cohortes 2007-2008 con dosis cero en todo (residuos no nulos tras EF); la muestra B "
         "(cohortes 1988-2003) y C (1995-2008) acotan el efecto de la composición de cohortes.")
L.append("- Las celdas 'nacido tras la salida' con la salida anual (último año con ≥3) sobreestiman las limpias: parte de esas cohortes recibe "
         "1-2 víctimas/año residuales (ver `exit_month_minus_exit_year` en `t2_A_T1_muestra_T.csv`).")
L.append(f"- La regla del 5% fecha el punto en que se ha acumulado el 95% de la dosis PARA fechada 1996-2006, no el cese de la violencia: en municipios "
         f"de dosis grande la cola del 5% son decenas o cientos de víctimas ({muni_info.loc[big,'muni_name']}: mes de salida {Tdf.loc[big,'exit_month_label']}, "
         f"con {post12_big} víctimas PARA fechadas en los 12 meses siguientes). En el {pct(share_le1)} de los municipios el año del mes de salida está a ±1 año "
         "del año de salida anual (último año con ≥3). Para fechar el cese conviene un umbral absoluto (p. ej. último mes con ≥k víctimas) además del relativo.")
L.append("- El criterio de aprobación del PI no fija la muestra de cohortes ni la transformación; se reporta la rejilla completa: en niveles aprueba, "
         "en log1p la varianza residual 0-2/3-5 cae a la zona gris (10-20%) y la mayor parte de la variación en niveles proviene de pocas ciudades grandes.")
with open(OUT_MD, "w", encoding="utf-8") as f:
    f.write("\n".join(L) + "\n")
log(f"Escrito {OUT_MD} y {PFX}*.csv")
