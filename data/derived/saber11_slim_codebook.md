# Codebook: saber11_slim.parquet

Generado por `/home/user/JMP/code/build/build_saber11_slim.py` el 2026-10-24. Fuente: 36 archivos oficiales Saber 11 (ICFES, FTP DataIcfes), periodos 2005-1 a 2022-2. Archivo: `/home/user/JMP/data/derived/saber11_slim.parquet` (9,293,650 filas).

## Columnas de salida

| columna | tipo | definicion |
|---|---|---|
| periodo | string | Periodo segun el nombre del archivo: aaaa + semestre ('20152'). OJO: desde 2019-2 el ICFES codifica el 2o semestre como 4 en la variable PERIODO ('20194'); ver `periodo_icfes`. |
| year | int16 | Anio del examen (de `periodo`). |
| sem | int8 | Semestre/calendario del archivo: 1 = archivo periodo 1 (marzo-abril, calendario B), 2 = archivo periodo 2 (agosto-septiembre, calendario A). |
| consecutivo | string | ESTU_CONSECUTIVO (identificador anonimo del ICFES, unico dentro del periodo tras deduplicar). |
| birth_year / birth_month / birth_day | Int16 / Int8 / Int8 | Fecha de nacimiento. 2005-1..2009-1: ESTU_NACIMIENTO_ANNO/MES/DIA; 2009-2+: ESTU_FECHANACIMIENTO (dd/mm/aaaa). NaN si falta o si el anio <= 1900 (placeholder 01/01/1900) o > anio del examen; mes/dia NaN si fuera de rango. Anios sin siglo (p.ej. "0003" en 2020-1, "0096" en 2013-2; 23% de 2020-1 y 10% de 2021-1) se completan con el siglo (1900 o 2000) que implica una edad al examen entre 10 y 40 anios; si ninguno la da quedan NaN (en 2013-2 ~4.100 registros con fecha corrupta: el campo dia contiene la edad). Conteos por periodo en la tabla de N. |
| age_at_exam | float32 | Edad en anios = (fecha examen - fecha nacimiento)/365.25, con fecha de examen aproximada 15-mar (sem 1) y 15-ago (sem 2). Si dia/mes invalidos pero anio valido se usa 1-jul del anio de nacimiento. Si la edad implicada es < 10 o > 90 anios se consideran erroneos y se ponen NaN la edad y los tres campos de nacimiento (conteos por periodo en la tabla de N). |
| muni_res | string | Codigo DANE (5 digitos, con ceros) del municipio de residencia (ESTU_COD_RESIDE_MCPIO). NaN si falta, no es numerico, departamento invalido o '99999'. 2009-2: construido por nombre (ESTU_MCPIO_RESIDE + ESTU_DEPTO_RESIDE) con el mapa nombre->codigo observado en 2010-1/2010-2. |
| dpto_res | string | Departamento de residencia (2 digitos): ESTU_COD_RESIDE_DEPTO si existe y es valido; si no, primeros 2 digitos de muni_res. |
| muni_cole | string | Codigo DANE del municipio del colegio: COLE_COD_MCPIO_UBICACION (2006+). 2005-1/2005-2 no traen esa columna: se derivan los digitos 2-6 del codigo DANE de 12 digitos del establecimiento (COLE_COD_DANE_INSTITUCION), que contienen el municipio. |
| cole_naturaleza | string | 'oficial' / 'no oficial' (COLE_NATURALEZA: O/N en 2005-2009-1, OFICIAL/NO OFICIAL despues). |
| sexo | string | ESTU_GENERO: 'F'/'M'; otros valores -> NaN. |
| estrato | Int8 | Estrato de la vivienda 1-6; 0 = 'Sin Estrato' (solo 2022-2); NaN si falta u otro codigo (en 2008-1..2009-1 el archivo trae codigos numericos 1-6 y 8; 8 -> NaN). Vacio en 2005-1/2005-2 y no existe en 2006-2007. |
| educ_madre | string | Educacion de la madre tal como viene en el archivo (FAMI_EDUCA_MADRE / FAMI_EDUCACIONMADRE). 2008-1..2009-1 son codigos numericos del ICFES (0, 9-17, 99), 2009-2+ son etiquetas de texto. Vacia en 2005; no existe en 2006-2007. |
| inse | float32 | Indice socioeconomico individual del ICFES (ESTU_INSE_INDIVIDUAL), disponible desde 2014-2. |
| score_global_raw | float32 | PUNT_GLOBAL tal como viene (escala 0-500), disponible desde 2014-2 (nuevo examen). NaN antes. |
| score_z | float32 | Puntaje estandarizado DENTRO de cada periodo (media 0, sd 1, ddof=0). Si existe PUNT_GLOBAL: z(PUNT_GLOBAL). Si no: promedio de los z-scores de las areas del nucleo comun disponibles ese periodo (cada una estandarizada dentro del periodo), exigiendo al menos 4 areas no ausentes, y luego re-estandarizado dentro del periodo. Valores crudos <= 0 (0 y -1) se tratan como ausentes. Ver tabla por periodo. |
| math_z | float32 | z(PUNT_MATEMATICAS) dentro del periodo (valores <= 0 ausentes). |
| lang_z | float32 | z(PUNT_LENGUAJE) hasta 2014-1; z(PUNT_LECTURA_CRITICA) desde 2014-2; dentro del periodo (valores <= 0 ausentes). |
| periodo_icfes | string | Valor crudo de la columna PERIODO del archivo (p.ej. 20194 para 2019-2). |
| flag_truncated_file | bool | True para 2017-2: el archivo SB11_20172.TXT.gz del FTP esta truncado (73.293 filas, la ultima incompleta; el periodo real tiene ~550 mil evaluados). Se incluye tal cual. |

## Deduplicacion

1. Se eliminan filas exactamente duplicadas (sobre el conjunto de columnas crudas leidas de cada archivo). 2. Dentro de cada periodo se conserva la primera fila por ESTU_CONSECUTIVO (las filas sin consecutivo se conservan todas).

## N por periodo (antes y despues de deduplicar) y cobertura

