# ¿Existe en Colombia un "NILS" (registros administrativos longitudinales enlazados)?

Nota: 25 búsquedas; proxy 403 a todo CONNECT (icfes, datos.gov.co, DANE, NBER, AEA, ScienceDirect). [V] snippet; [NV] memoria o no confirmado.

## 1. Proyecto ICFES-Uniandes de integración de bases [V parcial]
- [V] Existe. Dos infografías ICFES de julio 2026 (infografia_conectividad.pdf; infografia_documental_conectividad.pdf) describen una **base longitudinal que enlaza Saber 11 2000-2019 con SNIES, SPADIES, UARIV, RIPS y PILA; 8.253.202 estudiantes**. Autores: funcionarios ICFES + un investigador de Uniandes. El documento no dice nada sobre acceso.
- [V] "Agenda y Repositorio de Investigaciones" ICFES: ventanas por fuente: SNIES 2016-2024; SPADIES 1998-2015; UARIV corte 2025; **RIPS 2009-2024; PILA 2013-2023**; Saber 11 1999-2019 o 2013-2019 según entrada. Proyecto "Desempeño de la población afrocolombiana en Saber 11 (2017-2026) con integración UARIV".
- [NV] Liderazgo y convocatoria; sin papers publicados con RIPS/PILA hallados.
- Implicación: RIPS desde 2009, PILA desde 2013, Saber 11 hasta 2019 cubren exactamente las cohortes 1990-2008. Es, en papel, el "NILS colombiano".

## 2. Saber 11 microdatos (DataIcfes)
- [V] DataIcfes como repositorio abierto; bases cruzadas Saber 11-Saber Pro; estudio UAM 2024 usó DataIcfes 2010-2023. Tesis UNAD: base abierta con 51 variables y ~2,2 M registros 2015-2019 con ubicación geográfica.
- [NV] Nombres de variables (ESTU_FECHANACIMIENTO, ESTU_COD_RESIDE_MCPIO, COLE_COD_MCPIO_UBICACION, INSE): existen en el formato posterior a 2014-2; 2000-2014-1 otra estructura.
- Evaluados por año [V]: 2012 ≈545 mil; 2013 ≈543 mil; 2014-2: 463.722; 2014-2019: 459-475 mil (segundo semestre); 2022: 530.561; 2023-2: 551.149; 2025: 489.880. 2000-2011 no encontrado.

## 3. SIMAT y C-600
- [V] SIMAT desde 2005. Sánchez, Velasco, Ayala y Pulido (Uniandes DT-36, 2016) usan SIMAT por estudiante: el microdato individual existe y se ha cedido a Uniandes. [V] SIMAT es insumo del REBP. [NV] Sin procedimiento público de acceso.

## 4. RIPS / SISPRO
- [V] Base por paciente con diagnóstico CIE-10; BID advierte problemas de cobertura y calidad. Res. 1036/2022 y 1884.
- [V] **Banco de la República, Borradores 1300**: cohortes individuales con RIPS 2019-2022 (sobrevivientes COVID vs control), incidencia de ansiedad, depresión, estrés. Prueba de acceso al microdato identificable.
- [NV] Vía de acceso para externos.

## 5. PILA
- [V] NBER w31737 (Londoño-Vélez, Ser Pilo Paga): **Saber 11 + Sisbén (DNP) + PILA (Minsalud)**; cotizaciones individuales mensuales; muestra sobre 574.259 evaluados de agosto 2014; "administrative data linking the population of high school test-takers to all postsecondary attendees, financial aid beneficiaries, college exit test-takers, and formal workers".
- [V] Khanna et al. NBER w26313: PILA panel empleador-empleado. Banrep PILA+GEIH 2010-2021.

## 6. Sisbén y enlaces realizados
- [V] AEJ:Policy 2020 (Londoño-Vélez, Rodríguez, Sánchez): fuentes ICFES, DNP y MEN (2016). PILA confirmado en NBER 2023.
- [NV] Procedimiento de convenio DNP.

## 7. RUV / UARIV
- [V] Portal Datos Paz; glosario RUV jul-2026 con modelo integrado; DANE usó RUV para pobreza 2019-2021; acceso individual vía Red Nacional de Información con acuerdos de confidencialidad.

## 8-9. Otros
- [V] **DANE REBP (Registro Estadístico Base de Población)**: integra PILA, BDUA, Sisbén, RUT, SIMAT, SNIES; REBP 2018; 2019-2021 en actualización; RELAB derivado de PILA (CEPAL 2023). Acceso no documentado.

| Fuente | Años | Variables clave | Acceso | Uso |
|---|---|---|---|---|
| Saber 11 | 1999-2024; 460-550 mil/año 2014-23 | mpio residencia, mpio colegio, NSE, fecha nac. [NV nombres] | DataIcfes anonimizado | SPP (AEJ 2020, NBER 2023) |
| Base integrada ICFES | S11 2000-19; RIPS 2009-24; PILA 2013-23; SPADIES 1998-2015; SNIES 2016-24; UARIV 2025 | 8,25 M estudiantes | No documentado | Infografía jul-2026 |
| SIMAT | 2005- | trayectorias por estudiante | Cesión a Uniandes | Sánchez et al. 2016 |
| RIPS | 2009- | CIE-10 incl. F00-F99 | Banrep sí; externos [NV] | Borradores 1300 |
| PILA | 2013-23 (ICFES); 2010-21 (Banrep) | cotizaciones mensuales, salario | vía ICFES/DNP/Banrep | NBER w31737, w26313 |
| Sisbén | III 2009-11; IV 2017- | puntaje, hogar | convenio DNP | AEJ 2020 |
| RUV | 1985- | hecho, fecha, mpio | Datos Paz/RNI | ICFES Afro |
| REBP/RELAB | 2018-2021 | PILA+BDUA+Sisbén+RUT+SIMAT+SNIES | No documentado | — |

## Veredicto
Sí existe, pero no es accesible como un NILS. Tres custodios: ICFES (base integrada), DNP/MEN (vía Londoño-Vélez) y DANE-REBP/Banrep. Todos los usos verificados pasan por coautoría con un investigador colombiano (Uniandes-CEDE, Banrep) o convenio. Vía realista: contactar a la Dirección de Investigación del ICFES y al coautor de Uniandes de la infografía y proponer un proyecto bajo la agenda ICFES; alternativa, coautoría con CEDE para el enlace DNP. Riesgos: identidad del enlace, calidad de RIPS, y que el municipio de residencia esté en las bases 2006-2014.
