# 09. T6: perfil per cápita con dos relojes y event study de celdas relativas a la salida

Memo del RA (24-oct-2026). Scripts: `code/analysis/t6_percapita_profile.py` (perfil per cápita, controles por perpetrador, dos relojes) y `code/analysis/t6_event_study_exit.py` (celdas relativas a la salida y a la entrada municipal). Tablas `data/derived/t6_pc_*.csv`, `t6_dos_relojes_*.csv`, `t6_es_*.csv`; figuras `scoping/proposal/fig9_perfil_percapita.pdf` (y `slides/fig9_percapita_slides.pdf`) y `fig8_event_study_salida.pdf`. Responde a las pruebas 1 y 2 de 05e §4 y a la acción 2 (72 h) de la carta 08.

## 1. Muestra y especificación comunes

Saber 11 2005-1 a 2022-2, cohortes 1988-2003 (observadas completas a 16-19), calendario A, sin 2017-2 (truncado), con `score_z`, sexo y edad al examen. Flujo: 7.725.125 evaluados de esas cohortes → 6.165.470 en los 451 municipios T → 5.724.201 en calendario A → 5.668.766 sin 2017-2 → 5.666.185 con variables; **sin los 7 municipios de ≥ 500 mil habitantes: N = 3.192.473, 444 conglomerados**. Dosis = víctimas (CNMH, mensual) o expulsados (RUV, anual repartido a 1/12 por mes) por 1.000 habitantes de 2005 (Panel CEDE), acumulados en ventanas de longitud fija relativas al mes de nacimiento: pre-concepción [−45, −10], in utero [−9, −1], 0-2 [0, 35], 3-5 [36, 71], 6-11 [72, 143], 12-17 [144, 215] (sin truncar en el examen). Variante winsorizada en el p99 (`pcw`). EF: municipio, cohorte × departamento y **periodo de examen × edad al examen**; errores agrupados por municipio (CR1); EF absorbidos por proyecciones alternantes (comprobación de medias residuales < 2·10⁻¹¹). Coeficientes reportados por DE within de la dosis.

## 2. Prueba 2: perfil per cápita y perpetrador (`t6_pc_coefs.csv`, `t6_pc_tests.csv`)

Sin grandes ciudades, EF completos, β × DE within (EE):

| Ventana | PARA sola | PARA con GUE y EST | GUE sola | GUE (con PARA y EST) |
|---|---|---|---|---|
| Pre-concepción | +0,0058 (0,0031), p = 0,06 | +0,0041, p = 0,17 | +0,0046, p = 0,03 | +0,0024 |
| In utero | +0,0025 | +0,0014 | +0,0029 | +0,0016 |
| 0-2 | **+0,0090**, p = 0,003 | +0,0057, p = 0,07 | **+0,0067** | **+0,0044** |
| 3-5 | **+0,0075**, p = 0,02 | +0,0039 | **+0,0073** | **+0,0061** |
| 6-11 | **+0,0202**, p < 0,001 | **+0,0135** | **+0,0132** | **+0,0088** |
| 12-17 | **+0,0127**, p < 0,001 | **+0,0076** | **+0,0133** | **+0,0097** |
| H0: β(0-2) = β(3-5), p | 0,17 | 0,12 | 0,58 | 0,15 |

Negrita: p < 0,05. Con las ciudades grandes (N 5,67 M, 451 clusters) y con la dosis winsorizada el cuadro es el mismo (PARA sola: 0-2 +0,0054, 6-11 +0,0154, 12-17 +0,0104; placebo +0,0021, p = 0,46). Fuerza pública (EST) sola o conjunta: coeficientes negativos a 3-5 y 6-11 (−0,007 a −0,012, p 0,02-0,07) y nulos antes. Posdesmovilización (POSD) como placebo: todos nulos (p > 0,3).

Lectura. (i) En la escala per cápita, con ventanas fijas y EF de periodo × edad, **no hay gradiente de edad en la dirección predicha por H1 ni por H2**: la asociación es positiva, crece con la edad y es máxima en edad escolar (6-11). (ii) El perfil de la guerrilla tiene la misma forma y magnitud; condicional a guerrilla y Estado, el paramilitar se reduce a la mitad y pierde la significación en primera infancia. **Lo que se mide es cronología y composición, no edad de exposición a un actor.** (iii) El placebo pre-concepción paramilitar es +0,006 (p = 0,06; +0,004 condicional), menor que en log (05b) pero del mismo signo; el de la guerrilla es significativo (p = 0,03). (iv) Respecto de 05b: la escala per cápita elimina el cambio de signo de 12-17 (que era mecánico por el truncamiento en el examen) y reduce el placebo, pero no crea ningún perfil.

## 3. Dos relojes: separabilidad (`t6_dos_relojes_corr.csv`, `t6_dos_relojes_coefs.csv`)

Correlación residual entre V_a (víctimas PARA por 1.000) y E_a (expulsados RUV por 1.000) a nivel de celda municipio × cohorte (7.104 celdas sin grandes ciudades), tras EF municipio + cohorte × departamento: **0,49 / 0,46 / 0,50 / 0,49 / 0,51 / 0,48** (pre-concepción, in utero, 0-2, 3-5, 6-11, 12-17); VIF del par 1,27-1,34; VIF de cada ventana dentro de las 12 dosis 1,7-5,7. Correlación residual V_a con guerrilla 0,22-0,38. **Veredicto PI: aprobado (ρ < 0,7) en todas las ventanas**: los dos relojes son separables.

Conjunta (PARA + RUV, sin grandes ciudades, β × DE within):

| Ventana | V_a (víctimas, dado E) | E_a (expulsiones, dado V) |
|---|---|---|
| Pre-concepción | **+0,0103** (p = 0,005) | **−0,0140** (p = 0,01) |
| In utero | **+0,0039** (p = 0,02) | **−0,0039** (p = 0,03) |
| 0-2 | **+0,0126** (p < 0,001) | **−0,0136** (p = 0,009) |
| 3-5 | **+0,0091** (p = 0,02) | −0,0100 (p = 0,05) |
| 6-11 | **+0,0210** (p < 0,001) | **−0,0165** (p = 0,03) |
| 12-17 | **+0,0088** (p = 0,002) | −0,0015 (p = 0,80) |

Con guerrilla y Estado añadidos, igual (V: +0,0087 placebo, +0,0090 0-2, +0,0160 6-11; E: −0,0146 placebo, −0,0134 0-2, −0,0169 6-11). RUV sola: negativa en todas las ventanas, −0,013 en pre-concepción (p = 0,03).

Lectura. Separables sí; identificados no. **Ambos relojes fallan el placebo**, con signos opuestos: entre quienes residen en el municipio a los 17 y se presentan, los de municipios con más víctimas puntúan mejor y los de municipios con más expulsión puntúan peor, y lo hacen ya para la ventana anterior a la concepción, sin gradiente de edad. Es exactamente la firma de la composición que la carta 08 describe: la violencia expulsa de forma selectiva y la muestra residente se queda con quienes no se fueron (o llegaron). Lo que sí deja este ejercicio: la condición previa de la diapositiva 10 (ρ < 0,7) se cumple en Saber 11 y, por la estructura municipal de ambos registros, cabe esperar que se cumpla con municipio de nacimiento en la GEIH; el test H1'/H2' es viable si la localización es pretratamiento.

## 4. Prueba 1: event study de celdas relativas a la salida y a la entrada

ES_PLACEHOLDER

## 5. Veredicto

ES_VEREDICTO
