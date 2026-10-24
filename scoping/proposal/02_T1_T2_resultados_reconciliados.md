# T1/T2 reconciliados: replicación del PI y test de identificación del perfil de edad

Memo del RA senior (2026-10-24). Insumos: `code/exploration/t2_A.py` → `scoping/proposal/t2_A_resultados.md` y `code/exploration/t2_B.py` → `scoping/proposal/t2_B_resultados.md`, dos implementaciones independientes sobre los microdatos CNMH-OMC (corte mar-2025, masacres + asesinatos selectivos). Comprobación propia: `python3 -I` sobre `data/derived/t2_A_T2_celdas_muni_cohorte.csv` y `t2_B_T2_celdas.csv`.

## 1. Grado de acuerdo

Ambas reconstruyen el panel municipio × mes desde los xlsx y coinciden entre sí y con `cnmh_muni_month_victims.csv`; las 9.492 celdas municipio × cohorte tienen dosis **idénticas** en las cuatro ventanas (diferencia máxima 0 en mi cruce) y todos los números clave de T2 coinciden a tres decimales. **Ninguna discrepancia supera el 15 %** en un número clave; las diferencias que hay son de convención y las reproduje una a una cambiando sólo esa convención:

- **452 vs 453 municipios, 63 vs 64 salidas en 2006, 94,2 % vs 94,3 %**: el filtro `\d{5}` del PI deja pasar el código DANE `00000` ("SIN INFORMACION", 63 víctimas PARA 1997-2006, entrada 1996 / salida 2006), que no es un municipio. B lo conserva sólo para replicar el 453 del PI; su T de trabajo es también 452 y el ratio T1(c) es 0,122 con o sin él.
- **Cobertura del mes de salida 92,5 % vs 92,6 %**: mismo numerador (431 municipios); A incluye en el denominador las 49 víctimas con código de exterior.
- **Distribución semestral del mes de salida**: A titula con los 452 (V1) y B con los 433 que tienen ≤5 % de su dosis sin mes (V2); las columnas homólogas son idénticas. La lectura literal "sin ningún caso con mes faltante" (V3) deja 254 municipios y el 29 % de las víctimas: inutilizable; se adopta V2.
- **Número de condición 2,99 vs 3,13 y VIF 6-11 2,54 vs 2,80**: A usa los residuos de la residualización con 21 cohortes restringidos a 1988-2003; B re-residualiza dentro de la muestra balanceada 1988-2003. Reproducidos ambos; la convención de B es la pertinente para una regresión estimada en esa muestra.
- **Sin municipios grandes: corr 0,231 vs 0,283** (22 % de diferencia, pero no es el mismo ejercicio): A excluye los 10 de mayor dosis, B el top 1 % (5 municipios, subconjunto de los de A). Reproducidos ambos; los dos aprueban.
- **log1p (A) vs asinh (B)**: 16,9/14,7 %, corr 0,244 vs 16,8/14,0 %, corr 0,229. Misma conclusión (zona gris).
- **Nacidos tras el mes de salida: 1.745 vs 1.606**: A compara el mes de nacimiento (jul-c) con el mes de salida en los 431 municipios con mes asignado; B, el año de la cohorte con el año del mes de salida en los 450 con mes. Reproducidos ambos.

## 2. Tabla de números finales

