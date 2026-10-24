# T1/T2 — Replicación del PI y test de identificación del perfil de edad (t2_A)

Script: `code/exploration/t2_A.py` (implementación propia; ejecutado 2026-10-24 08:05). Fuente: CNMH-OMC corte mar-2025, masacres + asesinatos selectivos. PARA = 'GRUPO PARAMILITAR' + 'AGENTE DEL ESTADO - GRUPO PARAMILITAR' (idéntico, en estos archivos, a la regla `contains('PARAMILITAR')` del PI). T1(a)-(c) usan agregados anuales de los crudos (incluyen casos con Mes=0, ~1% de las víctimas); T1(d) y T2 usan el panel mensual derivado, verificado celda a celda contra una reagregación propia (60,375 filas muni-mes, diferencia máxima 0).

## T1. Replicación

**(a)** Municipios con ≥25 víctimas paramilitares 1997-2006: **452** (PI: 453). Concentran **94.2%** de las víctimas paramilitares 1997-2006 (64,904 de 68,918; PI: 94%). Con el filtro `\d{5}` del PI, que no excluye el código 00000 ('SIN INFORMACION', 63 víctimas PARA 1997-2006), salen 453. Usando solo casos con mes (lo que ve el panel mensual) salen 449.

| Umbral | Municipios | Share víctimas PARA 97-06 |
|---|---|---|
| ≥1 | 953 | 100.0% |
| ≥10 | 615 | 98.0% |
| ≥25 | 452 | 94.3% |
| ≥50 | 306 | 86.8% |
| ≥100 | 162 | 72.0% |
| ≥250 | 50 | 46.1% |

**(b)** Entrada = primer año 1996-2006 con ≥3 víctimas PARA; salida = último. Distribución de salida: 1998: 1, 1999: 1, 2000: 5, 2001: 4, 2002: 17, 2003: 52, 2004: 93, 2005: 216, 2006: 63 (PI: 2003: 52, 2004: 93, 2005: 216, 2006: 64). Entrada: 1996: 216, 1997: 85, 1998: 40, 1999: 40, 2000: 35, 2001: 26, 2002: 7, 2003: 3. Duración mediana **9 años** (PI: 9); p10/p25/p75/p90 = 5/7/10/10. 331 municipios (73.2%) ya tenían ≥3 víctimas PARA en 1988-95 (PI: 73%).

**(c)** Víctimas totales (todos los perpetradores) en T: media anual 2000-02 = 15,202, 2007-10 = 1,850, **ratio = 0.122** (PI: 0,12 con 15.226 → 1.856). Nacional: 16,611 → 2,246, ratio 0.135.

**(d) Mes de salida** (nuevo): primer mes m tal que las víctimas PARA fechadas desde m hasta dic-2006 son ≤5% del total municipal fechado 1996-2006. Se calcula solo con casos con Mes≥1; se marca *no fiable* si >5% de la dosis PARA 1996-2006 del municipio carece de mes (19 municipios) y *censurado* si el último 5% cae en dic-2006 (2 municipios). Mes asignado en **431/452** municipios, que concentran **92.5%** de las víctimas PARA 1997-2006 (criterio del PI: ≥80%); 98.2% de las de T. Sin la exclusión por mes faltante: 94.1%.

| Semestre de salida | Municipios (todos T) | Share munis | Share víctimas PARA 97-06 (T) | Municipios (≤5% sin mes) |
|---|---|---|---|---|
| <2002 | 4 | 0.9% | 0.3% | 3 |
| 2002-S1 | 2 | 0.4% | 0.3% | 2 |
| 2002-S2 | 2 | 0.4% | 0.3% | 2 |
| 2003-S1 | 19 | 4.2% | 2.1% | 19 |
| 2003-S2 | 29 | 6.4% | 3.6% | 26 |
| 2004-S1 | 59 | 13.1% | 12.5% | 57 |
| 2004-S2 | 92 | 20.4% | 26.8% | 89 |
| 2005-S1 | 121 | 26.8% | 29.3% | 117 |
| 2005-S2 | 101 | 22.3% | 21.7% | 95 |
| 2006-S1 | 16 | 3.5% | 2.7% | 16 |
| 2006-S2 | 5 | 1.1% | 0.4% | 5 |
| >=2007 (censurado) | 2 | 0.4% | 0.1% | 2 |

