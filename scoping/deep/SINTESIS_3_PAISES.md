# Tres países a fondo: Colombia, Nepal e Indonesia con encuestas longitudinales

Fecha: 16-oct-2026. Basado en cinco dossiers de verificación (ver `deep/`). Advertencia: el proxy del entorno bloqueó todas las descargas directas, de modo que los agentes trabajaron con fragmentos de búsqueda. Los detalles están marcados [V]/[NV] en cada dossier.

## 1. El resultado en una frase

Con la restricción de encuesta longitudinal, ninguno de los tres países da por sí solo un job market paper de top 5: los tres diseños puramente de encuesta puntúan 4 sobre 10. El evento colombiano es el mejor de los tres con diferencia; la encuesta colombiana es la más débil. La combinación ganadora es un diseño híbrido en Colombia: identificación en registros administrativos masivos y mecanismos en la encuesta.

## 2. Por qué fallan los tres diseños de encuesta

Una encuesta longitudinal sigue a unos miles de niños. Un episodio violento acotado golpea a unos pocos municipios o barrios. La intersección son cientos de niños expuestos, repartidos en tres o cuatro bins de edad. Con esa potencia no se distingue 0-2 de 3-5. Los papers que sí lo han hecho con encuestas (Akbulut-Yuksel con el GSOEP y los bombardeos alemanes) tenían un shock que cubría todo el territorio de la encuesta con intensidad variable, de modo que toda la muestra estaba expuesta.

| País | Episodio | Encuesta | Niños 0-5 expuestos observables | Outcome adulto de salud mental | Lo que ya está hecho | Nota |
|---|---|---|---|---|---|---|
| Colombia | AUC 1997-2002, desmovilización escalonada 2003-2006 (38 actos fechados) | ELCA 2010/2013/2016, continuada como ELCO-DANE 2019/2022 | ~450-550 (nacidos 2000-2003 en Córdoba-Sucre, tras atrición del 51%) | No identificado; outcomes hasta 13-16 años (ELCO podría llevarlos a 19-22) | Duque (2024): homicidios años 80 × Saber 11 × edad | 4/10 |
| Nepal | Insurgencia 1996-2006, escalada 2001, CPA nov-2006 | CVFS Chitwan: registro mensual desde 1997, CIDI 2016-18 (10.714 personas) | ~1.000-1.300 in utero/0-2 y ~700-900 de 3-5; solo 10% de vecindarios con exposición alta | Sí (CIDI), pero no público: colaboración con Axinn/Ghimire | Benjet et al. (2020): <11 vs ≥11 y depresión; Tafesse (2024): DHS 2022 × INSEC, ventana 0-6 | 4/10 |
| Indonesia | Disturbios 13-15 mayo 1998 (Jakarta, Solo, Medan; 1.217 muertos en Jakarta) | IFLS 1993/1997/1998/2000/2007/2014 | ~400-500 en Jakarta, ~150 en Solo y Medan | CES-D-10 a 16-21 años en 2014; sin ola posterior | Nadie | 4/10 |

## 3. Qué tiene cada país que no tienen los otros

**Colombia tiene el evento.** Treinta y ocho desmovilizaciones con fecha y lugar entre noviembre de 2003 y agosto de 2006, entradas de bloques fechadas desde 1996, y el Observatorio de Memoria y Conflicto con cada masacre y asesinato selectivo por día, municipio y perpetrador, público. Ocho zonas con entrada y salida limpias: Catatumbo (1999 a dic-2004), Montes de María (1997 a jul-2005), centro del Valle (1999 a dic-2004), Cesar y Magdalena (1996 a mar-2006), Casanare y Meta (1997 a sep-2005), Oriente antioqueño (2000 a ago-2005), Sur de Bolívar (1998 a ene-2006), Nordeste antioqueño (hasta dic-2005). La entrada y la salida escalonadas por municipio separan edad de exposición de dosis, que es exactamente lo que un referee pedirá. Nadie ha estudiado los efectos de largo plazo de esta ola en niños.

