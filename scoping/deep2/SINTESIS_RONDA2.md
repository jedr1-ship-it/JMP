# Segunda ronda: qué datos jugosos aparecieron en Colombia, Nepal e Indonesia

Fecha: 17-oct-2026. Diez memos de verificación en `deep2/`. El proxy siguió bloqueando las descargas directas, pero dos agentes sortearon el bloqueo clonando repositorios públicos de GitHub que redistribuyen microdatos originales, y de ahí salen los hallazgos más sólidos.

## 1. Lo que cambia respecto a la ronda anterior

| Hallazgo | Antes | Ahora | Estado |
|---|---|---|---|
| Microdato del Observatorio de Memoria (CNMH) | "existe, estructura no verificada" | **Tabulado**: 8 modalidades, 157.136 asesinatos selectivos y 4.751 masacres con año, mes, día, código DANE, presunto responsable y coordenadas; series anuales 1996-2010 que replican las cifras oficiales. Copia en `data/raw/cnmh_omc_202503/` | Verificado con los archivos |
| CIDI del CVFS (Nepal) | "no público, solo colaboración" | **Depositado en ICPSR 4538 como DS42**, uso restringido, N = 10.714, con edad de inicio de cada trastorno | Verificado en documentación CVFS |
| Base integrada del ICFES | "una infografía" | Saber 11 2000-2019 (8,25 M) enlazada con RIPS 2009-2024, PILA 2013-2023, SPADIES, SNIES y UARIV; hay precedente de Londoño-Vélez usando Saber 11 + Sisbén + PILA; Banrep usa RIPS individual | Verificado existencia; acceso sin protocolo público |
| ENSM 2025 | no se conocía | **110.842 personas de 7+ años en 32 departamentos**, campo 2025, microdatos anunciados para 2026 | Verificado en prensa y Minsalud; diseño y microdato pendientes |
| ELCA | "~500 niños útiles" (estimación) | 8.693 niños en 2010 confirmados; retención del 75% en 2016 con SDQ y TVIP; ≈565 nacidos 2000-2003 en zonas AUC; **municipio anonimizado en los microdatos públicos** | Verificado con los archivos (vía repo de replicación) |
| Saber 11 | "municipio a verificar" | Municipio de residencia del estudiante existe al menos desde 2012-2; llave pública Saber 11 ↔ Saber Pro; **el censo 2018 no identifica municipio de nacimiento** | Verificado en diccionarios |
| UNSFIR (Indonesia) | no se conocía | Violencia colectiva 1990-2003 por kabupaten en 14 provincias (incluye Jakarta y Solo, no Medan); 15 kabupaten concentran el 85% de las muertes | Verificado existencia; descarga por solicitud a los autores |
| Banyuwangi 1998 | no se conocía | 307 muertos (Komnas HAM) en Java Este, sep-dic 1998, provincia IFLS | Verificado |
| IFLS | "kecamatan probablemente" | Kabupaten y kecamatan en los ficheros públicos (bk_sc, geo_i97); censo 2010 en IPUMS con kabupaten de nacimiento | Verificado |

## 2. Colombia: el país que más ganó

**Exposición.** Ya tenemos la variable de tratamiento en la mano. Con el microdato del CNMH se construye un panel municipio × mes 1996-2010 de masacres y asesinatos selectivos por presunto responsable. Tres decisiones de diseño que salen de las tablas:

- Las masacres son raras (1,4% de las celdas municipio-mes 1997-2002); los asesinatos selectivos paramilitares (17% de celdas, 65.997 casos) son la variable con varianza útil. Las masacres sirven como shock extremo.
- La categoría "grupo paramilitar" se cierra administrativamente en 2006 y todo pasa a "posdesmovilización". Eso es a la vez el fin del tratamiento y una trampa: hay que decidir si 2007-2010 cuenta como post limpio o como continuación.
- El bloque responsable solo aparece en un 5% de casos. La fecha de desmovilización por municipio tiene que venir de una capa externa (las 38 desmovilizaciones ya fechadas en el dossier anterior, más mapas de estructuras de Justicia y Paz).

Complemento: las 100 réplicas del proyecto JEP-CEV-HRDAG (paquete verdata, catálogo DANE 795) dan homicidios municipio-mes con responsable y corrección de subregistro. Es la robustez natural.

**Outcomes.** Tres capas, de más a menos accesible:

