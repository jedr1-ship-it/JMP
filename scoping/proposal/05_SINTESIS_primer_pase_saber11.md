# 05. Síntesis del primer pase en Saber 11 (memos 05a-05e)

Memo del RA senior (24-oct-2026). Fuentes: 05a (T3 conteos y potencia), 05b (T2b perfil dosis-por-edad), 05c (T5 desplazamiento), 05d (verificación adversarial), 05e (crítica del referee) y `data/derived/saber11_slim_codebook.md`. Cifras contrastadas con `t2b_coeficientes.csv`, `t2b_verify_compare.csv`, `t3_potencia.csv` y `t5_stayer_umbrales.csv`.

## 1. Datos en mano y cobertura

- **Saber 11** (`data/derived/saber11_slim.parquet`): 36 archivos ICFES, periodos 2005-1 a 2022-2, 9.293.650 filas deduplicadas. Variables: periodo/año/calendario, consecutivo, fecha de nacimiento (día, mes, año), edad al examen, municipio y departamento de residencia (desde 2005-1; cobertura ≥ 97,6 % salvo 2009-2 = 93 %, reconstruido por nombre, y 2010-1 = 88 %), municipio y naturaleza del colegio, sexo, estrato y educación de la madre (2005 y 2008+; no existen en 2006-07), INSE y puntaje global (2014-2+), `score_z` estandarizado dentro de cada periodo, `math_z`, `lang_z`. Defectos documentados: 2017-2 truncado (73.293 de ~550 mil filas; muerde en las cohortes 1999-2001), cambio de escala en 2014-2, calendario B estandarizado sobre una población no comparable.
- **Cohortes**: 1985-2005 con residencia = 8,80 M (7,07 M en T, 1,73 M fuera; T = 80 % de los evaluados, con Bogotá 1,60 M). Observadas a edades 16-19 completas sólo 1988-2003 (385 mil por cohorte en T; mediana de celda municipio × cohorte 206; 415 municipios T con ≥ 30 evaluados en las 16 cohortes). Coincidencia residencia = colegio 94,4 % (T 95,1 %): proxy válido para 2005-2011. Rezago (> 19 años) 10,1 % en T, 12,2 % fuera.
- **Muestra analítica T2b**: N = 8.796.382 (1.122 municipios, 693 celdas cohorte × dpto); T = 7.065.327 (451 municipios, 588 celdas); T con mes de salida fiable = 6.943.699 (430 municipios).
- **CNMH** (`cnmh_muni_month_victims.csv`): panel municipio × mes 1985-2015 por perpetrador; PARA 1997-2006 = 67.974 víctimas con municipio válido. T = 451 municipios con ≥ 25 víctimas (452 códigos; `47000` no es municipio: los memos deben unificar en 451).
- **RUV** (corte sep-2016): 5.694.661 expulsados 1997-2010, panel municipio × año. **Población 2005 DANE** (Panel CEDE, 1.122 municipios): ya está en el repositorio, contra lo que afirma 05b, y habilita la dosis per cápita.

## 2. Perfil dosis-por-edad: tabla única con verificación

Especificación: score_z = Σ_a β_a·dosis_a + γ·mujer + μ_muni + λ_{cohorte×dpto} + ε; muestra T, cohortes 1985-2005, N = 7.065.327, 451 clusters (CR1 por municipio), R² within 0,006. Dosis = víctimas PARA en el municipio de residencia en ventanas de meses relativas al nacimiento. Verificación (05d): código independiente, dosis contrastada en 420 celdas sin discrepancias, los 28 coeficientes de la tabla principal reproducidos con máx |Δβ| = 4·10⁻¹⁰ y N y clusters idénticos.

