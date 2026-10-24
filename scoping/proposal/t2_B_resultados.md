# T1/T2 (RA B): replicacion del PI y test de identificacion del perfil de edad

Script: `code/exploration/t2_B.py` (implementacion independiente; panel reconstruido desde los xlsx crudos CNMH-OMC, corte marzo 2025, masacres + asesinatos selectivos). Tablas: `data/derived/t2_B_*.csv`. Fecha de ejecucion: 2026-10-24.

## Definiciones y filtros

- Victimas = `Total de Victimas del Caso`; PARA = `GRUPO PARAMILITAR` + `AGENTE DEL ESTADO - GRUPO PARAMILITAR`; POSD = posdesmovilizacion (+ mixto con Estado); GUE; EST; NI = resto (no identificado, desconocido, otro, crimen organizado, agente extranjero).
- Casos con codigo DANE de 5 digitos y anio 1985-2015: 150461 de 161887; se excluyen codigos de exterior (EXVEN, EXPAN, EXECU). El codigo `00000` ('SIN INFORMACION') se mantiene solo para replicar el conteo del PI.
- Panel anual usa todos los casos (incl. Mes=0); panel mensual solo Mes 1-12 (ym = anio*12 + mes - 1). Mi panel mensual coincide exactamente con `cnmh_muni_month_victims.csv` del PI en las filas comunes (max |diff| = 0); las 64 filas que solo estan en el panel del PI son los codigos de exterior ['EXVEN', 'EXECU', 'EXPAN'] que aqui se excluyen.

## T1 (a): muestra T

| Umbral PARA 1997-2006 | Municipios | Share victimas PARA 1997-2006 |
|---|---|---|
| >= 1 | 954 | 100.0% |
| >= 10 | 616 | 98.0% |
| >= 25 | 453 | 94.3% |
| >= 50 | 307 | 86.8% |
| >= 100 | 162 | 71.9% |
| >= 250 | 50 | 46.1% |

- **453 municipios con >= 25 victimas PARA 1997-2006 (94.3% de 68869 victimas PARA nacionales)**: replica exactamente el 453 / 94% del PI. Uno de los 453 es `00000` = 'SIN INFORMACION' (63 victimas): pasa el filtro `\d{5}` del PI pero no es un municipio. **T de trabajo (T1d y T2) = 452 municipios (94.2%)**.

## T1 (b): entrada y salida anual (>= 3 victimas PARA, 1996-2006)

| Anio | Salida (T=452) | Salida (453 con 00000) | Entrada (T) | PI (salida) |
|---|---|---|---|---|
| 1996 | 0 | 0 | 216 |  |
| 1997 | 0 | 0 | 85 |  |
| 1998 | 1 | 1 | 40 |  |
| 1999 | 1 | 1 | 40 |  |
| 2000 | 5 | 5 | 35 |  |
| 2001 | 4 | 4 | 26 |  |
| 2002 | 17 | 17 | 7 |  |
| 2003 | 52 | 52 | 3 | 52 |
| 2004 | 93 | 93 | 0 | 93 |
| 2005 | 216 | 216 | 0 | 216 |
| 2006 | 63 | 64 | 0 | 64 |

- Duracion (salida - entrada + 1): **mediana 9 anios** (p25 = 7, p75 = 10, media 8.1); PI: mediana 9, cuartiles 7-10. 00000: entrada 1996, salida 2006.

## T1 (c): caida de la violencia total tras la desmovilizacion

- Victimas TOTALES (todos los perpetradores) por anio en T: media 2000-02 = 15202, media 2007-10 = 1850, **ratio = 0.122** (PI: 15.226 -> 1.856, 0,12). Con `00000`: 0.122; nacional (todos los municipios): 0.135; solo PARA+POSD en T: 0.060.

