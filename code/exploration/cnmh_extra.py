import sys, pandas as pd, os, warnings
warnings.filterwarnings("ignore")
d = sys.argv[1]
ma = pd.read_excel(os.path.join(d,"CMasacres_202503.xlsx")); as_ = pd.read_excel(os.path.join(d,"CAsesionatosSelectivos_202503.xlsx"))
for df in (ma, as_):
    for c in ["Año","Mes","Total de Víctimas del Caso"]: df[c]=pd.to_numeric(df[c],errors="coerce")
print("MA victims 1998-2002 total:", int(ma[(ma.Año>=1998)&(ma.Año<=2002)]["Total de Víctimas del Caso"].sum()), "cases:", int(((ma.Año>=1998)&(ma.Año<=2002)).sum()))
print("MA cases 1958-2019:", int(((ma.Año>=1958)&(ma.Año<=2019)).sum()), " MA victims all:", int(ma["Total de Víctimas del Caso"].sum()), " min victims per case:", int(ma["Total de Víctimas del Caso"].min()))
print("MA cases 2022+ with 3 victims:", int(((ma.Año>=2022)&(ma["Total de Víctimas del Caso"]==3)).sum()), " pre-2022 with 3:", int(((ma.Año<2022)&(ma["Total de Víctimas del Caso"]==3)).sum()))
print("AS victims all:", int(as_["Total de Víctimas del Caso"].sum()), " AS cases 1981-2012:", int(((as_.Año>=1981)&(as_.Año<=2012)).sum()))
# paramilitar incl. mixed state-para, 1996-2010 by year: cases, victims, and share with bloque identified
para_set = ["GRUPO PARAMILITAR","AGENTE DEL ESTADO - GRUPO PARAMILITAR"]
for name, df in (("MA",ma),("AS",as_)):
    w = df[(df.Año>=1996)&(df.Año<=2010)&(df["Presunto Responsable"].isin(para_set))].copy()
    w["bloque_id"] = ~w["Descripción Presunto Responsable"].isin(["NO IDENTIFICADO","NO IDENTIFICADA","NO APLICA","OTRO","OTRA","AUTODEFENSAS UNIDAS DE COLOMBIA AUC"])
    w["auc_generic"] = w["Descripción Presunto Responsable"].eq("AUTODEFENSAS UNIDAS DE COLOMBIA AUC")
    g = w.groupby("Año").agg(casos=("ID Caso","size"), victimas=("Total de Víctimas del Caso","sum"), pct_estructura=("bloque_id","mean"), pct_auc_generica=("auc_generic","mean"), mes_missing=("Mes", lambda s:(s==0).sum()))
    g["pct_estructura"]=(100*g["pct_estructura"]).round(1); g["pct_auc_generica"]=(100*g["pct_auc_generica"]).round(1)
    print("\n==", name, "PARAMILITAR (+AGENTE DEL ESTADO-PARAMILITAR) 1996-2010\n", g.to_string())
    # municipality-month coverage
    w2 = w[w.Mes>0]
    mm = w2.groupby(["Código DANE de Municipio","Año","Mes"]).size()
    print(name, "mun-months with >=1 para event 1996-2010:", len(mm), "of", 1122*15*12, "=> %.2f%%" % (100*len(mm)/(1122*15*12)))
    w3 = w[(w.Año>=1997)&(w.Año<=2002)&(w.Mes>0)]
    mm3 = w3.groupby(["Código DANE de Municipio","Año","Mes"]).size()
    print(name, "mun-months with >=1 para event 1997-2002:", len(mm3), "of", 1122*6*12, "=> %.2f%%" % (100*len(mm3)/(1122*6*12)), " municipios:", w3["Código DANE de Municipio"].nunique())
# Department distribution of paramilitary massacres 1997-2002
w = ma[(ma.Año>=1997)&(ma.Año<=2002)&(ma["Presunto Responsable"]=="GRUPO PARAMILITAR")]
print("\nMA paramilitar 1997-2002 by departamento (top 15):\n", w["Departamento"].value_counts().head(15).to_string())
print("\nRegión values:", ma["Región"].value_counts().to_dict())
print("\nOtro Hecho Simultáneo sample:", ma["Otro Hecho Simultáneo"].value_counts(dropna=False).head(8).to_dict())
print("Desplazamiento Forzado flag values:", ma["Desplazamiento Forzado"].value_counts(dropna=False).to_dict())
print("ID Caso sample:", ma["ID Caso"].head(3).tolist(), " ID Caso Relacionado sample:", ma["ID Caso Relacionado"].dropna().head(3).tolist())
# GUERRILLA description top for comparison
print("\nGUERRILLA descripciones MA:", ma[ma["Presunto Responsable"]=="GUERRILLA"]["Descripción Presunto Responsable"].value_counts().head(8).to_dict())
# POSDESMOV description
print("POSDESMOV descripciones AS:", as_[as_["Presunto Responsable"]=="GRUPO POSDESMOVILIZACIÓN"]["Descripción Presunto Responsable"].value_counts().head(8).to_dict())
# share 1996-2010 para massacres with Mes==0 and SIN INFORMACION municipio
w = ma[(ma.Año>=1996)&(ma.Año<=2010)]
print("\nMA 1996-2010 Municipio SIN INFORMACION:", int(w["Municipio"].astype(str).str.contains("SIN INFORMACION").sum()), " AS 1996-2010:", int(as_[(as_.Año>=1996)&(as_.Año<=2010)]["Municipio"].astype(str).str.contains("SIN INFORMACION").sum()))
