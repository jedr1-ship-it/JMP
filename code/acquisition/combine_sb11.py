import pandas as pd, re
C='/tmp/claude-0/-home-user/40b2b058-37e9-5cd5-a91b-60b9905d5a88/scratchpad/dl2/counts/'
parts=[]
for p in ['sb11_p1','sb11_p2']:
    d=pd.read_csv(C+p+'_auc_long.csv',dtype={'cod_mpio':str}); d['src']=p; parts.append(d)
d=pd.concat(parts); d['periodo']=d['file'].str.extract(r'(20\d\d[12])')[0].fillna('20221'); d['anio']=d['periodo'].str[:4].astype(int); d['sem']=d['periodo'].str[4]
d['birth_year']=pd.to_numeric(d['birth_year'],errors='coerce')
# 1) evaluados por municipio x año de examen (p1+p2)
pv=d.pivot_table(index='municipio',columns='anio',values='n',aggfunc='sum',fill_value=0).astype(int)
pv.to_csv(C+'saber11_auc_evaluados_por_anio_examen.csv'); print("=== Evaluados Saber 11 por municipio de residencia x año de examen (periodos 1+2)"); print(pv.to_string())
# 2) por año de nacimiento x municipio (todos los periodos 2005-2022)
bb=d[(d.birth_year>=1980)&(d.birth_year<=2008)]
pv2=bb.pivot_table(index='municipio',columns='birth_year',values='n',aggfunc='sum',fill_value=0).astype(int); pv2.columns=[int(c) for c in pv2.columns]
pv2.to_csv(C+'saber11_auc_evaluados_por_anio_nacimiento.csv'); print("\n=== Evaluados por municipio x año de nacimiento (suma periodos 2005-1 a 2022-1/2)"); print(pv2.loc[:, [c for c in pv2.columns if 1986<=c<=2006]].to_string())
# 3) long: periodo x municipio x birth_year
d[['periodo','cod_mpio','municipio','birth_year','n']].sort_values(['periodo','cod_mpio','birth_year']).to_csv(C+'saber11_auc_long_periodo_mpio_birthyear.csv',index=False)
# 4) N por archivo
s=pd.concat([pd.read_csv(C+'sb11_p1_summary.csv'),pd.read_csv(C+'sb11_p2_summary.csv')]); s['periodo']=s['file'].str.extract(r'(20\d\d[12])')[0].fillna('20221')
s=s.sort_values('periodo'); s[['periodo','file','N','N_muni','N_birthyear','ncols','enc']].to_csv(C+'saber11_N_por_archivo.csv',index=False)
print("\n=== N por archivo"); print(s[['periodo','file','N','N_muni','N_birthyear','ncols']].to_string(index=False))
nat=pd.concat([pd.read_csv(C+'sb11_p1_nat_birthyear.csv'),pd.read_csv(C+'sb11_p2_nat_birthyear.csv')]); nat['periodo']=nat['file'].str.extract(r'(20\d\d[12])')[0].fillna('20221')
nat.to_csv(C+'saber11_nacional_por_periodo_birthyear.csv',index=False)
