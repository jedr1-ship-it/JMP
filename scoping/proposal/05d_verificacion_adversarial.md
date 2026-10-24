# T2b. Verificación adversarial del perfil dosis-por-edad

Memo del econometrista revisor (2026-10-24). Script propio `code/analysis/t2b_verify.py` (python3 -I; 7,5 min), que parte de `saber11_slim.parquet` y `cnmh_muni_month_victims.csv` sin leer ningún intermedio `t2b_*` del RA B (`t2b_coeficientes.csv` sólo para la tabla comparativa). Salidas: `data/derived/t2b_verify_{coefs,compare,fecheck,dosecheck,resumen}.*`; figura `scoping/proposal/fig7_verificacion_adversarial.pdf` (p. 1 log, p. 2 por 100).

## 1. Réplica

Mismo flujo muestral (8.862.194 → 8.796.382; T = 7.065.327, 451 municipios). Dosis con código propio, contrastada en 30 individuos × 7 ventanas × 2 perpetradores (420 celdas) contra sumas directas del panel: 0 discrepancias. Absorción de EF propia, contrastada con `linearmodels.AbsorbingLS` en 400.000 obs: |Δβ| ≤ 3·10⁻¹⁷, EE iguales (ratio 1,0005). **Los 28 coeficientes y EE de la tabla principal del RA B (todos/T × log/por 100) se reproducen: máx |Δβ| = 4·10⁻¹⁰, N y clusters idénticos.** El perfil de 4 ventanas (c) también.

## 2. Pruebas de ruptura (muestra T, score_z, escala log; β (EE); * p<0,10 ** p<0,05 *** p<0,01)

| Ventana | Base | P1 sin post contam. | P2 antigua <2014-2 | P2 nueva ≥2014-2 | P3 colegio | P4 coh. 1992+ | P5 GUE sola | P5 PARA \| GUE | E3 + edad examen |
|---|---|---|---|---|---|---|---|---|---|
| pre2 (−81..−46) | — | — | — | — | — | **+0,0082** (0,0028)*** | — | — | — |
| pre-concepción | **+0,0140** (0,0035)*** | **+0,0116** (0,0035)*** | **+0,0211** (0,0039)*** | +0,0042 (0,0042) | **+0,0154** (0,0034)*** | **+0,0088** (0,0029)*** | +0,0033 (0,0039) | **+0,0161** (0,0039)*** | +0,0072 (0,0041)* |
| in utero | +0,0023 (0,0019) | −0,0001 (0,0017) | +0,0025 (0,0026) | +0,0078 (0,0048) | +0,0026 (0,0019) | +0,0033 (0,0018)* | −0,0015 (0,0021) | +0,0029 (0,0019) | +0,0035 (0,0027) |
| 0-2 | +0,0030 (0,0032) | +0,0013 (0,0030) | **+0,0114** (0,0048)** | −0,0083 (0,0048)* | +0,0025 (0,0032) | −0,0007 (0,0034) | −0,0013 (0,0034) | **+0,0075** (0,0034)** | +0,0064 (0,0036)* |
| 3-5 | −0,0013 (0,0023) | −0,0037 (0,0023) | +0,0061 (0,0041) | +0,0007 (0,0027) | −0,0020 (0,0023) | −0,0005 (0,0022) | −0,0023 (0,0042) | +0,0037 (0,0027) | +0,0011 (0,0028) |
| 6-11 | **+0,0070** (0,0035)** | +0,0009 (0,0040) | **+0,0186** (0,0061)*** | −0,0073 (0,0040)* | +0,0049 (0,0034) | +0,0022 (0,0038) | −0,0001 (0,0055) | **+0,0201** (0,0054)*** | +0,0002 (0,0033) |
| 12-17 | **−0,0102** (0,0041)** | **−0,0201** (0,0041)*** | **−0,0100** (0,0033)*** | **−0,0585** (0,0074)*** | **−0,0121** (0,0040)*** | −0,0026 (0,0027) | **−0,0258** (0,0071)*** | +0,0059 (0,0055) | −0,0077 (0,0041)* |
| p: β(0-2)=β(3-5) | 0,05 | 0,02 | 0,27 | 0,06 | 0,04 | 0,93 | — | 0,10 | 0,02 |
| N (M) / clusters | 7,07 / 451 | 6,14 / 419 | 3,63 / 451 | 3,44 / 451 | 7,01 / 451 | 5,40 / 451 | 7,07 / 451 | 7,07 / 451 | 7,07 / 451 |