| periodo | archivo | delim | BOM | ncols | N crudo | N tras dup. exactos | N tras dup. consecutivo | % fecha nac. completa | n anio sin siglo reparado | n anio sin siglo irrecuperable | n fecha aprox. 1-jul | n edad implausible (NaN) | % muni_res | % muni_cole | % score_z | % estrato | % educ_madre | % inse | edad media (p5-p95) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 20051 | SB11_20051.txt | `|` | no | 83 | 72,842 | 67,082 | 67,082 | 100.0% | 0 | 0 | 0 | 0 | 100.0% | 97.5% | 100.0% | 0.0% | 0.0% | 0.0% | 18.6 (16-27) |
| 20052 | SB11_20052.txt.gz | `|` | no | 82 | 383,964 | 383,964 | 383,964 | 100.0% | 0 | 0 | 0 | 0 | 100.0% | 98.5% | 100.0% | 0.0% | 0.1% | 0.0% | 17.9 (16-22) |
| 20061 | SB11_20061.txt | `¬` | si | 53 | 61,070 | 61,070 | 61,070 | 99.8% | 0 | 0 | 0 | 18 | 99.9% | 100.0% | 100.0% | 0.0% | 0.0% | 0.0% | 18.0 (16-23) |
| 20062 | SB11_20062.txt.gz | `¬` | si | 53 | 410,808 | 410,808 | 410,808 | 99.6% | 0 | 0 | 0 | 71 | 99.8% | 100.0% | 100.0% | 0.0% | 0.0% | 0.0% | 17.9 (16-22) |
| 20071 | SB11_20071.txt | `¬` | si | 52 | 67,703 | 67,703 | 67,703 | 99.7% | 0 | 0 | 0 | 20 | 99.8% | 100.0% | 100.0% | 0.0% | 0.0% | 0.0% | 18.2 (16-25) |
| 20072 | SB11_20072.txt.gz | `¬` | si | 53 | 434,686 | 434,686 | 434,686 | 99.6% | 0 | 0 | 0 | 103 | 99.7% | 100.0% | 100.0% | 0.0% | 0.0% | 0.0% | 18.0 (16-22) |
| 20081 | SB11_20081.txt | `¬` | si | 65 | 68,897 | 68,897 | 68,897 | 99.6% | 0 | 0 | 0 | 9 | 99.7% | 100.0% | 100.0% | 98.8% | 99.7% | 0.0% | 18.3 (16-25) |
| 20082 | SB11_20082.txt.gz | `¬` | si | 73 | 437,534 | 437,534 | 437,534 | 99.5% | 0 | 0 | 0 | 69 | 99.5% | 100.0% | 100.0% | 98.8% | 99.9% | 0.0% | 18.1 (16-22) |
| 20091 | SB11_20091.txt | `¬` | si | 87 | 69,743 | 69,743 | 69,743 | 99.6% | 0 | 0 | 0 | 26 | 99.7% | 100.0% | 100.0% | 99.0% | 99.8% | 0.0% | 18.3 (16-24) |
| 20092 | SB11_20092.txt.gz | `¬` | no | 118 | 455,363 | 455,363 | 455,363 | 100.0% | 0 | 0 | 0 | 103 | 93.3% | 100.0% | 100.0% | 92.5% | 93.3% | 0.0% | 18.1 (16-23) |
| 20101 | SB11_20101.txt | `¬` | no | 83 | 30,399 | 30,399 | 30,399 | 99.7% | 0 | 0 | 0 | 41 | 87.6% | 100.0% | 100.0% | 87.1% | 86.7% | 0.0% | 20.0 (16-35) |
| 20102 | SB11_20102.txt.gz | `¬` | no | 116 | 540,545 | 540,545 | 540,545 | 99.5% | 23 | 0 | 0 | 2,572 | 98.3% | 100.0% | 100.0% | 98.4% | 98.2% | 0.0% | 18.2 (16-24) |
| 20111 | SB11_20111.txt | `¬` | no | 116 | 31,713 | 31,713 | 31,713 | 99.0% | 0 | 0 | 0 | 311 | 97.6% | 100.0% | 100.0% | 97.5% | 97.3% | 0.0% | 20.1 (16-35) |
| 20112 | SB11_20112.txt.gz | `¬` | no | 116 | 540,707 | 540,707 | 540,707 | 99.5% | 0 | 0 | 0 | 2,708 | 98.0% | 100.0% | 100.0% | 97.8% | 98.3% | 0.0% | 18.2 (16-23) |
| 20121 | SB11_20121.TXT | `¬` | no | 120 | 30,410 | 30,410 | 30,410 | 99.2% | 0 | 0 | 0 | 229 | 98.9% | 100.0% | 100.0% | 98.7% | 97.3% | 0.0% | 19.6 (16-32) |
| 20122 | SB11_20122.txt.gz | `¬` | no | 121 | 550,141 | 550,141 | 550,141 | 99.4% | 2 | 2 | 0 | 3,078 | 98.7% | 100.0% | 100.0% | 98.4% | 96.2% | 0.0% | 18.2 (16-23) |
| 20131 | SB11_20131.TXT | `¬` | no | 136 | 28,366 | 28,366 | 28,366 | 99.3% | 33 | 198 | 0 | 2 | 99.8% | 100.0% | 100.0% | 99.8% | 99.8% | 0.0% | 19.5 (16-32) |
| 20132 | SB11_20132.TXT.gz | `¬` | no | 136 | 547,728 | 547,728 | 547,728 | 99.2% | 916 | 4,071 | 0 | 16 | 99.9% | 100.0% | 100.0% | 100.0% | 99.9% | 0.0% | 18.1 (16-22) |
| 20141 | SB11_20141.TXT | `¬` | no | 136 | 24,893 | 24,893 | 24,893 | 100.0% | 0 | 3 | 0 | 0 | 100.0% | 100.0% | 100.0% | 99.9% | 99.9% | 0.0% | 19.4 (16-32) |
| 20142 | SB11_20142.TXT.gz | `¬` | no | 138 | 544,535 | 544,535 | 544,535 | 99.6% | 2 | 12 | 0 | 2,152 | 100.0% | 100.0% | 100.0% | 99.7% | 99.7% | 99.6% | 18.2 (16-22) |
| 20151 | SB11_20151.txt | `¬` | no | 131 | 25,947 | 25,947 | 25,947 | 99.9% | 0 | 0 | 0 | 29 | 100.0% | 100.0% | 100.0% | 100.0% | 100.0% | 100.0% | 19.4 (16-31) |
| 20152 | SB11_20152.txt.gz | `¬` | no | 89 | 542,450 | 542,450 | 542,450 | 100.0% | 21 | 8 | 0 | 146 | 100.0% | 100.0% | 100.0% | 100.0% | 99.8% | 99.8% | 18.1 (16-22) |
| 20161 | SB11_20161.TXT | `¬` | no | 84 | 13,064 | 13,064 | 13,064 | 99.9% | 0 | 0 | 0 | 14 | 100.0% | 100.0% | 100.0% | 100.0% | 98.2% | 98.2% | 17.3 (16-19) |
| 20162 | SB11_20162.TXT.gz | `¬` | no | 84 | 548,205 | 548,205 | 548,205 | 99.9% | 24 | 0 | 0 | 409 | 100.0% | 100.0% | 100.0% | 99.6% | 99.6% | 99.6% | 18.1 (16-21) |
| 20171 | SB11_20171.TXT | `¬` | no | 81 | 12,993 | 12,993 | 12,993 | 99.9% | 1 | 0 | 0 | 11 | 100.0% | 100.0% | 100.0% | 97.2% | 97.4% | 97.6% | 17.3 (16-19) |
| 20172 | SB11_20172.TXT.gz | `¬` | no | 82 | 73,293 | 73,293 | 73,293 | 99.9% | 6 | 0 | 0 | 50 | 100.0% | 100.0% | 100.0% | 95.1% | 95.7% | 98.8% | 18.0 (16-21) |
| 20181 | SB11_20181.TXT | `¬` | no | 82 | 12,527 | 12,527 | 12,527 | 99.9% | 1 | 0 | 0 | 15 | 100.0% | 100.0% | 100.0% | 96.3% | 96.6% | 97.9% | 17.4 (16-19) |
| 20182 | SB11_20182.TXT.gz | `¬` | no | 83 | 549,934 | 549,934 | 549,934 | 99.9% | 5 | 0 | 0 | 408 | 100.0% | 100.0% | 100.0% | 92.9% | 93.6% | 96.7% | 18.0 (16-21) |
| 20191 | SB11_20191_.txt | `|` | no | 81 | 21,083 | 21,083 | 21,083 | 99.3% | 0 | 0 | 0 | 39 | 99.9% | 100.0% | 100.0% | 93.3% | 93.7% | 96.0% | 18.9 (16-27) |
| 20192 | SB11_20192.TXT.gz | `¬` | no | 82 | 546,212 | 546,212 | 546,212 | 99.6% | 0 | 0 | 0 | 450 | 99.9% | 100.0% | 100.0% | 93.7% | 94.4% | 96.9% | 18.0 (16-21) |
| 20201 | SB11_20201.txt | `¬` | no | 81 | 15,435 | 15,435 | 15,435 | 99.9% | 3,594 | 1 | 0 | 13 | 95.1% | 100.0% | 100.0% | 89.9% | 90.0% | 95.5% | 18.2 (16-21) |
| 20202 | SB11_20202.txt.gz | `¬` | no | 81 | 504,872 | 504,872 | 504,872 | 100.0% | 14 | 0 | 0 | 201 | 100.0% | 100.0% | 100.0% | 96.6% | 97.3% | 97.2% | 17.7 (16-20) |
| 20211 | SB11_20211.txt | `¬` | no | 78 | 15,528 | 15,528 | 15,528 | 100.0% | 1,547 | 0 | 0 | 6 | 99.9% | 100.0% | 100.0% | 95.1% | 95.5% | 0.0% | 17.8 (16-19) |
| 20212 | SB11_20212.txt.gz | `¬` | no | 82 | 532,979 | 532,979 | 532,979 | 100.0% | 9 | 0 | 0 | 180 | 100.0% | 100.0% | 100.0% | 94.4% | 95.1% | 97.2% | 17.7 (16-20) |
| 20221 | Data_Icfes_SABER11_2022-1_v2.TXT | `¬` | no | 81 | 20,049 | 20,049 | 20,049 | 99.9% | 10 | 0 | 0 | 19 | 100.0% | 100.0% | 100.0% | 94.8% | 95.3% | 96.1% | 18.5 (16-23) |
| 20222 | SB11_20222.TXT.gz | `¬` | no | 81 | 532,792 | 532,792 | 532,792 | 100.0% | 3 | 0 | 0 | 112 | 100.0% | 100.0% | 100.0% | 93.3% | 94.2% | 95.7% | 17.7 (16-20) |

