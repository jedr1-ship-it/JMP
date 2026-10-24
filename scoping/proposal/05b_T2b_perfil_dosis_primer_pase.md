# T2b. Perfil dosis-por-edad en Saber 11: primer pase de viabilidad

Memo del RA (2026-10-24). Script: `code/analysis/t2b_dose_profile_saber11.py` (python3 -I; 8 min en 4 CPU). Insumos: `data/derived/saber11_slim.parquet`, `cnmh_muni_month_victims.csv` (PARA), `t2_A_T1_muestra_T.csv` (mes de salida `exit_ym` por municipio; `t2_A_T1d_salida_mensual_mes.csv` es su distribución). Salidas: `data/derived/t2b_dose_individual_sample.parquet`, `t2b_coeficientes.csv`, `t2b_tests.csv`, `t2b_descriptivos.csv`, `t2b_within_corr.csv`, `t2b_fe_check*.csv`, `t2b_tabla_principal.csv`; figura `fig5_perfil_dosis_edad_saber11.pdf`.

## 1. Construcción y especificación

**Dosis.** Para cada evaluado con año y mes de nacimiento, `muni_res` y `score_z`, víctimas PARA (masacres + asesinatos selectivos CNMH, panel 1985-01 a 2015-12, PARA = 0 desde 2007) acumuladas en el municipio de residencia en ventanas de meses relativas al mes de nacimiento: pre-concepción [−45, −10], in utero [−9, −1], 0-2 [0, 35], 3-5 [36, 71], 6-11 [72, 143], 12-17 [144, 215], todas truncadas en el mes del examen (15-mar/15-ago), lo que sólo muerde en 12-17. Implementación: matriz municipio × mes de acumulados y diferencias por índice (sin bucles); verificada contra sumas directas del panel en cinco individuos (0 discrepancias). Municipios sin víctimas registradas reciben dosis 0. Limitación central: el municipio de exposición es la residencia a los 16-18. La ventana pre-concepción está censurada a la izquierda para las cohortes 1985-88 (panel desde 1985); se añade la robustez 1989-2005.

**Escalas.** (i) log(1 + víctimas). (ii) víctimas por 100 evaluados de la celda municipio × cohorte de nacimiento: el repositorio no tiene población DANE por municipio y edad, y el número de evaluados de la cohorte es el único proxy de tamaño disponible a esa resolución; su defecto es que es endógeno (sólo quienes llegan a 11º; el denominador cae donde la violencia reduce la presentación), por lo que la tabla añade (ii-f) con denominador fijo (media municipal de la celda, cohortes 1990-2003) y (ii-w) winsorizada en el p99 (cola: máximos de 500-3.500 por 100 en municipios pequeños).

**Muestra.** Cohortes 1985-2005 con mes de nacimiento, `muni_res`, `score_z` y sexo: **N = 8.796.382** (de 8.862.194 filas de esas cohortes), 1.122 municipios, 693 celdas cohorte × departamento. Muestra T: 451 de los 452 municipios con evaluados, **N = 7.065.327** (80,3 % de los evaluados, 99,7 % de la dosis: T incluye las grandes ciudades). Dosis 0-2 > 0 en el 85 % (media 109 víctimas, mediana 22).

**Modelo.** score_z = Σ_a β_a·dosis_a + γ·mujer + μ_muni + λ_{cohorte×dpto} + ε, errores agrupados por municipio (CR1). EF absorbidos por proyecciones alternantes (8 iteraciones; medias de grupo residuales < 2·10⁻¹¹ relativas) y verificados contra OLS con dummies en una submuestra de 80.000 (3 departamentos): diferencia máxima en β 2·10⁻¹⁶, EC agrupados iguales salvo el factor de grados de libertad. Correlaciones within de las dosis (log) 0-2/3-5 = 0,10, 0-2/6-11 = −0,24: sin colinealidad.

## 2. Resultados (score_z, 6 ventanas; β, EE)