| Ventana | T, log(1+v): β [IC 95 %] | T, por 100 evaluados (×10³): β [IC 95 %] | Réplica 05d | Ruptura 05d, log: sin post contaminado (N 6,14 M) / escala nueva ≥ 2014-2 (N 3,44 M) |
|---|---|---|---|---|
| Pre-concepción [−45, −10] (placebo) | **+0,0140** [0,0072; 0,0209] | −0,01 [−0,52; 0,49] | Δβ < 10⁻⁹ | **+0,0116*** / +0,0042 |
| In utero | +0,0023 [−0,0015; 0,0061] | −0,27 [−0,90; 0,35] | ídem | −0,0001 / +0,0078 |
| 0-2 | +0,0030 [−0,0032; 0,0092] | **+0,44** [0,12; 0,77] | ídem | +0,0013 / −0,0083* |
| 3-5 | −0,0013 [−0,0058; 0,0033] | +0,36 [−0,01; 0,72] | ídem | −0,0037 / +0,0007 |
| 6-11 | **+0,0070** [0,0001; 0,0139] | **+0,61** [0,36; 0,85] | ídem | +0,0009 / −0,0073* |
| 12-17 (hasta el examen) | **−0,0102** [−0,0183; −0,0021] | **+0,48** [0,36; 0,60] | ídem | **−0,0201*** / **−0,0585*** |
| Mujer | −0,152 [−0,174; −0,130] | −0,152 [−0,174; −0,130] | ídem | — |
| H0: β(0-2) = β(3-5), p | 0,05 | 0,56 | — | 0,02 / 0,06 |
| H0: placebo = 0, p | < 0,001 | 0,96 | — | — |

Negrita: p < 0,05. En DE de puntaje por DE within de dosis, todos los β caen entre −0,006 y +0,008; EE típico 0,0015 DE. La muestra completa (N 8.796.382, 1.122 clusters) da el mismo cuadro. "Nacidos ≥ 12 meses tras la salida" = +0,028 (EE 0,015, p = 0,06; T431): **no verificado en 05d, no citar**. Lectura común de 05b y 05d: ningún perfil H1/H2. El placebo es positivo y significativo en log con cualquier submuestra (cohortes 1989-2005 +0,009; sin top-5 +0,013; ventana −81..−46 +0,008***), y el signo de cada ventana cambia con la escala, el periodo de examen y el perpetrador (la guerrilla sola reproduce el perfil en por 100 y lo absorbe en la conjunta). Es selección por composición de cohortes y calendario, no un efecto de la edad de exposición.

## 3. Potencia y desplazamiento frente a los umbrales del PI

| Test | Umbral PI (aprobado / gris / letal) | Resultado | Estado |
|---|---|---|---|
| T2 identificación (02) | ρ resid 0-2/3-5 < 0,7 / 0,7-0,8 / > 0,8; var. resid > 20 % / 10-20 % / < 10 % | niveles: ρ = 0,41, var 44-48 %; log: ρ ≈ 0,23, var 17 % y 14-15 %; 6-11 en log 7-8 %; ρ(0-2, 6-11) = −0,72 | **Aprobado en niveles, gris en log, letal para 6-11 en log**; escala sin fijar |
| T3 potencia | MDE ≤ 0,04 DE | T vs resto 0,058; dentro de T con cluster municipio: ventana 0,025, nacidas ≤ 2 años antes de la salida 0,024, 3-5 antes 0,010, placebo post-salida 0,034; estimador real post-salida EE 0,015 ⇒ MDE 0,042 | **Aprobado** para contrastes binarios dentro de T; **gris** para el placebo post-salida tal como se estimó; Moulton por celda (0,003-0,006) no vinculante |
| T3 presentación | tasa 0,3-1,2 en 90 % de T | sin EEVV; índice T/resto cae de 1,02 (1989) a 0,91 (1998-2004) | **Pendiente** |
| T5 stayers (expulsión < 10 %) | ≥ 30 % / 15-30 % / < 15 % de la dosis | 37,0 % (35,8 % de la dosis T); al 5 %: 28,4 %; sin Medellín: 31,3 %; T con < 100 mil hab.: 19,3 % | **Aprobado en el agregado, gris sin Medellín, al borde de letal en los municipios pequeños** que aportan la variación de calendario |
| Muerte: pendiente pre > 1/3 del efecto | — | placebo pre-concepción +0,014 (t ≈ 4) ≥ cualquier β post-natal | **Incumplido** en el perfil continuo (05d) |

Tasa mediana de expulsión 1997-2010 en T: 22,9 % de la población 2005 (fuera de T, 4,6 %); 70,7 % de T supera el 10 %. Correlación con la dosis per cápita 0,63 (0,56 en T), la misma para guerrilla: el desplazamiento responde a la violencia total.

## 4. Lo que el referee considera defendible y lo que no