| Anio | PARA | POSD | GUE | EST | NI | TOT |
|---|---|---|---|---|---|---|
| 1996 | 4322 | 0 | 1143 | 82 | 3260 | 8807 |
| 1997 | 5917 | 0 | 1246 | 89 | 3486 | 10738 |
| 1998 | 5052 | 0 | 1033 | 97 | 2862 | 9044 |
| 1999 | 6074 | 0 | 1361 | 55 | 3175 | 10665 |
| 2000 | 8730 | 0 | 1303 | 67 | 4179 | 14279 |
| 2001 | 9662 | 0 | 1358 | 48 | 3851 | 14919 |
| 2002 | 10503 | 0 | 1504 | 265 | 4135 | 16407 |
| 2003 | 8599 | 0 | 987 | 280 | 2932 | 12798 |
| 2004 | 6106 | 0 | 784 | 351 | 2536 | 9777 |
| 2005 | 3580 | 0 | 620 | 401 | 1787 | 6388 |
| 2006 | 681 | 718 | 539 | 656 | 1151 | 3745 |
| 2007 | 0 | 776 | 451 | 1151 | 771 | 3149 |
| 2008 | 0 | 584 | 321 | 489 | 551 | 1945 |
| 2009 | 0 | 537 | 278 | 49 | 481 | 1345 |
| 2010 | 0 | 399 | 211 | 32 | 320 | 962 |

## T1 (d) NUEVO: mes de salida municipal

Definicion: primer mes m (1996-01..2006-12) tal que las victimas PARA con mes conocido en [m, dic-2006] son <= 5% del total municipal 1996-2006 con mes conocido. Los casos con Mes=0 (sin dato) no entran en el panel mensual. Variantes de inclusion de municipios: V1 = todos los 452; **V2 (primaria) = municipios cuyas victimas PARA 1996-2006 con Mes=0 son <= 5% del total municipal** (un mes faltante no puede mover el corte del 5%); V3 (literal estricta) = municipios sin ningun caso PARA con Mes=0 en 1996-2006.

| Variante | Municipios incluidos | Con mes de salida | Share PARA 1997-2006 nacional | Share PARA 1997-2006 de T |
|---|---|---|---|---|
| V1_todos_T | 452 | 450 | 94.2% | 99.9% |
| V2_mes0_le5pct | 433 | 431 | 92.6% | 98.2% |
| V3_sin_ningun_mes0 | 254 | 252 | 28.9% | 30.6% |

Distribucion del mes de salida por semestre:

| Semestre | V1_todos_T | V2_mes0_le5pct | V3_sin_ningun_mes0 |
|---|---|---|---|
| <2002 | 4 | 3 | 2 |
| 2002S1 | 2 | 2 | 2 |
| 2002S2 | 2 | 2 | 1 |
| 2003S1 | 19 | 19 | 15 |
| 2003S2 | 29 | 26 | 18 |
| 2004S1 | 59 | 57 | 30 |
| 2004S2 | 92 | 89 | 52 |
| 2005S1 | 121 | 117 | 65 |
| 2005S2 | 101 | 95 | 54 |
| 2006S1 | 16 | 16 | 9 |
| 2006S2 | 5 | 5 | 4 |
| censurado (>dic-2006) | 2 | 2 | 2 |

- Anio del mes de salida menos anio de salida anual (V2): {-2.0: 12, -1.0: 96, 0.0: 256, 1.0: 49, 2.0: 10, 3.0: 3, 4.0: 4, 6.0: 1} (0 = mismo anio; +1 = la salida mensual cae en enero del anio siguiente o la cola del 5% se extiende). Criterio del PI (mes de salida para municipios con >= 80% de las victimas): V2 cubre 92.6% de las victimas PARA 1997-2006 nacionales.

## T2: test de identificacion del perfil de edad

Celdas municipio x cohorte: 452 municipios de T x cohortes 1988-2008 = 9492. Nacimiento en julio de c. Dosis = victimas PARA del panel mensual (solo Mes>=1) en in utero (-9..-1), 0-2 (0..35), 3-5 (36..71), 6-11 (72..143) meses; faltante si la ventana sale de 1985-2015 (6-11 disponible solo para cohortes 1988-2003; las demas para 1988-2008). Nota: por construccion del CNMH no hay victimas PARA despues de 2006 (se reetiquetan como posdesmovilizacion), asi que las dosis de las cohortes 2007-2008 son 0 en todas las ventanas postnatales.