| Número | A | B | Adoptado |
|---|---|---|---|
| Municipios con ≥25 víctimas PARA 1997-2006 | 452 | 453 (452 sin `00000`) | **452** (el 453 del PI incluye `00000`) |
| Share víctimas PARA 1997-2006 en T | 94,2 % | 94,3 % | **94,2 %** (452) |
| Salida anual 2003/04/05/06 | 52/93/216/63 | 52/93/216/64 | **52/93/216/63** |
| Duración mediana (cuartiles) | 9 (7-10) | 9 (7-10) | **9 (7-10)** |
| Ratio TOT 2007-10 / 2000-02 en T | 0,122 (15.202→1.850) | 0,122 | **0,122** |
| Mes de salida: municipios con mes / cobertura | 431/452; 92,5 % | 431/433 (V2); 92,6 % | **431; 92,6 %** (≥80 % del PI: cumplido) |
| Mes de salida, moda | 2004-S2 a 2005-S2: 314/452 | 301/433 | **70 % de T sale entre jul-2004 y dic-2005**; 2 censurados (Abriaquí, Riofrío) |
| Celdas municipio × cohorte | 9.492 | 9.492 | **9.492** (452 × 1988-2008; 6-11 sólo 1988-2003, n=7.232) |
| Corr bruta 0-2 / 3-5 | 0,678 | 0,678 | **0,678** |
| Corr residual 0-2 / 3-5 (EF muni + cohorte×depto) | 0,407 | 0,407 | **0,407** |
| Corr residual in utero/0-2; 3-5/6-11 | 0,614; −0,007 | 0,614; −0,007 | **0,614; −0,007** |
| Var. residual / bruta: iu, 0-2, 3-5, 6-11 | 49,4/44,4/47,5/40,0 % | idem | **49,4/44,4/47,5/40,0 %** |
| Spec alternativa (EF muni + cohorte) | 0,403; 46,9/50,1 % | idem | **0,403; 46,9/50,1 %** |
| Balanceada 1988-2003 (niveles) | 0,200; 33,8/35,5 % | idem | **0,200; 33,8/35,5 %** |
| Sin municipios grandes (niveles) | top10: 0,231; 43,2/44,5 % | top1 %: 0,283; 43,9/45,7 % | **0,23-0,28; 43-46 %** |
| Dosis en escala log | log1p: 0,244; 16,9/14,7 % | asinh: 0,229; 16,8/14,0 % | **≈0,23; 17 % / 14-15 %** |
| Dosis como share del total municipal | — | −0,076; 35,8/30,8 % | **−0,08; 36/31 %** |
| VIF máx. / cond. (4 ventanas, 1988-2003) | 2,54 / 2,99 | 2,80 / 3,13 | **2,8 / 3,1** (sin colinealidad conjunta) |
| Corr residual 0-2 / 6-11 (balanceada) | — | −0,72 | **−0,72** |
| Concentración SS residual 0-2 | Medellín 51,9 %; top5 75,5 % | — | **52 % / 76 %** |
| Celdas 0-2>0 y 3-5=0 | 1.483 (15,6 %) | 1.483 (15,6 %; 20,4 % de las 0-2>0) | **1.483**, 1.092 nacidas entre 2 años antes y el año de la salida |
| Celdas nacidas tras la salida anual | 1.595 | 1.595 (691 en cohortes ≤2006, 389 municipios) | **1.595 (691 informativas)** |
| Ídem con mes de salida | 1.745 (mes de nacimiento) | 1.606 (año del mes) | reportar ambas con su definición |

## 3. Veredicto frente a los umbrales del PI

**APROBADO en la especificación literal del PI** (dosis en niveles, EF municipio + EF cohorte × departamento, cohortes 1988-2008): correlación residual 0-2/3-5 = **0,407** (< 0,7; letal > 0,8) y varianza residual = **44,4 %** (0-2) y **47,5 %** (3-5) de la bruta (> 20 %; letal < 10 %). El veredicto se mantiene con EF de cohorte simples (0,403; 47/50 %), en la muestra balanceada 1988-2003 (0,200; 34/36 %), sin los 5 o 10 municipios de mayor dosis (0,23-0,28; 43-46 %) y con la dosis como share del total municipal (−0,08; 36/31 %).

**ZONA GRIS en escala logarítmica**: con log1p o asinh la correlación baja (≈0,23) pero la varianza residual cae a 17 % (0-2) y 14-15 % (3-5), dentro de la franja 10-20 % del PI. Para la ventana 6-11 en escala log la varianza residual es 7-8 %, por debajo del 10 %: esa ventana sí sería letal en log, no en niveles.

**Ningún caso letal para el par 0-2/3-5** en ninguna variante. El matiz decisivo es que en niveles la variación identificadora la aportan pocas ciudades: el 52 % de la suma de cuadrados residual de la dosis 0-2 es Medellín y el 76 % cinco municipios. Pendiente: el PI debe fijar la escala de la dosis (recomendamos per cápita con población DANE, ausente del repositorio) antes de aplicar los umbrales de forma vinculante.

## 4. Implicaciones para el diseño

1. El perfil dosis-por-edad (un β por ventana) es estimable en niveles —las ventanas adyacentes se separan (ρ = 0,41, VIF < 3)— pero será, de facto, el perfil de Medellín, Cúcuta, Valledupar y un puñado de ciudades, de modo que exige errores agrupados por municipio, estimaciones dejando fuera las grandes ciudades y una versión per cápita que hoy no podemos calcular.
2. Para las cohortes 1988-2003 la correlación residual entre 0-2 y 6-11 es −0,72 (quien recibe mucha dosis en la primera infancia por nacer cerca del pico recibe poca en edad escolar por la salida 2003-06): el perfil de cuatro ventanas no distingue primera infancia de edad escolar, así que conviene limitarlo a in utero/0-2/3-5 o anclarlo a la salida municipal.
3. El diseño de celdas (cohortes relativas al mes de salida dentro del municipio) usa la variación de calendario, que sobrevive a cualquier escala (share del total: ρ = −0,08, varianza residual 31-36 %) y dispone de 1.483 celdas con dosis 0-2 > 0 y 3-5 = 0 y 691 celdas placebo nacidas tras la salida local; debe ser el diseño principal y el perfil continuo la pieza complementaria, usando además un umbral absoluto para fechar el cese (la regla relativa del 5 % sitúa la salida de Medellín en sep-2004 con 172 víctimas PARA en los 12 meses siguientes).