Año del mes de salida menos año de salida anual (≥3): -2: 12, -1: 98, +0: 271, +1: 49, +2: 11, +3: 4, +4: 4, +6: 1. El criterio del 5% suele adelantar la salida respecto al 'último año con ≥3' porque la cola de 1-2 víctimas/año ya es <5% en municipios con dosis grande.

## T2. Test de identificación del perfil de edad

Panel: 452 municipios de T × 21 cohortes (1988-2008, nacimiento en julio) = 9,492 celdas. Dosis = víctimas PARA fechadas del panel mensual en las ventanas in utero (−9..−1), 0-2 (0..35), 3-5 (36..71) y 6-11 (72..143 meses). La ventana 6-11 sale de 1985-2015 para las cohortes 2004-2008 (faltante); las otras tres están completas. Por construcción del CNMH no hay víctimas PARA después de 2006 (pasan a 'posdesmovilización'), así que las cohortes 2007-2008 tienen dosis cero en todas las ventanas.

**(1)** Correlación bruta 0-2/3-5 (n = 9,492): **0.678**.

**(2)** Residualización con EF de municipio y EF cohorte × departamento (demeaning iterado; converge en 1 iteración(es) con media de grupo residual máxima 2.0e-13; diferencia máxima frente a la regresión con dummies 5.2e-12). Una sola pasada es exacta porque el panel es balanceado dentro de cada departamento (todos los municipios tienen las 21 cohortes y la falta de 6-11 depende solo de la cohorte); el criterio de convergencia se evalúa igualmente y el residuo coincide con el de la regresión con dummies. Cada ventana se residualiza en su propia muestra no faltante; las correlaciones usan celdas con ambas ventanas.

| Muestra | Transf. | Especificación | var res. in utero | var res. 0-2 | var res. 3-5 | var res. 6-11 | ρ in utero/0-2 | ρ 0-2/3-5 | ρ 3-5/6-11 | cond. 4w | cond. 3w |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A_1988_2008 | levels | muni+cohort_x_depto | 49.4% | 44.4% | 47.5% | 40.0% | 0.614 | 0.407 | -0.007 | 3.0 | 2.7 |
| A_1988_2008 | levels | muni+cohort | 52.2% | 46.9% | 50.1% | 41.9% | 0.610 | 0.403 | -0.006 | 3.0 | 2.7 |
| A_1988_2008 | log1p | muni+cohort_x_depto | 30.4% | 16.9% | 14.7% | 7.6% | 0.271 | 0.244 | -0.014 | 1.4 | 1.5 |
| A_1988_2008 | log1p | muni+cohort | 37.5% | 23.7% | 20.5% | 10.3% | 0.331 | 0.311 | 0.059 | 1.5 | 1.6 |
| D_1988_2008_sin_top10 | levels | muni+cohort_x_depto | 53.6% | 43.2% | 44.5% | 33.1% | 0.397 | 0.231 | -0.035 | 1.9 | 1.7 |
| D_1988_2008_sin_top10 | levels | muni+cohort | 60.5% | 49.3% | 50.7% | 38.2% | 0.404 | 0.236 | -0.030 | 1.9 | 1.7 |
| D_1988_2008_sin_top10 | log1p | muni+cohort_x_depto | 32.8% | 17.5% | 14.7% | 7.4% | 0.250 | 0.223 | -0.025 | 1.4 | 1.4 |
| D_1988_2008_sin_top10 | log1p | muni+cohort | 40.5% | 24.7% | 20.7% | 10.2% | 0.311 | 0.292 | 0.049 | 1.5 | 1.6 |
| B_1988_2003_balanced | levels | muni+cohort_x_depto | 45.0% | 33.8% | 35.5% | 40.0% | 0.582 | 0.200 | -0.007 | 3.1 | 2.4 |
| B_1988_2003_balanced | levels | muni+cohort | 47.3% | 35.9% | 37.7% | 41.9% | 0.578 | 0.199 | -0.006 | 3.1 | 2.4 |
| B_1988_2003_balanced | log1p | muni+cohort_x_depto | 29.7% | 17.9% | 17.2% | 7.6% | 0.175 | 0.109 | -0.015 | 1.3 | 1.2 |
| B_1988_2003_balanced | log1p | muni+cohort | 35.6% | 25.3% | 25.3% | 10.3% | 0.221 | 0.200 | 0.061 | 1.5 | 1.4 |
| C_1995_2008 | levels | muni+cohort_x_depto | 40.5% | 39.1% | 51.7% | 55.9% | 0.549 | 0.428 | 0.437 | 2.8 | 2.6 |
| C_1995_2008 | levels | muni+cohort | 43.2% | 41.4% | 53.9% | 58.3% | 0.547 | 0.421 | 0.422 | 2.7 | 2.5 |
| C_1995_2008 | log1p | muni+cohort_x_depto | 29.2% | 13.0% | 10.0% | 9.5% | 0.271 | 0.151 | -0.084 | 1.3 | 1.4 |
| C_1995_2008 | log1p | muni+cohort | 37.1% | 18.8% | 12.1% | 10.9% | 0.343 | 0.190 | -0.111 | 1.4 | 1.5 |