Departamentos en T: 28; 3 con un solo municipio en T (BOGOTA, D. C., BOYACA, VICHADA): bajo EF cohorte x dpto su residuo es 0 por construccion, por eso se reporta tambien 'sin dpto singleton'.

Residualizacion: demeaning iterado (tolerancia 1e-9 relativa) verificado contra regresion con dummies (lstsq): max iteraciones 2, todas convergen, max |diff| vs lstsq = 5.9e-12.

### (1) Correlacion bruta

- corr(0-2, 3-5) bruta = **0.678** (n = 9492); in utero/0-2 = 0.790; 3-5/6-11 = 0.541. Spearman 0-2/3-5 = 0.612.

### (2) y (6) Varianza residual y correlaciones residuales

| Metrica | Spec A: EF muni + cohorte x dpto | A sin dpto singleton | A asinh(dosis) | Spec B: EF muni + cohorte | Muestra (cohortes) |
|---|---|---|---|---|---|
| var. residual / bruta, in utero (-9..-1) | 49.4% | 49.4% | 30.5% | 52.2% | 1988-2008 |
| var. residual / bruta, 0-2 (0..35) | 44.4% | 44.4% | 16.8% | 46.9% | 1988-2008 |
| var. residual / bruta, 3-5 (36..71) | 47.5% | 47.6% | 14.0% | 50.1% | 1988-2008 |
| var. residual / bruta, 6-11 (72..143) | 40.0% | 40.1% | 7.0% | 41.9% | 1988-2003 |
| corr residual in utero (-9..-1) / 0-2 (0..35) | 0.614 | 0.614 | 0.246 | 0.610 | 1988-2008 |
| corr residual 0-2 (0..35) / 3-5 (36..71) | 0.407 | 0.407 | 0.229 | 0.403 | 1988-2008 |
| corr residual 3-5 (36..71) / 6-11 (72..143) | -0.007 | -0.007 | -0.029 | -0.006 | 1988-2003 |

Matriz de correlaciones residuales, muestra balanceada (4 ventanas, cohortes 1988-2003, n = 7232):

| | A: in utero (-9..-1) | A: 0-2 (0..35) | A: 3-5 (36..71) | A: 6-11 (72..143) | B: in utero (-9..-1) | B: 0-2 (0..35) | B: 3-5 (36..71) | B: 6-11 (72..143) |
|---|---|---|---|---|---|---|---|---|
| in utero (-9..-1) | 1.000 | 0.582 | -0.257 | -0.709 | 1.000 | 0.578 | -0.257 | -0.701 |
| 0-2 (0..35) | 0.582 | 1.000 | 0.200 | -0.715 | 0.578 | 1.000 | 0.199 | -0.705 |
| 3-5 (36..71) | -0.257 | 0.200 | 1.000 | -0.007 | -0.257 | 0.199 | 1.000 | -0.006 |
| 6-11 (72..143) | -0.709 | -0.715 | -0.007 | 1.000 | -0.701 | -0.705 | -0.006 | 1.000 |

Diferencia A vs B: la spec B (EF cohorte comunes) deja en el residuo toda la variacion departamental del ciclo paramilitar (la expansion 1997-2002 y la salida 2003-06 difieren por region); la spec A la absorbe. La varianza residual de 0-2 pasa de 46.9% (B) a 44.4% (A) y la correlacion residual 0-2/3-5 de 0.403 (B) a 0.407 (A). En niveles la diferencia es pequena porque la variacion dominante es la de los municipios grandes dentro de su departamento, que ningun EF de cohorte absorbe; en asinh la diferencia es mayor (var. residual 0-2: 23.7% en B vs 16.8% en A; corr 0-2/3-5: 0.303 vs 0.229).

