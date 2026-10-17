# Verificación del microdato OMC/SIEVCAC (CNMH) para exposición municipal-mensual 1996-2010

Cómo: el proxy bloqueó CNMH, datos.gov.co, HRDAG; pero se clonó un repo público de GitHub con los archivos originales "Casos" del OMC (corte marzo 2025, 8 modalidades, 33 MB) y se tabularon con pandas. Copia en `data/raw/cnmh_omc_202503/`; scripts en `code/exploration/`. [V-micro] = tabulado; [V-web] = snippet; [NV] = no verificado.

## 1. Archivos

| Modalidad | Archivo (corte 2025-03) | Filas | Campos | datos.gov.co |
|---|---|---|---|---|
| Masacres (MA) | CMasacres_202503.xlsx | 4.751 | 27 | x4vk-mjnh (1944-2026) [V-web] |
| Asesinatos selectivos (AS) | CAsesionatosSelectivos_202503.xlsx | 157.136 | 30 | djr9-7s3i víctimas [V-web] |
| Desaparición forzada (DF) | CDesaparicionForzada_202503.xlsx | 68.796 | 27 | — |
| Secuestro (SE) | CSecuestros_202503.xlsx | 31.688 | 30 | x9r5-6ne4 [V-web] |
| Reclutamiento (RU) | CReclyUtiliNinoNinasAdo_202503.xlsx | 17.280 | 28 | — |
| Violencia sexual (VS) | CViolenciaSex_202503.xlsx | 16.573 | 27 | — |
| Minas (MI) | CMinas_202503.xlsx | 10.220 | 32 | 52eu-ic7d [V-web] |
| Ataque a poblados (AP) | CAtaquesPoblaciones_202503.xlsx | 500 | 48 | — |
| Acciones bélicas (AB) | CasosAB_202509.xlsx (repo LSE) | — | Grupo Armado 1-3 | 39qq-a72j [V-web] |
| Víctimas MA | — | 18 cols | código DANE, fecha, sexo, etnia | cj8q-zu3u, CC BY-SA 4.0 [V-web] |

Notas: el OMC renombró a Casos{AB,AP,AS,AT,DB,DF,MA,MI,RU,SE,VS}_{AAAAMM}.xlsx (11 modalidades). Ficha u8eq-92tb: desde 2022 el umbral de masacre pasa a 3+ víctimas [V-web]; en el archivo 2025-03 el mínimo observado sigue siendo 4 [V-micro].

## 2. Estructura "Casos" [V-micro]
ID Caso, ID Caso Relacionado (macro-caso), Año, Mes, Día (0 = sin dato), Código DANE de Municipio (5 dígitos), Municipio, Departamento, Región (76 subregiones), Modalidad (ASALTO, INCURSIÓN, SICARIATO, FALSO POSITIVO…), **Presunto Responsable**, **Descripción Presunto Responsable**, 11 flags de hechos simultáneos, Total de Víctimas del Caso, Tipo de Armas, Latitud, Longitud. Sin vereda ni fuente en la versión pública.

**Presunto Responsable (MA / AS):** GRUPO PARAMILITAR (2.097 / 65.997), GUERRILLA (785 / 24.068), GRUPO ARMADO NO IDENTIFICADO (661 / 22.368), DESCONOCIDO (205 / 31.756), AGENTE DEL ESTADO (339 / 4.917), GRUPO POSDESMOVILIZACIÓN (114 / 4.130), BANDOLERISMO (486 / 1.641), AGENTE DEL ESTADO - GRUPO PARAMILITAR (42 / 559), otros.

**¿Bloque?** Solo en Descripción Presunto Responsable: AUC genérica, NO IDENTIFICADO, ACCU, AC Magdalena Medio, BCB, Bloque Metro, Hernán Giraldo, AC Casanare, AC Meta y Vichada, AC Sur del Cesar, MAS, Tangueros. **No aparecen Bloque Norte, Calima, Catatumbo, Mineros, Élmer Cárdenas.** 1996-2010: de 1.630 masacres paramilitares, 51% "AUC", 40% "NO IDENTIFICADO", 1-21% estructura concreta. El bloque debe venir de capa externa (Justicia y Paz, Verdad Abierta, mapas AUC).

## 3. Series anuales 1996-2010 [V-micro]

