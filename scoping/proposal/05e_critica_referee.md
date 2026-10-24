# 05e. Crítica del referee: identificación (ronda 1)

Referee AER, 24-oct-2026. Leídos 01, 02, 05a-c y los scripts de `code/analysis/`; nada re-ejecutado.

## 1. Especificaciones: errores y decisiones cuestionables

**Escala.** Los umbrales de T2 no son invariantes a la escala: aprobados en niveles (Medellín = 52 % de la variación residual de 0-2), letales en log para 6-11. T2b hereda el problema: `log(1+v)` identifica con municipios pequeños que pasan de 0 a pocas víctimas; `p100` divide por evaluados, denominador endógeno con sesgo positivo mecánico (menos presentados ⇒ más dosis por 100 y mejor selección); 12-17 cambia de signo entre escalas. La escala necesaria, víctimas por habitante, existe desde T5 (`pobl_tot` CEDE), pero 05b afirma que no está.

**Ventanas.** 12-17 se trunca en el mes del examen: su longitud depende del rezago, que predice el puntaje; β(12-17) < 0 es en parte mecánico. PARA = 0 desde 2007 por construcción, así que 3-5 y 6-11 son cero para las cohortes ≥ 2001-2004: el perfil se identifica con la correlación −0,72 entre 0-2 y 6-11 que mide 02, no con la "no colinealidad" de 05b (0,10), que pondera individuos y por tanto a Bogotá y Medellín.

**Efectos fijos.** μ_m + λ_{c×dpto} dejan la cronología municipal de PARA sin dosis de guerrilla ni fuerza pública (P4), sin EF periodo × edad al examen ni tendencias municipales. `score_z` se estandariza dentro de cada archivo: en calendario B (élite más validantes adultos) fuerza media 0 sobre una población no comparable, y 2017-2 se estandariza sobre 73 mil filas truncadas que T2b no excluye.

**Errores estándar.** CR1 por municipio es correcto, pero los MDE aprobados (0,010-0,034) son contrastes binarios con todo el N; el de `born_after_exit` (EE 0,015 ⇒ MDE 0,042) ya supera 0,04.

**Muestra.** El umbral absoluto (≥25 víctimas) selecciona por población: Bogotá, Medellín y Cali son 2,5 de los 7,07 M de T. T2b usa cohortes 1985-2005 aunque solo 1988-2003 se observan completas (05a). El placebo post-salida usa `exit_ym` con la regla del 5 % que 02 desaconseja (Medellín: sep-2004, 172 víctimas después) y compara con la misma cohorte en municipios de salida posterior: bajo H1 ambos reciben el canal hogar, luego no separa H1 de H2.

## 2. Consistencia entre memos

- T: 453 (01), 452 (02: "incluye `00000`"), 451 (05a, 05c: "47000 no es municipio"). El archivo tiene 452 códigos con 47000, no 00000; el filtro `!= "00000"` de T2b no hace nada y el 94,2 % y las 9.492 celdas incluyen un no-municipio.
- "99,7 % de la dosis" (05b) pondera por evaluados; 94,2 % (02) es municipal: dos conceptos con un nombre.
- Placebo post-salida: 64 mil / 173 municipios (05a), 38 mil / 197 (05b), 691 celdas / 389 (02). La potencia de 05a no corresponde al estimador de 05b.
- Coincidencia 93,7 % (constructor) vs 94,4 % (05a): denominadores distintos sin declarar.
- Correlación 0-2/3-5: 0,41 niveles y 0,23 log (02), 0,10 (05b): compatibles, pero 05b omite la varianza residual, el umbral vinculante.
- Sí cuadran: N, ratio 0,122, 70 % de salidas jul-2004 a dic-2005, stayer 37,0 % (31,3 % sin Medellín).

## 3. Qué es defendible y qué no

Defendible: los hechos del panel CNMH (94 % de la dosis en ~450 municipios, mediana 9 años, salida 2004-05, ratio 0,12); que la tubería estima el perfil a escala con EE ≈ 0,0015 DE; una cota: entre residentes a los 17 que llegan a 11º, la asociación within-municipio entre cronología PARA y puntaje es ≤ 0,01 DE por DE de dosis, sin gradiente de edad; y que el desplazamiento rural en T es masivo (mediana 23 %) y responde a la violencia total.

No defendible: toda lectura causal de 05b sobre H1/H2 (el placebo pre-concepción es positivo y significativo: selección); el "APROBADO" de T2 sin escala fijada; que P2 "es acotable" con stayers, cierto en ciudades y falso en los municipios rurales que retienen el 19 % de su dosis y concentran la variación de calendario; que el margen extensivo sea fecundidad (sin EEVV no se distingue); y el pitch, que promete empleo y diagnósticos que ningún dato del repositorio contiene.

## 4. Tres pruebas en una semana

1. **Event study alrededor de la salida** (y de la entrada en los ~120 municipios limpios): cohorte relativa al mes de salida (−10 a +3 años), EF municipio y cohorte × dpto, sin municipios ≥ 500 mil, salida con umbral absoluto; resultados `score_z`, log N de celda (margen extensivo sin EEVV) y composición (educ_madre, estrato, colegio no oficial, rezago). Pre-tendencias o saltos de N junto al puntaje ⇒ selección. Es el diseño principal según 02 y nadie lo ha estimado.
2. **Perfil per cápita y por perpetrador:** repetir T2 y T2b con víctimas por 1.000 habitantes, ventanas de longitud fija, cohortes 1988-2003, sin 2017-2 ni calendario B, EF periodo × edad, con GUE, EST y POSD como controles y placebos. Si perfil PARA ≈ GUE ≈ total, el paper no trata de edad de exposición paramilitar.
3. **Balance y heterogeneidad por desplazamiento:** regresar covariables predeterminadas y la expulsión RUV per cápita (mismas ventanas de edad) sobre las dosis con los mismos EF; estimar el perfil por cuartil de tasa de expulsión y para receptores masivos. Si β cambia con la expulsión o la dosis "predice" la educación de la madre, queda cuantificado P2 y puede empezar la cota de Lee por tramos.
