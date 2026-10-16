# Verificación: ELCA (Encuesta Longitudinal Colombiana, Uniandes)

Advertencia: el proxy bloqueó todas las conexiones directas; todo procede de fragmentos de búsqueda (documentos *Colombia en movimiento* 2011/2014/2017/2019, Ficha Técnica, Boletines ELCA, Guías de usuario, catálogo ANDA del DANE, Atlas of Longitudinal Datasets). [V] visto en fragmento; [NV] no verificado.

## 1. Rondas, cuarta ronda y atrición
- Rondas: línea base 2010; seguimientos 2013 y 2016 [V]. Bases de 2016 publicadas en noviembre 2017 [V].
- Cuarta ronda: la ronda 2019 no se levantó como ELCA. Desde 2019 ELCA se fusionó con la ELPS del DANE en la **ELCO (Encuesta Longitudinal de Colombia)**, rondas 2019 y 2022, a cargo del DANE [V]. ELCO 2019 en ANDA (catálogo 814) [V]. DANE publicó en marzo 2026 una guía para integrar rondas ELCO-ELCA con identificadores [V]; el refollow efectivo y si se mantuvo el módulo infantil: [NV].
- Atrición de hogares: 2010: 10.164 hogares (5.446 urb., 4.718 rur.) [V]; 2013: 9.262 (94,2%) [V]; 2016: 8.818 (89,5%; 96,6% rural, 83,3% urbano) [V]. 31% cambió de municipio entre 2010 y 2016 [V].
- Atrición del panel infantil: el panel de niños con información completa en las tres rondas es el 48,7% de los 8.693 niños originales y "no es representativo de ninguna población" [V].

## 2. Muestra y geografía
- Diseño: 1.200 hogares por cada una de 5 regiones urbanas (estratos 1-4) y por cada una de 4 microrregiones rurales (pequeños productores) [V]. 2010: 48 municipios urbanos + 17 rurales [V]; 2016: ~290 municipios por migración [V].
- Microrregiones rurales: **Atlántica Media, Cundiboyacense, Eje Cafetero, Centro-Oriente**, elegidas "según crecimiento económico, producción, pobreza y condiciones de violencia" [V]. Departamentos y municipios de cada una: [NV]. Atlántica Media es plausiblemente Caribe interior (zona AUC), inferencia. No hay microrregión en Catatumbo, Urabá, Meta ni Magdalena Medio.
- Ciudades urbanas: lista [NV]; aparece Montería [V].

## 3. Niños e instrumentos
- Elegibles: menores de 10 años en 2010 (nacidos ~2000-2010), N = 8.693 [V]. Nacidos 1996-1999 solo en roster, sin pruebas.
- Instrumentos: TVIP/PPVT (3-9), ASQ-SE y SDQ, talla y peso [V]. Rondas exactas y si SDQ es de padres: [NV]. 2016: módulo "Jóvenes 10-16" [V], contenido [NV]. Raven, Woodcock-Johnson, Big Five: no hallados.
- Salud mental adultos: el Atlas lista "mental health" [V]; instrumento y ronda [NV].
- Choques: módulo de choques violentos y respuestas del hogar en todas las rondas; en rural, presencia histórica de grupos armados [V]. Historia de desplazamiento con año y municipio, lugar y fecha de nacimiento por miembro: [NV].

## 4. Geografía en microdatos
Bases públicas en Stata por registro en Datos CEDE [V]. Código de municipio o solo región: [NV]. Historial municipio-año: solo municipio por ronda [inferencia].

## 5. Vinculación administrativa
Sin indicio de vínculo con Saber 11/SPADIES/Sisbén/RUV [NV, probablemente no]. Existe un proyecto ICFES-Uniandes (Saber 11 2000-2019 + SNIES, SPADIES, UARIV, RIPS, PILA; 8,25 M estudiantes) [V], sin ELCA.

## 6. Acceso
Registro en datoscede.uniandes.edu.co; módulos de tierras restringidos [V]. ELCO: ANDA o SPEE del DANE [V].

## 7. Trabajos previos
Arias & Ibáñez (CEDE 2012-44) [V]; ponencia IAES ELCA 2010-2013 sobre conflicto y educación [V]; boletín ELCA sobre choques violentos tempranos y desarrollo cognitivo [V]. Moya en el comité científico [V]; sus papers de conflicto y salud mental infantil usan encuestas propias [NV].

## 8. Veredicto: 4/10
1. Cohortes: módulo infantil cubre nacidos 2000-2010; solo los nacidos 2000-2003 (~3.500) tienen exposición in utero/0-2 a la ola de masacres.
2. N realista: ~25-30% en zonas AUC → ~900-1.000; con retención del 49% → **~450-550 niños** con outcomes en 2016 (13-16 años) [estimación].
3. Killers: municipio de residencia 1997-2006 solo si hay módulo retrospectivo [NV]; código municipal en bases públicas [NV]; muestra rural purposiva elegida en parte por violencia; sin instrumento de salud mental adulta identificado; outcomes posteriores a 2016 dependen de ELCO-DANE; atrición del panel infantil >50%.

Uso sensato: validación de mecanismos (SDQ/TVIP a 3-15 años) o complemento, no base del JMP.

| Variable | 2010 | 2013 | 2016 | ELCO 2019/2022 |
|---|---|---|---|---|
| Hogares | 10.164 [V] | 9.262 [V] | 8.818 [V] | [NV] |
| Niños con módulo | 8.693, 0-9 [V] | seguimiento [V] | 6-15 + Jóvenes 10-16 [V] | [NV] |
| TVIP/PPVT | [V] | probable | [NV] | [NV] |
| ASQ-SE | [V] | [NV] | — | — |
| SDQ (padres) | [V] | probable | probable | [NV] |
| Antropometría | [V] | [V] | [V] | [NV] |
| Salud mental adultos | [NV] | [NV] | listado, instrumento [NV] | [NV] |
| Choques violentos | [V] | [V] | [V] | [NV] |
| Desplazamiento (año, origen) | [NV] | [NV] | [NV] | [NV] |
| Municipio en microdatos | [NV] | [NV] | [NV] | ANDA anonimizado; SPEE |
| Vínculo administrativo | no | no | no | no [NV] |