| Año | MA casos para | MA víct. para | MA casos total | MA víct. total | AS casos para | AS víct. para | AS víct. total | AS+MA víct. todos |
|---|---|---|---|---|---|---|---|---|
| 1996 | 110 | 627 | 183 | 1.003 | 3.191 | 3.786 | 8.430 | 9.433 |
| 1997 | 141 | 800 | 208 | 1.189 | 4.540 | 5.343 | 10.399 | 11.588 |
| 1998 | 149 | 882 | 213 | 1.216 | 3.702 | 4.377 | 8.579 | 9.795 |
| 1999 | 191 | 1.219 | 284 | 1.684 | 4.278 | 5.094 | 9.923 | 11.607 |
| 2000 | 279 | 1.689 | 379 | 2.230 | 6.167 | 7.463 | 13.306 | 15.536 |
| 2001 | 297 | 1.718 | 404 | 2.376 | 7.079 | 8.511 | 13.939 | 16.315 |
| 2002 | 216 | 1.085 | 332 | 1.735 | 8.385 | 9.968 | 16.342 | 18.077 |
| 2003 | 126 | 646 | 191 | 998 | 7.363 | 8.495 | 13.191 | 14.189 |
| 2004 | 64 | 390 | 118 | 720 | 5.424 | 6.199 | 10.284 | 11.004 |
| 2005 | 48 | 258 | 89 | 496 | 3.137 | 3.558 | 6.677 | 7.173 |
| 2006 | 9 (+6 posdesm.) | 42 (+34) | 70 | 377 | 603 (+629) | 677 (+726) | 3.987 | 4.364 |
| 2007 | 0 (+9) | 0 (+45) | 64 | 310 | 0 (+705) | 0 (+795) | 3.408 | 3.718 |
| 2008 | 0 (+12) | 0 (+56) | 50 | 254 | 0 (+526) | 0 (+623) | 2.170 | 2.424 |
| 2009 | 0 (+10) | 0 (+51) | 30 | 164 | 0 (+475) | 0 (+557) | 1.511 | 1.675 |
| 2010 | 0 (+22) | 0 (+115) | 28 | 161 | 0 (+298) | 0 (+367) | 1.056 | 1.217 |

Guerrilla MA: 29, 27, 24, 48, 49, 55, 48, 29, 22, 15, 11, 6, 5, 13, 3. Agente del Estado MA 19-38/año en 2002-2008. **La categoría "GRUPO PARAMILITAR" se cierra en 2006 y todo pasa a "GRUPO POSDESMOVILIZACIÓN" desde 2007.**

Validación: 1998-2002 suman 1.612 masacres (CEV cita 1.620) [V-web]; 2010 = 28 (coincide) [V-web]. JEP-CEV-HRDAG: 450.664 homicidios 1985-2018, 45% paramilitares [V-web]; **microdatos de 100 réplicas (homicidio-v2, DANE catálogo 795, paquete HRDAG/verdata) con yymm_hecho, muni_code_hecho, p_str (PARA, GUE-FARC, GUE-ELN, EST…), sexo, edad, flags _imputed** [V-repo]: alternativa natural para total de muertos municipio-mes con corrección de subregistro.

## 4. Cobertura y sesgos [V-micro]
- Municipios con ≥1 masacre paramilitar 1997-2002: **368 de 1.122 (33%)**; con ≥1 AS paramilitar: 876 (78%). 1996-2010: 434 con masacre paramilitar.
- Celdas municipio-mes con ≥1 masacre paramilitar 1997-2002: 1.099 de 80.784 (1,4%); con ≥1 AS paramilitar: 13.717 (17%). Antioquia 33% de las masacres paramilitares 1997-2002; luego N. Santander 115, Cesar 103, Magdalena 82, Bolívar 81.
- Faltantes: Mes=0 en 0,7% de masacres y 1,1% de AS paramilitares 1996-2010; municipio "SIN INFORMACION" 5 MA / 455 AS.
- Subregistro mayor en zonas sin prensa y en AS; comparación formal con Panel CEDE no encontrada; vía: réplicas HRDAG.

## 5. GIS REST
serviciosgiscnmh…/rest/services/OMC/Masacres/MapServer con capas Casos y Víctimas; hub geoportal-de-datos-abiertos-cnmh [V-web]; query no probado [NV].

## 6. Reutilizables
fabiantovarc/delitos_casos_reclutamiento_COL (xlsx crudos); LSE-61296-2526/Capstone-MY498-61296 (pipeline R: 11 archivos → panel municipio-año DIVIPOLA); HRDAG/verdata + réplicas; Princeton DSS datasets "Basta Ya" municipio-día.

## Veredicto
El OMC **sí permite** exposición municipio-mes 1996-2010 por responsable: fecha, código DANE y Presunto Responsable limpios; series anuales replican cifras oficiales. Límites: (1) bloque solo en ~5% de casos → capa externa; (2) paramilitar termina en 2006 → tratar 2007-2010 como posdesmovilización o truncar; (3) masacres escasas (1,4% de celdas) → AS paramilitarias (17%) es la variable con varianza útil; (4) sin vereda ni fuente.
