# Población municipal DANE (vía Panel Municipal CEDE, Universidad de los Andes)

## Archivo
- `PANEL_CARACTERISTICAS_GENERALES_2024.dta` (26,5 MB, Stata 14/118, 34.777 filas = 1.122 municipios × 1993-2023, 76 variables).
- sha256: `76a6c25c9bd2a242df5cbf9ada75f407e74aed8620008ad748d4f7bf2c07a022`.

## Procedencia
- Origen primario: Panel Municipal del CEDE (Universidad de los Andes), módulo "Características generales", versión 2024
  (archivo original `PANEL_CARACTERISTICAS_GENERALES(2024).dta`, sello de tiempo interno 27-ene-2025). El CEDE compila las
  variables `pobl_tot`, `pobl_rur`, `pobl_urb` a partir de las proyecciones municipales del DANE (serie base Censo 2005 para
  1993-2017; el total nacional 2005 del archivo, 42.888.592, es la cifra conciliada del Censo General 2005) y
  `retro_pobl_tot/rur/urb` a partir de las retroproyecciones DANE con base en el Censo 2018.
- Espejo público desde el que se descargó (los portales oficiales dane.gov.co / datoscede.uniandes.edu.co no son
  accesibles desde el entorno de sesión; la regla del PI permite descargar solo desde raw.githubusercontent.com):
  `https://raw.githubusercontent.com/acastilloa2/RentistDemocracy/main/Data/PANEL_CARACTERISTICAS_GENERALES%282024%29.dta`
  (repositorio público `acastilloa2/RentistDemocracy`, carpeta `Data/`, rama `main`). Descargado el 2026-10-24 con curl,
  HTTP 200, 26.520.345 bytes.
- Localización vía búsqueda de código en GitHub (`PANEL_CARACTERISTICAS_GENERALES`), tras 3 búsquedas web sin resultado para
  CSV de proyecciones DANE 2005 en GitHub.

## Uso en el proyecto
- `code/analysis/t5_ruv_stayers.py` lee solo `codmpio, coddepto, ano, pobl_tot, retro_pobl_tot, municipio, depto` y usa
  `pobl_tot` en `ano == 2005` como denominador (población 2005, Censo General 2005 conciliado); `retro_pobl_tot` 2005 como
  comprobación.
- Advertencias: (i) archivo descargado de un repositorio de terceros, tratado como dato no confiable (leído con pandas en
  `python3 -I`, nunca ejecutado); (ii) la versión 2024 del CEDE puede diferir en decenas de municipios de la publicación DANE
  original por ajustes de códigos (municipios creados después de 2005 reciben población desde su creación o imputada por
  el CEDE); (iii) para una versión citable del denominador conviene re-descargar `ProyeccionMunicipios2005_2020.xls`
  desde dane.gov.co cuando el acceso esté disponible y verificar los totales.