## Correspondencia de columnas por periodo

| periodo | consecutivo | birth | muni_res | dpto_res | muni_cole | cole_naturaleza | sexo | estrato | educ_madre | inse | score_global_raw | math_z | lang_z |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 20051 | ESTU_CONSECUTIVO | ESTU_NACIMIENTO_DIA / _MES / _ANNO | ESTU_COD_RESIDE_MCPIO | muni_res[:2] | COLE_COD_DANE_INSTITUCION[1:6] (digitos 2-6 del codigo DANE de 12 digitos del establecimiento) | COLE_NATURALEZA | ESTU_GENERO | FAMI_ESTRATO_VIVIENDA (1-6; 0 = "Sin Estrato"; otros -> NaN) | FAMI_EDUCA_MADRE (vacia en este periodo) | - | - | PUNT_MATEMATICAS | PUNT_LENGUAJE |
| 20052 | ESTU_CONSECUTIVO | ESTU_NACIMIENTO_DIA / _MES / _ANNO | ESTU_COD_RESIDE_MCPIO | muni_res[:2] | COLE_COD_DANE_INSTITUCION[1:6] (digitos 2-6 del codigo DANE de 12 digitos del establecimiento) | COLE_NATURALEZA | ESTU_GENERO | FAMI_ESTRATO_VIVIENDA (1-6; 0 = "Sin Estrato"; otros -> NaN) | FAMI_EDUCA_MADRE (texto/codigo crudo) | - | - | PUNT_MATEMATICAS | PUNT_LENGUAJE |
| 20061 | ESTU_CONSECUTIVO | ESTU_NACIMIENTO_DIA / _MES / _ANNO | ESTU_COD_RESIDE_MCPIO | muni_res[:2] | COLE_COD_MCPIO_UBICACION | COLE_NATURALEZA | ESTU_GENERO | - | - | - | - | PUNT_MATEMATICAS | PUNT_LENGUAJE |
| 20062 | ESTU_CONSECUTIVO | ESTU_NACIMIENTO_DIA / _MES / _ANNO | ESTU_COD_RESIDE_MCPIO | muni_res[:2] | COLE_COD_MCPIO_UBICACION | COLE_NATURALEZA | ESTU_GENERO | - | - | - | - | PUNT_MATEMATICAS | PUNT_LENGUAJE |
| 20071 | ESTU_CONSECUTIVO | ESTU_NACIMIENTO_DIA / _MES / _ANNO | ESTU_COD_RESIDE_MCPIO | muni_res[:2] | COLE_COD_MCPIO_UBICACION | COLE_NATURALEZA | ESTU_GENERO | - | - | - | - | PUNT_MATEMATICAS | PUNT_LENGUAJE |
| 20072 | ESTU_CONSECUTIVO | ESTU_NACIMIENTO_DIA / _MES / _ANNO | ESTU_COD_RESIDE_MCPIO | muni_res[:2] | COLE_COD_MCPIO_UBICACION | COLE_NATURALEZA | ESTU_GENERO | - | - | - | - | PUNT_MATEMATICAS | PUNT_LENGUAJE |
| 20081 | ESTU_CONSECUTIVO | ESTU_NACIMIENTO_DIA / _MES / _ANNO | ESTU_COD_RESIDE_MCPIO | muni_res[:2] | COLE_COD_MCPIO_UBICACION | COLE_NATURALEZA | ESTU_GENERO | FAMI_ESTRATO_VIVIENDA (1-6; 0 = "Sin Estrato"; otros -> NaN) | FAMI_EDUCA_MADRE (texto/codigo crudo) | - | - | PUNT_MATEMATICAS | PUNT_LENGUAJE |
| 20082 | ESTU_CONSECUTIVO | ESTU_NACIMIENTO_DIA / _MES / _ANNO | ESTU_COD_RESIDE_MCPIO | muni_res[:2] | COLE_COD_MCPIO_UBICACION | COLE_NATURALEZA | ESTU_GENERO | FAMI_ESTRATO_VIVIENDA (1-6; 0 = "Sin Estrato"; otros -> NaN) | FAMI_EDUCA_MADRE (texto/codigo crudo) | - | - | PUNT_MATEMATICAS | PUNT_LENGUAJE |
| 20091 | ESTU_CONSECUTIVO | ESTU_NACIMIENTO_DIA / _MES / _ANNO | ESTU_COD_RESIDE_MCPIO | muni_res[:2] | COLE_COD_MCPIO_UBICACION | COLE_NATURALEZA | ESTU_GENERO | FAMI_ESTRATO_VIVIENDA (1-6; 0 = "Sin Estrato"; otros -> NaN) | FAMI_EDUCA_MADRE (texto/codigo crudo) | - | - | PUNT_MATEMATICAS | PUNT_LENGUAJE |
| 20092 | ESTU_CONSECUTIVO | ESTU_FECHANACIMIENTO (dd/mm/aaaa) | ESTU_MCPIO_RESIDE + ESTU_DEPTO_RESIDE (nombres) -> codigo via mapa 2010-1/2010-2 | muni_res[:2] | COLE_COD_MCPIO_UBICACION | COLE_NATURALEZA | ESTU_GENERO | FAMI_ESTRATOVIVIENDA (1-6; 0 = "Sin Estrato"; otros -> NaN) | FAMI_EDUCACIONMADRE (texto/codigo crudo) | - | - | PUNT_MATEMATICAS | PUNT_LENGUAJE |
| 20101 | ESTU_CONSECUTIVO | ESTU_FECHANACIMIENTO (dd/mm/aaaa) | ESTU_COD_RESIDE_MCPIO | ESTU_COD_RESIDE_DEPTO (si falta: muni_res[:2]) | COLE_COD_MCPIO_UBICACION | COLE_NATURALEZA | ESTU_GENERO | FAMI_ESTRATOVIVIENDA (1-6; 0 = "Sin Estrato"; otros -> NaN) | FAMI_EDUCACIONMADRE (texto/codigo crudo) | - | - | PUNT_MATEMATICAS | PUNT_LENGUAJE |
| 20102 | ESTU_CONSECUTIVO | ESTU_FECHANACIMIENTO (dd/mm/aaaa) | ESTU_COD_RESIDE_MCPIO | ESTU_COD_RESIDE_DEPTO (si falta: muni_res[:2]) | COLE_COD_MCPIO_UBICACION | COLE_NATURALEZA | ESTU_GENERO | FAMI_ESTRATOVIVIENDA (1-6; 0 = "Sin Estrato"; otros -> NaN) | FAMI_EDUCACIONMADRE (texto/codigo crudo) | - | - | PUNT_MATEMATICAS | PUNT_LENGUAJE |
| 20111 | ESTU_CONSECUTIVO | ESTU_FECHANACIMIENTO (dd/mm/aaaa) | ESTU_COD_RESIDE_MCPIO | ESTU_COD_RESIDE_DEPTO (si falta: muni_res[:2]) | COLE_COD_MCPIO_UBICACION | COLE_NATURALEZA | ESTU_GENERO | FAMI_ESTRATOVIVIENDA (1-6; 0 = "Sin Estrato"; otros -> NaN) | FAMI_EDUCACIONMADRE (texto/codigo crudo) | - | - | PUNT_MATEMATICAS | PUNT_LENGUAJE |
| 20112 | ESTU_CONSECUTIVO | ESTU_FECHANACIMIENTO (dd/mm/aaaa) | ESTU_COD_RESIDE_MCPIO | ESTU_COD_RESIDE_DEPTO (si falta: muni_res[:2]) | COLE_COD_MCPIO_UBICACION | COLE_NATURALEZA | ESTU_GENERO | FAMI_ESTRATOVIVIENDA (1-6; 0 = "Sin Estrato"; otros -> NaN) | FAMI_EDUCACIONMADRE (texto/codigo crudo) | - | - | PUNT_MATEMATICAS | PUNT_LENGUAJE |
| 20121 | ESTU_CONSECUTIVO | ESTU_FECHANACIMIENTO (dd/mm/aaaa) | ESTU_COD_RESIDE_MCPIO | ESTU_COD_RESIDE_DEPTO (si falta: muni_res[:2]) | COLE_COD_MCPIO_UBICACION | COLE_NATURALEZA | ESTU_GENERO | FAMI_ESTRATOVIVIENDA (1-6; 0 = "Sin Estrato"; otros -> NaN) | FAMI_EDUCACIONMADRE (texto/codigo crudo) | - | - | PUNT_MATEMATICAS | PUNT_LENGUAJE |
| 20122 | ESTU_CONSECUTIVO | ESTU_FECHANACIMIENTO (dd/mm/aaaa) | ESTU_COD_RESIDE_MCPIO | ESTU_COD_RESIDE_DEPTO (si falta: muni_res[:2]) | COLE_COD_MCPIO_UBICACION | COLE_NATURALEZA | ESTU_GENERO | FAMI_ESTRATOVIVIENDA (1-6; 0 = "Sin Estrato"; otros -> NaN) | FAMI_EDUCACIONMADRE (texto/codigo crudo) | - | - | PUNT_MATEMATICAS | PUNT_LENGUAJE |
| 20131 | ESTU_CONSECUTIVO | ESTU_FECHANACIMIENTO (dd/mm/aaaa) | ESTU_COD_RESIDE_MCPIO | ESTU_COD_RESIDE_DEPTO (si falta: muni_res[:2]) | COLE_COD_MCPIO_UBICACION | COLE_NATURALEZA | ESTU_GENERO | FAMI_ESTRATOVIVIENDA (1-6; 0 = "Sin Estrato"; otros -> NaN) | FAMI_EDUCACIONMADRE (texto/codigo crudo) | - | - | PUNT_MATEMATICAS | PUNT_LENGUAJE |
| 20132 | ESTU_CONSECUTIVO | ESTU_FECHANACIMIENTO (dd/mm/aaaa) | ESTU_COD_RESIDE_MCPIO | ESTU_COD_RESIDE_DEPTO (si falta: muni_res[:2]) | COLE_COD_MCPIO_UBICACION | COLE_NATURALEZA | ESTU_GENERO | FAMI_ESTRATOVIVIENDA (1-6; 0 = "Sin Estrato"; otros -> NaN) | FAMI_EDUCACIONMADRE (texto/codigo crudo) | - | - | PUNT_MATEMATICAS | PUNT_LENGUAJE |
| 20141 | ESTU_CONSECUTIVO | ESTU_FECHANACIMIENTO (dd/mm/aaaa) | ESTU_COD_RESIDE_MCPIO | ESTU_COD_RESIDE_DEPTO (si falta: muni_res[:2]) | COLE_COD_MCPIO_UBICACION | COLE_NATURALEZA | ESTU_GENERO | FAMI_ESTRATOVIVIENDA (1-6; 0 = "Sin Estrato"; otros -> NaN) | FAMI_EDUCACIONMADRE (texto/codigo crudo) | - | - | PUNT_MATEMATICAS | PUNT_LENGUAJE |
| 20142 | ESTU_CONSECUTIVO | ESTU_FECHANACIMIENTO (dd/mm/aaaa) | ESTU_COD_RESIDE_MCPIO | ESTU_COD_RESIDE_DEPTO (si falta: muni_res[:2]) | COLE_COD_MCPIO_UBICACION | COLE_NATURALEZA | ESTU_GENERO | FAMI_ESTRATOVIVIENDA (1-6; 0 = "Sin Estrato"; otros -> NaN) | FAMI_EDUCACIONMADRE (texto/codigo crudo) | ESTU_INSE_INDIVIDUAL | PUNT_GLOBAL | PUNT_MATEMATICAS | PUNT_LECTURA_CRITICA |
| 20151 | ESTU_CONSECUTIVO | ESTU_FECHANACIMIENTO (dd/mm/aaaa) | ESTU_COD_RESIDE_MCPIO | ESTU_COD_RESIDE_DEPTO (si falta: muni_res[:2]) | COLE_COD_MCPIO_UBICACION | COLE_NATURALEZA | ESTU_GENERO | FAMI_ESTRATOVIVIENDA (1-6; 0 = "Sin Estrato"; otros -> NaN) | FAMI_EDUCACIONMADRE (texto/codigo crudo) | ESTU_INSE_INDIVIDUAL | PUNT_GLOBAL | PUNT_MATEMATICAS | PUNT_LECTURA_CRITICA |
| 20152 | ESTU_CONSECUTIVO | ESTU_FECHANACIMIENTO (dd/mm/aaaa) | ESTU_COD_RESIDE_MCPIO | ESTU_COD_RESIDE_DEPTO (si falta: muni_res[:2]) | COLE_COD_MCPIO_UBICACION | COLE_NATURALEZA | ESTU_GENERO | FAMI_ESTRATOVIVIENDA (1-6; 0 = "Sin Estrato"; otros -> NaN) | FAMI_EDUCACIONMADRE (texto/codigo crudo) | ESTU_INSE_INDIVIDUAL | PUNT_GLOBAL | PUNT_MATEMATICAS | PUNT_LECTURA_CRITICA |
| 20161 | ESTU_CONSECUTIVO | ESTU_FECHANACIMIENTO (dd/mm/aaaa) | ESTU_COD_RESIDE_MCPIO | ESTU_COD_RESIDE_DEPTO (si falta: muni_res[:2]) | COLE_COD_MCPIO_UBICACION | COLE_NATURALEZA | ESTU_GENERO | FAMI_ESTRATOVIVIENDA (1-6; 0 = "Sin Estrato"; otros -> NaN) | FAMI_EDUCACIONMADRE (texto/codigo crudo) | ESTU_INSE_INDIVIDUAL | PUNT_GLOBAL | PUNT_MATEMATICAS | PUNT_LECTURA_CRITICA |
| 20162 | ESTU_CONSECUTIVO | ESTU_FECHANACIMIENTO (dd/mm/aaaa) | ESTU_COD_RESIDE_MCPIO | ESTU_COD_RESIDE_DEPTO (si falta: muni_res[:2]) | COLE_COD_MCPIO_UBICACION | COLE_NATURALEZA | ESTU_GENERO | FAMI_ESTRATOVIVIENDA (1-6; 0 = "Sin Estrato"; otros -> NaN) | FAMI_EDUCACIONMADRE (texto/codigo crudo) | ESTU_INSE_INDIVIDUAL | PUNT_GLOBAL | PUNT_MATEMATICAS | PUNT_LECTURA_CRITICA |
| 20171 | ESTU_CONSECUTIVO | ESTU_FECHANACIMIENTO (dd/mm/aaaa) | ESTU_COD_RESIDE_MCPIO | ESTU_COD_RESIDE_DEPTO (si falta: muni_res[:2]) | COLE_COD_MCPIO_UBICACION | COLE_NATURALEZA | ESTU_GENERO | FAMI_ESTRATOVIVIENDA (1-6; 0 = "Sin Estrato"; otros -> NaN) | FAMI_EDUCACIONMADRE (texto/codigo crudo) | ESTU_INSE_INDIVIDUAL | PUNT_GLOBAL | PUNT_MATEMATICAS | PUNT_LECTURA_CRITICA |
| 20172 | ESTU_CONSECUTIVO | ESTU_FECHANACIMIENTO (dd/mm/aaaa) | ESTU_COD_RESIDE_MCPIO | ESTU_COD_RESIDE_DEPTO (si falta: muni_res[:2]) | COLE_COD_MCPIO_UBICACION | COLE_NATURALEZA | ESTU_GENERO | FAMI_ESTRATOVIVIENDA (1-6; 0 = "Sin Estrato"; otros -> NaN) | FAMI_EDUCACIONMADRE (texto/codigo crudo) | ESTU_INSE_INDIVIDUAL | PUNT_GLOBAL | PUNT_MATEMATICAS | PUNT_LECTURA_CRITICA |
| 20181 | ESTU_CONSECUTIVO | ESTU_FECHANACIMIENTO (dd/mm/aaaa) | ESTU_COD_RESIDE_MCPIO | ESTU_COD_RESIDE_DEPTO (si falta: muni_res[:2]) | COLE_COD_MCPIO_UBICACION | COLE_NATURALEZA | ESTU_GENERO | FAMI_ESTRATOVIVIENDA (1-6; 0 = "Sin Estrato"; otros -> NaN) | FAMI_EDUCACIONMADRE (texto/codigo crudo) | ESTU_INSE_INDIVIDUAL | PUNT_GLOBAL | PUNT_MATEMATICAS | PUNT_LECTURA_CRITICA |
| 20182 | ESTU_CONSECUTIVO | ESTU_FECHANACIMIENTO (dd/mm/aaaa) | ESTU_COD_RESIDE_MCPIO | ESTU_COD_RESIDE_DEPTO (si falta: muni_res[:2]) | COLE_COD_MCPIO_UBICACION | COLE_NATURALEZA | ESTU_GENERO | FAMI_ESTRATOVIVIENDA (1-6; 0 = "Sin Estrato"; otros -> NaN) | FAMI_EDUCACIONMADRE (texto/codigo crudo) | ESTU_INSE_INDIVIDUAL | PUNT_GLOBAL | PUNT_MATEMATICAS | PUNT_LECTURA_CRITICA |
| 20191 | ESTU_CONSECUTIVO | ESTU_FECHANACIMIENTO (dd/mm/aaaa) | ESTU_COD_RESIDE_MCPIO | ESTU_COD_RESIDE_DEPTO (si falta: muni_res[:2]) | COLE_COD_MCPIO_UBICACION | COLE_NATURALEZA | ESTU_GENERO | FAMI_ESTRATOVIVIENDA (1-6; 0 = "Sin Estrato"; otros -> NaN) | FAMI_EDUCACIONMADRE (texto/codigo crudo) | ESTU_INSE_INDIVIDUAL | PUNT_GLOBAL | PUNT_MATEMATICAS | PUNT_LECTURA_CRITICA |
| 20192 | ESTU_CONSECUTIVO | ESTU_FECHANACIMIENTO (dd/mm/aaaa) | ESTU_COD_RESIDE_MCPIO | ESTU_COD_RESIDE_DEPTO (si falta: muni_res[:2]) | COLE_COD_MCPIO_UBICACION | COLE_NATURALEZA | ESTU_GENERO | FAMI_ESTRATOVIVIENDA (1-6; 0 = "Sin Estrato"; otros -> NaN) | FAMI_EDUCACIONMADRE (texto/codigo crudo) | ESTU_INSE_INDIVIDUAL | PUNT_GLOBAL | PUNT_MATEMATICAS | PUNT_LECTURA_CRITICA |
| 20201 | ESTU_CONSECUTIVO | ESTU_FECHANACIMIENTO (dd/mm/aaaa) | ESTU_COD_RESIDE_MCPIO | ESTU_COD_RESIDE_DEPTO (si falta: muni_res[:2]) | COLE_COD_MCPIO_UBICACION | COLE_NATURALEZA | ESTU_GENERO | FAMI_ESTRATOVIVIENDA (1-6; 0 = "Sin Estrato"; otros -> NaN) | FAMI_EDUCACIONMADRE (texto/codigo crudo) | ESTU_INSE_INDIVIDUAL | PUNT_GLOBAL | PUNT_MATEMATICAS | PUNT_LECTURA_CRITICA |
| 20202 | ESTU_CONSECUTIVO | ESTU_FECHANACIMIENTO (dd/mm/aaaa) | ESTU_COD_RESIDE_MCPIO | ESTU_COD_RESIDE_DEPTO (si falta: muni_res[:2]) | COLE_COD_MCPIO_UBICACION | COLE_NATURALEZA | ESTU_GENERO | FAMI_ESTRATOVIVIENDA (1-6; 0 = "Sin Estrato"; otros -> NaN) | FAMI_EDUCACIONMADRE (texto/codigo crudo) | ESTU_INSE_INDIVIDUAL | PUNT_GLOBAL | PUNT_MATEMATICAS | PUNT_LECTURA_CRITICA |
| 20211 | ESTU_CONSECUTIVO | ESTU_FECHANACIMIENTO (dd/mm/aaaa) | ESTU_COD_RESIDE_MCPIO | ESTU_COD_RESIDE_DEPTO (si falta: muni_res[:2]) | COLE_COD_MCPIO_UBICACION | COLE_NATURALEZA | ESTU_GENERO | FAMI_ESTRATOVIVIENDA (1-6; 0 = "Sin Estrato"; otros -> NaN) | FAMI_EDUCACIONMADRE (texto/codigo crudo) | - | PUNT_GLOBAL | PUNT_MATEMATICAS | PUNT_LECTURA_CRITICA |
| 20212 | ESTU_CONSECUTIVO | ESTU_FECHANACIMIENTO (dd/mm/aaaa) | ESTU_COD_RESIDE_MCPIO | ESTU_COD_RESIDE_DEPTO (si falta: muni_res[:2]) | COLE_COD_MCPIO_UBICACION | COLE_NATURALEZA | ESTU_GENERO | FAMI_ESTRATOVIVIENDA (1-6; 0 = "Sin Estrato"; otros -> NaN) | FAMI_EDUCACIONMADRE (texto/codigo crudo) | ESTU_INSE_INDIVIDUAL | PUNT_GLOBAL | PUNT_MATEMATICAS | PUNT_LECTURA_CRITICA |
| 20221 | ESTU_CONSECUTIVO | ESTU_FECHANACIMIENTO (dd/mm/aaaa) | ESTU_COD_RESIDE_MCPIO | ESTU_COD_RESIDE_DEPTO (si falta: muni_res[:2]) | COLE_COD_MCPIO_UBICACION | COLE_NATURALEZA | ESTU_GENERO | FAMI_ESTRATOVIVIENDA (1-6; 0 = "Sin Estrato"; otros -> NaN) | FAMI_EDUCACIONMADRE (texto/codigo crudo) | ESTU_INSE_INDIVIDUAL | PUNT_GLOBAL | PUNT_MATEMATICAS | PUNT_LECTURA_CRITICA |
| 20222 | ESTU_CONSECUTIVO | ESTU_FECHANACIMIENTO (dd/mm/aaaa) | ESTU_COD_RESIDE_MCPIO | ESTU_COD_RESIDE_DEPTO (si falta: muni_res[:2]) | COLE_COD_MCPIO_UBICACION | COLE_NATURALEZA | ESTU_GENERO | FAMI_ESTRATOVIVIENDA (1-6; 0 = "Sin Estrato"; otros -> NaN) | FAMI_EDUCACIONMADRE (texto/codigo crudo) | ESTU_INSE_INDIVIDUAL | PUNT_GLOBAL | PUNT_MATEMATICAS | PUNT_LECTURA_CRITICA |