### Robustez de escala de la dosis (spec A, par 0-2/3-5)

| Escala / muestra | var. residual 0-2 | var. residual 3-5 | corr residual 0-2/3-5 | n celdas | Umbrales PI |
|---|---|---|---|---|---|
| niveles (titular) | 44.4% | 47.5% | 0.407 | 9492 | APROBADO |
| niveles sin top 1% municipios | 43.9% | 45.7% | 0.283 | 9387 | APROBADO |
| share del total municipal 1996-2006 | 35.8% | 30.8% | -0.076 | 9492 | APROBADO |
| asinh(dosis) | 16.8% | 14.0% | 0.229 | 9492 | ZONA GRIS |
| niveles, balanceada 1988-2003 | 33.8% | 35.5% | 0.200 | 7232 | APROBADO |

Top 1% de municipios excluidos en la fila correspondiente (victimas PARA 1996-2006 con mes conocido): MEDELLIN (5997), VALLEDUPAR (1283), SANTA MARTA (1217), CIENAGA (1251), CUCUTA (2502). La fila 'share del total municipal' divide cada dosis por el total PARA 1996-2006 del municipio: aisla la variacion de *timing* y elimina la de escala. Lectura: niveles (titular) -> APROBADO; niveles sin top 1% municipios -> APROBADO; share del total municipal 1996-2006 -> APROBADO; asinh(dosis) -> ZONA GRIS; niveles, balanceada 1988-2003 -> APROBADO. Correlacion residual 0-2/3-5 maxima entre escalas = 0.407 (umbral letal 0,8); varianza residual minima (0-2 o 3-5) entre escalas = 14.0% (umbral letal 10%). En escala relativa (asinh, share) la mayor parte de la variacion bruta es el ciclo comun del departamento y la escala del municipio, que los EF absorben; el veredicto sobre la varianza residual depende de como entre la dosis en la regresion del perfil.

### (3) Celdas con dosis 0-2 > 0 y 3-5 = 0

- 1483 de 9492 celdas (15.6%); entre las 7286 celdas con dosis 0-2 > 0, 20.4%. Posicion relativa a la salida anual (cohorte - anio de salida): {-17: 11, -16: 17, -15: 28, -14: 23, -13: 16, -12: 17, -11: 10, -10: 2, -9: 2, -8: 1, -3: 36, -2: 305, -1: 395, 0: 392, 1: 138, 2: 54, 3: 23, 4: 9, 5: 3, 6: 1}. En la muestra balanceada 1988-2003, celdas con 0-2 > 0, 3-5 = 0 y 6-11 = 0: 483 (y ademas in utero = 0: 32).

### (4) Cohortes nacidas tras la salida

- Celdas con cohorte > anio de salida anual: **1595** de 9492; de ellas 691 con cohorte <= 2006 (en 389 municipios), que son las unicas que distinguen 'tras la salida local' de 'tras el fin nacional' (las cohortes 2007-08 son post-salida en todos los municipios: 904 celdas). Con el anio del mes de salida (T1d, V1): 1606 (<= 2006: 706). Dosis media 0-2 en las celdas post-salida (anual) = 0.26 victimas, share con 0-2 > 0 = 15.1% (la cola de <3 victimas/anio tras la salida).

### (5) Colinealidad conjunta (muestra balanceada 1988-2003, dosis residualizadas)

| | VIF in utero | VIF 0-2 | VIF 3-5 | VIF 6-11 | cond(X estandarizada) | cond(matriz corr) |
|---|---|---|---|---|---|---|
| bruto | 3.21 | 5.07 | 2.84 | 1.49 | 4.61 | 21.23 |
| Spec A | 2.55 | 2.42 | 1.34 | 2.80 | 3.13 | 9.78 |
| Spec B | 2.49 | 2.36 | 1.33 | 2.68 | 3.05 | 9.30 |

### Veredicto frente a los umbrales del PI

