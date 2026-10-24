import pandas as pd, sys, warnings
warnings.filterwarnings('ignore')
AUC = {"54810":"Tibu","54250":"El Tarra","54800":"Teorama","54206":"Convencion","13244":"El Carmen de Bolivar","70713":"San Onofre","70508":"Ovejas","13442":"Maria la Baja","76834":"Tulua","76111":"Buga","76113":"Bugalagrande","20001":"Valledupar","20238":"El Copey","47288":"Fundacion","47189":"Cienaga","05649":"San Carlos","05313":"Granada","05197":"Cocorna","13688":"Santa Rosa del Sur","13670":"San Pablo","05604":"Remedios","05736":"Segovia","85001":"Yopal","50568":"Puerto Gaitan","50325":"Mapiripan"}
base='/tmp/claude-0/-home-user/40b2b058-37e9-5cd5-a91b-60b9905d5a88/scratchpad/dl2/ruv_jngaravitoc/'
# 1) Desplazados por año
d=pd.read_excel(base+'Reporte_Personas_Desplazados_por_Anio.xlsx', dtype=str)
print("cols:", d.columns.tolist()); print("TIPO DE VICTIMA:", d['TIPO DE VICTIMA'].value_counts().to_dict())
d['ANIO']=pd.to_numeric(d['ANIO'],errors='coerce'); 
for c in ['PERSONAS EXPULSADOS','PERSONAS RECIBIDOS','PERSONAS DECLARADOS']: d[c]=pd.to_numeric(d[c],errors='coerce').fillna(0)
d['cod']=d['CODIGO DANE'].str.strip().str.zfill(5)
print("años:", sorted(d['ANIO'].dropna().unique().astype(int).tolist())[:5], '...', sorted(d['ANIO'].dropna().unique().astype(int).tolist())[-5:])
nat=d.groupby('ANIO')[['PERSONAS EXPULSADOS','PERSONAS RECIBIDOS','PERSONAS DECLARADOS']].sum()
print("\n=== TOTAL NACIONAL por año (suma de municipios; todas las 'TIPO DE VICTIMA')")
print(nat.loc[1985:2016].astype(int).to_string())
a=d[d.cod.isin(AUC)].copy(); a['mun']=a.cod.map(AUC)
pv=a[(a.ANIO>=1997)&(a.ANIO<=2010)].pivot_table(index='mun',columns='ANIO',values='PERSONAS EXPULSADOS',aggfunc='sum',fill_value=0).astype(int)
pv.columns=[int(c) for c in pv.columns]
print("\n=== PERSONAS EXPULSADAS por año de ocurrencia 1997-2010, 25 municipios AUC (RUV corte 2016, repo jngaravitoc)")
print(pv.to_string())
pv.to_csv('/tmp/claude-0/-home-user/40b2b058-37e9-5cd5-a91b-60b9905d5a88/scratchpad/dl2/counts/ruv2016_expulsados_auc_1997_2010.csv')
nat.astype(int).to_csv('/tmp/claude-0/-home-user/40b2b058-37e9-5cd5-a91b-60b9905d5a88/scratchpad/dl2/counts/ruv2016_nacional_por_anio.csv')
# 2) Municipio siniestro - año ocurrencia (todos los hechos)
s=pd.read_excel(base+'Reporte_Personas_Municipio_Siniestro_Anio_Ocurrencia.xlsx', dtype=str)
print("\ncols2:", s.columns.tolist()); print("HECHOS:", s['HECHO VICTIMIZANTE'].value_counts().head(15).to_dict())
s['TOTAL']=pd.to_numeric(s['TOTAL'],errors='coerce').fillna(0); s['ANIO']=pd.to_numeric(s['ANIO OCURRENCIA'],errors='coerce'); s['cod']=s['DANE OCURRENCIA'].str.strip().str.zfill(5)
dz=s[s['HECHO VICTIMIZANTE'].str.contains('Desplazamiento',case=False,na=False)]
print("Desplazamiento total nacional (todas las filas):", int(dz['TOTAL'].sum()))
a2=dz[dz.cod.isin(AUC)].copy(); a2['mun']=a2.cod.map(AUC)
pv2=a2[(a2.ANIO>=1997)&(a2.ANIO<=2010)].pivot_table(index='mun',columns='ANIO',values='TOTAL',aggfunc='sum',fill_value=0).astype(int); pv2.columns=[int(c) for c in pv2.columns]
print("\n=== Desplazamiento (TOTAL personas) por año ocurrencia x municipio de siniestro, 25 AUC (archivo 2)")
print(pv2.to_string())
pv2.to_csv('/tmp/claude-0/-home-user/40b2b058-37e9-5cd5-a91b-60b9905d5a88/scratchpad/dl2/counts/ruv2016_desplazamiento_siniestro_auc_1997_2010.csv')