## Definicion exacta de score_z por periodo

| periodo | definicion | columnas usadas | descartadas (duplicadas) | notas |
|---|---|---|---|---|
| 20051 | promedio de z-scores por area (cada area estandarizada dentro del periodo, valores <= 0 ausentes), con al menos 5 areas no ausentes; el promedio se re-estandariza dentro del periodo | PUNT_LENGUAJE, PUNT_MATEMATICAS, PUNT_HISTORIA, PUNT_GEOGRAFIA, PUNT_FILOSOFIA, PUNT_BIOLOGIA, PUNT_QUIMICA, PUNT_FISICA, PUNT_IDIOMA | - | - |
| 20052 | promedio de z-scores por area (cada area estandarizada dentro del periodo, valores <= 0 ausentes), con al menos 5 areas no ausentes; el promedio se re-estandariza dentro del periodo | PUNT_LENGUAJE, PUNT_MATEMATICAS, PUNT_HISTORIA, PUNT_GEOGRAFIA, PUNT_FILOSOFIA, PUNT_BIOLOGIA, PUNT_QUIMICA, PUNT_FISICA, PUNT_IDIOMA | - | - |
| 20061 | promedio de z-scores por area (cada area estandarizada dentro del periodo, valores <= 0 ausentes), con al menos 4 areas no ausentes; el promedio se re-estandariza dentro del periodo | PUNT_LENGUAJE, PUNT_MATEMATICAS, PUNT_C_SOCIALES, PUNT_FILOSOFIA, PUNT_BIOLOGIA, PUNT_QUIMICA, PUNT_FISICA, PUNT_IDIOMA | - | - |
| 20062 | promedio de z-scores por area (cada area estandarizada dentro del periodo, valores <= 0 ausentes), con al menos 4 areas no ausentes; el promedio se re-estandariza dentro del periodo | PUNT_LENGUAJE, PUNT_MATEMATICAS, PUNT_C_SOCIALES, PUNT_FILOSOFIA, PUNT_BIOLOGIA, PUNT_QUIMICA, PUNT_FISICA, PUNT_IDIOMA | - | - |
| 20071 | promedio de z-scores por area (cada area estandarizada dentro del periodo, valores <= 0 ausentes), con al menos 4 areas no ausentes; el promedio se re-estandariza dentro del periodo | PUNT_LENGUAJE, PUNT_MATEMATICAS, PUNT_C_SOCIALES, PUNT_FILOSOFIA, PUNT_BIOLOGIA, PUNT_QUIMICA, PUNT_FISICA | PUNT_INGLES | Areas descartadas por ser copia exacta de otra columna: ['PUNT_INGLES'] |
| 20072 | promedio de z-scores por area (cada area estandarizada dentro del periodo, valores <= 0 ausentes), con al menos 4 areas no ausentes; el promedio se re-estandariza dentro del periodo | PUNT_LENGUAJE, PUNT_MATEMATICAS, PUNT_C_SOCIALES, PUNT_FILOSOFIA, PUNT_BIOLOGIA, PUNT_QUIMICA, PUNT_FISICA, PUNT_INGLES | - | - |
| 20081 | promedio de z-scores por area (cada area estandarizada dentro del periodo, valores <= 0 ausentes), con al menos 4 areas no ausentes; el promedio se re-estandariza dentro del periodo | PUNT_LENGUAJE, PUNT_MATEMATICAS, PUNT_C_SOCIALES, PUNT_FILOSOFIA, PUNT_BIOLOGIA, PUNT_QUIMICA, PUNT_FISICA, PUNT_INGLES | - | - |
| 20082 | promedio de z-scores por area (cada area estandarizada dentro del periodo, valores <= 0 ausentes), con al menos 4 areas no ausentes; el promedio se re-estandariza dentro del periodo | PUNT_LENGUAJE, PUNT_MATEMATICAS, PUNT_C_SOCIALES, PUNT_FILOSOFIA, PUNT_BIOLOGIA, PUNT_QUIMICA, PUNT_FISICA, PUNT_INGLES | - | - |
| 20091 | promedio de z-scores por area (cada area estandarizada dentro del periodo, valores <= 0 ausentes), con al menos 4 areas no ausentes; el promedio se re-estandariza dentro del periodo | PUNT_LENGUAJE, PUNT_MATEMATICAS, PUNT_C_SOCIALES, PUNT_FILOSOFIA, PUNT_BIOLOGIA, PUNT_QUIMICA, PUNT_FISICA, PUNT_INGLES | - | - |
| 20092 | promedio de z-scores por area (cada area estandarizada dentro del periodo, valores <= 0 ausentes), con al menos 4 areas no ausentes; el promedio se re-estandariza dentro del periodo | PUNT_LENGUAJE, PUNT_MATEMATICAS, PUNT_CIENCIAS_SOCIALES, PUNT_FILOSOFIA, PUNT_BIOLOGIA, PUNT_QUIMICA, PUNT_FISICA, PUNT_INGLES | - | muni_res por nombre: 424,769 de 424,771 filas con nombre no vacio emparejadas (100.0%); 30,592 filas sin nombre. |
| 20101 | promedio de z-scores por area (cada area estandarizada dentro del periodo, valores <= 0 ausentes), con al menos 4 areas no ausentes; el promedio se re-estandariza dentro del periodo | PUNT_LENGUAJE, PUNT_MATEMATICAS, PUNT_CIENCIAS_SOCIALES, PUNT_FILOSOFIA, PUNT_BIOLOGIA, PUNT_QUIMICA, PUNT_FISICA, PUNT_INGLES | - | - |
| 20102 | promedio de z-scores por area (cada area estandarizada dentro del periodo, valores <= 0 ausentes), con al menos 4 areas no ausentes; el promedio se re-estandariza dentro del periodo | PUNT_LENGUAJE, PUNT_MATEMATICAS, PUNT_CIENCIAS_SOCIALES, PUNT_FILOSOFIA, PUNT_BIOLOGIA, PUNT_QUIMICA, PUNT_FISICA, PUNT_INGLES | - | - |
| 20111 | promedio de z-scores por area (cada area estandarizada dentro del periodo, valores <= 0 ausentes), con al menos 4 areas no ausentes; el promedio se re-estandariza dentro del periodo | PUNT_LENGUAJE, PUNT_MATEMATICAS, PUNT_CIENCIAS_SOCIALES, PUNT_FILOSOFIA, PUNT_BIOLOGIA, PUNT_QUIMICA, PUNT_FISICA, PUNT_INGLES | - | - |
| 20112 | promedio de z-scores por area (cada area estandarizada dentro del periodo, valores <= 0 ausentes), con al menos 4 areas no ausentes; el promedio se re-estandariza dentro del periodo | PUNT_LENGUAJE, PUNT_MATEMATICAS, PUNT_CIENCIAS_SOCIALES, PUNT_FILOSOFIA, PUNT_BIOLOGIA, PUNT_QUIMICA, PUNT_FISICA, PUNT_INGLES | - | - |
| 20121 | promedio de z-scores por area (cada area estandarizada dentro del periodo, valores <= 0 ausentes), con al menos 4 areas no ausentes; el promedio se re-estandariza dentro del periodo | PUNT_LENGUAJE, PUNT_MATEMATICAS, PUNT_CIENCIAS_SOCIALES, PUNT_FILOSOFIA, PUNT_BIOLOGIA, PUNT_QUIMICA, PUNT_FISICA, PUNT_INGLES | - | - |
| 20122 | promedio de z-scores por area (cada area estandarizada dentro del periodo, valores <= 0 ausentes), con al menos 4 areas no ausentes; el promedio se re-estandariza dentro del periodo | PUNT_LENGUAJE, PUNT_MATEMATICAS, PUNT_CIENCIAS_SOCIALES, PUNT_FILOSOFIA, PUNT_BIOLOGIA, PUNT_QUIMICA, PUNT_FISICA, PUNT_INGLES | - | - |
| 20131 | promedio de z-scores por area (cada area estandarizada dentro del periodo, valores <= 0 ausentes), con al menos 4 areas no ausentes; el promedio se re-estandariza dentro del periodo | PUNT_LENGUAJE, PUNT_MATEMATICAS, PUNT_CIENCIAS_SOCIALES, PUNT_FILOSOFIA, PUNT_BIOLOGIA, PUNT_QUIMICA, PUNT_FISICA, PUNT_INGLES | - | - |
| 20132 | promedio de z-scores por area (cada area estandarizada dentro del periodo, valores <= 0 ausentes), con al menos 4 areas no ausentes; el promedio se re-estandariza dentro del periodo | PUNT_LENGUAJE, PUNT_MATEMATICAS, PUNT_CIENCIAS_SOCIALES, PUNT_FILOSOFIA, PUNT_BIOLOGIA, PUNT_QUIMICA, PUNT_FISICA, PUNT_INGLES | - | - |
| 20141 | promedio de z-scores por area (cada area estandarizada dentro del periodo, valores <= 0 ausentes), con al menos 4 areas no ausentes; el promedio se re-estandariza dentro del periodo | PUNT_LENGUAJE, PUNT_MATEMATICAS, PUNT_CIENCIAS_SOCIALES, PUNT_FILOSOFIA, PUNT_BIOLOGIA, PUNT_QUIMICA, PUNT_FISICA, PUNT_INGLES | - | - |
| 20142 | z(PUNT_GLOBAL) dentro del periodo (valores <= 0 tratados como ausentes) | PUNT_GLOBAL | - | - |
| 20151 | z(PUNT_GLOBAL) dentro del periodo (valores <= 0 tratados como ausentes) | PUNT_GLOBAL | - | - |
| 20152 | z(PUNT_GLOBAL) dentro del periodo (valores <= 0 tratados como ausentes) | PUNT_GLOBAL | - | - |
| 20161 | z(PUNT_GLOBAL) dentro del periodo (valores <= 0 tratados como ausentes) | PUNT_GLOBAL | - | - |
| 20162 | z(PUNT_GLOBAL) dentro del periodo (valores <= 0 tratados como ausentes) | PUNT_GLOBAL | - | - |
| 20171 | z(PUNT_GLOBAL) dentro del periodo (valores <= 0 tratados como ausentes) | PUNT_GLOBAL | - | - |
| 20172 | z(PUNT_GLOBAL) dentro del periodo (valores <= 0 tratados como ausentes) | PUNT_GLOBAL | - | - |
| 20181 | z(PUNT_GLOBAL) dentro del periodo (valores <= 0 tratados como ausentes) | PUNT_GLOBAL | - | - |
| 20182 | z(PUNT_GLOBAL) dentro del periodo (valores <= 0 tratados como ausentes) | PUNT_GLOBAL | - | - |
| 20191 | z(PUNT_GLOBAL) dentro del periodo (valores <= 0 tratados como ausentes) | PUNT_GLOBAL | - | - |
| 20192 | z(PUNT_GLOBAL) dentro del periodo (valores <= 0 tratados como ausentes) | PUNT_GLOBAL | - | - |
| 20201 | z(PUNT_GLOBAL) dentro del periodo (valores <= 0 tratados como ausentes) | PUNT_GLOBAL | - | - |
| 20202 | z(PUNT_GLOBAL) dentro del periodo (valores <= 0 tratados como ausentes) | PUNT_GLOBAL | - | - |
| 20211 | z(PUNT_GLOBAL) dentro del periodo (valores <= 0 tratados como ausentes) | PUNT_GLOBAL | - | - |
| 20212 | z(PUNT_GLOBAL) dentro del periodo (valores <= 0 tratados como ausentes) | PUNT_GLOBAL | - | - |
| 20221 | z(PUNT_GLOBAL) dentro del periodo (valores <= 0 tratados como ausentes) | PUNT_GLOBAL | - | - |
| 20222 | z(PUNT_GLOBAL) dentro del periodo (valores <= 0 tratados como ausentes) | PUNT_GLOBAL | - | - |