**APROBADO: corr residual 0-2/3-5 = 0.407 (umbral aprobado < 0,7; letal > 0,8); varianza residual 0-2 = 44.4%, 3-5 = 47.5% (aprobado > 20%; letal < 10%); spec A (EF muni + cohorte x dpto), cohortes 1988-2008, dosis en niveles. Sensibilidad a la escala: niveles sin top 1% municipios: corr 0.28, var. res. 0-2 44%, 3-5 46% -> APROBADO; share del total municipal 1996-2006: corr -0.08, var. res. 0-2 36%, 3-5 31% -> APROBADO; asinh(dosis): corr 0.23, var. res. 0-2 17%, 3-5 14% -> ZONA GRIS; niveles, balanceada 1988-2003: corr 0.20, var. res. 0-2 34%, 3-5 35% -> APROBADO.**

### Diferencias con el PI y caveats

- Replicacion T1: 453 municipios, 94.3%, salida 52/93/216/64 (2003-06), mediana 9 anios y ratio 0.12: coincide con el PI. El 453 incluye `00000` (SIN INFORMACION).
- El 5% del mes de salida se calcula sobre victimas con mes conocido; los casos con Mes=0 (~1% de las victimas PARA) se ignoran. Para municipios pequenos (25-40 victimas) el corte del 5% equivale al ultimo caso, lo que hace el mes de salida ruidoso; V2 solo controla el sesgo por meses faltantes, no ese ruido.
- Dosis en niveles (como pide la tarea): la varianza bruta esta dominada por los municipios grandes, y es ahi donde los EF absorben menos. Sin el top 1% de municipios y con la dosis como share del total municipal el veredicto se mantiene (varianza residual 43.9% y 35.8% en 0-2); en asinh baja a 16.8% (0-2) y 14.0% (3-5), zona gris. El umbral del PI (>20%) no especifica la escala: recomiendo fijarla antes de declarar aprobado/letal, y usar la version per capita (poblacion DANE) cuando este disponible. Las dosis de 6-11 solo existen para 1988-2003 y las de 2007-08 son cero por construccion (reetiquetado CNMH a posdesmovilizacion), lo que infla mecanicamente la variacion entre cohortes que absorben los EF cohorte x dpto; la muestra balanceada 1988-2003 da varianzas residuales mas bajas por ese motivo.
- Los dos municipios de T sin mes de salida (Abriaqui, Riofrio) tienen victimas en diciembre de 2006 por encima del 5% de un total pequeno: estan censurados a dic-2006, no faltan por datos.
- La residualizacion aqui es de cada dosis por separado (lo que pide T2); en la regresion del perfil Y = sum_a beta_a V_{m,c+a} + mu_m + lambda_{c x dpto} lo relevante es la matriz completa de dosis residualizadas, de ahi el VIF y el numero de condicion.

Tiempo de ejecucion: 58 s.

## Log de ejecucion

