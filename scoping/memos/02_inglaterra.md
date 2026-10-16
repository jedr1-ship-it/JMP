# Memo: exposición temprana a violencia/terrorismo en Inglaterra/Gran Bretaña — episodios, datos y diseño factible

Nota: verificado vía búsquedas web (el proxy bloqueó PDFs de gov.uk, parliament.uk y cls.ucl.ac.uk). [NV] = no verificado; [est.] = cálculo propio.

## 1. Episodios de violencia: ¿son lo bastante "concretos"?

- **Disturbios de agosto de 2011** (6–11 ago; Tottenham 6 ago, resto de Londres 7–8, Birmingham/Manchester/Salford/Liverpool/Nottingham/Bristol 8–10). El episodio más nítido: 4–5 noches, inicio y fin claros. Datos: Home Office "An overview of recorded crimes and arrests resulting from disorder events in August 2011" (5.175 delitos, 4.105 detenciones, 19 fuerzas) con tablas XLS en data.gov.uk; boletín del MoJ (13 sep 2012) sobre acusados, con cruce al NPD (83% de menores emparejados) y domicilio por IMD/LSOA; mapa de la Met de delitos vinculados al disturbio a nivel LSOA/MSOA usado por Baudains, Braithwaite & Johnson (Criminology 2013), Kawalerowicz & Biggs (Social Forces 2015; >1.600 acusados geocodificados por domicilio) y Tiratelli (UCL); lista de incidentes verificados del Guardian (descargable). police.uk publica delitos a nivel calle/LSOA mensual desde dic-2010 (archivo oficial completo desde dic-2013; copia Zenodo dic-2010–abr-2016; versión ONS-IDS 2010–2023 para acreditados): permite construir "exceso de delitos ago-2011 vs ago-2010" por LSOA. Variación espacial fina: sí, concentrada en pocas decenas de LSOAs comerciales. Veredicto: el único episodio con intensidad geocodificada a LSOA y cohortes de 0–5 observables en datos administrativos.
- **7/7** (7 jul 2005, 52 muertos, 4 puntos) y 21/7. Concreto en tiempo, sin variación espacial de intensidad residencial. Literatura: Hole & Ratcliffe (SJE 2020, LSYPE: caída de bienestar de adolescentes musulmanas, timing de entrevista); Ratcliffe (Economic Inquiry 2015: precios de vivienda −2%); Nugent et al. (J Obstet Gynaecol 2011: −16 g peso al nacer en el noroeste por exposición mediática). Veredicto: útil para "estrés mediático/discriminación", no para exposición local.
- **Manchester Arena** (22 may 2017). Punto único; datos del Resilience Hub no accesibles. Niños 0–5 en 2017 llegan a KS2 en 2022–2028. Veredicto: demasiado reciente, sin gradiente residencial.
- **Campaña del IRA en Inglaterra** (1973–1997). Episodios puntuales y dispersos. GTD con lat/long pero acceso bajo solicitud desde ~2025. Sin datos individuales con cohortes 0–5 y residencia, salvo BCS70 (4,5 años en Birmingham 1974; pocos cientos [est.]). Veredicto: variación cohorte × lugar insuficiente.
- **Blitz** (sep 1940–may 1941) y **V-1/V-2** (jun 1944–mar 1945). Geodatos: Bomb Sight (>31.000 puntos de Londres; descarga masiva no publicada); Evans & Delaney (Applied Geography 2018) 2.420 V-1; TNA HO 193 sin georreferenciar; Civilian War Dead Roll de la CWGC (~66.000–68.000 nombres con domicilio, lugar y fecha) descargable por lotes y geocodificable: la mejor medida nacional de intensidad. Individuos: NSHD 1946 nace después; ONS LS empieza en 1971; **UK Biobank** (nacidos 1937–1970, ~500.000, coordenadas del lugar de nacimiento [NV], cuestionario de salud mental, educación, empleo) permite cohorte × lugar de nacimiento para nacidos 1935–45. Precedentes: Labour Economics 2019 ("Infant mortality and adult wellbeing: evidence from wartime Britain", UKB); Akbulut-Yuksel (JHR 2014; "World War II Blues", NBER w30284, 2022: peor salud mental de por vida en expuestos <5 años). Veredicto: viable como segundo diseño; solo lugar de nacimiento; evacuación (Pied Piper) como contaminante enorme.
- **Disturbios de 1981 y 1985**: concretos y localizados, sin incidentes geocodificados públicos y sin datos individuales adecuados. Inviable.
- Lockerbie, huelga minera, Hillsborough, Bradford: puntuales sin gradiente o shocks económicos. No recomendables.

