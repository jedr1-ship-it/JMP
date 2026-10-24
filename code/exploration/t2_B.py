"""t2_B.py -- Tareas T1 (replicacion del PI) y T2 (test de identificacion del perfil de edad).

Implementacion independiente (RA "B"): reconstruye el panel municipio x anio y municipio x mes
desde los xlsx crudos del CNMH-OMC (corte marzo 2025), masacres + asesinatos selectivos.
Los efectos fijos de T2 se estiman por demeaning iterado (proyecciones alternantes) y se
verifican contra una regresion con dummies via numpy.linalg.lstsq.

Uso:   python3 -I /home/user/JMP/code/exploration/t2_B.py
Salidas: /home/user/JMP/data/derived/t2_B_*.csv  y  /home/user/JMP/scoping/proposal/t2_B_resultados.md
"""
import time
import warnings

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")
pd.set_option("display.width", 250)
pd.set_option("display.max_rows", 500)
pd.set_option("display.max_columns", 60)

ROOT = "/home/user/JMP"
RAW = f"{ROOT}/data/raw/cnmh_omc_202503"
DER = f"{ROOT}/data/derived"
MD_OUT = f"{ROOT}/scoping/proposal/t2_B_resultados.md"
PI_PANEL = f"{DER}/cnmh_muni_month_victims.csv"

PARA_LABELS = {"GRUPO PARAMILITAR", "AGENTE DEL ESTADO - GRUPO PARAMILITAR"}
POSD_LABELS = {"GRUPO POSDESMOVILIZACIÓN", "AGENTE DEL ESTADO - GRUPO POSDESMOVILIZACIÓN"}
GRPS = ["PARA", "POSD", "GUE", "EST", "NI"]
YEAR_LO, YEAR_HI = 1985, 2015
YM_LO, YM_HI = YEAR_LO * 12, YEAR_HI * 12 + 11          # ym = year*12 + month-1
COHORTS = list(range(1988, 2009))
WINDOWS = {"iu": (-9, -1), "a02": (0, 35), "a35": (36, 71), "a611": (72, 143)}
WLAB = {"iu": "in utero (-9..-1)", "a02": "0-2 (0..35)", "a35": "3-5 (36..71)", "a611": "6-11 (72..143)"}
PAIRS = [("iu", "a02"), ("a02", "a35"), ("a35", "a611")]
EXIT_SHARE = 0.05
MES0_MAX_SHARE = 0.05
SIN_INFO = "00000"

t0 = time.time()
log_lines = []


def log(s=""):
    print(s)
    log_lines.append(str(s))


def ym_label(ym):
    if pd.isna(ym):
        return ""
    ym = int(ym)
    return f"{ym // 12}-{ym % 12 + 1:02d}"


# ----------------------------------------------------------------------------------------------
# 1. Carga de casos crudos
# ----------------------------------------------------------------------------------------------
def load_cases():
    use = ["Año", "Mes", "Código DANE de Municipio", "Municipio", "Departamento",
           "Presunto Responsable", "Total de Víctimas del Caso"]
    parts = []
    for fn, tipo in [("CMasacres_202503.xlsx", "MA"), ("CAsesionatosSelectivos_202503.xlsx", "AS")]:
        x = pd.read_excel(f"{RAW}/{fn}", sheet_name=0, usecols=use)
        x["tipo"] = tipo
        parts.append(x)
    d = pd.concat(parts, ignore_index=True)
    d = d.rename(columns={"Año": "year", "Mes": "month", "Código DANE de Municipio": "cod",
                          "Municipio": "muni_name", "Departamento": "depto",
                          "Presunto Responsable": "resp", "Total de Víctimas del Caso": "victims"})
    for c in ["year", "month", "victims"]:
        d[c] = pd.to_numeric(d[c], errors="coerce")
    d["cod"] = d["cod"].astype(str).str.strip().str.replace(r"\.0$", "", regex=True).str.zfill(5)
    n_vic_na = int(d["victims"].isna().sum())
    d["victims"] = d["victims"].fillna(1).clip(lower=1).astype(int)
    r = d["resp"].astype(str).str.strip()
    d["grp"] = np.select([r.isin(PARA_LABELS), r.isin(POSD_LABELS), r.eq("GUERRILLA"), r.eq("AGENTE DEL ESTADO")],
                         ["PARA", "POSD", "GUE", "EST"], default="NI")
    d["cod_ok"] = d["cod"].str.fullmatch(r"\d{5}")
    return d, n_vic_na


raw, n_vic_na = load_cases()
n_raw = len(raw)
keep = raw["cod_ok"] & raw["year"].between(YEAR_LO, YEAR_HI)
cases = raw.loc[keep].copy()
log(f"Casos leidos: {n_raw} (MA+AS); con codigo DANE 5 digitos y anio {YEAR_LO}-{YEAR_HI}: {len(cases)}; "
    f"excluidos: {int((~raw['cod_ok']).sum())} con codigo no numerico (exterior), "
    f"{int((raw['cod_ok'] & ~raw['year'].between(YEAR_LO, YEAR_HI)).sum())} con anio fuera de rango; victimas NA: {n_vic_na}")
log(f"Victimas por grupo {YEAR_LO}-{YEAR_HI}: " + cases.groupby("grp")["victims"].sum().to_dict().__str__())
names = cases.drop_duplicates("cod").set_index("cod")[["muni_name", "depto"]]

# ----------------------------------------------------------------------------------------------
# 2. Paneles municipio x anio (todos los meses) y municipio x mes (Mes 1-12)
# ----------------------------------------------------------------------------------------------
ann = cases.pivot_table(index=["cod", "year"], columns="grp", values="victims", aggfunc="sum", fill_value=0)
for g in GRPS:
    if g not in ann.columns:
        ann[g] = 0
ann = ann[GRPS].reset_index()
ann["TOT"] = ann[GRPS].sum(axis=1)

mcases = cases[cases["month"].between(1, 12)].copy()
mcases["ym"] = (mcases["year"] * 12 + mcases["month"] - 1).astype(int)
mon = mcases.pivot_table(index=["cod", "ym"], columns="grp", values="victims", aggfunc="sum", fill_value=0)
for g in GRPS:
    if g not in mon.columns:
        mon[g] = 0
mon = mon[GRPS].reset_index()
mon["TOT"] = mon[GRPS].sum(axis=1)

# Contraste con el panel mensual del PI (solo verificacion; no se usa en los calculos)
pi_panel = pd.read_csv(PI_PANEL, dtype={"muni": str})
chk = mon.merge(pi_panel.rename(columns={"muni": "cod"}), on=["cod", "ym"], how="outer", suffixes=("", "_pi"), indicator=True)
chk_both = chk[chk["_merge"] == "both"]
chk_diff = {g: float(np.max(np.abs(chk_both[g] - chk_both[f"{g}_pi"]))) for g in GRPS}
chk_only_pi_codes = chk.loc[chk["_merge"] == "right_only", "cod"].value_counts().to_dict()
chk_n_unmatched = int((chk["_merge"] != "both").sum())
log(f"Verificacion vs panel del PI ({PI_PANEL.split('/')[-1]}): filas solo mias={int((chk['_merge'] == 'left_only').sum())}, "
    f"solo PI={int((chk['_merge'] == 'right_only').sum())} (codigos: {chk_only_pi_codes}), max |diff| por grupo en filas comunes={chk_diff}")