```
Casos leidos: 161887 (MA+AS); con codigo DANE 5 digitos y anio 1985-2015: 150461; excluidos: 81 con codigo no numerico (exterior), 11345 con anio fuera de rango; victimas NA: 0
Victimas por grupo 1985-2015: {'EST': 7011, 'GUE': 30826, 'NI': 61491, 'PARA': 88615, 'POSD': 4717}
Verificacion vs panel del PI (cnmh_muni_month_victims.csv): filas solo mias=0, solo PI=64 (codigos: {'EXVEN': 43, 'EXECU': 12, 'EXPAN': 9}), max |diff| por grupo en filas comunes={'PARA': 0.0, 'POSD': 0.0, 'GUE': 0.0, 'EST': 0.0, 'NI': 0.0}

== T1(a) == PARA 1997-2006 nacional (codigos 5 digitos, incl. 00000) = 68869
Municipios con >=25 victimas PARA 1997-2006: 453 (concentran 94.3%); 00000 ('SIN INFORMACION', 63 victimas) esta dentro: True -> T de trabajo = 452 municipios (94.2%)

== T1(b) == entrada/salida anual (>=3 PARA, 1996-2006), T=452 (sin 00000); 00000: entry=1996, exit=2006
Salida (T sin 00000): {1998: 1, 1999: 1, 2000: 5, 2001: 4, 2002: 17, 2003: 52, 2004: 93, 2005: 216, 2006: 63}
Salida (453 con 00000): {1998: 1, 1999: 1, 2000: 5, 2001: 4, 2002: 17, 2003: 52, 2004: 93, 2005: 216, 2006: 64}
Entrada (T): {1996: 216, 1997: 85, 1998: 40, 1999: 40, 2000: 35, 2001: 26, 2002: 7, 2003: 3}
Duracion: mediana=9, p25=7, p75=10, media=8.10; sin NA: 452

== T1(c) == TOT medio/anio en T: 2000-02=15202, 2007-10=1850, ratio=0.122 (453 con 00000: 15226 -> 1856, ratio 0.122; nacional: 0.135; solo PARA+POSD en T: 0.060)
grp    PARA  POSD   GUE   EST    NI    TOT
year                                      
1996   4322     0  1143    82  3260   8807
1997   5917     0  1246    89  3486  10738
1998   5052     0  1033    97  2862   9044
1999   6074     0  1361    55  3175  10665
2000   8730     0  1303    67  4179  14279
2001   9662     0  1358    48  3851  14919
2002  10503     0  1504   265  4135  16407
2003   8599     0   987   280  2932  12798
2004   6106     0   784   351  2536   9777
2005   3580     0   620   401  1787   6388
2006    681   718   539   656  1151   3745
2007      0   776   451  1151   771   3149
2008      0   584   321   489   551   1945
2009      0   537   278    49   481   1345
2010      0   399   211    32   320    962

== T1(d) == mes de salida (<= 5% de victimas PARA restantes hasta dic-2006; solo Mes>=1)
          variante  n_munis_incluidos  n_con_mes_salida  share_para_9706_nacional  share_para_9706_en_T
        V1_todos_T                452               450                    0.9416                0.9991
    V2_mes0_le5pct                433               431                    0.9259                0.9825
V3_sin_ningun_mes0                254               252                    0.2885                0.3062
                       V1_todos_T  V2_mes0_le5pct  V3_sin_ningun_mes0
<2002                           4               3                   2
2002S1                          2               2                   2
2002S2                          2               2                   1
2003S1                         19              19                  15
2003S2                         29              26                  18
2004S1                         59              57                  30
2004S2                         92              89                  52
2005S1                        121             117                  65
2005S2                        101              95                  54
2006S1                         16              16                   9
2006S2                          5               5                   4
censurado (>dic-2006)           2               2                   2
Diferencia anio(mes de salida) - anio de salida anual, variante V2_mes0_le5pct: {-2.0: 12, -1.0: 96, 0.0: 256, 1.0: 49, 2.0: 10, 3.0: 3, 4.0: 4, 6.0: 1}
Distribucion anual del mes de salida (variante primaria): {2000.0: 2, 2001.0: 1, 2002.0: 4, 2003.0: 45, 2004.0: 146, 2005.0: 212, 2006.0: 21}

== T2 == celdas municipio x cohorte: 9492 (452 municipios x 21 cohortes). Cohortes con dato por ventana: {'iu': '1988-2008', 'a02': '1988-2008', 'a35': '1988-2008', 'a611': '1988-2003'}
Departamentos en T: 28; con un solo municipio en T (residuo = 0 mecanicamente bajo EF cohorte x dpto): 3 ['BOGOTA, D. C.', 'BOYACA', 'VICHADA']

(1) corr bruta 0-2/3-5 (n=9492): 0.6784

(2) spec A (EF muni + EF cohorte x dpto): var share: {'iu': 0.4935, 'a02': 0.4436, 'a35': 0.475, 'a611': 0.4001}
    corr resid: {'iu_a02': 0.6138, 'a02_a35': 0.4074, 'a35_a611': -0.0069}
    balanceada (n=7232): VIF=[2.55, 2.42, 1.34, 2.8], cond(X std)=3.13, cond(corr)=9.78
    matriz corr residual (balanceada):
         iu    a02    a35   a611
iu    1.000  0.582 -0.257 -0.709
a02   0.582  1.000  0.200 -0.715
a35  -0.257  0.200  1.000 -0.007
a611 -0.709 -0.715 -0.007  1.000

(2) spec B (EF muni + EF cohorte): var share: {'iu': 0.5224, 'a02': 0.4689, 'a35': 0.5013, 'a611': 0.4192}
    corr resid: {'iu_a02': 0.61, 'a02_a35': 0.4032, 'a35_a611': -0.006}
    balanceada (n=7232): VIF=[2.49, 2.36, 1.33, 2.68], cond(X std)=3.05, cond(corr)=9.30
    matriz corr residual (balanceada):
         iu    a02    a35   a611
iu    1.000  0.578 -0.257 -0.701
a02   0.578  1.000  0.199 -0.705
a35  -0.257  0.199  1.000 -0.006
a611 -0.701 -0.705 -0.006  1.000

Robustez de escala (spec A): top 1% municipios excluidos = ['MEDELLIN (5997)', 'VALLEDUPAR (1283)', 'SANTA MARTA (1217)', 'CIENAGA (1251)', 'CUCUTA (2502)']
    niveles (titular): var share 0-2=0.444, 3-5=0.475, corr resid 0-2/3-5=0.407 (n=9492)
    niveles sin top 1% municipios: var share 0-2=0.439, 3-5=0.457, corr resid 0-2/3-5=0.283 (n=9387)
    share del total municipal 1996-2006: var share 0-2=0.358, 3-5=0.308, corr resid 0-2/3-5=-0.076 (n=9492)

(3) celdas 0-2>0 & 3-5=0: 1483 de 9492 (15.62%); entre celdas con 0-2>0 (7286): 20.35%
    cohorte - anio de salida anual en esas celdas: {-17: 11, -16: 17, -15: 28, -14: 23, -13: 16, -12: 17, -11: 10, -10: 2, -9: 2, -8: 1, -3: 36, -2: 305, -1: 395, 0: 392, 1: 138, 2: 54, 3: 23, 4: 9, 5: 3, 6: 1}
    balanceada 1988-2003: 0-2>0 & 3-5=0 & 6-11=0: 483; ademas in utero=0: 32

(4) celdas nacidas tras la salida (anual): 1595 de 9492; con cohorte <= 2006: 691 en 389 municipios; con salida por mes: 1606 (<=2006: 706)
    dosis en celdas tras salida (anual):
            iu      a02      a35
count  1595.00  1595.00  1595.00
mean      0.64     0.26     0.02
std       1.58     0.73     0.18
min       0.00     0.00     0.00
25%       0.00     0.00     0.00
50%       0.00     0.00     0.00
75%       1.00     0.00     0.00
max      26.00     6.00     3.00

VEREDICTO T2: APROBADO: corr residual 0-2/3-5 = 0.407 (umbral aprobado < 0,7; letal > 0,8); varianza residual 0-2 = 44.4%, 3-5 = 47.5% (aprobado > 20%; letal < 10%); spec A (EF muni + cohorte x dpto), cohortes 1988-2008, dosis en niveles. Sensibilidad a la escala: niveles sin top 1% municipios: corr 0.28, var. res. 0-2 44%, 3-5 46% -> APROBADO; share del total municipal 1996-2006: corr -0.08, var. res. 0-2 36%, 3-5 31% -> APROBADO; asinh(dosis): corr 0.23, var. res. 0-2 17%, 3-5 14% -> ZONA GRIS; niveles, balanceada 1988-2003: corr 0.20, var. res. 0-2 34%, 3-5 35% -> APROBADO.

Convergencia demeaning: max iteraciones=2, todas convergieron=True, max |diff| vs lstsq=5.91e-12
```
