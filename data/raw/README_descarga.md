# Receta de descarga de microdatos (espejos públicos en GitHub)

Los portales oficiales (datos.gov.co, microdatos.dane.gov.co, icfes.gov.co) no son accesibles desde el entorno de sesión. Todo lo que sigue procede de espejos públicos de archivos oficiales en GitHub (raw.githubusercontent.com y media.githubusercontent.com para Git LFS). La procedencia archivo por archivo está en `data/derived/counts/manifest_fuentes.csv`.

## Saber 11 (ICFES, FTP DataIcfes, archivos SB11_YYYYP.txt)
- Repo espejo: `jaolartem/ColombiaEd-ViolenceImpact`, carpeta `Data/3. Resultados Saber11/`.
- Periodo 1 (2005-1 … 2022-1): blobs normales, vía raw.githubusercontent.com. Guardados en `data/raw/saber11/saber11_sb11/` (374 MB, no versionados en git).
- Periodo 2 (2005-2 … 2022-2, calendario A, 160-500 MB cada uno): punteros Git LFS; descargar con `https://media.githubusercontent.com/media/jaolartem/ColombiaEd-ViolenceImpact/main/Data/3.%20Resultados%20Saber11/<archivo>`. Guardados comprimidos en `data/raw/saber11/saber11_sb11_p2/` (1,2 GB; ~7,9 GB descomprimidos; no versionados).
- Hueco conocido: SB11_20172 está truncado en el espejo (73.293 filas). Resto completo.
- Cabeceras de todos los archivos (incluidos 2000-2004) en `data/raw/saber11/saber11_headers/` (versionadas).
- Variables clave: 2005 `ESTU_COD_RESIDE_MCPIO` + `ESTU_NACIMIENTO_DIA/MES/ANNO`; 2006-2009 en minúsculas (delimitador `¬`, BOM); 2010+ `ESTU_COD_RESIDE_MCPIO` + `ESTU_FECHANACIMIENTO`. 2000-2004 sin municipio de residencia. 2009-2 solo nombres de municipio y departamento.

## Estadísticas Vitales (DANE)
- Nacimientos 2017, 2018, 2020-2024 (microdato completo) desde espejos `ddi4z/Proyecto-2-BI`, `RubianoAndy/DANE_EEVV`, `Manuelfmachado/AlertaMaterna`. En `data/raw/eevv/eevv_nacimientos/` (513 MB, no versionados). Variables: `CODPTORE`+`CODMUNRE` (residencia de la madre), `COD_DPTO`+`COD_MUNIC` (ocurrencia), `ANO`, `MES`, `EDAD_MADRE`, `PESO_NAC`, `T_GES`, `NIV_EDUM`.
- Nacimientos 1998-2010: NO disponibles en espejos; requieren descarga directa de DANE (catálogos 366 y 375).
- Defunciones: cabeceras 1998-2022 (muestras de 100 filas, `jdrengifoc/dataRC`) y 2020-2024 (AlertaMaterna). Variables: `CODPTORE`, `CODMUNRE`, `C_BAS1` (CIE-10), `GRU_ED1/2` (grupos de edad; sin fecha de nacimiento), `ANO`, `MES`, `SEXO`, `MAN_MUER`. Microdato completo 1998-2019: solo DANE directo.

## RUV (Unidad para las Víctimas, corte sep-2016)
- Repo `jngaravitoc/RUV_data`: `Reporte_Personas_Desplazados_por_Anio.xlsx` (año × código DANE × expulsados/recibidos/declarados, 1985-2016) y reporte de todos los hechos por municipio del siniestro y año. En `data/raw/ruv/ruv_jngaravitoc/` (versionado, 36 MB).
- Advertencia: el RUV sigue creciendo por declaraciones tardías; cortes posteriores solo vía datos.gov.co (bloqueado aquí).

## GEIH módulo de migración
- No disponible en espejos. Variables según DANE: `P756S1` (departamento de nacimiento), `P756S2` (municipio), `P756S3` (país). Catálogo 641 (2019) y 700 (2021).
