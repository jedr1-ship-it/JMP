# Memo: viabilidad de un diseño "cohorte × intensidad local de violencia" para los Troubles (Irlanda del Norte)

Fuentes verificadas vía búsqueda web (16-oct-2026). No se pudo abrir directamente cain.ulster.ac.uk, nils.ac.uk ni nisra.gov.uk (bloqueo de red del entorno); lo dicho de ellos procede de resúmenes de búsqueda, perfiles de cohorte publicados y páginas secundarias. Lo marcado "[no verificado]" es memoria o inferencia.

## 1. Datos de violencia

**Perfil temporal.** El Sutton Index (CAIN, Ulster Univ.) registra 3.532 muertes entre el 14-jul-1969 y el 31-dic-2001 (3.524 en la versión geocodificada), 93% ocurridas en NI. Serie anual aproximada: 1969 ≈16-19; 1970 ≈26; 1971 171; 1972 480 (el peor año, 13,6% del total); 1973 ≈255; 1974 ≈294; 1975 ≈260; 1976 295; 1977-80 ≈80-120/año; 1981 111-114; 1982-93 ≈50-100/año; alto el fuego ago-1994 (≈60); 1998 ≈55 (Omagh = 29). Salto muy brusco (×18 entre 1970 y 1972, tras el internamiento de ago-1971) y pico 1971-76 que decae a una meseta larga. El conflicto es "difuso" de 1977 a 1994, pero el sub-episodio 1971-76 es nítido y sirve de tratamiento.

**Datos geocodificados disponibles:**
- *Sutton Index (CAIN)*: fecha, nombre, edad, estatus, organización responsable, descripción textual del lugar. Cunningham y Gregory (proyecto AHRC *Troubled Geographies*, 2008) añadieron coordenadas a cada muerte; CAIN no publica las coordenadas, pero sí mapas por ward (1991/2001), cuadrícula 1 km y Small Output Area. Hay una capa de Google Maps (XML público) con 3.529 muertes geolocalizadas a nivel de calle, usada por un artículo de PSRM (2022). Vía realista: pedir coordenadas a CAIN/Cunningham (Newcastle) o geocodificar el texto de lugar (2-4 semanas).
- *McKeown database* (CAIN): única base completa descargable (Excel/Access v1.1, 2013), criterios más amplios que Sutton; uso investigador permitido.
- *Lost Lives*: libro, 3.636 muertes 1966-99; no es dataset.
- *NIRI* (Loyle, Sullivan, Davenport, CMPS 2014): eventos 1968-98, geolocalización por ML con errores graves documentados. Cautela.
- *Besley & Mueller (AER 2012)*: muertes por región y mes a partir de Sutton; replicación en AEA.
- *Fay, Morrissey & Smyth (1998), Cost of the Troubles Study*: tasas de muerte por ward/distrito postal.
- *GTD (START)*: NI dentro de "United Kingdom"; 1993 perdido. Complementario para bombas no mortales.
- *PSNI security statistics*: anual, nivel NI entero [no verificado].

**Concentración espacial** (CAIN/Mesev-Shirlow 2009): Belfast norte y oeste (interfaces), Derry, South Armagh. Alta correlación con privación y composición religiosa del ward.

**Sub-episodios "sharp"**: (a) ago-1971–1976: el único con potencia; (b) huelgas de hambre 1981: demasiado débil; (c) Omagh 1998: N insuficiente; (d) alto el fuego 1994/GFA 1998: útil como "fin" del tratamiento, con intensidad ya baja.

## 2. Datos individuales

El activo central es **NILS**: 28% de la población (104 fechas de nacimiento), ~516.000 miembros en 2021, censos 1981-1991-2001-2011-2021 enlazados, registros de nacimiento desde 1974, Health Card con domicilio/código postal y eventos migratorios, mortalidad; "Distinct Linkage Projects" (DLP) para enlazar prescripciones (Enhanced Prescribing Database, desde ene-2010: psicotrópicos), hospitalizaciones. Y **NIMS** (toda la población censal, ~1,87 M, 1991-2021 + defunciones). Acceso: NISRA Secure Environment en Belfast (presencial), ONS Accredited Researcher obligatorio, Research Approvals Group cada 2 meses, 2-4 meses de solicitud a dataset; DLP 6-8 meses o más. Gratuito.