## 2. Datos individuales

Para cohortes 0–5 en 2011 el único conjunto con N suficiente y residencia a LSOA es el **NPD**, accesible como **ECHILD** (NPD + HES + notificaciones de nacimiento + salud mental y servicios comunitarios; nacidos sep-1984–mar-2022; ~20 M; vía UCL + ONS SRS; gratuito para investigación acreditada basada en el Reino Unido) o como extracto NPD/LEO (DfE estima 124 días laborables). MCS (19.517 niños nacidos sep-2000–ene-2002; SDQ a 3, 5, 7, 11, 14 [NV], 17; K6 a 17; NPD y HES vinculados) sirve para 7/7 (3–5 años) pero no para 2011 (9–11 años). Born in Bradford (13.776 embarazos 2007–11) está fuera de las zonas de disturbios → control. Understanding Society: muy pocos niños 0–5 en LSOAs de disturbios.

## 3. Emparejamientos episodio × datos

(a) **Disturbios 2011 × NPD/ECHILD [recomendado]**. Tratados: nacidos ago-2005–ago-2011 (in utero/0–2/3–5) residentes en LSOAs con delitos de disturbio; comparación: mismos LSOAs, nacidos sep-2011–2014 (no expuestos) y nacidos 2002–2005 (edad escolar), con LSOAs vecinos sin incidentes. Outcomes: fonética (2012–17), KS1 (hasta 2018), KS2 (2016–2022), KS4 (2021–2027), absentismo, exclusiones, SEN, NEET/KS5, LEO (ingresos a 18–21 solo cohortes mayores); HES ingresos/A&E por autolesión, MHSDS/CAMHS desde 2016. Tamaño [est.]: ~500 LSOAs con algún delito de disturbio → ~50.000 niños de 0–4 expuestos y ~10.000 en los ~100 LSOAs de alta intensidad; potencia razonable para 0,03–0,05 DE en KS2. Amenazas: focalización en zonas comerciales deprimidas (pre-tendencias testables con cohortes 2002–05), movilidad residencial (usar LSOA de primera observación o del nacimiento vía ECHILD-MB), exposición parental vía detenciones. Ventaja: la literatura sobre 2011 (Bell, Jaitman & Machin, EJ 2014) se centra en disuasión; ningún estudio de efectos sobre niños.
(b) 7/7 × MCS/NPD: solo timing; sin gradiente local.
(c) **Blitz/V-weapons × UK Biobank**: cohortes 1935–45 × intensidad (CWGC geocodificada; Bomb Sight para Londres) en el lugar de nacimiento; outcomes PHQ/GAD, cualificaciones, empleo. Limitaciones: solo lugar de nacimiento, evacuación, selección de UKB.
(d) Manchester Arena × NPD, IRA × BCS70, 1981/85 × ONS LS: descartados.

## 4. Literatura existente (verificada)

Bell, Jaitman & Machin (EJ 2014); Baudains et al. (2013); Kawalerowicz & Biggs (2015). Ningún trabajo sobre niños y los disturbios de 2011. Hole & Ratcliffe (SJE 2020) y Ratcliffe (EI 2015) sobre 7/7; Nugent et al. (2011). Dericks & Koster, "The Billion Pound Drop" (Blitz); Evans & Delaney (2018); Akbulut-Yuksel (2014, 2022). Manchester Arena: BJPsych 2021/2025, solo clínico. Camacho (AER P&P 2008), Quintana-Domeque & Ródenas-Serrano (JHE 2017, ETA).

## 5. Veredicto

Mejor diseño factible: **Disturbios de agosto de 2011 × ECHILD**, cohorte (edad en agosto de 2011) × intensidad por LSOA, con control de cohortes nacidas después. **Puntuación 6/10.** Killers: (i) acceso ONS SRS/ECHILD exige investigador acreditado y acceso desde el Reino Unido (hace falta coautor/institución británica [NV]); 6–12 meses; (ii) intensidad modesta (4 noches) → efectos pequeños, riesgo de nulo; (iii) outcomes laborales adultos no disponibles aún; (iv) endogeneidad de la localización. Alternativa: Blitz × UK Biobank (5/10).

