# T3: conteos, cobertura y potencia en Saber 11 (2005-1 a 2022-2)

Memo del RA (2026-10-24). Script `code/analysis/t3_counts_power.py`; tablas `data/derived/t3_*.csv` (`t3_numeros_clave.json` resume); figuras `scoping/proposal/figs_t3_*.pdf`. T = los 452 códigos de `t2_A_T1_muestra_T.csv`; uno (47000, "SIN INFORMACION") no es municipio ni tiene evaluados: T efectivo = 451.

## 1. Conteos (`t3_N_muni_cohorte.csv`, `t3_resumen_cohorte.csv`, `t3_T_munis_N.csv`)

- Cohortes 1985-2005 con residencia: 8,80 M (94,7 % de 9,29 M); **7,07 M en T, 1,73 M fuera**. T concentra el **80 % de los evaluados** (Bogotá 1,60 M, Medellín 0,50 M, Cali 0,39 M): "tratados vs no tratados" es ciudades frente a municipios pequeños.
- Cohortes observadas a las edades 16-19 completas: **1988-2003**; 1985-87 y 2004-05 están truncadas por edad. En 1988-2003: 385 mil evaluados por cohorte en T y 94 mil fuera; **municipios T con ≥30 evaluados por cohorte: 425-446 de 452**, 415 en las 16 cohortes; mediana de la celda municipio × cohorte: 206.
- **2017-2 truncado** (73 de ~550 mil filas, 682 de 1.114 municipios): las cohortes 1999-2001 pierden 80-150 mil cada una. Se imputa por celda con el promedio de 2016-2 y 2018-2 a la misma edad (`N_ajust`; cohorte 2000 en T: 288 → 439 mil).

## 2. Coincidencia residencia = colegio (`t3_coincidencia_*.csv`)

- Contra P5 de la carta, `ESTU_COD_RESIDE_MCPIO` existe **desde 2005-1** con cobertura ≥97,6 % salvo 2009-2 (93 %) y 2010-1 (88 %).
- Coincidencia **94,4 %**; **T 95,1 %**, resto 91,7 %; 2005-1 a 2012-1: 93,2 %. Calendario B: 89,5 % (resto 80 %, y 42-65 % desde 2010-1). El 99,2 % de quienes estudian en colegio de T residen en T; de los residentes en T no coincidentes, el 69 % va a otro municipio T. El municipio del colegio es un proxy válido para 2005-2011.

## 3. Edad (`t3_edad_cohorte.csv`)

Mediana 17,1-17,2 años en 1989-2003, igual en T y fuera. **Rezago (> 19): 10,1 % en T vs 12,2 % fuera** (1988-2003); por municipio T, mediana 14,4 %, p90 21,8 %. Sin rezago diferencial por cohorte; el repunte de la cohorte 2000 es artefacto de 2017-2.

## 4. Potencia (`t3_icc.csv`, `t3_potencia.csv`)

- **ICC municipal de score_z: 0,114** (T 0,103; resto 0,159); los EF de cohorte no la alteran.
- **(a) T vs resto, cluster municipio: MDE = 0,058 DE** (451 vs 671 clusters). Lo fija el número de clusters (una sola cohorte: 0,059). No cumple 0,04, pero no es el diseño.
- **(b) Ventanas dentro de T** (1995-2000: 2,33 M, 2.706 celdas; 2001-05: 1,80 M, 2.255 celdas), EF municipio + cohorte × dpto. Moulton con el ICC de celda municipio × cohorte (0,0009 tras los EF) da **0,003-0,006 DE**, pero ignora la correlación entre cohortes del mismo municipio y subestima. **Con SE empírico agrupado por municipio: 0,025 DE** (dummy de ventana, EF municipio). Regresores anclados al año de salida municipal (EF municipio + cohorte × dpto, cluster municipio): **0,024 DE** para "nacidas ≤2 años antes de la salida o después" (888 mil obs; 12 % de su varianza sobrevive a los EF), **0,010 DE** para "nacidas 3-5 años antes" y **0,034 DE** para el placebo "nacidas tras la salida" (64 mil evaluados, 302 celdas, 173 municipios con salida ≤2004).

## 5. Margen extensivo (`t3_margen_extensivo.csv`)

El cociente índice T / índice resto (base 1988-92, 2017-2 imputado) **baja de 1,02 (cohorte 1989) a 0,91-0,92 (1998-2004) y 0,90 (2005)**; igual perfil con la base 1985-90 y con solo edad ≤ 19. La caída es suave desde 1990, anterior al pico paramilitar: más compatible con una fecundidad urbana que cae antes que con la violencia. Sin EEVV no hay tasa de presentación (umbral 0,3-1,2): **pendiente**.

## Veredicto

**APROBADO** frente a MDE ≤ 0,04 DE para el contraste por tramos de edad dentro de T: **0,010-0,034 DE** con inferencia agrupada por municipio (vinculante la cifra empírica, no la de Moulton por celda). El placebo post-salida es el más ajustado (0,034) y mejorará con los archivos 2023-25. Advertencias: (i) son MDE de contrastes binarios con todo el N; cada β_a del perfil continuo tendrá un MDE mayor; (ii) T vs resto no alcanza 0,04 (0,058); (iii) con el 80 % de los evaluados en T, reportar siempre la versión sin grandes ciudades; (iv) la cohorte 2000 exige `N_ajust` o excluir 2017-2.
