# ¿Cuántos niños útiles tiene la ELCA? Verificación numérica

Fuente decisiva: paquete de replicación público en GitHub (tesis de maestría Uniandes, oct-2026) que documenta columna por columna los microdatos públicos de ELCA del Dataverse de Uniandes (DOI 10.57924/DPF0M5, DE9LP7, BLUILW) y publica conteos agregados. [V] fuente primaria; [V2] visto en el repo (secundario); [NV] no verificado; [est] cálculo propio.

## 1. Niños por ronda [V2]

| Ronda | Archivo | Edad | Urbano | Rural | Total |
|---|---|---|---|---|---|
| 2010 | Ninosde0a9 | 0-9 | 4.282 | 4.411 | **8.693** |
| 2013 | Ninos0a13 | 0-13 | 5.130 | 5.254 | 10.384 |
| 2016 | Ninos6a16 (99,98% miembros originales) | 6-16 | 3.409 | 3.150 | 6.559 |

TVIP con dato en 69,6% de 8.693 (≈6.050, niños 3-9); antropometría 46,6% (≈4.050 de 0-4) [V2]. Hogares públicos 2010: 9.853; 2013: 9.261; 2016: 8.818 [V2]. Hogares en las tres rondas: 7.735 (78,5%) [V2].

**Hogares por región 2010 y niños estimados [V2/est]:**

| Región | Hogares 2010 | 2013 | 2016 | Niños 0-9 2010 [est] |
|---|---|---|---|---|
| Atlántica (urb.) | 1.107 | 1.067 | 1.090 | ≈900 |
| Oriental (urb.) | 1.074 | 947 | 903 | ≈870 |
| Central (urb.) | 1.098 | 937 | 859 | ≈890 |
| Pacífica (urb.) | 1.081 | 1.016 | 892 | ≈880 |
| Bogotá | 915 | 714 | 613 | ≈740 |
| Atlántica Media (rur.) | 1.134 | 1.178 | 1.232 | ≈1.090 |
| Cundi-Boyacense (rur.) | 1.176 | 1.158 | 1.117 | ≈1.130 |
| Eje Cafetero (rur.) | 1.170 | 1.123 | 1.012 | ≈1.130 |
| Centro-Oriente (rur.) | 1.098 | 1.121 | 1.063 | ≈1.060 |

## 2. Municipios [NV]
ANDA 816: 48 municipios urbanos y 17 rurales; diseño rural con "Sub-región B: Bolívar y Atlántico; Sub-región C: Córdoba y Sucre" [V snippet]; 2013: 183 municipios; 2016: 244 [V]. Lista nominal no obtenida.

## 3. Retención del panel infantil
- Niños 2010 reobservados en 2016: 6.559/8.693 = **75,5%** (rural 71,4%, urbano 79,6%) [V2]. Con SDQ 2016: 98,1% de ellos (≈6.430); con TVIP 97,5% [V2].
- El 48,7% "con información completa" = niños con pruebas válidas en las tres rondas [inferencia].
- SDQ 2016 reportado por el cuidador (25 ítems + escalas) [V2]. ASQ-SE solo 2013 (31,9%) [V2]. Módulo Jóvenes 10-16 no está en Dataverse [V2].

## 4. Geografía en microdatos públicos
Hogar: zona, region (9), id_dpto, id_mpio con 100% cobertura [V2]. **Pero el autor documenta que id_dpto/id_mpio son códigos anonimizados sin correspondencia con DIVIPOLA** [V2]. Coordenadas solo en sala de datos del CEDE [V2]. Nivel público efectivo: región/microrregión + zona.

## 5. Nacimiento y migración (Personas) [V2]
2010: lugar_nacimiento (59,3%), id_dpto_nac/id_mpio_nac (19,9% en 2010; 100% en 2013), lugar_vivia, lugar_vivia5, id_mpio_vivia (12,8%), razon_llego. 2013: migra_ult3, mpio_migra_1. 2016: mig_mpio2010, mig_mpio2013, mig_seguridad (7,8%). **No hay año de llegada ni módulo individual de desplazamiento con año/municipio de origen**; solo ayu_desplazados (hogar) y variables comunitarias.

## 6. ELCO 2019/2022 [NV]
ANDA 814 y 902 existen [V2]. DANE: ELCO "incorpora la medición antropométrica, desarrollo de lenguaje y socioemocional de los niños de seguimiento" de ELCA [V]. N reencontrados, instrumentos, guía de integración [NV].

## 7. Salud mental de adultos
En 1.359 campos del archivo Personas no hay SRQ, CES-D, PHQ [V2]. Solo depresion_m/p en 2010 (antecedentes de los padres del informante). Big Five/Raven no aparecen.

## 8. Veredicto numérico

| Grupo | Nacional 2010 | Atlántica Media | Urbana Atlántica | Observados 2016 (SDQ+TVIP) |
|---|---|---|---|---|
| Nacidos 2000-2003 (~38% de 0-9) [est] | ≈3.300 | ≈415 | ≈340 | ≈295 + ≈270 = **≈565** (≈300 solo rural) |
| Nacidos 1996-1999 (solo roster) [est] | ≈3.650 | ≈440 | ≈400 | sin módulo infantil |

La estimación de "~500 niños útiles" se sostiene en orden de magnitud: ≈300 solo con Atlántica Media, ≈550-600 sumando urbana Atlántica, con SDQ (cuidador) y TVIP a 13-16 años. Caveat decisiva: en los datos públicos la exposición solo se asigna por microrregión (9 categorías), no por municipio, y no hay residencia 1997-2006; municipio × edad requiere la sala de datos del CEDE.

Nota: el agente clonó el repositorio de replicación en /home/user/jonathanmelosa/replicacion_tesis_vulnerabilidad (lectura; no ejecutado).
