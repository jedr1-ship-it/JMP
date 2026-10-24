# Adquisición de microdatos Colombia: qué se consiguió y por dónde

Entrega en `data/raw/` (grandes fuera de git; receta en `data/raw/README_descarga.md`); conteos en `data/derived/counts/`; scripts en `code/acquisition/`. Nada descargado fue ejecutado. 16 búsquedas.

## 1. Qué bloquea y qué funciona [V]
- datos.gov.co (Socrata), microdatos.dane.gov.co, icfes.gov.co, dane.gov.co, unidadvictimas.gov.co: **CONNECT 403 del proxy**.
- Espejos amerigeoss, Kaggle, Hugging Face, Zenodo, Mendeley, archive.org, Dataverse, OSF, figshare, HDX, ICPSR: 403.
- api.github.com: 403 por política de sesión; **GitHub MCP search_code, raw.githubusercontent.com, media.githubusercontent.com (LFS) y git clone: OK**.
Conclusión: la única vía desde aquí son espejos GitHub de archivos oficiales.

## 2. Saber 11: CONSEGUIDO 2005-2022 (36 archivos oficiales DataIcfes) [V]
Repo `jaolartem/ColombiaEd-ViolenceImpact` aloja `SB11_YYYYP.txt` del FTP DataIcfes. Periodo 1 (2005-1…2022-1, 374 MB) y periodo 2 (2005-2…2022-2, LFS, 1,2 GB comprimidos, ~7,9 GB sin comprimir). Cabeceras de 2000-2022 incluidas.
- Variables: 2005 `ESTU_COD_RESIDE_MCPIO` + `ESTU_NACIMIENTO_DIA/MES/ANNO`; 2006-2009 idem minúsculas (delimitador `¬`, BOM); 2010+ `ESTU_COD_RESIDE_MCPIO` + `ESTU_FECHANACIMIENTO`. **2000-2004 sin municipio de residencia.** 2009-2 solo nombres (mapeo nombre+departamento validado contra 2010-2 sin discrepancias). Códigos verificados contra nombres en 2005-2020.
- N por año (p1+p2): 2005 456.806; 2006 471.878; 2007 502.389; 2008 506.431; 2009 525.106; 2010 570.944; 2011 572.420; 2012 580.551; 2013 576.094; 2014 569.428; 2015 568.397; 2016 561.269; **2017 86.286 (SB11_20172 truncado en el espejo)**; 2018 562.461; 2019 567.295; 2020 520.307; 2021 548.507; 2022 552.841.
- Evaluados por municipio de residencia × año de nacimiento (25 municipios AUC, suma 2005-2022): total 313.689; por cohorte 1988-2005 entre 11.296 y 18.613/año. Ejemplos (cohortes 1990/1996/2002): Tibú 196/266/388; El Carmen de Bolívar 631/811/802; Tuluá 2.354/2.516/2.209; Valledupar 4.554/4.915/5.435; San Carlos 127/173/165; Mapiripán 22/36/29.
- Secundario: `Saber11.parquet` (jgbabativam/AnaDatos; 1.065.888 filas, sin código de residencia).

## 3. Estadísticas Vitales DANE: PARCIAL
- **Nacimientos 1998-2010: no conseguidos** (sin espejo). Conseguidos microdatos completos 2017, 2018, 2020-2024 (656.704 … 453.901 nacimientos/año) con `CODPTORE`+`CODMUNRE` (residencia de la madre), ocurrencia, `EDAD_MADRE`, `PESO_NAC`, `T_GES`, `NIV_EDUM`.
- Defunciones: cabeceras 1998-2022 y 2020-2024: `CODPTORE`, `CODMUNRE`, `C_BAS1` (CIE-10), `GRU_ED1/2` (grupos de edad; **sin fecha de nacimiento**), `MAN_MUER`. Microdato completo 1998-2019 solo vía DANE.

## 4. RUV desplazamiento: CONSEGUIDO corte sep-2016 [V]
Repo `jngaravitoc/RUV_data` (RNI): expulsados/recibidos/declarados por año × código DANE 1985-2016 (74.118 filas). Nacional, expulsados por año de ocurrencia: 1997 238.105; 1998 221.727; 1999 255.441; 2000 525.197; 2001 625.333; 2002 731.596; 2003 435.224; 2004 401.573; 2005 454.870; 2006 443.344; 2007 470.270; 2008 422.866; 2009 252.409; 2010 216.706. Ejemplos (1999/2000/2001/2002): El Carmen de Bolívar 13.162/39.844/17.323/9.774; Tibú 10.697/6.260/7.853/8.726; Valledupar 2.855/8.488/9.530/18.597; San Carlos 3.107/4.401/7.510/7.291. Advertencia: el RUV sigue creciendo por declaraciones tardías. El dataset Socrata 9qih-4vkc solo trae el año en curso.

## 5. GEIH migración: no descargable aquí
Variables según DANE: `P756S1` (depto nacimiento), `P756S2` (municipio), `P756S3` (país). Catálogos 641 (2019) y 700 (2021); GEIH rediseñada desde 2022.

## 6. Rutas alternativas
1. Máquina sin proxy: Socrata `kgxf-xxbe.csv` (y 2017-2 para el hueco), DANE catálogos 366/375/807/843 (EEVV), 641/700 (GEIH).
2. Repetir espejos GitHub (URLs en `manifest_fuentes.csv`).
3. BigQuery de tercero (`ph-jabri.SABER11`): no consultado.
4. Pendiente clave: nacimientos 1998-2010 y defunciones 1998-2019 solo vía DANE directo.