Por 100 evaluados (β × 1.000, T; 0-2/3-5/6-11/12-17): base +0,44/+0,36/+0,61/+0,48 (todas p<0,10); P1 +0,42/+0,22/+0,57/+0,46; P2 antigua +0,47/+0,10/+0,44/+0,47, nueva +0,29/+0,90/+1,50/+0,23; colegio +0,45/+0,40/+0,69/+0,43; cohortes 1992+: pre2 **+0,65 (0,26)**, pre +0,48; **GUE sola +1,44/+1,21/+1,57/+0,52 (in utero +2,01; todas p<0,01) y en la conjunta PARA cae a +0,17/+0,11 (n.s.) en 0-2/3-5** mientras GUE conserva +1,11/+0,76.

**Lectura.** (P1) Sin el post contaminado desaparece el único coeficiente post-natal positivo en log (6-11) y el 12-17 se duplica: el "+6-11" era Medellín, Córdoba y Urabá. (P2) El perfil pooled mezcla dos perfiles incompatibles: en la escala antigua (cohortes 1988-96) todo es positivo; en la nueva (cohortes 1997-2004) 0-2 y 6-11 son negativos y 12-17 vale −0,059. Cohorte y periodo van juntos: cada tramo de edad mide un calendario distinto. (P3) Colegio = residencia (95 % coincide); los 335.000 no coincidentes dan +0,019/+0,020/+0,046 en 0-2/3-5/6-11: quien estudia fuera de su municipio es el grupo seleccionado. (P4) **El placebo no es cero**: +0,009 a +0,014 (t = 3-4) en log con cualquier cohorte, y la ventana 4-7 años antes de nacer (+0,008*** log; +0,65** por 100) pesa tanto como cualquier ventana post-natal. Es el análogo más cercano al criterio de muerte del PI ("pendiente pre > 1/3 del efecto") y lo incumple de largo; con el placebo solo, +0,016*** (log) y −0,97*** (por 100): hasta el signo depende de la escala. (P5) La guerrilla produce el mismo "perfil" que los paramilitares en por 100 (más grande) y en la conjunta absorbe el de PARA en 0-2/3-5; en log, PARA y GUE tienen signos opuestos en todas las ventanas. Ni signo ni forma son del niño: son del tipo de municipio y del calendario. Extras: con cluster por departamento (28) en log sólo sobrevive el placebo (t = 2,6); con EF cohorte×municipio + mes de nacimiento (E2) el perfil cambia de signo (log: 0-2 −0,017***, 6-11 +0,049***; por 100: las seis ventanas negativas); con dummies de edad al examen (E3) desaparecen el 6-11 y la mitad del placebo, porque el tramo 12-17, truncado en el examen, va unido a la edad al examen.

## 3. Veredicto: **replica con matices**

Replica en sentido fuerte: cada número del RA B se reproduce desde cero y su lectura ("ningún perfil H1/H2; selección") se confirma y se agrava. Los matices van contra el memo: (i) los coeficientes que destaca (6-11 y 12-17 en log; "todas positivas" en por 100) no son ni hallazgos descriptivos robustos: cambian de signo por submuestra y por perpetrador; (ii) el placebo falla con cualquier definición y la ventana −81..−46 lo confirma, cosa que el memo relativiza; (iii) "nacidos tras la salida +0,028" no se verificó aquí y no debe citarse. De este pase sólo entra en el paper la prueba de que la tubería escala.

## 4. Lo que un referee aún atacaría

1. Dosis sin población: log(1+v) y v/evaluados dan signos distintos; hace falta DANE por municipio-edad o EEVV.
2. Municipio = residencia a los 16-18 (P2 del PI): sin UARIV/GEIH cada β es efecto + migración selectiva; los no coincidentes lo ilustran.
3. Edad y calendario confundidos (ρ(0-2, 6-11) = −0,72 en T2): el perfil continuo no los separa; sólo el diseño de celdas relativas a la salida municipal lo hace.
4. Inferencia: 451 clusters, pero la dosis vive en cinco ciudades; con 28 departamentos todo cae; faltan wild-cluster bootstrap y corrección por 6 ventanas × 2 escalas.
5. Margen extensivo: presentación y edad al examen responden a la dosis; cotas de Lee obligatorias.
6. Tendencias pre (cohortes 1983-94 con municipio del colegio, pendiente en dosis futura) siguen pendientes.
7. 2017-2 truncado (cohortes 1999-2001) y 2009-2 por nombre: excluir o reponderar.