## Tabla de episodios

| Episodio | Fechas | Geografía | Incidentes geocodificados | Variación fina | Datos 0–5 años |
|---|---|---|---|---|---|
| Disturbios 2011 | 6–11 ago 2011 | Londres + 8 ciudades | Sí: Met (LSOA), Home Office/MoJ, Guardian, police.uk | Alta | NPD/ECHILD, HES, MHSDS |
| 7/7 y 21/7 | jul 2005 | Centro de Londres | Sí, trivial | Nula | MCS (3–5 años), NPD |
| Manchester Arena | 22 may 2017 | Punto único | Sí, trivial | Nula | NPD (KS2 desde 2022) |
| IRA en Inglaterra | 1973–1997 | Puntual, disperso | GTD (restringido), Sutton [NV] | Baja | BCS70/NCDS |
| Blitz / V-weapons | 1940–41; 1944–45 | Londres y ciudades industriales | Bomb Sight, CWGC, HO 193 | Alta (Londres) | UK Biobank (nacimiento) |
| Disturbios 1981/1985 | 1981; 1985 | Brixton, Toxteth, Handsworth, Tottenham | No públicos | Alta | ONS LS (N ínfimo) |

## Tabla de datos

| Dataset | Años | N | Cohortes | Geografía | Salud mental / educación / laboral | Acceso | URL |
|---|---|---|---|---|---|---|---|
| NPD / ECHILD | NPD 2002–; ECHILD nacidos 1984–2022 | ~20 M | Todos los alumnos | LSOA/código postal | HES, MHSDS; KS1–KS5, absentismo, exclusiones, SEN; LEO | UCL + ONS SRS; 124 días laborables | echild.ac.uk |
| LEO | ~2002– | ~39 M | Todos | Vía NPD | Ingresos HMRC, prestaciones, HE | ONS SRS vía DfE | adruk.org |
| HES | 1989– | Universal | Todos | LSOA | Diagnósticos, autolesión | NHS England DARS (3–12 meses) | digital.nhs.uk |
| MCS | 2001–2018 | 19.517 | Nacidos 2000–02 | LSOA seguro | SDQ 3–17, K6 | UKDS | cls.ucl.ac.uk |
| Next Steps (LSYPE) | 2004–2023 | 15.770 | Nacidos 1989–90 | Escuela/LA | GHQ-12; empleo a 25/32 | UKDS SN 5545 | ukdataservice.ac.uk |
| Our Future (LSYPE2) | 2013– | ~13.100 [NV] | Nacidos 1998–99 | NPD | GHQ-12 | UKDS/DfE | [NV] |
| NCDS | 1958– | 17.415 | 1958 | Región/LA | Malaise, Rutter; empleo | UKDS | cls.ucl.ac.uk |
| BCS70 | 1970– | 17.196 | 1970 | Región/LA | Malaise, Rutter | UKDS | cls.ucl.ac.uk |
| NSHD 1946 | 1946– | 5.362 [NV] | 1946 | Región | GHQ, PSE | MRC LHA | [NV] |
| ONS LS | 1971–2021 | ~500 k | Todos | Ward/LSOA | Sin salud mental | ONS/CeLSIUS | ons.gov.uk |
| Scottish LS | 1991–2011+ | 274.055 | Todos | Datazone | Hospital, SQA | SLS-DSU | sls.lscs.ac.uk |
| Born in Bradford | 2007–2011 | 13.776 | 2007–11 | Bradford | NPD (85%), salud | BiB executive | borninbradford.nhs.uk |
| Understanding Society/BHPS | 1991–/2009– | ~40 k hogares | Todos | LSOA bajo SL | SDQ 10–15, GHQ-12 | UKDS | ukdataservice.ac.uk |
| UK Biobank | 2006–10 + seguimiento | ~500 k | 1937–70 | Coordenadas de nacimiento [NV] | PHQ/GAD, cualificaciones, empleo | Solicitud UKB (coste) | ukbiobank.ac.uk |