**Defendible (05e §3, confirmado por 05d):** los hechos del panel CNMH (94 % de la dosis en ~450 municipios, duración mediana 9 años, 70 % de las salidas entre jul-2004 y dic-2005, ratio post/pre 0,12); que la tubería estima el perfil a escala (8,8 M de observaciones, EF absorbidos y verificados, EE ≈ 0,0015 DE); una cota descriptiva: entre residentes a los 17 que llegan a 11º, la asociación within-municipio entre cronología PARA y puntaje es ≤ 0,01 DE por DE de dosis y sin gradiente de edad; y que el desplazamiento rural en T es masivo y responde a la violencia total.

**No defendible:** cualquier lectura causal de 05b sobre H1/H2 (placebo positivo = selección); el "APROBADO" de T2 sin escala fijada (log(1+v) identifica con municipios pequeños que pasan de 0 a pocas víctimas; por 100 evaluados tiene denominador endógeno con sesgo positivo mecánico); la ventana 12-17 truncada en el examen (su longitud depende del rezago, luego β < 0 es en parte mecánico); EF sin guerrilla ni fuerza pública y sin periodo × edad al examen; cohortes 1985-2005 cuando sólo 1988-2003 están completas, con 2017-2 incluido; el placebo post-salida con la regla del 5 % (Medellín sale en sep-2004 con 172 víctimas después), que además bajo H1 no separa H1 de H2; que P2 "sea acotable" con stayers (cierto en ciudades, falso en los municipios rurales que retienen el 19 % de su dosis); que el margen extensivo sea fecundidad; y el pitch de empleo y diagnósticos sin datos. Inconsistencias a cerrar: T = 453/452/451; "99,7 % de la dosis" (ponderado por evaluados) frente a 94,2 % (municipal); placebo post-salida 64 mil/173 (05a) vs 38 mil/197 (05b) vs 691 celdas (02); coincidencia 93,7 % vs 94,4 %.

**Tres pruebas en una semana (05e §4):** (1) event study de cohortes relativas al mes de salida (y de entrada en los ~120 municipios limpios), sin municipios ≥ 500 mil hab., con score_z, log N de celda y composición; (2) perfil per cápita (víctimas por 1.000 hab. con población CEDE), ventanas de longitud fija, cohortes 1988-2003, sin 2017-2 ni calendario B, EF periodo × edad, guerrilla y estatales como controles; (3) balance de covariables predeterminadas y heterogeneidad por cuartil de expulsión RUV, inicio de las cotas de Lee.

## 5. Figuras y tablas disponibles para la presentación

1. `scoping/proposal/fig5_perfil_dosis_edad_saber11.pdf` — perfil de 6 ventanas, todos/T × log/por 100 (tabla: `data/derived/t2b_tabla_principal.csv`).
2. `scoping/proposal/fig7_verificacion_adversarial.pdf` — réplica y pruebas de ruptura P1-P5, E2-E3 (p. 1 log, p. 2 por 100; `data/derived/t2b_verify_compare.csv`, `t2b_verify_coefs.csv`).
3. `scoping/proposal/fig6_desplazamiento_vs_dosis.pdf` — tasa de expulsión vs dosis (a-b) y dosis retenida por umbral stayer (c; `data/derived/t5_stayer_umbrales.csv`, `t5_correlaciones.csv`).
4. `scoping/proposal/figs_t3_N_cohorte_T.pdf` — evaluados por cohorte en T y fuera, con 2017-2 imputado (`data/derived/t3_resumen_cohorte.csv`).
5. `scoping/proposal/figs_t3_margen_extensivo.pdf` — índice T/resto por cohorte (`data/derived/t3_margen_extensivo.csv`).
6. `scoping/proposal/figs_t3_coincidencia.pdf` — coincidencia residencia = colegio por periodo (`data/derived/t3_coincidencia_periodo.csv`).
7. `scoping/proposal/figs_t3_edad_rezago.pdf` — edad al examen y rezago por cohorte, T vs resto (`data/derived/t3_edad_cohorte.csv`).
8. Tabla de potencia `data/derived/t3_potencia.csv` (resumen en `t3_numeros_clave.json`); contexto CNMH de la ronda anterior en `scoping/proposal/slides/fig1_victimas_anuales.pdf` a `fig4_dosis_por_cohorte_y_ventana.pdf`.

**Veredicto de síntesis:** la pata pública de Saber 11 está construida y verificada de extremo a extremo; de este pase entran en el paper la prueba de escala y una cota descriptiva, no un perfil de edad. El diseño principal (celdas relativas a la salida municipal) sigue sin estimarse y es la prueba 1 de la semana próxima.