| Ventana | Todos, log | T, log | Todos, por 100 | T, por 100 |
|---|---|---|---|---|
| Pre-concepción (placebo) | **+0,0143** (0,0031) | **+0,0140** (0,0035) | +0,0001 (0,0002) | −0,0000 (0,0003) |
| In utero | +0,0021 (0,0019) | +0,0023 (0,0019) | −0,0002 (0,0003) | −0,0003 (0,0003) |
| 0-2 | +0,0028 (0,0026) | +0,0030 (0,0032) | **+0,0004** (0,0002) | **+0,0004** (0,0002) |
| 3-5 | −0,0004 (0,0019) | −0,0013 (0,0023) | **+0,0004** (0,0002) | +0,0004 (0,0002) |
| 6-11 | **+0,0073** (0,0025) | **+0,0070** (0,0035) | **+0,0006** (0,0001) | **+0,0006** (0,0001) |
| 12-17 (hasta examen) | **−0,0092** (0,0035) | **−0,0102** (0,0041) | **+0,0004** (0,0001) | **+0,0005** (0,0001) |
| Mujer | −0,148 (0,010) | −0,152 (0,011) | −0,148 (0,010) | −0,152 (0,011) |
| H0: β(0-2) = β(3-5), p | 0,07 | 0,05 | 0,69 | 0,56 |

Negrita: p < 0,05. R² within ≈ 0,006. En unidades de una DE within de la dosis, todos los β están entre −0,006 y +0,011 DE de puntaje; el EE típico es 0,0015 DE, de modo que la precisión no es el problema. (c) Con sólo in utero/0-2/3-5/6-11 el perfil es el mismo (0-2: +0,0055, 3-5: −0,0000 en log; igualdad p = 0,005). (e) Matemáticas y lectura reproducen el patrón (log: placebo +0,009, 12-17 −0,011/−0,012; por 100: +0,0002 a +0,0008). (f) En T con mes de salida fiable (430 municipios, N = 6.943.699), "nacido ≥ 12 meses después de la salida" (38.291 evaluados, 197 municipios, cohortes 2001-2005) da **+0,028 (0,015)** en la especificación log y +0,021 (0,015) en la de por 100. (g) Placebo: +0,014 (p < 0,001) en log, con cohortes 1989-2005 (+0,009, p < 0,001) y sin los 5 municipios de mayor dosis (+0,013); ≈ 0 en por 100.

## 3. Lectura frente a H1/H2

H1 (hogar) predice β_a < 0 desde in utero y decreciente con la edad; H2 (memoria) β_a ≈ 0 antes de los 3 y crecientemente negativo después. **Este pase no muestra ninguna de las dos formas.** El perfil es plano y de signo positivo; la ventana con mayor coeficiente en log es la pre-concepción, que debía ser cero (bajo H1 estricta no es placebo puro porque alcanza a los padres, pero su signo positivo no es un daño); en por 100 las cuatro ventanas post-natales valen lo mismo (+0,0004 a +0,0006), es decir, una asociación con la dosis total, no un gradiente de edad; y 12-17 cambia de signo entre escalas. Los nacidos tras la salida puntúan marginalmente más, lo contrario de la herencia que predice H1, y sólo compatible con H2 en el sentido débil de "no hay efecto". La lectura más plausible es selección: con EF de municipio y cohorte × departamento, la variación identificadora es el calendario de la violencia dentro de cada municipio, y las cohortes que la recibieron en la infancia están compuestas por quienes se quedaron o llegaron y además llegaron a 11º (P2 y P5 de la carta), un grupo positivamente seleccionado. A esto se suma la residencia a los 16-18 como municipio de exposición y una dosis sin población.

Qué queda establecido: la tubería funciona a escala (8,8 M de observaciones, EF absorbidos y verificados), las ventanas no son colineales a nivel individual y la potencia sobra (un efecto de 0,02 DE por DE within de dosis se detectaría con holgura). Qué no: la identificación. Siguientes pasos: municipio del colegio para las cohortes pre (2005-2011); municipio de nacimiento (GEIH) o enlace UARIV; muestra de stayers con RUV; margen extensivo con denominadores EEVV; dosis per cápita con población DANE; diseño de celdas relativas a la salida municipal con EF de periodo de examen y edad al examen, que es donde la variación de calendario es más limpia.
