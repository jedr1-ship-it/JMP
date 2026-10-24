# Carta del PI/Editor, ronda 1 (24-oct-2026)

Propuesta juzgada: "Edad de exposición a la violencia paramilitar (AUC 1997-2006) y resultados de largo plazo", Colombia, arquitectura híbrida. El PI recalculó sobre los archivos CNMH (script `code/exploration/cnmh_stagger_check.py`) las magnitudes de las que depende la identificación.

## 1. Veredicto
**Major revision, no "go"**: el evento y la variable de tratamiento son material de top-5, pero la arquitectura de localización y de outcomes, tal como está, produce un paper de JDE/JHR sobre puntajes Saber 11 con gradiente de edad (cuya mitad ya firmó Duque) y no puede ejecutar el test "memoria vs hogar".

## 2. Cinco problemas por letalidad
**P1. El diseño no genera la celda que el test de mecanismo necesita.** En los 453 municipios con ≥25 víctimas paramilitares 1997-2006 (94% de la dosis), la actividad paramilitar dura una mediana de 9 años (cuartiles 7-10). El 73% ya tenía asesinatos paramilitares en 1988-95: la entrada 1997-2002 es limpia en unos 120 municipios. La salida se amontona: 52 municipios en 2003, 93 en 2004, 216 en 2005, 64 en 2006. El niño expuesto a 0-2 casi siempre lo está también a 3-5 y en edad escolar; la celda "0-2 y nada más" son los nacidos en los tres años previos a la salida (mediana del 30% de la dosis). "0-2 vs 3-5" como celdas no está identificado. Lo que sí: un perfil dosis-por-edad, Y_imc = Σ_a β_a·V_{m,c+a} + μ_m + λ_{c×dpto}, que explota picos en años distintos (Tuluá 1999-2000, Tibú 2000, San Carlos 2001, Valledupar 2002-03) y salida 2003-2006. Hipótesis como formas del perfil: H2 (memoria) ⇒ β_a ≈ 0 para a<3 y creciente después; H1 (hogar) ⇒ β_a > 0 desde in utero y decreciente. Tests limpios: cohortes nacidas tras la salida en municipios tratados (tratadas bajo H1, placebo bajo H2) y perfiles por perpetrador. Resoluble: sí, exige comprobar no colinealidad de dosis por tramo tras efectos fijos (T2).

**P2. La localización en el momento de la exposición no se observa y el desplazamiento es el canal principal.** El examinado que aparece a los 17 en m es quien se quedó o quien llegó; el más golpeado se fue y figura como control. Error de clasificación diferencial correlacionado con el tratamiento y con la edad del niño. Soluciones: (a) enlace individual con UARIV en la base ICFES (hecho, fecha y municipio de expulsión); (b) muestra de "stayers" (expulsión acumulada baja según RUV) más cotas Lee/Manski; (c) GEIH 2012-2024 con municipio de nacimiento. Resoluble parcialmente con datos públicos; del todo solo con (a).

**P3. La salud mental es la pata más débil.** Suicidios: cientos al año, sin potencia por edad. ENSM 2025: departamental, transversal, sin residencia infantil. RIPS: uso de servicios, aseguramiento expandido en los mismos municipios y años. Solo RIPS vía ICFES da N; acceso no confirmado. Segunda fila: intentos de suicidio SIVIGILA 2016+ (≈39.000/año), mortalidad violenta adulta.

**P4. Entrada endógena, tendencias no paralelas y post contaminado.** Municipios con actividad paramilitar en 1996 tenían 157 víctimas en 1988-95 de media frente a 6,7 en no tratados, y doce veces más asesinatos de guerrilla. Escalada FARC 1998-2002, fumigación 2000, Plan Patriota 2004 golpean a los mismos municipios. Post: falsos positivos (48 en 2001, 1.151 en 2007) y BACRIM no registradas como conflicto. Buena noticia: la caída tras la desmovilización es real: violencia total pasa de 15.226 víctimas/año (2000-02) a 1.856 (2007-10), ratio 0,12. Soluciones: event study con cohortes pre (nacidas 1983-1994, Saber 11 2005-2011 con municipio del colegio); dosis por perpetrador como test; homicidios Policía del Panel CEDE; exclusión de Córdoba, Urabá, Bajo Cauca, Medellín y Nariño en el post.

**P5. Selección en Saber 11 y medición.** Presenta quien llega a 11º (la mitad de la cohorte en rural tratado); cambio de escala 2014-2; residencia solo desde 2012-2; duplicados. Soluciones: margen extensivo con denominadores EEVV; edad al examen; cotas de Lee; estandarización dentro de aplicación; municipio del colegio para 2005-2011 con tasa de coincidencia.