1. Saber 11 abierto (460-550 mil por año) con municipio de residencia desde 2012-2, es decir, cohortes nacidas 1995-2008. Cubre in utero, 0-2 y 3-5 para la ola 1997-2002 y el fin 2003-2006. Es público y se puede empezar mañana.
2. Salud mental: ENSM 2025 con 110.842 personas en 32 departamentos (las cohortes 1990-2008 tienen 17-35 años) si el microdato trae municipio o departamento e historia de desplazamiento. Mientras tanto, suicidios de Estadísticas Vitales 1998-2024 por municipio de residencia y edad (público) e intentos de suicidio SIVIGILA 2016+.
3. La base integrada del ICFES con RIPS y PILA, que daría diagnósticos de salud mental administrativos y empleo formal para millones. Sin protocolo público; la vía es un proyecto bajo la agenda de investigación del ICFES o coautoría con Uniandes-CEDE.

**El problema de la residencia infantil** sigue abierto: Saber 11 da residencia a los 16-18, no a los 0-5, y el censo 2018 no identifica municipio de nacimiento. Soluciones: Estadísticas Vitales de nacimientos (municipio de residencia de la madre, sin identificador) como denominador y para validar la estabilidad; GEIH con municipio de nacimiento; registro de víctimas (RUV) de expulsión por municipio y año para acotar el desplazamiento; y el supuesto de baja movilidad en municipios rurales, que hay que documentar.

**ELCA** queda confirmado como complemento de mecanismos, no como base: unos 565 niños útiles, SDQ reportado por el cuidador y TVIP a los 13-16 años, y municipio solo en la sala de datos del CEDE.

## 3. Nepal: mejor acceso, misma limitación

El CIDI está en ICPSR como dataset restringido, lo que convierte el acceso en un trámite (acuerdo de uso restringido, IRB, plan de seguridad) y no en un favor. Pero los eventos de conflicto georreferenciados por vecindario no están depositados, y sin ellos la exposición dentro de Chitwan no se puede construir. Las cohortes alternativas (Sarlahi con 2.055 y 676 niños seguidos, Makwanpur con 6.075) llegan solo a los 9-13 años sin salud mental. La fuente de eventos con aldea y fecha (INSEC vía Joshi y Pyakurel) no tiene descarga pública. Nepal se queda como está: viable solo con colaboración directa con el equipo del CVFS.

## 4. Indonesia: más dosis de la que pensábamos

Dos cosas nuevas. UNSFIR da muertes por kabupaten 1990-2003 en 14 provincias, lo que permite una exposición continua y no solo "Jakarta frente al resto". Y aparecieron episodios adicionales dentro de las provincias IFLS: los asesinatos de "dukun santet" en Banyuwangi y Jember (307 muertos, sep-dic 1998), Situbondo 1996, Tasikmalaya 1996, Ketapang 1998. Sumando, el conjunto de niños IFLS nacidos 1993-1998 en kabupaten con violencia colectiva ronda los 1.000, no los 500. IFLS tiene kabupaten y kecamatan públicos, y el censo 2010 en IPUMS tiene kabupaten de nacimiento para potencia en educación. Sigue sin haber ola posterior a 2014 ni medida de salud mental más allá del CES-D a los 16-21 años.

## 5. Ranking actualizado

| País | Antes | Ahora | Por qué |
|---|---|---|---|
| Colombia híbrido | 7/10 | **8/10** | Tratamiento construido y verificado; Saber 11 público con municipio desde 2012-2; ENSM 2025 a la vista; vía ICFES-RIPS-PILA identificada |
| Indonesia IFLS + UNSFIR + censo 2010 | 4/10 | 5/10 | Dosis y N mayores; sigue sin outcomes adultos ni salud mental fuerte |
| Nepal CVFS | 4/10 | 5/10 | CIDI accesible por trámite; eventos siguen cerrados |

## 6. Lo que se puede hacer esta semana sin pedir permiso a nadie

1. Construir el panel municipio × mes 1996-2010 del CNMH con los archivos ya en el repo: masacres y asesinatos selectivos por responsable, más mapa de intensidad y perfil temporal por zona AUC.
2. Descargar Saber 11 2012-2 a 2025 de datos.gov.co, deduplicar por consecutivo, y contar evaluados por municipio de residencia × año de nacimiento en los municipios con masacres paramilitares 1997-2002.
3. Descargar Estadísticas Vitales de nacimientos 1998-2008 y defunciones 1998-2024 del DANE para denominadores de cohorte y suicidios por municipio × edad.
4. Cruzar las 38 fechas de desmovilización con los municipios del CNMH para definir la fecha de fin del tratamiento por municipio.
5. Escribir al ICFES (Dirección de Investigación) y al CEDE preguntando por el acceso a la base integrada, y a Minsalud por el calendario de microdatos de la ENSM 2025.