# ----------------------------------------------------------------------------------------------
# 3. T1 (a): muestra T (>=25 victimas PARA 1997-2006)
# ----------------------------------------------------------------------------------------------
w9706 = ann[ann["year"].between(1997, 2006)]
ptot = w9706.groupby("cod")["PARA"].sum()
nat_para_9706 = float(ptot.sum())
thr_rows = [{"umbral": k, "n_munis": int((ptot >= k).sum()), "share_victimas_para_9706": float(ptot[ptot >= k].sum() / nat_para_9706)}
            for k in [1, 10, 25, 50, 100, 250]]
T_all = ptot.index[ptot >= 25]
n_T_all = len(T_all)
share_T_all = float(ptot[T_all].sum() / nat_para_9706)
T = T_all[T_all != SIN_INFO]            # muestra de trabajo sin el codigo 'SIN INFORMACION'
n_T = len(T)
share_T = float(ptot[T].sum() / nat_para_9706)
log(f"\n== T1(a) == PARA 1997-2006 nacional (codigos 5 digitos, incl. {SIN_INFO}) = {nat_para_9706:.0f}")
log(f"Municipios con >=25 victimas PARA 1997-2006: {n_T_all} (concentran {100 * share_T_all:.1f}%); "
    f"{SIN_INFO} ('SIN INFORMACION', {ptot.get(SIN_INFO, 0):.0f} victimas) esta dentro: {SIN_INFO in T_all} -> T de trabajo = {n_T} municipios ({100 * share_T:.1f}%)")

# ----------------------------------------------------------------------------------------------
# 4. T1 (b): entrada/salida anual (>=3 victimas PARA), duracion
# ----------------------------------------------------------------------------------------------
act = ann[ann["cod"].isin(T_all) & ann["year"].between(1996, 2006) & (ann["PARA"] >= 3)]
entry = act.groupby("cod")["year"].min().rename("entry")
exit_y = act.groupby("cod")["year"].max().rename("exit")
fl = pd.concat([entry, exit_y], axis=1).reindex(T_all)
fl["dur"] = fl["exit"] - fl["entry"] + 1
exit_counts_all = fl["exit"].value_counts().sort_index()
exit_counts = fl.loc[T, "exit"].value_counts().sort_index()
entry_counts = fl.loc[T, "entry"].value_counts().sort_index()
dur_q = fl.loc[T, "dur"].describe(percentiles=[.1, .25, .5, .75, .9])
med_dur = float(fl.loc[T, "dur"].median())
log(f"\n== T1(b) == entrada/salida anual (>=3 PARA, 1996-2006), T={n_T} (sin {SIN_INFO}); {SIN_INFO}: entry={fl.loc[SIN_INFO, 'entry'] if SIN_INFO in fl.index else 'NA'}, exit={fl.loc[SIN_INFO, 'exit'] if SIN_INFO in fl.index else 'NA'}")
log("Salida (T sin 00000): " + exit_counts.to_dict().__str__())
log("Salida (453 con 00000): " + exit_counts_all.to_dict().__str__())
log("Entrada (T): " + entry_counts.to_dict().__str__())
log(f"Duracion: mediana={med_dur:.0f}, p25={dur_q['25%']:.0f}, p75={dur_q['75%']:.0f}, media={dur_q['mean']:.2f}; sin NA: {int(fl.loc[T, 'dur'].notna().sum())}")

# ----------------------------------------------------------------------------------------------
# 5. T1 (c): ratio de victimas TOTALES 2007-2010 / 2000-2002
# ----------------------------------------------------------------------------------------------
def ratio_block(sub):
    s = sub.groupby("year")[GRPS + ["TOT"]].sum().reindex(range(YEAR_LO, YEAR_HI + 1), fill_value=0)
    return s, float(s.loc[2007:2010, "TOT"].mean() / s.loc[2000:2002, "TOT"].mean())


ser_T, ratio_T = ratio_block(ann[ann["cod"].isin(T)])
ser_Tall, ratio_Tall = ratio_block(ann[ann["cod"].isin(T_all)])
ser_nat, ratio_nat = ratio_block(ann)
ratio_T_pp = float((ser_T.loc[2007:2010, "PARA"] + ser_T.loc[2007:2010, "POSD"]).mean() / (ser_T.loc[2000:2002, "PARA"] + ser_T.loc[2000:2002, "POSD"]).mean())
log(f"\n== T1(c) == TOT medio/anio en T: 2000-02={ser_T.loc[2000:2002, 'TOT'].mean():.0f}, 2007-10={ser_T.loc[2007:2010, 'TOT'].mean():.0f}, ratio={ratio_T:.3f} "
    f"(453 con 00000: {ser_Tall.loc[2000:2002, 'TOT'].mean():.0f} -> {ser_Tall.loc[2007:2010, 'TOT'].mean():.0f}, ratio {ratio_Tall:.3f}; nacional: {ratio_nat:.3f}; solo PARA+POSD en T: {ratio_T_pp:.3f})")
log(ser_T.loc[1996:2010].astype(int).to_string())