Principal (A, niveles, muni + cohorte×depto): varianza residual como fracción de la bruta: in utero 49.4%, 0-2 **44.4%**, 3-5 **47.5%**, 6-11 40.0%. Correlaciones residuales: in utero/0-2 = 0.614, **0-2/3-5 = 0.407**, 3-5/6-11 = -0.007.

**Concentración de la variación identificadora** (principal, niveles): in utero (-9..-1): 47.4% de la suma de cuadrados residual en MEDELLIN, 71.4% en cinco municipios (MEDELLIN, CUCUTA, TURBO, VALLEDUPAR, APARTADO); 0-2 (0..35): 51.9% de la suma de cuadrados residual en MEDELLIN, 75.5% en cinco municipios (MEDELLIN, CUCUTA, TURBO, VALLEDUPAR, APARTADO); 3-5 (36..71): 53.3% de la suma de cuadrados residual en MEDELLIN, 75.9% en cinco municipios (MEDELLIN, CUCUTA, TURBO, APARTADO, VALLEDUPAR); 6-11 (72..143): 61.5% de la suma de cuadrados residual en MEDELLIN, 79.2% en cinco municipios (MEDELLIN, CUCUTA, VALLEDUPAR, APARTADO, CIENAGA). Por eso se añaden la muestra D (sin los 10 municipios de mayor dosis 1997-2006: MEDELLIN, CUCUTA, CIENAGA, VALLEDUPAR, SANTA MARTA, TIBU, BARRANCABERMEJA, APARTADO, SAN ANDRES DE TUMACO, BELLO) y la transformación log1p, que muestran qué variación queda para el municipio típico.

**(3)** Celdas con dosis 0-2 > 0 y 3-5 = 0: **1,483 de 9,492 (15.6%)**; 0-2 = 0 y 3-5 > 0: 557; ambas cero: 1,649. Por cohorte (véase `t2_A_T2_celdas_por_cohorte.csv`): 1988: 20, 1989: 19, 1990: 30, 1991: 30, 1992: 15, 1993: 7, 1994: 4, 1995: 1, 1996: 1, 1999: 1, 2000: 3, 2001: 23, 2002: 123, 2003: 332, 2004: 429, 2005: 328, 2006: 117.

