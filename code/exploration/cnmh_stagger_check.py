# Uso: python3 -I cnmh_stagger_check.py <CMasacres_202503.xlsx> <CAsesionatosSelectivos_202503.xlsx>
# Ronda 3 (24-oct-2026): entrada/salida municipal, dosis en los 3 ultimos anos, reetiquetado 2006, entrada endogena.
import sys, warnings
warnings.filterwarnings("ignore")
import pandas as pd, numpy as np
pd.set_option("display.width", 250); pd.set_option("display.max_rows", 500); pd.set_option("display.max_columns", 60)
ma_path, as_path = sys.argv[1], sys.argv[2]

def load(p, mod):
    df = pd.read_excel(p, sheet_name=0)
    for c in ["Año", "Mes", "Total de Víctimas del Caso"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df["cod"] = df["Código DANE de Municipio"].astype(str).str.replace(r"\.0$", "", regex=True).str.zfill(5)
    df["mod"] = mod
    r = df["Presunto Responsable"].astype(str).str.upper()
    df["resp"] = np.select(
        [r.str.contains("POSDESMOV"), r.eq("GRUPO PARAMILITAR"), r.str.contains("PARAMILITAR"),
         r.str.contains("GUERRILLA"), r.str.contains("AGENTE DEL ESTADO"), r.str.contains("NO IDENTIFICADO"),
         r.str.contains("DESCONOCIDO")],
        ["POSDESM", "PARA", "PARA_MIX", "GUER", "ESTADO", "NOID", "DESC"], default="OTRO")
    df["vic"] = df["Total de Víctimas del Caso"].fillna(1).clip(lower=1)
    return df[["cod", "Municipio", "Departamento", "Año", "Mes", "resp", "vic", "mod"]]

ma = load(ma_path, "MA"); as_ = load(as_path, "AS")
d = pd.concat([ma, as_], ignore_index=True)
d = d[d["cod"].str.fullmatch(r"\d{5}") & (d["Año"] >= 1985) & (d["Año"] <= 2012)]
print("== Víctimas (MA+AS) 1985-2012 por categoría de responsable ==")
print(d.groupby("resp")["vic"].agg(["count", "sum"]).to_string())

py = d.pivot_table(index=["cod", "Año"], columns="resp", values="vic", aggfunc="sum", fill_value=0)
for c in ["PARA", "PARA_MIX", "POSDESM", "GUER", "ESTADO", "NOID", "DESC", "OTRO"]:
    if c not in py.columns: py[c] = 0
py = py.reset_index()
codes = sorted(d["cod"].unique()); years = list(range(1985, 2013))
grid = pd.MultiIndex.from_product([codes, years], names=["cod", "Año"]).to_frame(index=False)
py = grid.merge(py, on=["cod", "Año"], how="left").fillna(0)
py["P"] = py["PARA"] + py["PARA_MIX"]
py["TOT"] = py[["PARA", "PARA_MIX", "POSDESM", "GUER", "ESTADO", "NOID", "DESC", "OTRO"]].sum(axis=1)
names = d.drop_duplicates("cod").set_index("cod")[["Municipio", "Departamento"]]

W = py[(py["Año"] >= 1997) & (py["Año"] <= 2006)]
ptot = W.groupby("cod")["P"].sum()
print("\n== Municipios por víctimas paramilitares (MA+AS) 1997-2006 ==")
for k in [1, 10, 25, 50, 100, 250]:
    print(f"  >= {k:>3}: {(ptot >= k).sum()}")
T = ptot[ptot >= 25].index  # muestra 'tratada' de trabajo
print(f"\nMuestra T (>=25 víctimas para 1997-2006): {len(T)} municipios; víctimas para en T = {ptot[T].sum():.0f} de {ptot.sum():.0f} ({100*ptot[T].sum()/ptot.sum():.1f}%)")

pt = py[py["cod"].isin(T)].copy()
# entrada y salida: primer/último año 1996-2006 con >=3 víctimas paramilitares
def first_last(g, thr=3):
    gg = g[(g["Año"] >= 1996) & (g["Año"] <= 2006) & (g["P"] >= thr)]
    if len(gg) == 0: return pd.Series({"entry": np.nan, "exit": np.nan})
    return pd.Series({"entry": gg["Año"].min(), "exit": gg["Año"].max()})
fl = pt.groupby("cod").apply(first_last)
pre = pt[(pt["Año"] >= 1988) & (pt["Año"] <= 1995)].groupby("cod")["P"].sum()
fl["pre_para_88_95"] = pre
fl["pre_any"] = (pre >= 3)
print("\n== Distribución del año de ENTRADA (primer año >=3 víctimas para), T ==")
print(fl["entry"].value_counts().sort_index().to_string())
print("\n== Distribución del año de SALIDA (último año >=3 víctimas para, techo 2006), T ==")
print(fl["exit"].value_counts().sort_index().to_string())
print(f"\nMunicipios de T con violencia paramilitar ya en 1988-95 (>=3 víctimas): {fl['pre_any'].sum()} de {len(fl)} ({100*fl['pre_any'].mean():.0f}%)")
print("\n== Tabla cruzada entrada x salida (T) ==")
print(pd.crosstab(fl["entry"], fl["exit"]).to_string())
dur = fl["exit"] - fl["entry"] + 1
print("\n== Duración (años con para activa, entrada→salida) en T: cuantiles ==")
print(dur.describe(percentiles=[.1, .25, .5, .75, .9]).to_string())

# dosis en los ÚLTIMOS 3 años antes de la salida (celda '0-2 solo') y en los PRIMEROS 3 años
def dose_shares(g):
    e, x = fl.loc[g.name, "entry"], fl.loc[g.name, "exit"]
    if np.isnan(e): return pd.Series({"last3": np.nan, "first3": np.nan})
    tot = g[(g["Año"] >= 1996) & (g["Año"] <= 2006)]["P"].sum()
    last3 = g[(g["Año"] >= x - 2) & (g["Año"] <= x)]["P"].sum() / tot
    first3 = g[(g["Año"] >= e) & (g["Año"] <= e + 2)]["P"].sum() / tot
    return pd.Series({"last3": last3, "first3": first3})
ds = pt.groupby("cod").apply(dose_shares)
print("\n== Share de la dosis paramilitar 1996-2006 recibida en los 3 últimos años antes de la salida (T) ==")
print(ds["last3"].describe(percentiles=[.1, .25, .5, .75, .9]).to_string())
print("\n== Share en los 3 primeros años desde la entrada (T) ==")
print(ds["first3"].describe(percentiles=[.1, .25, .5, .75, .9]).to_string())

# reetiquetado: serie anual en T por categoría
print("\n== Víctimas anuales en T por categoría, 1996-2010 (¿la caída de 2006 es real?) ==")
ser = pt[(pt["Año"] >= 1996) & (pt["Año"] <= 2010)].groupby("Año")[["P", "POSDESM", "NOID", "DESC", "GUER", "ESTADO", "TOT"]].sum().astype(int)
ser["P+POSDESM+NOID+DESC"] = ser["P"] + ser["POSDESM"] + ser["NOID"] + ser["DESC"]
print(ser.to_string())
m0002 = ser.loc[2000:2002, "TOT"].mean(); m0710 = ser.loc[2007:2010, "TOT"].mean(); m0305 = ser.loc[2003:2005, "TOT"].mean()
print(f"\nTOT medio 2000-02 = {m0002:.0f}; 2003-05 = {m0305:.0f}; 2007-10 = {m0710:.0f}; ratio 2007-10 / 2000-02 = {m0710/m0002:.2f}")

# por grupo de año de salida: ¿cae la violencia TOTAL tras la salida?
print("\n== Por año de salida: TOTAL de víctimas (todas las categorías) alrededor de la salida, suma en T ==")
rows = []
for x in [2003, 2004, 2005, 2006]:
    cs = fl.index[fl["exit"] == x]
    if len(cs) == 0: continue
    g = pt[pt["cod"].isin(cs)]
    rel = {k: int(g[g["Año"] == x + k]["TOT"].sum()) for k in range(-3, 5)}
    relP = {k: int(g[g["Año"] == x + k]["P"].sum()) for k in range(-3, 5)}
    rows.append((x, len(cs), rel, relP))
for x, n, rel, relP in rows:
    print(f"salida {x} (n={n}): TOT por t-rel  {rel}")
    print(f"                 PARA por t-rel {relP}")

# entrada endógena: guerrilla 1988-1995 por grupo de año de entrada, vs no tratados
g8895 = py[(py["Año"] >= 1988) & (py["Año"] <= 1995)].groupby("cod")[["GUER", "TOT"]].sum()
g8895["entry"] = fl["entry"]
g8895["grp"] = g8895["entry"].fillna(-1).astype(int).astype(str)
g8895.loc[~g8895.index.isin(T), "grp"] = "no-T"
print("\n== Violencia 1988-95 (guerrilla y total, media por municipio) según año de entrada paramilitar ==")
print(g8895.groupby("grp")[["GUER", "TOT"]].agg(["mean", "median", "count"]).round(1).to_string())

# municipios de referencia
ref = {"54810": "TIBU", "13244": "EL CARMEN DE BOLIVAR", "76834": "TULUA", "05649": "SAN CARLOS", "05604": "REMEDIOS",
       "20001": "VALLEDUPAR", "85001": "YOPAL", "23807": "TIERRALTA", "47189": "CIENAGA", "13688": "SANTA ROSA DEL SUR",
       "05837": "TURBO", "05001": "MEDELLIN", "70508": "OVEJAS", "54250": "EL TARRA"}
print("\n== Series 1996-2010 en municipios de referencia: PARA / TOTAL (verificar nombre) ==")
for c, nm in ref.items():
    if c not in names.index: print(f"{c} {nm}: no está en el archivo"); continue
    g = py[(py["cod"] == c) & (py["Año"] >= 1996) & (py["Año"] <= 2010)].set_index("Año")
    print(f"{c} {names.loc[c,'Municipio']} ({names.loc[c,'Departamento']}) [esperado {nm}] entry={fl['entry'].get(c, np.nan)} exit={fl['exit'].get(c, np.nan)}")
    print("   PARA :", g["P"].astype(int).tolist())
    print("   TOTAL:", g["TOT"].astype(int).tolist())