Menores: bloque en 5% de casos (usar salida municipal observada); ELCA ≈565 niños, ilustración; ventana de dosis desde 1988.

## 3. Qué falta para top-5 y pitch
"La edad importa, también en Saber 11" no es contribución. Sí: (i) perfil dosis-por-edad mensual 0-17 con inicio y fin escalonados y dosis un orden de magnitud mayor que Duque; (ii) los mismos individuos en educación, empleo formal y diagnósticos; (iii) test falsable del mecanismo: cohortes nacidas tras la salida, perfiles por perpetrador, disociación entre dominios con RIPS; (iv) linealidad de Chetty-Hendren para violencia. Sin (ii) y (iii) es un buen JDE. Aviso: Carneiro, Salvanes, Willage y Willén (HCEO 2023-018): un shock al hogar pesa tanto en la adolescencia como en la primera infancia; "H1 ⇒ 0-2 ≥ 3-5" no es automática. Ramirez y Haas (2021, Demography; autoría a confirmar) ya tienen el marco directo vs indirecto según timing.

**Pitch condicional:** "Usando la llegada y la desmovilización escalonadas de los bloques paramilitares colombianos como variación mensual en la edad a la que la violencia alcanza a cada niño, muestro que la exposición antes de los tres años reduce la escolaridad y el empleo formal adultos sin elevar los diagnósticos de ansiedad y trauma, mientras que la exposición posterior produce el patrón inverso; las cohortes nacidas tras la desmovilización heredan el primer efecto y no el segundo, lo que separa un canal indirecto vía el hogar de un canal directo que solo opera cuando existe memoria episódica."

## 4. Alternativas
NI × NILS: mejores outcomes, pero pico de cinco años sin salida escalonada, residencia post (1981) y acceso presencial 12+ meses: paper 2 / postdoc; carta a NISRA ahora. Nepal: inferior. Indonesia: capítulo de mecanismo. Ruanda: inferior. Inglaterra 2011: no. Eventos únicos: ilustración.

**Elección: Colombia reconstruida, tres patas y go/no-go al mes 6.** Pata 1 (pública): Saber 11 2012-2025 con perfil dosis-por-edad, margen extensivo con EEVV, cohortes pre con municipio del colegio. Pata 2 (pública): GEIH 2012-2024 con municipio de nacimiento. Pata 3 (acceso): base ICFES con UARIV (prioridad 1) y RIPS/PILA. Si al mes 6 no hay compromiso del ICFES, el paper se redefine como educación + empleo con cotas, y la salud mental pasa a NI.

## 5. Tareas para los RA
T1. Panel municipio × mes 1985-2010 por perpetrador con fecha municipal de salida (mes). Aprobado: replica 453 municipios ≥25, mediana 9 años, ratio 0,12; mes de salida para municipios con ≥80% de las víctimas.
T2. Test de identificación del perfil de edad: dosis in utero, 0-2, 3-5, 6-11 por cohorte 1988-2008 × municipio; residualizar con EF municipio y cohorte × departamento; varianza residual y correlaciones; celdas con dosis 0-2 > 0 y 3-5 = 0. Aprobado: correlación residual 0-2/3-5 < 0,7 y varianza residual > 20%.
T3. Saber 11 2012-2 a 2025: descarga, deduplicación, estandarización; N por municipio × cohorte; coincidencia residencia = colegio; tasa de presentación sobre EEVV. Aprobado: MDE ≤ 0,04 DE; tasa de presentación 0,3-1,2 en 90% de tratados.
T4. Diccionarios Saber 11 2005-2012-1: matriz variable × año.
T5. RUV expulsión por municipio × año sobre población 2005; muestra "stayer" (<10%). Aprobado: retiene ≥30% de la dosis; <15% → P2 no acotable.
T6. GEIH 2012-2024 migración: ≥2.000 obs por cohorte nacidas en los 453 municipios.
T7. Potencia en salud mental pública: MDE suicidios e intentos. Aprobado: MDE < 25% agregado.
T8. Cartas: ICFES (UARIV, RIPS, residencia 2006-2011), Minsalud (ENSM 2025), NISRA. Confirmar Ramirez y Haas (2021) y Duque (2024).

## 6. Criterios de muerte
- T2: correlación residual > 0,8 o varianza residual < 10% → la pregunta de edad no es identificable en Colombia.
- T5 < 15% de la dosis y el ICFES no responde sobre UARIV al mes 6 → JDE con cotas o pivote a GEIH.
- Cohortes pre con pendiente correlacionada con la dosis futura > 1/3 del efecto → identificación muerta.
- Sin RIPS ni ENSM con geografía al mes 9 → redefinir.
- Aparece un WP con la base integrada y exposición por edad → la ventaja es solo el diseño y el mecanismo.
