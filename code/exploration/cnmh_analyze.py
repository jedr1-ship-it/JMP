import sys, pandas as pd, os, warnings
warnings.filterwarnings("ignore")
d = sys.argv[1]
pd.set_option("display.width", 250); pd.set_option("display.max_rows", 500); pd.set_option("display.max_columns", 50)
files = {"MA": "CMasacres_202503.xlsx", "AS": "CAsesionatosSelectivos_202503.xlsx"}
for k, fn in files.items():
    df = pd.read_excel(os.path.join(d, fn), sheet_name=0)
    for c in ["Año","Mes","Día","Total de Víctimas del Caso"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    print("\n################", k, fn, "rows", len(df))
    print("\n-- Modalidad:\n", df["Modalidad"].value_counts(dropna=False).to_string())
    print("\n-- Presunto Responsable:\n", df["Presunto Responsable"].value_counts(dropna=False).to_string())
    print("\n-- Descripción Presunto Responsable (top 45):\n", df["Descripción Presunto Responsable"].value_counts(dropna=False).head(45).to_string())
    pm = df[df["Presunto Responsable"]=="GRUPO PARAMILITAR"]
    print("\n-- Descripción para GRUPO PARAMILITAR (top 40 / n distinct=%d):\n" % pm["Descripción Presunto Responsable"].nunique(), pm["Descripción Presunto Responsable"].value_counts(dropna=False).head(40).to_string())
    print("\n-- Tipo de Armas (top10):\n", df["Tipo de Armas"].value_counts(dropna=False).head(10).to_string())
    print("\n-- Año==0:", int((df["Año"]==0).sum()), " Mes==0:", int((df["Mes"]==0).sum()), " Día==0:", int((df["Día"]==0).sum()), " Mes NaN:", int(df["Mes"].isna().sum()))
    print("-- Código DANE dtype:", df["Código DANE de Municipio"].dtype, " sample:", df["Código DANE de Municipio"].head(5).tolist(), " n unique:", df["Código DANE de Municipio"].nunique())
    print("-- Municipio SIN INFORMACION:", int((df["Municipio"].astype(str).str.upper().str.contains("SIN INFORMACION")).sum()), " Departamento EXTERIOR:", int((df["Departamento"].astype(str)=="EXTERIOR").sum()))
    print("-- ID Caso Relacionado non-null:", int(df["ID Caso Relacionado"].notna().sum()))
    print("-- Latitud==0 / NaN:", int(((df["Latitud"]==0)|df["Latitud"].isna()).sum()))
    w = df[(df["Año"]>=1996)&(df["Año"]<=2010)].copy()
    print("\n-- 1996-2010: rows", len(w), " Mes==0:", int((w["Mes"]==0).sum()), " Día==0:", int((w["Día"]==0).sum()))
    wp = w[w["Presunto Responsable"]=="GRUPO PARAMILITAR"]
    print("-- 1996-2010 PARAMILITAR: rows", len(wp), " Mes==0:", int((wp["Mes"]==0).sum()), " Día==0:", int((wp["Día"]==0).sum()))
    tab = w.groupby(["Año","Presunto Responsable"]).size().unstack(fill_value=0)
    tab["TOTAL"] = tab.sum(axis=1)
    print("\n-- CASOS por año x responsable 1996-2010:\n", tab.to_string())
    tabv = w.groupby(["Año","Presunto Responsable"])["Total de Víctimas del Caso"].sum().unstack(fill_value=0)
    tabv["TOTAL"] = tabv.sum(axis=1)
    print("\n-- VÍCTIMAS por año x responsable 1996-2010:\n", tabv.to_string())
    # full-period totals by responsible
    print("\n-- Víctimas totales (todos los años) por responsable:\n", df.groupby("Presunto Responsable")["Total de Víctimas del Caso"].sum().to_string())
    # coverage 1997-2002
    cov = df[(df["Año"]>=1997)&(df["Año"]<=2002)]
    allm = df["Código DANE de Municipio"].nunique()
    print("\n-- Cobertura 1997-2002: municipios con >=1 caso (cualquier resp):", cov["Código DANE de Municipio"].nunique(),
          " | con >=1 caso PARAMILITAR:", cov[cov["Presunto Responsable"]=="GRUPO PARAMILITAR"]["Código DANE de Municipio"].nunique(),
          " | con >=1 GUERRILLA:", cov[cov["Presunto Responsable"]=="GUERRILLA"]["Código DANE de Municipio"].nunique(),
          " | municipios únicos en todo el archivo:", allm)
    cov2 = df[(df["Año"]>=1996)&(df["Año"]<=2010)]
    print("-- Cobertura 1996-2010: municipios con >=1 caso PARAMILITAR:", cov2[cov2["Presunto Responsable"]=="GRUPO PARAMILITAR"]["Código DANE de Municipio"].nunique())
    # monthly distribution check for paramilitar 1996-2010
    print("-- Meses (PARAMILITAR 1996-2010):", wp["Mes"].value_counts().sort_index().to_dict())
    # Descripción paramilitar 1996-2010 top
    print("\n-- Descripción PARAMILITAR 1996-2010 (top 30):\n", wp["Descripción Presunto Responsable"].value_counts().head(30).to_string())
