# Síntesis del scoping: país, evento, datos y outcomes

Fecha: 16-oct-2026. Basado en seis memos de scoping (ver `memos/`). Advertencia global: los agentes agotaron el presupuesto de búsqueda y el proxy bloqueó varios dominios oficiales, de modo que muchos detalles (variables concretas, olas, acceso) están marcados como no verificados en los memos. Esta síntesis prioriza; la verificación puntual es el siguiente paso.

## 1. Qué dice la literatura sobre el hueco

- **In utero** está saturado (Camacho; Mansour & Rees; Quintana-Domeque & Ródenas-Serrano; Brown; Currie et al.; Persson & Rossin-Slater en AER).
- **Preescolar vs escolar** tiene respuesta gruesa: León (2012, JHR, Perú) y Akbulut-Yuksel, Tekin & Turan (2025, JHR, "World War II Blues": <5 años → peor salud mental 60 años después). Este último es el competidor directo y hay que diferenciarse de él explícitamente.
- **Dentro de 0–5 (0–2 vs 3–5) con un episodio acotado, y el test memoria-vs-hogar**: nadie lo ha hecho, ni en top-5 ni en segundo nivel. En top-5 los papers de violencia y niños (Ang 2021 QJE; Cabral et al. 2026 REStud; Damm & Dustmann 2014 AER; Sviatschi 2022 AER) son todos de escolares o adolescentes.
- Contraejemplo a reconciliar: Chetty & Hendren (2018, QJE) encuentran exposición lineal a barrios sin periodo crítico.

La contribución tiene que ser el gradiente fino y el mecanismo, no la mera existencia de efectos tempranos.

## 2. Un problema de diseño que condiciona la elección del evento

Hay una tensión entre nitidez y dosis:

- Un episodio de días o semanas (atentado, disturbio) da variación de edad limpísima (todas las cohortes reciben la misma dosis a distinta edad), pero la dosis es pequeña y la variación espacial suele reducirse a "una ciudad frente al resto", es decir, una sola unidad tratada. Riesgo de nulo y de inferencia frágil.
- Un episodio de 3–5 años con fin nítido (guerra civil, campaña de un grupo que luego se desmoviliza) da dosis y muchas unidades tratadas con intensidad variable, pero las ventanas de edad se solapan: el nacido en el año 1 está expuesto de 0 a 4, el nacido tres años antes de 3 a 7. Se puede separar edad de dosis si hay variación en la fecha de inicio o de fin por localidad (entrada escalonada de un grupo, desmovilización escalonada), que es exactamente lo que ofrece Colombia.

Conclusión: el evento ideal dura unos años, tiene inicio y fin escalonados por localidad, y deja datos de violencia fechados y geocodificados.

## 3. Ranking de combinaciones

| # | País y evento | Nitidez | Datos de violencia | Datos individuales y outcomes | ¿Hecho? | Viabilidad | Killer principal |
|---|---|---|---|---|---|---|---|
| 1 | **Colombia: ola paramilitar AUC 1997–2002 y desmovilización escalonada 2003–2006** | Alta por zona (fecha de desmovilización del bloque) | CNMH-OMC: evento, día, municipio, perpetrador, público | Saber 11 (fecha de nacimiento + municipio, ~500k/año, cohortes 1992–2008): educación a 17. CNPV 2018 (municipio de nacimiento, a verificar) y GEIH: educación y empleo adultos. ENSM 2015: salud mental, N limitado. Sisbén III→IV: ubicación 2009–11 | Duque (2024) hizo homicidios años 80 × Saber 11 × edad. La ola AUC + fin escalonado + salud mental + adultos está libre | 7/10 | Desplazamiento forzado hace endógena y no observada la ubicación infantil; sin salud mental administrativa a escala |
| 2 | **Irlanda del Norte: pico de los Troubles 1971–76 × NILS** | Media: salto ×18 en 1971–72, pico 1971–76, meseta larga después | Sutton/McKeown: muertes con fecha y lugar; geocodificables a ward | NILS (28% de la población, censos 1981–2021 enlazados, ward de residencia infantil en 1981, salud mental censal 2011/2021, psicotrópicos 2010+, mortalidad). Cohortes 1964–82, hoy 44–62 | French & Cruise (2021) y Devlin et al. (2025) con adultos; nadie con primera infancia por cohorte × ward | 6/10 | Residencia pre-tratamiento solo para nacidos ≥1974; migración por intimidación 1969–73; boicot al censo 1981; acceso presencial en Belfast, 12+ meses |
| 3 | **Ruanda 1994 (100 días)** | Máxima | Verpoorten: intensidad por 1.484 sectores, pública | EICV, DHS, censos; Rwanda Mental Health Survey 2018 (N 19.110, MINI). Cohortes 1989–94, hoy 32–37 | Educación y talla hechas (Akresh & de Walque; Akresh, Verwimp & Bundervoet); salud mental adulta por edad 0–2/3–5 libre | 5–6/10 | Mortalidad selectiva masiva y 2M de refugiados: la composición de cohortes está contaminada; acceso al RMHS con residencia en 1994 no verificado |
| 4 | **Inglaterra: disturbios de agosto de 2011 × ECHILD/NPD** | Máxima (5 noches) | police.uk y Met a nivel LSOA | ~50.000 niños 0–4 expuestos; KS1–KS4, absentismo, exclusiones, HES autolesiones, MHSDS | Nadie ha mirado niños | 6/10 | Dosis mínima, riesgo de nulo; outcomes adultos no disponibles; acceso desde el Reino Unido |
| 5 | **Nepal 1996–2006 × CVFS** | Fin nítido, inicio difuso | INSEC por distrito y fecha | CVFS: historial residencial mensual, CIDI 2016–18; NLSS, DHS, NMHS 2020 | Valente (2014) educación; 0–5 libre | 6/10 | Un solo distrito; guerra de 10 años |
| 6 | **Perú 1980–92 × ENDES PHQ-9 + censo 2017** | Baja (12 años, dos picos) | CVR distrito-fecha | PHQ-9 anual desde 2014; censo con distrito de nacimiento | León (2012) educación | 6/10 | Educación ya hecha; ENDES sin lugar de nacimiento |
| 7 | Atentado único × cohorte (ELFE × París 2015; Noruega registros × Utøya 2011; Future of Families × 11-S; IFLS × mayo 1998; MCS × 7/7; Finlandia × Jokela) | Máxima | Trivial | Instrumentos de salud mental excelentes | Libres en su mayoría | 4–5/10 como paper principal | Una sola unidad tratada; dosis baja; N expuesto de cientos. Buenos como capítulo de mecanismo, no como JMP |

