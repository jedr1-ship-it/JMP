# Colombia: microdatos educativos para seguir cohortes 1990-2008 por municipio

Nota: 18 búsquedas; proxy rechazó datos.gov.co (API incluida), icfes, DANE. [V] snippet; [NV] no verificado.

## 1. Saber 11
- Base abierta "Resultados únicos Saber 11" (datos.gov.co kgxf-xxbe): 7,11 M filas, 51 columnas, semestral [V]; cubre 2010-2022 o hasta 2025 [V/NV]. Periodos 2000-1 a 2009-2 en fichas separadas [V existen].
- ESTU_CONSECUTIVO = identificador del examinando [V]; filas duplicadas en la base abierta (1.065.888 filas, 532.792 consecutivos en un periodo) [V]; específico de cada aplicación, no enlaza años por sí solo [NV]. ICFES: "dispuso una llave que permite cruzar Saber Pro con Saber 11" en DataIcfes [V]. Dataset Mendeley "Linked Saber 11 and Saber Pro" [V].
- **Municipio de residencia del estudiante**: ESTU_COD_RESIDE_MCPIO (código DANE), ESTU_MCPIO_RESIDE, ESTU_COD_RESIDE_DEPTO en diccionarios 2019-2022 [V]; ESTU_CODIGO_RESIDE_MCPIO en 2012-2 y 2013 [V]. **Existe al menos desde 2012-2 [V]**; 2000-2012-1 [NV].
- ESTU_FECHANACIMIENTO, ESTU_GENERO, FAMI_ESTRATOVIVIENDA, FAMI_EDUCACIONPADRE/MADRE, ESTU_INSE_INDIVIDUAL, COLE_COD_MCPIO_UBICACION, PUNT_GLOBAL: recuerdo del catálogo [NV].
- N por año [V]: calendario A 2014→2025: 463.722 → 489.880; mínimo 457.214 (2020); 2019-2: 541.901; 2023-2: 551.149; 2024-2: ~557 mil.

## 2. Saber 3°, 5°, 9°
DataIcfes (SB359) [V]; microdato con fecha de nacimiento y municipio [NV]; desde 2022 "3°, 5°, 7° y 9°" [V].

## 3. Saber Pro / TyT
datos.gov.co u37r-hjmu y iwgf-bkfk con ESTU_CONSECUTIVO, ESTU_COD_RESIDE_MCPIO [V]; llave Saber 11↔Pro pública vía DataIcfes [V].

## 4. SPADIES
Agregados web (SPADIES 3.0) [V]; microdato individual sin ruta oficial [NV]. Base longitudinal ICFES de 8.253.202 evaluados 2000-2019 enlazada con educación superior, salud, empleo y victimización [V]; acceso [NV].

## 5. SIMAT / Anexo 6A
Sin microdato nacional público [NV]; uso por convenio: Medellín 2019 (Rev. Econ. Rosario 2023) [V]; estudio ICFES que integra SIMAT + ICBF + Saber desde primera infancia [V]. Namen, Prem & Vargas: fuente de deserción [NV].

## 6. Nacidos vivos DANE (EEVV)
1992/1998-2023, microdatos libres [V]; área y municipio de residencia de la madre, edad de la madre [V parcial]; peso, educación [NV].

## 7. Censos
- **CNPV 2018: PA_LUG_NAC es categórica ("en este municipio" / "en otro municipio" / otro país), no DIVIPOLA** [V]; P_EDADR quinquenal [V]; PA_VIVIA_5ANOS, PA_VIVIA_1ANO existen [V].
- Censo 2005 IPUMS: BPLCO2 = municipio de nacimiento agrupado ≥20.000 hab. [V].

## 8. GEIH migración
2012-2019; 2020-21+; P756 (S1 depto, S2 municipio, S3 país) dónde nació; P755 hace 5 años; P753 hace 12 meses (2021) [V].

| Fuente | Años | N/año | Variables clave | Geografía | ID | Acceso |
|---|---|---|---|---|---|---|
| Saber 11 | 2000-1 → ≥2022 | 460-560 mil | ESTU_CONSECUTIVO; ESTU_COD_RESIDE_MCPIO [V]; fecha nac., INSE, colegio [NV] | mun. residencia ≥2012-2 | llave ↔ Pro | libre; DataIcfes |
| Saber 3-5-9 | 2012-17 | [NV] | [NV] | [NV] | [NV] | DataIcfes |
| Saber Pro/TyT | 2007-2025 | [NV] | ESTU_CONSECUTIVO, ESTU_COD_RESIDE_MCPIO | mun. residencia | sí | libre |
| SPADIES | 1998- | universo ES | [NV] | IES | Saber 11 | trámite |
| SIMAT | 2005- | universo | grado, sede | sede/mun. | — | convenio |
| EEVV nacimientos | 1992-2023 | ~650-700 mil | mun. residencia madre | municipio | no | libre |
| CNPV 2018 | 2018 | censal | PA_LUG_NAC categórica | mun. residencia | no | libre |
| Censo 2005 IPUMS | 2005 | 10% | BPLCO2 | agrupaciones ≥20 mil | no | libre |
| GEIH migración | 2012- | ~700-800 mil | P756, P755, P753 | mun. nacimiento | no | libre |

## Veredicto
1. Cohortes seguibles con municipio de residencia en adolescencia: con certeza las que presentaron Saber 11 desde 2012-2 (nacidas ≈1995-2008) [V]; si las bases 2000-2012 traen residencia, hasta nacidas ≈1983 [NV].
2. "Residencia infantil" no existe en Saber 11 (residencia a los 16-18); municipio de infancia solo vía EEVV (sin ID), Saber 3-5-9 [NV] o SIMAT (convenio).
3. Cadena: Saber 11 → Saber Pro/TyT (llave pública) → SPADIES (trámite) → PILA/RIPS/RUV (solo vía base ICFES). **CNPV 2018 no identifica municipio de nacimiento** [V]; GEIH sí (sin ID).
4. Riesgos: duplicados; cambios de nombres de variables; BPLCO2 agrupado.