Lo decisivo: el censo de 1981 da lugar de residencia (ward) de los niños nacidos 1966-81, y los registros de nacimiento desde 1974 dan [a verificar] domicilio materno al nacer. Censos 2001/2011/2021 dan cualificaciones, empleo, salud autopercibida, hogar, y desde 2011 la casilla "emotional, psychological or mental health condition" (2021 verificado; 2011 [no verificado]).

Cohortes británicas: NCDS 1958 no incluyó NI; BCS70 incluyó 628 nacimientos en NI solo en la sweep de nacimiento, nunca seguidos. MCS (nac. 2000-02, ~2.000 NI) es post-conflicto. BHPS-NIHPS/Understanding Society: 2.000 hogares desde 2001, GHQ-12 y SF-12, sin localización infantil fina y N pequeño. NISHS (Bunting, O'Neill, Ferry, Murphy): 4.340 adultos, WMH-CIDI, 2004-08, trauma relacionado con el conflicto; ICPSR 39555; follow-up de Ferry 2017 n=225. NICOLA: 8.478 en ola 1 (2013-16, ≥50 años → nacidos ≤1965), preguntas de exposición a los Troubles; acceso al equipo (QUB). Health Survey NI: anual desde 2010/11, GHQ-12, transversal. NI Health & Social Wellbeing Survey 1997 y 2001 (UKDS) con GHQ-12. YLT/KLT: post-conflicto. ADR NI: Education Outcomes Linkage 2018/19-2021/22, CGIAD, Honest Broker Service para HSC (2-6 meses); sin pasarela legal para enlazar salud con otros departamentos, aunque NILS-DLP sí lo hace vía Trusted Third Party.

## 3. República de Irlanda

GUI Cohort '98 y '08: nacidos tras el conflicto. TILDA (8.504 ≥50 años, 2009-11, 6 olas, ISSDA): armonizado con NICOLA; permite comparar cohortes 1945-60 NI vs ROI, expuestas de adolescentes/adultos. Censo CSO: RMF vía ROSA, gratis, ~10 días, sin enlace a otros ficheros. ROI sirve de placebo macro; el control principal debe ser intra-NI.

## 4. Literatura previa

Economía: Besley & Mueller (AER 2012, precios de vivienda); Dorsett (EJPE 2013, PIB −10%); French & Cruise (OBES 2021): censo 2011, incapacidad laboral de 50-64 años vs muertes por DEA 1969-98; Devlin, French & McVicar (SSM 2025): NICOLA + tasas de muertes por DEA, +21 pp en DLA y efecto en salud mental, con muestra "4-19 años en 1969". Epidemiología: Bunting et al. 2013 (PTSD 8,8% vida), Ferry et al. 2014, O'Neill et al. (suicidalidad), Ferry et al. 2017 (n=225), NICOLA-memoria 2022 (la edad de exposición no modera), Cummings et al. (jóvenes de Belfast). Proyecto NILS en curso sobre fertilidad y salud infantil y los Troubles/GFA. **No se encontró ningún trabajo que estime el efecto de la exposición en primera infancia (in utero/0-2/3-5) por cohorte × ward con outcomes adultos enlazados.** El hueco existe.

## 5. Veredicto

**Diseño recomendado (NILS):** cohortes nacidas 1964-1982 observadas en el censo de 1981 (ward de residencia infantil; ~100.000 niños), exposición = muertes Sutton/McKeown por ward (o buffer 1 km) en la ventana de edad de cada cohorte centrada en el pico 1971-76; outcomes en 1991 (abandono escolar temprano), 2001/2011/2021 (cualificaciones, empleo, salud mental autodeclarada, hogar), mortalidad/suicidio (NIMS), psicotrópicos vía DLP 2010+. Controles: efectos fijos de ward y cohorte, tendencias por religión/privación del ward 1971; placebo con cohortes nacidas 1977-82. Extensión: NICOLA vs TILDA como placebo.

**Killers:** (1) Migración selectiva 1969-73 (desplazados por intimidación en Belfast en los wards tratados); la residencia en 1981 es post-tratamiento para los nacidos antes de 1974. (2) Censo de 1981 boicoteado en áreas nacionalistas durante las huelgas de hambre → subregistro correlacionado con el tratamiento [no verificado aquí]. (3) Emigración a GB/ROI no observada en NILS. (4) Conflicto largo: tras 1976 exposición baja pero no nula; modelar dosis acumulada por ventana. (5) Acceso: Belfast presencial, acreditación ONS, RAG bimestral; censos+mortalidad en ~12 meses, prescripciones quizá no. (6) Unidad: ward 1981 (~560 wards) da potencia, pero hay que geocodificar Sutton.

**Puntuación de viabilidad: 6/10.** Sube a 7-8 si NISRA confirma domicilio al nacer desde 1974 y CAIN cede las coordenadas; baja a 4 si la única localización infantil es la de 1981.

## Tabla de datasets

| Dataset | Años | N | Cohortes | Geografía | Outcomes | Acceso | URL |
|---|---|---|---|---|---|---|---|
| Sutton Index (CAIN) | 1969-2001 | 3.532 muertes | — | Texto de lugar; mapas ward/1km/SOA | Muertes | Web | cain.ulster.ac.uk/sutton |
| McKeown database (CAIN) | 1969-2001 | ≈3.600+ | — | Localidad | Muertes | Descarga Excel/Access | cain.ulster.ac.uk/victims/mckeown |
| NIRI (Loyle et al. 2014) | 1968-98 | eventos | — | ML-geolocalizado (errores) | Eventos | Autores | doi:10.1177/0738894213501974 |
| GTD | 1970- | 1993 perdido | — | Ciudad/coords | Atentados | START | start.umd.edu/gtd |
| Besley-Mueller killings | 1969-2000s | región×mes | — | Regiones NI | Muertes | AEA replicación | aeaweb.org |
| NILS | 1981-2021 (+nac. 1974-) | ~516k (28%) | Niños 1981 nac. 1966-81 | Ward/código postal | Educación, empleo, salud mental censal, mortalidad, prescripciones (DLP) | NISRA SE Belfast; 2-4 m + DLP 6-8 m | nisra.gov.uk |
| NIMS | 1991-2021 | ~1,87 M | Todas | Ward | Mortalidad/suicidio | Igual que NILS | atlaslongitudinaldatasets.ac.uk |
| Censo NI microdatos 2011 | 2011 | 10%/5%/1% | Todas | LGD | Educación, empleo, salud mental | NISRA SE / UKDS | nisra.gov.uk |
| NCDS 1958 | 1958- | 17.415 | 1958 | Sin NI | — | UKDS | cls.ucl.ac.uk |
| BCS70 | 1970- | 628 NI solo al nacer | 1970 | NI no seguido | — | UKDS | cls.ucl.ac.uk |
| MCS | 2000- | ~2.000-2.500 NI | 2000-02 | Ward | Salud mental, educación | UKDS | cls.ucl.ac.uk |
| BHPS-NIHPS / Understanding Society | 2001- | 2.000 hog. | Todas | Región; LSOA especial | GHQ-12, SF-12, empleo | UKDS | understandingsociety.ac.uk |
| NISHS (WMH-CIDI) | 2004-08 | 4.340 | Nac. ≈1930-90 | Región | PTSD, trauma Troubles | ICPSR 39555 | icpsr.umich.edu |
| NICOLA | 2013-16; 2017-22; 2024- | 8.478 / 6.852 | ≤1965 | Dirección (equipo) | Salud mental, cognición, DLA, empleo | Equipo QUB | — |
| Health Survey NI | 2010/11- | 3.100-3.900 | Todas | LGD | GHQ-12 | DoH / UKDS | health-ni.gov.uk |
| NI Health & Social Wellbeing Survey | 1997, 2001 | n.v. | Todas | Región | GHQ-12 | UKDS | ukdataservice.ac.uk |
| YLT / KLT (ARK) | 2003- / 2008- | 1.000-2.100 / ~5.500 | 16 años / P7 | Región | Bienestar | UKDS / ARK | ark.ac.uk |
| ADR NI | 2018/19- | Población | Alumnos ≥14 | NI | Educación, ingresos, salud | NISRA SE / ONS SRS | adruk.org |
| GUI (ROI) | 2008- | 8.568 / 11.134 | 1997-98 / 2007-08 | Condado | Salud mental, educación | ISSDA / CSO | ucd.ie/issda |
| TILDA (ROI) | 2009-23 | 8.504 | ≤1960 | Región | Salud mental, cognición | ISSDA | ucd.ie/issda |
| Censo ROI RMF (CSO) | 2002- | Población | Todas | ED/condado | Educación, empleo | ROSA, gratis | cso.ie |