**Nepal tiene la medición.** El CVFS registra la residencia mes a mes desde 1997, es decir, localización pre-tratamiento, y aplicó el CIDI completo a toda su muestra adulta en 2016-18 con edad de inicio de cada trastorno. Es la única encuesta de un país en desarrollo con esas dos cosas. Pero el conflicto en Chitwan fue de intensidad baja-media, la variación interna es escasa y el equipo del CVFS ya ha publicado el corte infancia frente a adultez.

**Indonesia tiene la foto inmediata.** IFLS tiene una ola en 1997 (antes), otra en el segundo semestre de 1998 (tres a seis meses después, justo en las provincias afectadas) y seguimiento hasta 2014. Ningún otro panel del mundo observa un hogar antes, inmediatamente después y dieciséis años después de un episodio violento. Pero la dosis fue de tres días, la variación es casi solo entre ciudades y la crisis asiática cayó en el mismo mes.

## 4. Lo que cambia la jugada en Colombia

El dossier de ELCA encontró un proyecto ICFES-Uniandes que enlaza Saber 11 (2000-2019, 8,25 millones de estudiantes) con SNIES, SPADIES, UARIV (registro de víctimas), RIPS (registros de atención en salud, con diagnósticos) y PILA (empleo formal). Si ese enlace es accesible en colaboración, Colombia tiene lo que tiene Irlanda del Norte con NILS: millones de personas con fecha de nacimiento, municipio, educación, empleo formal y diagnósticos de salud mental administrativos. Es el dato longitudinal que ELCA no puede dar. Además, la ELCO del DANE (2019 y 2022) parece seguir a los hogares de ELCA, lo que llevaría a los niños nacidos en 2000-2003 hasta los 19-22 años.

## 5. Recomendación: arquitectura híbrida en Colombia

1. **Identificación**: cohortes 1990-2008 × municipio de nacimiento o de residencia infantil × exposición mensual a violencia paramilitar (OMC) con fecha de entrada y de desmovilización del bloque. Datos: Saber 11 para educación a los 17 (cientos de miles por cohorte); CNPV 2018 y GEIH para educación y empleo adulto; el enlace ICFES-RIPS-PILA para salud mental y empleo formal si se consigue.
2. **Mecanismos**: ELCA/ELCO en Córdoba-Sucre para el canal hogar (choques violentos declarados, ingresos, composición, salud mental parental si existe) y desarrollo infantil (TVIP, SDQ) a 3-16 años.
3. **Desplazamiento**: RUV de expulsión por municipio y año para acotar la atrición selectiva; Sisbén III como localización 2009-11.
4. **Post contaminado**: excluir o tratar aparte Córdoba, Urabá, Bajo Cauca, Medellín, Nariño, donde las BACRIM reemplazaron a las AUC desde 2008.

Si la restricción de encuesta longitudinal es estricta y no negociable, entonces la alternativa honesta es Nepal con el CVFS en colaboración con Axinn y Ghimire, aceptando que el ángulo tendrá que ser outcomes económicos por bin fino de edad y no salud mental, porque ese espacio ya está ocupado. Indonesia queda como capítulo de mecanismo, no como paper.

## 6. Verificaciones que decidirían

- ICFES-Uniandes: alcance real del enlace Saber 11 + RIPS + PILA + UARIV y vía de acceso.
- ELCO 2019/2022: si re-sigue a los niños de ELCA y con qué módulos.
- ELCA: código de municipio en bases públicas; municipios de la microrregión Atlántica Media; instrumento de salud mental adulta.
- Saber 11 2009-2026: fecha de nacimiento y municipio de residencia.
- CNPV 2018: codificación municipal del lugar de nacimiento.
- OMC: estructura del microdato y conteo de masacres paramilitares por subperiodo.
- CVFS: condiciones de acceso a CIDI 2016-18 y a las georreferencias.
