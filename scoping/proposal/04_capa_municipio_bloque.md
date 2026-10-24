# Capa municipio → bloque AUC → fecha de desmovilización (1997-2006)

Restricción: el proxy devolvió 403 a todos los hosts salvo GitHub (clonación de repos públicos). [V] snippets (26 búsquedas) y 4 repos clonados; [NV] memoria. Ningún paquete de replicación pudo descargarse.

## 1. Fuentes

| Fuente | Cobertura | Unidad | ¿Tabla lista? | Estado |
|---|---|---|---|---|
| Coy (2024) "A Farewell to Arms", JDE 171, 103350 (SDID, autor único) | todos los bloques (panel municipal) | municipio | Probable en Mendeley Data (bloqueado); no localizado | [V] existe; [NV] paquete |
| Acemoglu, Robinson & Santos (2013 JEEA) | presencia paramilitar 1991-2006 | municipio | No por bloque | [NV] fuente |
| Namen, Prem & Vargas (2023 JHR 58(3)) | municipios con bloque desmovilizado | municipio-año | Pestaña supplemental JHR (bloqueada) | [V] existe |
| **Colectivo de Abogados (2006) "Cuadro desmovilizaciones colectivas" (OACP)** | 38 actos: bloque, fecha, N, **municipios de operación** (p. ej. B. Noroccidente Antioqueño: 22 municipios) | bloque→municipios | **Sí, la más cercana a una tabla hecha** | [V] snippet; PDF no descargable |
| OACP "Proceso de paz con las Autodefensas" (2006), espejos Indepaz/CJA | 38 actos, 31.671, 18.051 armas; fichas con zona de influencia | acto | Fichas | [V] cifras |
| **CNMH-OMC "Portal de datos del paramilitarismo"** (Mecanismo No Judicial, Ley 1424) | **39 estructuras, 31 deptos, ~700 municipios; "distribución espacial de las 39 estructuras por municipio"** | estructura × municipio | Candidata principal | [V] snippet; [NV] formato |
| CNMH (2018) *Paramilitarismo. Balance*; serie DAV por bloque | narrativo, mapas | región/bloque | No | [V] |
| Observatorio DDHH Vicepresidencia | 279 mpios (1997) → 455 (2002); 531 en 1997-2002 | municipio-año | No por bloque | [V] cifras |
| Fiscalía DJT: informes con "zonas de injerencia" por postulado; directorio de despachos por bloque | frente→municipios | Parcial | [V] |
| Sentencias Justicia y Paz (~60): índice sentencia × estructura descargado | frente→municipios | Extraer | [V] índice |
| **Rutas del Conflicto, masacres (snapshot 2015 vía GitHub)** | 741 masacres; 548 paramilitares; 451 en 1997-2006, 381 con bloque; **194 municipios con bloque identificado, 23 con >1 bloque** | masacre→municipio | CSV descargado | [V] |

## 2. Material en el repo
- `data/raw/rutas_del_conflicto/Masacres_Data.csv` (741 masacres con autor codificado por bloque y años).
- `data/derived/rdc_masacres_municipio_bloque_1997_2006.csv` (municipio × bloque × n masacres × años).
- `data/raw/jyp_index/bloques.csv`, `links.csv`: índice de 62 sentencias JyP × 64 estructuras.

## 3. Muestra de 12 municipios

| Municipio | Bloque dominante | Entrada aprox. | Desmovilización | Confianza |
|---|---|---|---|---|
| Tibú | Bloque Catatumbo (ACCU) | may-1999 (La Gabarra) [V] | 10-dic-2004 [V] | Alta |
| El Carmen de Bolívar | Héroes de los Montes de María (El Salado atribuido a B. Norte) | mar-1997 [V] | 14-jul-2005 | Alta bloque; doble atribución |
| Tuluá | Bloque Calima | ago-1999 [V] | 18-dic-2004 [V] | Alta |
| Valledupar | Bloque Norte (Fte. Mártires del Cesar) | 1996-98 | 8/10-mar-2006 | Alta bloque |
| San Carlos (Ant.) | Metro 1998-2002 → Héroes de Granada 2003-05 | mar-1998 [V] | Metro extinguido 2003; H. Granada 1-ago-2005 | Secuencia clara; fin ambiguo |
| Santa Rosa del Sur | BCB Sur de Bolívar | 1998-99 | 31-ene-2006 | Media-alta |
| Remedios | Metro 1998-2001 → BCB Nordeste | 1997-98 [V] | 12-dic-2005 | Media |
| Yopal | AC del Casanare (sin acto colectivo); Centauros disputa 2004 | 1990s | Centauros sep-2005/abr-2006 | Baja |
| Mapiripán | ACCU jul-1997 → Centauros → H. Guaviare | jul-1997 [V] | 2005/2006 | Media |
| Puerto Asís | Bloque Sur Putumayo (BCB) | mar-1998 [V] | 1-mar-2006 | Alta |
| Tumaco | Libertadores del Sur (BCB) | oct-2000 [V] | 30-jul-2005 | Alta |
| Tame | Vencedores de Arauca | mar-2002 [V] | 23-dic-2005 | Alta |

## 4. Plan (2-3 semanas) y veredicto
Semana 1: Cuadro Colectivo de Abogados/OACP (bloque→municipios por acto) + portal CNMH-OMC paramilitarismo (39 × ~700) + scrape de Rutas del Conflicto + 5% identificado del microdato CNMH. Semana 2: secciones "zona de injerencia" de ~15 macro-sentencias JyP e informes Fiscalía-DJT. Semana 3: panel municipio × año con bloque dominante (sucesiones Metro→H. Granada/BCB, ACCU→Centauros→H. Guaviare), fecha fin = acto del bloque dominante; censura para ACC y Metro; confianza por nº de fuentes.

**Veredicto: construible.** Asignación única y robusta en ~85-90% de los municipios con presencia intensa (171/194 de RDC con un solo bloque); fecha exacta al día una vez conocido el bloque. Imprecisión en ~10-15% de municipios con disputa/sucesión (Urabá, sur de Bolívar, Casanare/Meta, Montes de María, Buenaventura), estructuras sin acto (ACC, Metro) y presencia difusa (~250-300 municipios). Prioridad desde una red sin proxy: Cuadro del Colectivo de Abogados, portal OMC y paquete de Coy (2024).
