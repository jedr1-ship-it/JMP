# T5: desplazamiento (RUV) y muestra "stayer"

Memo del RA (2026-10-24). Script `code/analysis/t5_ruv_stayers.py`; tablas `data/derived/t5_*.csv` (`t5_numeros_clave.json` resume); figura `scoping/proposal/fig6_desplazamiento_vs_dosis.pdf`. Dosis = víctimas PARA 1997-2006 del panel CNMH municipio × mes (67.974 con municipio válido; omite víctimas sin mes, 1,0 % menos que la dosis T1). T = 451 municipios (`47000` no es municipio); Belén de Bajirá se funde en Riosucio.

## 1. Datos

- **RUV (corte sep-2016)**: 5.694.661 personas-evento expulsadas en 1997-2010 (13,3 % de la población 2005; pico 2002); el 82,7 % sale de municipios T. Panel municipio × año en `t5_ruv_expulsion_muni_anio.csv`. Supuestos: el año es el del hecho; una persona desplazada dos veces cuenta dos; las declaraciones tardías siguen creciendo.
- **Población 2005**: obtenida. `pobl_tot` DANE (base Censo 2005; total 42.888.592 = cifra conciliada) vía Panel CEDE 2024, espejo `raw.githubusercontent.com/acastilloa2/RentistDemocracy` (README en `data/raw/poblacion/`); 1.122 municipios. No hizo falta el proxy de Saber 11.
- **Tasa acumulada 1997-2010 / población 2005**: mediana 8,9 % en los 1.122 municipios; **en T, 22,9 % (cuartiles 7,6-58,5 %)**, el 70,7 % de T supera el 10 % y el 10,6 % supera el 100 %; fuera de T, 4,6 %.

## 2. Correlación con la dosis (fig. 6a-b, `t5_correlaciones.csv`)

Tasa vs víctimas PARA: Spearman 0,50 en todos, **0,12 dentro de T** (Pearson −0,01): en niveles la dosis está en ciudades con tasas bajas (Medellín 2,7 %, Cúcuta 2,9 %). Tasa vs víctimas por 1.000 hab.: **0,63 (0,56 en T)**; en el cuartil alto de dosis per cápita de T la tasa mediana es 67,7 % y solo el 3,5 % es stayer. Las víctimas de guerrilla correlacionan igual (0,63): el desplazamiento responde a la violencia total.

## 3. Muestra stayer (fig. 6c, `t5_stayer_umbrales.csv`)

| Umbral | Municipios (T) | Población | Evaluados | Dosis PARA retenida | Dosis en T |
|---|---|---|---|---|---|
| < 5 % | 430 (87) | 66,2 % | 70,3 % | **28,4 %** | 28,0 % |
| < 10 % | 592 (132) | 73,2 % | 77,3 % | **37,0 %** | 35,8 % |
| < 20 % | 759 (212) | 82,4 % | 85,8 % | **52,0 %** | 50,9 % |
| < 30 % | 839 (255) | 87,0 % | 90,0 % | **60,0 %** | 58,9 % |

Retener el 30 % exige un umbral de 6,4 %; el 50 %, de 20,5 %. Variantes al 10 %: expulsión 1997-2006, 42,4 %; solo conflicto armado, 37,2 %; población retroproyectada 2018, 37,6 %; **sin Medellín, 31,3 %**. **Composición**: el 61 % de la dosis retenida está en municipios de ≥100 mil habitantes (39 % en los de ≥500 mil). En los 403 T con menos de 100 mil habitantes (59 % de la dosis) solo 97 son stayers y retienen el **19,3 %**; en los 48 T grandes, 63,8 %.

## 4. Mayor expulsión (`t5_top30_expulsion.csv`)

Los 30 municipios con más expulsados (27,7 % de las expulsiones, 28,1 % de la dosis) son todos T y solo Medellín es stayer: El Carmen de Bolívar 118.619 (175 % de su población; 392 víctimas PARA), Buenaventura 96.898 (30 %; 599), Riosucio 85.355 (302 %; 257), Santa Marta 81.990 (20 %; 1.132), Valledupar 79.693 (23 %; 1.202), Tierralta, Turbo, Tumaco (661), Medellín 60.621 (2,7 %; 5.666), Tibú 55.590 (160 %; 1.019); siguen Samaná, Apartadó (855), Fundación, San Onofre, Tame, Ciénaga (1.200), Puerto Asís, San Carlos (220 %; 481), Dabeiba.

## Veredicto

**APROBADO**: la muestra stayer (< 10 %) retiene el **37,0 %** de la dosis (umbral ≥ 30 %; letal < 15 %), 35,8 % de la dosis de T y 77 % de los evaluados; al 5 % cae a 28,4 % y al 20-30 % sube a 52-60 %. **Advertencia decisiva**: la aprobación descansa en las ciudades grandes (sin Medellín, 31,3 %); los municipios pequeños con salida escalonada, que son la variación de calendario del diseño de celdas (T2), tienen desplazamiento masivo y retienen un quinto de su dosis. P2 es acotable con stayers y cotas de Lee para el perfil en niveles, no para el diseño de celdas rurales, que sigue dependiendo del enlace ICFES-UARIV (T8). Pendientes: tratar la expulsión como variable continua (cotas por tramos), usar también los recibidos (Medellín 315 mil, Santa Marta 184 mil: la muestra stayer incluye receptores masivos) y actualizar el RUV cuando datos.gov.co sea accesible.