Descartados: Inglaterra IRA (puntual y disperso), Blitz × UK Biobank (solo lugar de nacimiento, evacuación), Bosnia/Kosovo (sin adultos con municipio de infancia), Kenia 2007–08 (dos meses, sin salud mental), México (sin fin), Sudáfrica Bt20 (cohorte única), Guatemala y Timor (sin salud mental), El Salvador/Sri Lanka/Líbano (largos).

## 4. Las tres historias candidatas

**Colombia.** Entre 1997 y 2002 los bloques paramilitares entraron municipio a municipio con masacres anunciadas; entre 2003 y 2006 se desmovilizaron bloque a bloque en fechas conocidas. Un niño nacido en 1998 en Montes de María vivió la ola de 0 a 4 años; uno nacido en 1994, de 3 a 8; uno nacido en 2005, nada. La entrada y la salida escalonadas permiten separar edad de exposición de dosis. Outcomes: Saber 11 a los 17 para todos, educación y empleo adulto en censo 2018 y GEIH, salud mental en ENSM 2015. La historia que se puede contar: la violencia paramilitar golpea al hogar (desplazamiento, pérdida del padre, caída de ingresos) y al niño; el efecto a 0–2 es el del hogar y el de 3–5 añade el trauma recordado. El riesgo es que el desplazamiento mezcle tratamiento y selección.

**Irlanda del Norte.** En 1971–72 la violencia se multiplicó por 18 en dos años y se concentró en wards concretos de Belfast y Derry; a partir de 1977 cayó a una meseta. NILS sigue al 28% de la población desde 1981 hasta 2021 con residencia por ward, cualificaciones, empleo, salud mental autodeclarada y psicotrópicos. Es el único caso con outcomes de salud mental objetivos (recetas) a los 40–60 años y con N de decenas de miles. La historia: exposición a 0–2 frente a 3–5 en el pico, con el ward de 1981 como localización, y placebo con cohortes nacidas 1977–82. El riesgo es la localización post-tratamiento y el acceso.

**Ruanda.** Cien días en 1994 con intensidad medida por sector. Cohortes hoy de 32–37 años y una encuesta nacional de salud mental diagnóstica. La historia más limpia en el papel, y la más contaminada por selección en la práctica.

## 5. Recomendación

Dos finalistas para la siguiente ronda, en este orden:

1. **Colombia AUC.** Es la que mejor encaja con la idea original (un grupo concreto, un periodo concreto, luego se desmoviliza), los datos de violencia son públicos y a nivel de evento, y Saber 11 da potencia sobrada. Siguiente paso: verificar que Saber 11 2009–2026 tiene fecha de nacimiento y municipio de residencia (no solo del colegio), que CNPV 2018 codifica municipio de nacimiento, y si ENSM 2015 trae municipio. Y pensar desde ya cómo tratar el desplazamiento (Sisbén III como localización 2009–11, RUV de expulsión por municipio como control o como canal).
2. **Irlanda del Norte NILS.** Es la que más impresionaría a un comité por la calidad de los outcomes, y está sin hacer. Siguiente paso: escribir a NISRA para confirmar si el registro de nacimientos desde 1974 incluye domicilio y si hay NI en BCS70 más allá de 1970, y a CAIN para las coordenadas de Sutton.

Mantener Ruanda como comodín si el RMHS 2018 resulta accesible con residencia en 1994.

Inglaterra solo funciona con los disturbios de 2011 y con outcomes escolares; no da el paper que se busca, aunque sí un capítulo de mecanismo si se quiere un episodio ultracorto para contrastar memoria vs hogar.

## 6. Verificaciones pendientes antes de decidir

- Saber 11: fecha de nacimiento y municipio de residencia por año; cobertura de cohortes 1992–2008.
- CNPV 2018: codificación municipal de PA_LUG_NAC.
- ENSM 2015: municipio en microdato.
- NILS: domicilio en registro de nacimientos desde 1974; inicio del enlace con prescripciones; pregunta de salud mental en censo 2011.
- Sutton/McKeown: disponibilidad de coordenadas.
- RMHS Ruanda 2018: acceso y residencia en 1994.
- Papers: "The Long Arm of Conflict" (Demography 2021) y HCEO 2023-018, autores y diseño exacto.