# ----------------------------------------------------------------------------------------------
# 6. T1 (d): mes de salida municipal (panel mensual, Mes>=1)
#    exit_ym = primer mes m tal que las victimas PARA en [m, dic-2006] son <= 5% del total 1996-2006
# ----------------------------------------------------------------------------------------------
ym96, ym06 = 1996 * 12, 2006 * 12 + 11
n_m = ym06 - ym96 + 1
mT = mon[mon["cod"].isin(T) & mon["ym"].between(ym96, ym06)]
Tlist = list(T)
pos = {c: i for i, c in enumerate(Tlist)}
PM = np.zeros((n_T, n_m))
PM[mT["cod"].map(pos).values, (mT["ym"] - ym96).values] = mT["PARA"].values
V = PM.sum(axis=1)
rem = PM[:, ::-1].cumsum(axis=1)[:, ::-1]                      # victimas restantes desde m hasta dic-2006
cond = rem <= EXIT_SHARE * V[:, None]
has = cond.any(axis=1)
first = np.where(has, cond.argmax(axis=1), -1)
exit_ym = pd.Series(np.where(has, first + ym96, np.nan), index=Tlist, name="exit_ym")
# victimas con Mes=0 (sin dato) 1996-2006 por municipio
p96 = cases[(cases["grp"] == "PARA") & cases["year"].between(1996, 2006) & cases["cod"].isin(T)]
v_all = p96.groupby("cod")["victims"].sum().reindex(Tlist).fillna(0)
v_mes0 = p96[p96["month"] == 0].groupby("cod")["victims"].sum().reindex(Tlist).fillna(0)
mes0_share = (v_mes0 / v_all).rename("mes0_share")
exit_tab = pd.DataFrame({"exit_ym": exit_ym, "para_9606_mesdato": V, "para_9606_total": v_all.values, "mes0_share": mes0_share.values}, index=Tlist)
exit_tab["exit_year_mes"] = exit_tab["exit_ym"] // 12
exit_tab["exit_label"] = exit_tab["exit_ym"].map(ym_label)
exit_tab["exit_sem"] = np.where(exit_tab["exit_ym"].isna(), "censurado (>dic-2006)",
                                np.where(exit_tab["exit_ym"] < 2002 * 12, "<2002",
                                         (exit_tab["exit_ym"] // 12).astype("Int64").astype(str) + "S" + ((exit_tab["exit_ym"] % 12 >= 6).astype(int) + 1).astype(str)))
variants = {
    "V1_todos_T": pd.Series(True, index=Tlist),
    "V2_mes0_le5pct": (exit_tab["mes0_share"] <= MES0_MAX_SHARE),
    "V3_sin_ningun_mes0": (exit_tab["mes0_share"] == 0),
}
sem_order = ["<2002"] + [f"{y}S{s}" for y in range(2002, 2007) for s in (1, 2)] + ["censurado (>dic-2006)"]
sem_rows = []
cov_rows = []
for vn, mask in variants.items():
    inc = exit_tab[mask]
    vc = inc["exit_sem"].value_counts().reindex(sem_order, fill_value=0)   # incluye la fila 'censurado'
    sem_rows.append(pd.Series(vc.values, index=sem_order, name=vn))
    sub = inc[inc["exit_ym"].notna()]
    cov_rows.append({"variante": vn, "n_munis_incluidos": int(mask.sum()), "n_con_mes_salida": int(len(sub)),
                     "share_para_9706_nacional": float(ptot[sub.index].sum() / nat_para_9706),
                     "share_para_9706_en_T": float(ptot[sub.index].sum() / ptot[T].sum())})
sem_table = pd.DataFrame(sem_rows).T
cov_table = pd.DataFrame(cov_rows)
primary = "V2_mes0_le5pct"
cov_primary = float(cov_table.set_index("variante").loc[primary, "share_para_9706_nacional"])
# comparacion con el anio de salida anual
exit_tab["exit_year_anual"] = fl.loc[Tlist, "exit"].values
exit_tab["diff_year_mes_menos_anual"] = exit_tab["exit_year_mes"] - exit_tab["exit_year_anual"]
diff_vc = exit_tab.loc[variants[primary], "diff_year_mes_menos_anual"].value_counts().sort_index()
log(f"\n== T1(d) == mes de salida (<= {100 * EXIT_SHARE:.0f}% de victimas PARA restantes hasta dic-2006; solo Mes>=1)")
log(cov_table.round(4).to_string(index=False))
log(sem_table.to_string())
log(f"Diferencia anio(mes de salida) - anio de salida anual, variante {primary}: {diff_vc.to_dict()}")
log("Distribucion anual del mes de salida (variante primaria): " + exit_tab.loc[variants[primary], "exit_year_mes"].value_counts().sort_index().to_dict().__str__())

# ----------------------------------------------------------------------------------------------
# 7. Tablas T1 a disco
# ----------------------------------------------------------------------------------------------
muni_tab = pd.DataFrame({"cod": Tlist}).set_index("cod")
muni_tab["muni_name"] = names.loc[Tlist, "muni_name"].values
muni_tab["depto"] = names.loc[Tlist, "depto"].values
muni_tab["para_9706"] = ptot[Tlist].values
muni_tab["entry_year"] = fl.loc[Tlist, "entry"].values
muni_tab["exit_year"] = fl.loc[Tlist, "exit"].values
muni_tab["duration"] = fl.loc[Tlist, "dur"].values
for c in ["exit_ym", "exit_label", "exit_year_mes", "exit_sem", "para_9606_mesdato", "para_9606_total", "mes0_share"]:
    muni_tab[c] = exit_tab.loc[Tlist, c].values
muni_tab["in_V2_mes0_le5pct"] = variants["V2_mes0_le5pct"].loc[Tlist].values
muni_tab.reset_index().to_csv(f"{DER}/t2_B_T1_munis.csv", index=False)
pd.DataFrame(thr_rows).to_csv(f"{DER}/t2_B_T1_umbrales.csv", index=False)
pd.DataFrame({"year": exit_counts.index, "n_exit_T": exit_counts.values,
              "n_exit_453": exit_counts_all.reindex(exit_counts.index, fill_value=0).values,
              "n_entry_T": entry_counts.reindex(exit_counts.index, fill_value=0).values}).to_csv(f"{DER}/t2_B_T1_entrada_salida_anual.csv", index=False)
sem_table.reset_index().rename(columns={"index": "semestre"}).to_csv(f"{DER}/t2_B_T1_mes_salida_semestre.csv", index=False)
cov_table.to_csv(f"{DER}/t2_B_T1_mes_salida_cobertura.csv", index=False)
ser_T.loc[1996:2010].reset_index().to_csv(f"{DER}/t2_B_T1_serie_anual_T.csv", index=False)

# ----------------------------------------------------------------------------------------------
# 8. T2: dosis por municipio x cohorte y ventana de edad
# ----------------------------------------------------------------------------------------------
n_ym = YM_HI - YM_LO + 1
mF = mon[mon["cod"].isin(T)]
P = np.zeros((n_T, n_ym))
P[mF["cod"].map(pos).values, (mF["ym"] - YM_LO).values] = mF["PARA"].values
rows = []
for c in COHORTS:
    b = c * 12 + 6                                   # nacimiento en julio de c
    rec = {"cohort": c}
    for wname, (a, z) in WINDOWS.items():
        lo, hi = b + a, b + z
        if lo < YM_LO or hi > YM_HI:
            rec[wname] = np.full(n_T, np.nan)
        else:
            rec[wname] = P[:, lo - YM_LO:hi - YM_LO + 1].sum(axis=1)
    rows.append(pd.DataFrame({"cod": Tlist, "cohort": c, **{k: rec[k] for k in WINDOWS}}))
cells = pd.concat(rows, ignore_index=True)
cells["depto"] = cells["cod"].map(names["depto"])
cells["exit_year"] = cells["cod"].map(fl["exit"])
cells["entry_year"] = cells["cod"].map(fl["entry"])
cells["exit_year_mes"] = cells["cod"].map(exit_tab["exit_year_mes"])
cells["born_after_exit"] = cells["cohort"] > cells["exit_year"]
cells["born_after_exit_mes"] = cells["cohort"] > cells["exit_year_mes"]
cells["cell_02pos_35zero"] = (cells["a02"] > 0) & (cells["a35"] == 0)
avail = {w: sorted(cells.loc[cells[w].notna(), "cohort"].unique().tolist()) for w in WINDOWS}
log(f"\n== T2 == celdas municipio x cohorte: {len(cells)} ({n_T} municipios x {len(COHORTS)} cohortes). Cohortes con dato por ventana: "
    + {w: f"{v[0]}-{v[-1]}" for w, v in avail.items()}.__str__())
dep_n = cells.drop_duplicates("cod").groupby("depto")["cod"].size().sort_values(ascending=False)
single_deptos = dep_n.index[dep_n == 1].tolist()
cells["single_depto"] = cells["depto"].isin(single_deptos)
log(f"Departamentos en T: {len(dep_n)}; con un solo municipio en T (residuo = 0 mecanicamente bajo EF cohorte x dpto): {len(single_deptos)} {single_deptos}")


# ----------------------------------------------------------------------------------------------
# 9. Residualizacion con efectos fijos: demeaning iterado + verificacion con dummies (lstsq)
# ----------------------------------------------------------------------------------------------
def demean_iter(y, groups, tol=1e-9, maxit=10000):
    """Proyecciones alternantes: resta medias de grupo hasta que el cambio maximo < tol."""
    r = y.astype(float) - y.mean()
    delta = np.inf
    for it in range(1, maxit + 1):
        r_old = r
        for g in groups:
            cnt = np.bincount(g)
            r = r - (np.bincount(g, weights=r) / cnt)[g]
        delta = float(np.max(np.abs(r - r_old)))
        if delta < tol * max(1.0, float(np.abs(y).max())):
            return r, it, delta, True
    return r, maxit, delta, False


def resid_lstsq(y, groups):
    n = len(y)
    blocks = []
    for g in groups:
        k = g.max() + 1
        X = np.zeros((n, k))
        X[np.arange(n), g] = 1.0
        blocks.append(X)
    X = np.hstack(blocks)
    beta, *_ = np.linalg.lstsq(X, y.astype(float), rcond=None)
    return y - X @ beta


def fe_groups(df, spec):
    muni = pd.factorize(df["cod"])[0]
    if spec == "A":   # EF municipio + EF cohorte x departamento
        g2 = pd.factorize(df["cohort"].astype(str) + "|" + df["depto"].astype(str))[0]
    else:             # EF municipio + EF cohorte
        g2 = pd.factorize(df["cohort"])[0]
    return [muni, g2]


conv_rows = []


def residualize(df, cols, spec, label):
    """Devuelve DataFrame con residuos de cada columna (misma muestra para todas), y registra convergencia."""
    groups = fe_groups(df, spec)
    out = pd.DataFrame(index=df.index)
    for c in cols:
        y = df[c].values.astype(float)
        r, it, delta, ok = demean_iter(y, groups)
        r2 = resid_lstsq(y, groups)
        maxdiff = float(np.max(np.abs(r - r2)))
        conv_rows.append({"spec": spec, "muestra": label, "ventana": c, "n": len(y), "iteraciones": it,
                          "cambio_final": delta, "convergio": ok, "max_abs_diff_vs_lstsq": maxdiff,
                          "n_grupos_g2": int(groups[1].max() + 1)})
        out[c] = r
    return out


def var_share(y, r):
    return float(np.var(r) / np.var(y)) if np.var(y) > 0 else np.nan


def corr(a, b):
    return float(np.corrcoef(a, b)[0, 1])


def vif_cond(R):
    """R: matriz n x k de dosis residualizadas. VIF por columna y numero de condicion (columnas estandarizadas)."""
    Rs = (R - R.mean(axis=0)) / R.std(axis=0)
    cond_X = float(np.linalg.cond(Rs))
    cond_corr = float(np.linalg.cond(np.corrcoef(Rs, rowvar=False)))
    vifs = []
    k = Rs.shape[1]
    for j in range(k):
        yj = Rs[:, j]
        Xj = np.column_stack([np.ones(len(yj)), np.delete(Rs, j, axis=1)])
        beta, *_ = np.linalg.lstsq(Xj, yj, rcond=None)
        ssr = float(np.sum((yj - Xj @ beta) ** 2))
        sst = float(np.sum((yj - yj.mean()) ** 2))
        r2 = 1 - ssr / sst
        vifs.append(1 / (1 - r2) if r2 < 1 else np.inf)
    return vifs, cond_X, cond_corr


summary = []          # filas (spec, muestra, metrica, valor)


def add(spec, sample, metric, value):
    summary.append({"spec": spec, "muestra": sample, "metrica": metric, "valor": value})


# --- (1) correlaciones brutas ---
both = cells[cells["a02"].notna() & cells["a35"].notna()]
corr_raw_02_35 = corr(both["a02"].values, both["a35"].values)
add("bruto", "1988-2008", "corr_bruta_a02_a35", corr_raw_02_35)
add("bruto", "1988-2008", "n_celdas", len(both))
for p, q in PAIRS:
    s = cells[cells[p].notna() & cells[q].notna()]
    add("bruto", f"{s['cohort'].min()}-{s['cohort'].max()}", f"corr_bruta_{p}_{q}", corr(s[p].values, s[q].values))
    add("bruto", f"{s['cohort'].min()}-{s['cohort'].max()}", f"corr_bruta_spearman_{p}_{q}", float(s[[p, q]].corr(method="spearman").iloc[0, 1]))
log(f"\n(1) corr bruta 0-2/3-5 (n={len(both)}): {corr_raw_02_35:.4f}")

# --- (2), (5), (6): residualizacion por especificacion ---
results = {}
for spec, spec_lab in [("A", "EF muni + EF cohorte x dpto"), ("B", "EF muni + EF cohorte")]:
    res = {}
    # varianza residual por ventana, cada ventana en su muestra disponible (balanceada en cohortes)
    for w in WINDOWS:
        s = cells[cells[w].notna()]
        lab = f"{s['cohort'].min()}-{s['cohort'].max()}"
        r = residualize(s, [w], spec, f"ventana {w}")
        vs = var_share(s[w].values, r[w].values)
        res[f"var_share_{w}"] = vs
        add(spec, lab, f"var_resid_share_{w}", vs)
        add(spec, lab, f"n_celdas_{w}", len(s))
        # sin departamentos con un solo municipio (donde el residuo es 0 por construccion en la spec A)
        s2 = s[~s["single_depto"]]
        r2 = residualize(s2, [w], spec, f"ventana {w} sin dptos singleton")
        add(spec, lab + " sin dpto singleton", f"var_resid_share_{w}", var_share(s2[w].values, r2[w].values))
    # correlaciones residuales entre ventanas adyacentes, en la muestra comun del par
    for p, q in PAIRS:
        s = cells[cells[p].notna() & cells[q].notna()]
        lab = f"{s['cohort'].min()}-{s['cohort'].max()}"
        r = residualize(s, [p, q], spec, f"par {p}-{q}")
        cr = corr(r[p].values, r[q].values)
        res[f"corr_resid_{p}_{q}"] = cr
        add(spec, lab, f"corr_resid_{p}_{q}", cr)
        add(spec, lab, f"n_celdas_{p}_{q}", len(s))
        s2 = s[~s["single_depto"]]
        r2 = residualize(s2, [p, q], spec, f"par {p}-{q} sin dptos singleton")
        add(spec, lab + " sin dpto singleton", f"corr_resid_{p}_{q}", corr(r2[p].values, r2[q].values))
        # robustez: transformacion asinh de la dosis
        sa = s.assign(**{p: np.arcsinh(s[p]), q: np.arcsinh(s[q])})
        ra = residualize(sa, [p, q], spec, f"par {p}-{q} asinh")
        add(spec, lab + " asinh", f"corr_resid_{p}_{q}", corr(ra[p].values, ra[q].values))
        add(spec, lab + " asinh", f"var_resid_share_{p}", var_share(sa[p].values, ra[p].values))
        add(spec, lab + " asinh", f"var_resid_share_{q}", var_share(sa[q].values, ra[q].values))
    # muestra balanceada (las 4 ventanas con dato): matriz de correlaciones residuales, VIF, condicion
    bal = cells.dropna(subset=list(WINDOWS))
    labb = f"balanceada {bal['cohort'].min()}-{bal['cohort'].max()}"
    rb = residualize(bal, list(WINDOWS), spec, "balanceada 4 ventanas")
    cm = rb.corr()
    results[f"corrmat_{spec}"] = cm
    for p, q in PAIRS:
        add(spec, labb, f"corr_resid_{p}_{q}", float(cm.loc[p, q]))
    for w in WINDOWS:
        add(spec, labb, f"var_resid_share_{w}", var_share(bal[w].values, rb[w].values))
    vifs, cond_X, cond_corr = vif_cond(rb[list(WINDOWS)].values)
    for w, v in zip(WINDOWS, vifs):
        add(spec, labb, f"VIF_{w}", v)
    add(spec, labb, "cond_number_X_std", cond_X)
    add(spec, labb, "cond_number_corrmat", cond_corr)
    res.update({"vifs": vifs, "cond_X": cond_X, "cond_corr": cond_corr, "corrmat": cm, "n_bal": len(bal)})
    if spec == "A":
        cells_res = rb.add_prefix("res_A_")
    else:
        cells_res_B = rb.add_prefix("res_B_")
    results[spec] = res
    log(f"\n(2) spec {spec} ({spec_lab}): var share: " + {w: round(res[f'var_share_{w}'], 4) for w in WINDOWS}.__str__())
    log(f"    corr resid: " + {f'{p}_{q}': round(res[f'corr_resid_{p}_{q}'], 4) for p, q in PAIRS}.__str__())
    log(f"    balanceada (n={len(bal)}): VIF={np.round(vifs, 2).tolist()}, cond(X std)={cond_X:.2f}, cond(corr)={cond_corr:.2f}")
    log("    matriz corr residual (balanceada):\n" + cm.round(3).to_string())
# --- robustez de escala (spec A, par 0-2/3-5, cohortes 1988-2008): niveles sin los municipios mas grandes y dosis como share del total municipal ---
def key_metrics(df, label):
    r = residualize(df, ["a02", "a35"], "A", label)
    out = {"var_a02": var_share(df["a02"].values, r["a02"].values), "var_a35": var_share(df["a35"].values, r["a35"].values),
           "corr": corr(r["a02"].values, r["a35"].values), "n": len(df)}
    add("A", label, "var_resid_share_a02", out["var_a02"])
    add("A", label, "var_resid_share_a35", out["var_a35"])
    add("A", label, "corr_resid_a02_a35", out["corr"])
    add("A", label, "n_celdas_a02_a35", out["n"])
    return out


tot_m = pd.Series(V, index=Tlist)                       # PARA 1996-2006 con mes conocido, por municipio
top_munis = tot_m.index[tot_m > tot_m.quantile(0.99)].tolist()
top_names = [f"{names.loc[c, 'muni_name']} ({int(tot_m[c])})" for c in top_munis]
rob = {"niveles (titular)": {"var_a02": results["A"]["var_share_a02"], "var_a35": results["A"]["var_share_a35"],
                             "corr": results["A"]["corr_resid_a02_a35"], "n": len(both)}}
rob["niveles sin top 1% municipios"] = key_metrics(both[~both["cod"].isin(top_munis)], "1988-2008 niveles sin top1pct")
sh = both.assign(a02=both["a02"] / both["cod"].map(tot_m), a35=both["a35"] / both["cod"].map(tot_m))
rob["share del total municipal 1996-2006"] = key_metrics(sh, "1988-2008 share municipal")
log(f"\nRobustez de escala (spec A): top 1% municipios excluidos = {top_names}")
for k, v in rob.items():
    log(f"    {k}: var share 0-2={v['var_a02']:.3f}, 3-5={v['var_a35']:.3f}, corr resid 0-2/3-5={v['corr']:.3f} (n={v['n']})")

# VIF/condicion de las dosis brutas (balanceada) para referencia
bal = cells.dropna(subset=list(WINDOWS))
vraw, cX_raw, cC_raw = vif_cond(bal[list(WINDOWS)].values)
for w, v in zip(WINDOWS, vraw):
    add("bruto", "balanceada", f"VIF_{w}", v)
add("bruto", "balanceada", "cond_number_X_std", cX_raw)
add("bruto", "balanceada", "cond_number_corrmat", cC_raw)
cells = cells.join(cells_res).join(cells_res_B)

# --- (3) celdas con dosis 0-2 > 0 y 3-5 = 0 ---
n_both = int(both.shape[0])
n_02pos = int((both["a02"] > 0).sum())
n_02pos_35zero = int(both["cell_02pos_35zero"].sum())
share_02pos_35zero = n_02pos_35zero / n_both
share_among_02pos = n_02pos_35zero / n_02pos
rel = (both.loc[both["cell_02pos_35zero"], "cohort"] - both.loc[both["cell_02pos_35zero"], "exit_year"]).value_counts().sort_index()
by_cohort_02 = both.groupby("cohort").agg(n=("cod", "size"), n_02pos=("a02", lambda x: int((x > 0).sum())),
                                          n_02pos_35zero=("cell_02pos_35zero", "sum"),
                                          mean_iu=("iu", "mean"), mean_a02=("a02", "mean"), mean_a35=("a35", "mean"), mean_a611=("a611", "mean"))
n_only02_bal = int(((bal["a02"] > 0) & (bal["a35"] == 0) & (bal["a611"] == 0)).sum())
n_only02_bal_iu0 = int(((bal["a02"] > 0) & (bal["a35"] == 0) & (bal["a611"] == 0) & (bal["iu"] == 0)).sum())
add("conteo", "1988-2008", "n_celdas_a02pos", n_02pos)
add("conteo", "1988-2008", "n_celdas_a02pos_a35zero", n_02pos_35zero)
add("conteo", "1988-2008", "share_celdas_a02pos_a35zero", share_02pos_35zero)
add("conteo", "1988-2008", "share_a35zero_entre_a02pos", share_among_02pos)
add("conteo", "balanceada 1988-2003", "n_celdas_a02pos_a35zero_a611zero", n_only02_bal)
add("conteo", "balanceada 1988-2003", "n_celdas_a02pos_a35zero_a611zero_iuzero", n_only02_bal_iu0)
log(f"\n(3) celdas 0-2>0 & 3-5=0: {n_02pos_35zero} de {n_both} ({100 * share_02pos_35zero:.2f}%); entre celdas con 0-2>0 ({n_02pos}): {100 * share_among_02pos:.2f}%")
log("    cohorte - anio de salida anual en esas celdas: " + rel.to_dict().__str__())
log(f"    balanceada 1988-2003: 0-2>0 & 3-5=0 & 6-11=0: {n_only02_bal}; ademas in utero=0: {n_only02_bal_iu0}")

# --- (4) cohortes nacidas tras la salida ---
n_after = int(cells["born_after_exit"].sum())
n_after_le2006 = int((cells["born_after_exit"] & (cells["cohort"] <= 2006)).sum())
n_after_mes = int(cells["born_after_exit_mes"].fillna(False).sum())
n_after_le2006_mes = int((cells["born_after_exit_mes"].fillna(False) & (cells["cohort"] <= 2006)).sum())
munis_with_after_le2006 = int(cells.loc[cells["born_after_exit"] & (cells["cohort"] <= 2006), "cod"].nunique())
after_dose = cells.loc[cells["born_after_exit"], ["iu", "a02", "a35"]].describe().round(2)
add("conteo", "1988-2008", "n_celdas_nacido_tras_salida_anual", n_after)
add("conteo", "1988-2006", "n_celdas_nacido_tras_salida_anual_cohorte_le_2006", n_after_le2006)
add("conteo", "1988-2008", "n_munis_con_celdas_tras_salida_cohorte_le_2006", munis_with_after_le2006)
add("conteo", "1988-2008", "n_celdas_nacido_tras_salida_mes", n_after_mes)
add("conteo", "1988-2006", "n_celdas_nacido_tras_salida_mes_cohorte_le_2006", n_after_le2006_mes)
add("conteo", "1988-2008", "share_celdas_tras_salida_con_a02_pos", float((cells.loc[cells["born_after_exit"], "a02"] > 0).mean()))
log(f"\n(4) celdas nacidas tras la salida (anual): {n_after} de {len(cells)}; con cohorte <= 2006: {n_after_le2006} en {munis_with_after_le2006} municipios; "
    f"con salida por mes: {n_after_mes} (<=2006: {n_after_le2006_mes})")
log("    dosis en celdas tras salida (anual):\n" + after_dose.to_string())

# ----------------------------------------------------------------------------------------------
# 10. Veredicto y tablas T2 a disco
# ----------------------------------------------------------------------------------------------
S = pd.DataFrame(summary)


def getv(spec, sample_contains, metric):
    s = S[(S["spec"] == spec) & S["muestra"].str.contains(sample_contains, regex=False) & (S["metrica"] == metric)]
    return float(s["valor"].iloc[0]) if len(s) else np.nan


def classify(cr, vmin):
    if cr > 0.8 or vmin < 0.10:
        return "LETAL"
    if cr < 0.7 and vmin > 0.20:
        return "APROBADO"
    return "ZONA GRIS"


A = results["A"]
B = results["B"]
cr = A["corr_resid_a02_a35"]
vs02, vs35 = A["var_share_a02"], A["var_share_a35"]
verdict = classify(cr, min(vs02, vs35))
rob["asinh(dosis)"] = {"var_a02": getv("A", "1988-2008 asinh", "var_resid_share_a02"), "var_a35": getv("A", "1988-2008 asinh", "var_resid_share_a35"),
                       "corr": getv("A", "1988-2008 asinh", "corr_resid_a02_a35"), "n": n_both}
rob["niveles, balanceada 1988-2003"] = {"var_a02": getv("A", "balanceada", "var_resid_share_a02"), "var_a35": getv("A", "balanceada", "var_resid_share_a35"),
                                        "corr": getv("A", "balanceada", "corr_resid_a02_a35"), "n": A["n_bal"]}
for k, v in rob.items():
    v["veredicto"] = classify(v["corr"], min(v["var_a02"], v["var_a35"]))
verdict_txt = (f"{verdict}: corr residual 0-2/3-5 = {cr:.3f} (umbral aprobado < 0,7; letal > 0,8); varianza residual 0-2 = {100 * vs02:.1f}%, "
               f"3-5 = {100 * vs35:.1f}% (aprobado > 20%; letal < 10%); spec A (EF muni + cohorte x dpto), cohortes 1988-2008, dosis en niveles. "
               "Sensibilidad a la escala: " + "; ".join(f"{k}: corr {v['corr']:.2f}, var. res. 0-2 {100 * v['var_a02']:.0f}%, 3-5 {100 * v['var_a35']:.0f}% -> {v['veredicto']}"
                                                         for k, v in rob.items() if k != "niveles (titular)") + ".")
log(f"\nVEREDICTO T2: {verdict_txt}")

conv = pd.DataFrame(conv_rows)
conv.to_csv(f"{DER}/t2_B_T2_convergencia.csv", index=False)
pd.DataFrame(summary).to_csv(f"{DER}/t2_B_T2_resumen.csv", index=False)
cells.to_csv(f"{DER}/t2_B_T2_celdas.csv", index=False)
by_cohort_02.reset_index().to_csv(f"{DER}/t2_B_T2_por_cohorte.csv", index=False)
cm_out = pd.concat([results["corrmat_A"].add_prefix("A_"), results["corrmat_B"].add_prefix("B_")], axis=1)
cm_out.to_csv(f"{DER}/t2_B_T2_corr_resid_balanceada.csv")
log(f"\nConvergencia demeaning: max iteraciones={conv['iteraciones'].max()}, todas convergieron={bool(conv['convergio'].all())}, "
    f"max |diff| vs lstsq={conv['max_abs_diff_vs_lstsq'].max():.2e}")

# ----------------------------------------------------------------------------------------------
# 11. Resumen en markdown
# ----------------------------------------------------------------------------------------------
def fmt_pct(x):
    return f"{100 * x:.1f}%"


md = []
md.append("# T1/T2 (RA B): replicacion del PI y test de identificacion del perfil de edad\n")
md.append(f"Script: `code/exploration/t2_B.py` (implementacion independiente; panel reconstruido desde los xlsx crudos CNMH-OMC, corte marzo 2025, masacres + asesinatos selectivos). "
          f"Tablas: `data/derived/t2_B_*.csv`. Fecha de ejecucion: {time.strftime('%Y-%m-%d')}.\n")
md.append("## Definiciones y filtros\n")
md.append(f"- Victimas = `Total de Victimas del Caso`; PARA = `GRUPO PARAMILITAR` + `AGENTE DEL ESTADO - GRUPO PARAMILITAR`; POSD = posdesmovilizacion (+ mixto con Estado); GUE; EST; NI = resto (no identificado, desconocido, otro, crimen organizado, agente extranjero).")
md.append(f"- Casos con codigo DANE de 5 digitos y anio {YEAR_LO}-{YEAR_HI}: {len(cases)} de {n_raw}; se excluyen codigos de exterior (EXVEN, EXPAN, EXECU). El codigo `00000` ('SIN INFORMACION') se mantiene solo para replicar el conteo del PI.")
md.append(f"- Panel anual usa todos los casos (incl. Mes=0); panel mensual solo Mes 1-12 (ym = anio*12 + mes - 1). Mi panel mensual coincide exactamente con `cnmh_muni_month_victims.csv` del PI en las filas comunes (max |diff| = {max(chk_diff.values()):.0f}); las {chk_n_unmatched} filas que solo estan en el panel del PI son los codigos de exterior {list(chk_only_pi_codes)} que aqui se excluyen.\n")

md.append("## T1 (a): muestra T\n")
md.append("| Umbral PARA 1997-2006 | Municipios | Share victimas PARA 1997-2006 |\n|---|---|---|")
for r in thr_rows:
    md.append(f"| >= {r['umbral']} | {r['n_munis']} | {fmt_pct(r['share_victimas_para_9706'])} |")
md.append(f"\n- **{n_T_all} municipios con >= 25 victimas PARA 1997-2006 ({fmt_pct(share_T_all)} de {nat_para_9706:.0f} victimas PARA nacionales)**: replica exactamente el 453 / 94% del PI. "
          f"Uno de los 453 es `00000` = 'SIN INFORMACION' ({ptot.get(SIN_INFO, 0):.0f} victimas): pasa el filtro `\\d{{5}}` del PI pero no es un municipio. **T de trabajo (T1d y T2) = {n_T} municipios ({fmt_pct(share_T)})**.\n")

md.append("## T1 (b): entrada y salida anual (>= 3 victimas PARA, 1996-2006)\n")
md.append("| Anio | Salida (T={}) | Salida (453 con 00000) | Entrada (T) | PI (salida) |\n|---|---|---|---|---|".format(n_T))
pi_exit = {2003: 52, 2004: 93, 2005: 216, 2006: 64}
for y in range(1996, 2007):
    md.append(f"| {y} | {int(exit_counts.get(y, 0))} | {int(exit_counts_all.get(y, 0))} | {int(entry_counts.get(y, 0))} | {pi_exit.get(y, '')} |")
md.append(f"\n- Duracion (salida - entrada + 1): **mediana {med_dur:.0f} anios** (p25 = {dur_q['25%']:.0f}, p75 = {dur_q['75%']:.0f}, media {dur_q['mean']:.1f}); PI: mediana 9, cuartiles 7-10. "
          f"{SIN_INFO}: entrada {int(fl.loc[SIN_INFO, 'entry']) if SIN_INFO in fl.index and pd.notna(fl.loc[SIN_INFO, 'entry']) else 'NA'}, salida {int(fl.loc[SIN_INFO, 'exit']) if SIN_INFO in fl.index and pd.notna(fl.loc[SIN_INFO, 'exit']) else 'NA'}.\n")

md.append("## T1 (c): caida de la violencia total tras la desmovilizacion\n")
md.append(f"- Victimas TOTALES (todos los perpetradores) por anio en T: media 2000-02 = {ser_T.loc[2000:2002, 'TOT'].mean():.0f}, media 2007-10 = {ser_T.loc[2007:2010, 'TOT'].mean():.0f}, **ratio = {ratio_T:.3f}** (PI: 15.226 -> 1.856, 0,12). "
          f"Con `00000`: {ratio_Tall:.3f}; nacional (todos los municipios): {ratio_nat:.3f}; solo PARA+POSD en T: {ratio_T_pp:.3f}.")
md.append("\n| Anio | PARA | POSD | GUE | EST | NI | TOT |\n|---|---|---|---|---|---|---|")
for y, r in ser_T.loc[1996:2010].iterrows():
    md.append(f"| {y} | {int(r['PARA'])} | {int(r['POSD'])} | {int(r['GUE'])} | {int(r['EST'])} | {int(r['NI'])} | {int(r['TOT'])} |")
md.append("")

md.append("## T1 (d) NUEVO: mes de salida municipal\n")
md.append(f"Definicion: primer mes m (1996-01..2006-12) tal que las victimas PARA con mes conocido en [m, dic-2006] son <= {100 * EXIT_SHARE:.0f}% del total municipal 1996-2006 con mes conocido. "
          f"Los casos con Mes=0 (sin dato) no entran en el panel mensual. Variantes de inclusion de municipios: V1 = todos los {n_T}; **V2 (primaria) = municipios cuyas victimas PARA 1996-2006 con Mes=0 son <= {100 * MES0_MAX_SHARE:.0f}% del total municipal** (un mes faltante no puede mover el corte del 5%); V3 (literal estricta) = municipios sin ningun caso PARA con Mes=0 en 1996-2006.\n")
md.append("| Variante | Municipios incluidos | Con mes de salida | Share PARA 1997-2006 nacional | Share PARA 1997-2006 de T |\n|---|---|---|---|---|")
for _, r in cov_table.iterrows():
    md.append(f"| {r['variante']} | {int(r['n_munis_incluidos'])} | {int(r['n_con_mes_salida'])} | {fmt_pct(r['share_para_9706_nacional'])} | {fmt_pct(r['share_para_9706_en_T'])} |")
md.append("\nDistribucion del mes de salida por semestre:\n")
md.append("| Semestre | " + " | ".join(sem_table.columns) + " |\n|---|" + "---|" * len(sem_table.columns))
for s, r in sem_table.iterrows():
    md.append(f"| {s} | " + " | ".join(str(int(v)) for v in r.values) + " |")
md.append(f"\n- Anio del mes de salida menos anio de salida anual (V2): {diff_vc.to_dict()} (0 = mismo anio; +1 = la salida mensual cae en enero del anio siguiente o la cola del 5% se extiende). "
          f"Criterio del PI (mes de salida para municipios con >= 80% de las victimas): V2 cubre {fmt_pct(cov_primary)} de las victimas PARA 1997-2006 nacionales.\n")

md.append("## T2: test de identificacion del perfil de edad\n")
md.append(f"Celdas municipio x cohorte: {n_T} municipios de T x cohortes 1988-2008 = {len(cells)}. Nacimiento en julio de c. Dosis = victimas PARA del panel mensual (solo Mes>=1) en in utero (-9..-1), 0-2 (0..35), 3-5 (36..71), 6-11 (72..143) meses; faltante si la ventana sale de 1985-2015 "
          f"(6-11 disponible solo para cohortes {avail['a611'][0]}-{avail['a611'][-1]}; las demas para {avail['a02'][0]}-{avail['a02'][-1]}). "
          f"Nota: por construccion del CNMH no hay victimas PARA despues de 2006 (se reetiquetan como posdesmovilizacion), asi que las dosis de las cohortes 2007-2008 son 0 en todas las ventanas postnatales.\n")
md.append(f"Departamentos en T: {len(dep_n)}; {len(single_deptos)} con un solo municipio en T ({', '.join(single_deptos)}): bajo EF cohorte x dpto su residuo es 0 por construccion, por eso se reporta tambien 'sin dpto singleton'.\n")
md.append(f"Residualizacion: demeaning iterado (tolerancia 1e-9 relativa) verificado contra regresion con dummies (lstsq): max iteraciones {conv['iteraciones'].max()}, todas convergen, max |diff| vs lstsq = {conv['max_abs_diff_vs_lstsq'].max():.1e}.\n")
md.append(f"### (1) Correlacion bruta\n\n- corr(0-2, 3-5) bruta = **{corr_raw_02_35:.3f}** (n = {n_both}); in utero/0-2 = {getv('bruto', '1988', 'corr_bruta_iu_a02'):.3f}; 3-5/6-11 = {getv('bruto', '1988-2003', 'corr_bruta_a35_a611'):.3f}. Spearman 0-2/3-5 = {getv('bruto', '1988-2008', 'corr_bruta_spearman_a02_a35'):.3f}.\n")
md.append("### (2) y (6) Varianza residual y correlaciones residuales\n")
md.append("| Metrica | Spec A: EF muni + cohorte x dpto | A sin dpto singleton | A asinh(dosis) | Spec B: EF muni + cohorte | Muestra (cohortes) |\n|---|---|---|---|---|---|")
for w in WINDOWS:
    lab = f"{avail[w][0]}-{avail[w][-1]}"
    md.append(f"| var. residual / bruta, {WLAB[w]} | {fmt_pct(A[f'var_share_{w}'])} | {fmt_pct(getv('A', lab + ' sin dpto singleton', f'var_resid_share_{w}'))} | "
              f"{fmt_pct(getv('A', 'asinh', f'var_resid_share_{w}'))} | {fmt_pct(B[f'var_share_{w}'])} | {lab} |")
for p, q in PAIRS:
    s = cells[cells[p].notna() & cells[q].notna()]
    lab = f"{s['cohort'].min()}-{s['cohort'].max()}"
    md.append(f"| corr residual {WLAB[p]} / {WLAB[q]} | {A[f'corr_resid_{p}_{q}']:.3f} | {getv('A', lab + ' sin dpto singleton', f'corr_resid_{p}_{q}'):.3f} | "
              f"{getv('A', lab + ' asinh', f'corr_resid_{p}_{q}'):.3f} | {B[f'corr_resid_{p}_{q}']:.3f} | {lab} |")
md.append("\nMatriz de correlaciones residuales, muestra balanceada (4 ventanas, cohortes 1988-2003, n = {}):\n".format(A["n_bal"]))
md.append("| | " + " | ".join(f"A: {WLAB[w]}" for w in WINDOWS) + " | " + " | ".join(f"B: {WLAB[w]}" for w in WINDOWS) + " |\n|---|" + "---|" * 8)
for w in WINDOWS:
    md.append(f"| {WLAB[w]} | " + " | ".join(f"{results['corrmat_A'].loc[w, v]:.3f}" for v in WINDOWS) + " | " + " | ".join(f"{results['corrmat_B'].loc[w, v]:.3f}" for v in WINDOWS) + " |")
md.append(f"\nDiferencia A vs B: la spec B (EF cohorte comunes) deja en el residuo toda la variacion departamental del ciclo paramilitar (la expansion 1997-2002 y la salida 2003-06 difieren por region); la spec A la absorbe. "
          f"La varianza residual de 0-2 pasa de {fmt_pct(B['var_share_a02'])} (B) a {fmt_pct(A['var_share_a02'])} (A) y la correlacion residual 0-2/3-5 de {B['corr_resid_a02_a35']:.3f} (B) a {A['corr_resid_a02_a35']:.3f} (A). "
          f"En niveles la diferencia es pequena porque la variacion dominante es la de los municipios grandes dentro de su departamento, que ningun EF de cohorte absorbe; en asinh la diferencia es mayor (var. residual 0-2: {fmt_pct(getv('B', '1988-2008 asinh', 'var_resid_share_a02'))} en B vs {fmt_pct(getv('A', '1988-2008 asinh', 'var_resid_share_a02'))} en A; corr 0-2/3-5: {getv('B', '1988-2008 asinh', 'corr_resid_a02_a35'):.3f} vs {getv('A', '1988-2008 asinh', 'corr_resid_a02_a35'):.3f}).\n")
md.append("### Robustez de escala de la dosis (spec A, par 0-2/3-5)\n")
md.append("| Escala / muestra | var. residual 0-2 | var. residual 3-5 | corr residual 0-2/3-5 | n celdas | Umbrales PI |\n|---|---|---|---|---|---|")
for k, v in rob.items():
    md.append(f"| {k} | {fmt_pct(v['var_a02'])} | {fmt_pct(v['var_a35'])} | {v['corr']:.3f} | {v['n']} | {v['veredicto']} |")
md.append(f"\nTop 1% de municipios excluidos en la fila correspondiente (victimas PARA 1996-2006 con mes conocido): {', '.join(top_names)}. "
          "La fila 'share del total municipal' divide cada dosis por el total PARA 1996-2006 del municipio: aisla la variacion de *timing* y elimina la de escala. "
          "Lectura: " + "; ".join(f"{k} -> {v['veredicto']}" for k, v in rob.items()) + ". "
          f"Correlacion residual 0-2/3-5 maxima entre escalas = {max(v['corr'] for v in rob.values()):.3f} (umbral letal 0,8); varianza residual minima (0-2 o 3-5) entre escalas = {fmt_pct(min(min(v['var_a02'], v['var_a35']) for v in rob.values()))} (umbral letal 10%). "
          "En escala relativa (asinh, share) la mayor parte de la variacion bruta es el ciclo comun del departamento y la escala del municipio, que los EF absorben; el veredicto sobre la varianza residual depende de como entre la dosis en la regresion del perfil.\n")
md.append("### (3) Celdas con dosis 0-2 > 0 y 3-5 = 0\n")
md.append(f"- {n_02pos_35zero} de {n_both} celdas ({fmt_pct(share_02pos_35zero)}); entre las {n_02pos} celdas con dosis 0-2 > 0, {fmt_pct(share_among_02pos)}. "
          f"Posicion relativa a la salida anual (cohorte - anio de salida): {rel.to_dict()}. En la muestra balanceada 1988-2003, celdas con 0-2 > 0, 3-5 = 0 y 6-11 = 0: {n_only02_bal} (y ademas in utero = 0: {n_only02_bal_iu0}).\n")
md.append("### (4) Cohortes nacidas tras la salida\n")
md.append(f"- Celdas con cohorte > anio de salida anual: **{n_after}** de {len(cells)}; de ellas {n_after_le2006} con cohorte <= 2006 (en {munis_with_after_le2006} municipios), que son las unicas que distinguen 'tras la salida local' de 'tras el fin nacional' (las cohortes 2007-08 son post-salida en todos los municipios: {int((cells['cohort'] >= 2007).sum())} celdas). "
          f"Con el anio del mes de salida (T1d, V1): {n_after_mes} (<= 2006: {n_after_le2006_mes}). Dosis media 0-2 en las celdas post-salida (anual) = {cells.loc[cells['born_after_exit'], 'a02'].mean():.2f} victimas, "
          f"share con 0-2 > 0 = {fmt_pct(float((cells.loc[cells['born_after_exit'], 'a02'] > 0).mean()))} (la cola de <3 victimas/anio tras la salida).\n")
md.append("### (5) Colinealidad conjunta (muestra balanceada 1988-2003, dosis residualizadas)\n")
md.append("| | VIF in utero | VIF 0-2 | VIF 3-5 | VIF 6-11 | cond(X estandarizada) | cond(matriz corr) |\n|---|---|---|---|---|---|---|")
md.append(f"| bruto | " + " | ".join(f"{v:.2f}" for v in vraw) + f" | {cX_raw:.2f} | {cC_raw:.2f} |")
md.append(f"| Spec A | " + " | ".join(f"{v:.2f}" for v in A['vifs']) + f" | {A['cond_X']:.2f} | {A['cond_corr']:.2f} |")
md.append(f"| Spec B | " + " | ".join(f"{v:.2f}" for v in B['vifs']) + f" | {B['cond_X']:.2f} | {B['cond_corr']:.2f} |")
md.append("\n### Veredicto frente a los umbrales del PI\n")
md.append(f"**{verdict_txt}**\n")
md.append("### Diferencias con el PI y caveats\n")
md.append(f"- Replicacion T1: 453 municipios, {fmt_pct(share_T_all)}, salida {exit_counts_all.get(2003, 0)}/{exit_counts_all.get(2004, 0)}/{exit_counts_all.get(2005, 0)}/{exit_counts_all.get(2006, 0)} (2003-06), mediana {med_dur:.0f} anios y ratio {ratio_T:.2f}: coincide con el PI. El 453 incluye `00000` (SIN INFORMACION).")
md.append("- El 5% del mes de salida se calcula sobre victimas con mes conocido; los casos con Mes=0 (~1% de las victimas PARA) se ignoran. Para municipios pequenos (25-40 victimas) el corte del 5% equivale al ultimo caso, lo que hace el mes de salida ruidoso; V2 solo controla el sesgo por meses faltantes, no ese ruido.")
md.append(f"- Dosis en niveles (como pide la tarea): la varianza bruta esta dominada por los municipios grandes, y es ahi donde los EF absorben menos. Sin el top 1% de municipios y con la dosis como share del total municipal el veredicto se mantiene (varianza residual {fmt_pct(rob['niveles sin top 1% municipios']['var_a02'])} y {fmt_pct(rob['share del total municipal 1996-2006']['var_a02'])} en 0-2); en asinh baja a {fmt_pct(rob['asinh(dosis)']['var_a02'])} (0-2) y {fmt_pct(rob['asinh(dosis)']['var_a35'])} (3-5), zona gris. El umbral del PI (>20%) no especifica la escala: recomiendo fijarla antes de declarar aprobado/letal, y usar la version per capita (poblacion DANE) cuando este disponible. Las dosis de 6-11 solo existen para 1988-2003 y las de 2007-08 son cero por construccion (reetiquetado CNMH a posdesmovilizacion), lo que infla mecanicamente la variacion entre cohortes que absorben los EF cohorte x dpto; la muestra balanceada 1988-2003 da varianzas residuales mas bajas por ese motivo.")
md.append("- Los dos municipios de T sin mes de salida (Abriaqui, Riofrio) tienen victimas en diciembre de 2006 por encima del 5% de un total pequeno: estan censurados a dic-2006, no faltan por datos.")
md.append("- La residualizacion aqui es de cada dosis por separado (lo que pide T2); en la regresion del perfil Y = sum_a beta_a V_{m,c+a} + mu_m + lambda_{c x dpto} lo relevante es la matriz completa de dosis residualizadas, de ahi el VIF y el numero de condicion.")
md.append(f"\nTiempo de ejecucion: {time.time() - t0:.0f} s.\n")
md.append("## Log de ejecucion\n\n```\n" + "\n".join(log_lines) + "\n```\n")
with open(MD_OUT, "w", encoding="utf-8") as f:
    f.write("\n".join(md))
print(f"\nResumen escrito en {MD_OUT}; tiempo total {time.time() - t0:.0f} s")