## Notas y advertencias

- Mapa nombre->codigo para 2009-2: 1,111 claves (municipio, departamento) normalizadas (mayusculas, sin acentos) observadas en 2010-1/2010-2; guardado en `saber11_muni_name_map_2010.csv`.
- 2009-2: nombres sin emparejar (top): {'SAN JOSE DE URE | CORDOBA': 2}
- 2007-1: la columna punt_ingles es copia exacta de punt_lenguaje en el archivo oficial; se excluye del promedio de areas.
- 2005-1 contiene 5.760 filas exactamente duplicadas (mismo consecutivo y contenido); se eliminan.
- 2005-2 no trae la columna PERIODO (periodo_icfes NaN); el periodo se toma del nombre del archivo.
- 2012-1 a 2014-1 traen ademas columnas RECAF_* (puntajes recalificados a la escala del nuevo examen); NO se usan: score_z usa las areas originales del periodo.
- Los puntajes por area 2005-2009-1 vienen con coma decimal; 2009-2 en adelante con punto. Ambos se parsean.
- Valores de puntaje 0 y -1 se consideran ausentes para las estandarizaciones (ausencia a una sesion); son raros en 2010+ (decenas por periodo) y mas frecuentes en inglés/idioma 2005-2009.
- En 2015-1, 2016-1, 2013-2, 2019-2, 2020-2 aparecen codigos de residencia 99999 (extranjero/no informado): se ponen NaN.
- `estrato` en 2008-1..2009-1: el archivo trae codigos 1-6 y 8 (8 = sin informacion/no aplica segun el patron de frecuencias); solo se conservan 1-6.
- 2010-1 (archivo periodo 1) tiene ~12% de filas sin codigo de residencia; 2009-2 ~7% sin nombre de municipio.
- Lectura: las columnas enteras con nulos (birth_year, birth_month, birth_day, estrato) estan almacenadas como int16/int8 nullable en parquet; `pandas.read_parquet` las devuelve como float64 por defecto (usar `dtype_backend="numpy_nullable"` o pyarrow para conservarlas como enteros).
- Columnas adicionales a las solicitadas: `periodo_icfes` (PERIODO crudo) y `flag_truncated_file` (marca 2017-2).