**(4)** Celdas 'nacido tras la salida' (cohorte > año de salida anual): **1,595** (16.8% de las celdas, 452 municipios); por cohorte: 1999: 1, 2000: 2, 2001: 7, 2002: 11, 2003: 28, 2004: 80, 2005: 173, 2006: 389, 2007: 452, 2008: 452. Con el mes de salida asignado (nacimiento en jul-c posterior al mes de salida): 1,745.

**(5)** Colinealidad conjunta de las dosis residualizadas (principal): número de condición de la matriz estandarizada = 2.99 con las cuatro ventanas (n = 7,232, cohortes 1988-2003) y 2.71 con tres (n = 9,492). VIF (4 ventanas): in utero 2.46, 0-2 2.49, 3-5 1.37, 6-11 2.54; (3 ventanas): in utero 1.98, 0-2 2.37, 3-5 1.48.

**(6)** Especificación alternativa (EF municipio + EF cohorte, sin interacción con departamento): var residual 0-2 46.9%, 3-5 50.1%; ρ 0-2/3-5 = 0.403; cond. 4w 2.95. Departamentos en T: 28, de los cuales 3 tienen un solo municipio en T (BOGOTA, D. C., BOYACA, VICHADA): en la especificación principal sus celdas quedan absorbidas por el EF cohorte × departamento (residuo exactamente cero), lo que reduce la varianza residual respecto a la alternativa; la alternativa deja en el residuo la variación entre departamentos dentro de cohorte, que es justamente la que el PI quiere no usar.

## Veredicto frente a los umbrales del PI

**APROBADO: corr residual 0-2/3-5 = 0.407 (aprobado <0,7; letal >0,8); varianza residual 0-2 = 44.4% y 3-5 = 47.5% de la bruta (aprobado >20%; letal <10%). Spec alternativa (EF muni + cohorte): corr = 0.403, var resid 0-2 = 46.9%, 3-5 = 50.1%. Matices: 51.9% de la suma de cuadrados residual de la dosis 0-2 proviene de MEDELLIN y 75.5% de cinco municipios; sin los 10 municipios de mayor dosis (niveles): var resid 0-2 = 43.2%, 3-5 = 44.5%, corr = 0.231 (APROBADO); con dosis log1p: var resid 0-2 = 16.9%, 3-5 = 14.7%, corr = 0.244 (ZONA GRIS).**

## Caveats

- Dosis en niveles (víctimas), no per cápita ni por 100.000: no hay población municipal en el repositorio. La fila `log1p` muestra la sensibilidad a las colas (Medellín, etc.).
- Las ventanas usan solo casos con mes; ~1% de las víctimas (Mes=0) no entran en la dosis. El mes de salida se marca no fiable si ese 1% se concentra en un municipio (>5% de su dosis).
- La correlación residual 0-2/3-5 en A incluye las cohortes 2007-2008 con dosis cero en todo (residuos no nulos tras EF); la muestra B (cohortes 1988-2003) y C (1995-2008) acotan el efecto de la composición de cohortes.
- Las celdas 'nacido tras la salida' con la salida anual (último año con ≥3) sobreestiman las limpias: parte de esas cohortes recibe 1-2 víctimas/año residuales (ver `exit_month_minus_exit_year` en `t2_A_T1_muestra_T.csv`).
- La regla del 5% fecha el punto en que se ha acumulado el 95% de la dosis PARA fechada 1996-2006, no el cese de la violencia: en municipios de dosis grande la cola del 5% son decenas o cientos de víctimas (MEDELLIN: mes de salida 2004-09, con 172 víctimas PARA fechadas en los 12 meses siguientes). En el 92.9% de los municipios el año del mes de salida está a ±1 año del año de salida anual (último año con ≥3). Para fechar el cese conviene un umbral absoluto (p. ej. último mes con ≥k víctimas) además del relativo.
- El criterio de aprobación del PI no fija la muestra de cohortes ni la transformación; se reporta la rejilla completa: en niveles aprueba, en log1p la varianza residual 0-2/3-5 cae a la zona gris (10-20%) y la mayor parte de la variación en niveles proviene de pocas ciudades grandes.
