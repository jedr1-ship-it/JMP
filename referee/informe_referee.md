# Informe de referee: "Mercado del alquiler e inmigración en España: evidencia sobre los precios de los nuevos contratos (2015-2024)"

Los 60 comentarios detallados están anclados al texto como comentarios de Word en `WORKING_PAPER_referee_comments.docx`. Este informe resume la valoración global y ordena los problemas por gravedad.

## Valoración global

La pregunta es relevante, los datos (SERPAVI + Padrón/Censo) son los adecuados y el diseño shift-share es el estándar de la literatura. Sin embargo, en su estado actual el trabajo no sostiene sus tres resultados principales (efecto del 2,1% sobre nuevos contratos, dualidad insider/outsider, regresividad), por cuatro motivos que se refuerzan entre sí:

1. La desagregación de precios genera resultados en gran parte mecánicos.
2. La inferencia ignora que el instrumento es débil (KP-F = 11,4).
3. La heterogeneidad P25/P75 no se contrasta estadísticamente.
4. La exogeneidad del instrumento se defiende verbalmente, sin ningún test.

Recomendación: revisión mayor. El trabajo es recuperable, pero exige rehacer la sección de validación y reescribir las conclusiones con un tono mucho más contenido.

## Problemas mayores

### 1. La desagregación P_new / P_old es mecánica en 2015-2020

Por las ecuaciones (14)-(15), `Δln P_new ≈ (1/α)·Δln P_stock − ((1−α)/α)·Δln P_old`. En 2015-2020 P_old se construye como `P_stock(t−1)·(1+g_t)` con g fijado por el IPC nacional y una ratio provincial constante. Consecuencias:

- P_old no puede responder a m_t por construcción en 6 de los 9 años. El "no efecto sobre contratos antiguos" es un artefacto de la calibración, no un hallazgo.
- β(P_new) ≈ β(P_total)/α por construcción. Con los números de la Tabla 2 se obtiene α ≈ 0,10. El resultado sobre nuevos contratos no es evidencia independiente del resultado sobre el stock.
- Cualquier error de medida en P_stock se amplifica por 1/α, lo que explica que la desviación típica de Δln P_new sea 5,5 veces la de Δln P_total (Tabla 1).

Qué hacer: (a) estimar con el P_new y P_old observados del IPVA en 2021-2024 y presentarlo como tabla completa, no como inciso; (b) validar P_new reconstruido contra precios de oferta (Idealista/Fotocasa) provincia a provincia; (c) reportar α y g por provincia y añadir robustez a α.

### 2. La ratio g/IPC de 2021-2024 está contaminada por los topes legales

En 2022-2024 la actualización de rentas estuvo topada por ley (2% y 3%) con IPC del 8,4% y 3,5%. La ratio observada refleja el tope, no la "tensión del mercado", y se extrapola a 2015-2020, cuando no había tope. La especificación "legal" (ratio = 1, Tabla 5) es la más defendible para 2015-2020, y ahí β₁ cae a 1,94 y pierde la significatividad al 5%.

### 3. Instrumento débil e inferencia

KP-F = 11,44 con un solo instrumento y errores cluster. El umbral de 10 de Staiger-Stock no aplica con SE robustos. Con el procedimiento tF (Lee et al., 2022) el valor crítico al 5% para F ≈ 11 ronda 2,9:

| Variable dependiente | β₁ | SE | t | ¿Significativo al 5% con tF? |
|---|---|---|---|---|
| P_new | 2,28 | 1,10 | 2,08 | No |
| P_total | 0,64 | 0,23 | 2,76 | No |

Reportar intervalos de Anderson-Rubin y el F efectivo de Montiel Olea y Pflueger. El argumento "MCO < 2SLS, luego el 2SLS es cota inferior" es lógicamente incorrecto.

### 4. Regresividad no contrastada

β(P25) = 2,20 (SE 1,22) y β(P75) = 0,55 (SE 1,59). La diferencia tiene SE ≈ 2,0 y t ≈ 0,8. Un coeficiente significativo al 10% y otro no significativo no demuestran que difieran. Hacer el test (estimación apilada o SUR). Tal como está, la sección 5.2 y la tercera conclusión no tienen soporte.

### 5. Exogeneidad sin contrastes

Faltan: placebo de pre-tendencias (Bartik acumulado 2016-2024 sobre crecimiento de precios 2008-2014), tabla de balance del instrumento frente a características de 2015, pesos de Rotemberg (GPSS 2020), robustez a shares de 1991/2011 y a excluir Madrid y Barcelona, instrumento rezagado (Jaeger, Ruist y Stuhler, 2018), SE de Adão, Kolesár y Morales (2019).

### 6. Convención temporal inconsistente

m_t es el flujo del año natural t−1. Construcción_{t−1} y apartamentos turísticos_{t−1} son también flujos del año natural t−1, luego son contemporáneos a las llegadas, no rezagados. El retardo no logra lo que el texto afirma. Además, el salto del coeficiente a 4,06 al excluir 2020 (llegadas de 2019 frente a precios de 2020) es en parte consecuencia de esta datación. Estimar también con alineación contemporánea y con estructura de retardos.

### 7. Efectos fijos en un modelo en diferencias

Con la ecuación en primeras diferencias, γ_i equivale a tendencias lineales provinciales y Z×t a tendencias cuadráticas. Con 9 periodos, la identificación procede solo de desviaciones de m respecto a su media provincial. Describirlo correctamente y mostrar la especificación sin γ_i y en diferencias largas.

### 8. Regulación catalana 2020-2022 omitida

La Llei 11/2020 (sept-2020 a marzo-2022) afectó a cuatro provincias de alta exposición al instrumento. No se menciona. Puede explicar que Barcelona aparezca con una subida de P_new (61,7%) inferior a Guadalajara, Toledo, Segovia o Castellón y por debajo de la media nacional, un resultado que por sí solo pide validación externa de P_new.

## Problemas menores

- Inflación acumulada 2015-2024: el 16% citado parece bajo; con los IPC medios anuales sale cerca del 24%.
- "KP-F (exclusión)" en todas las tablas: el F contrasta relevancia, no exclusión.
- Tablas 3a/3b mezclan unidades (porcentaje exponenciado frente a cociente de puntos logarítmicos). Faltan intervalos de confianza para la proporción explicada: con SE(β₂) ≈ 1,03, el IC al 95% de la cifra nacional va aproximadamente del 1% al 43%.
- Los SE de β₂ se obtienen tratando β₅ como fijo; usar método delta o bootstrap por cluster y no asignar estrellas hasta entonces. Reportar β₃ y β₅ con sus SE.
- El canal "vegetativo" incluye nacimientos de madres inmigrantes (>33% de los nacimientos), luego no aísla lo que dice aislar.
- El párrafo sobre "simetría oferta-demanda" se apoya en un coeficiente no significativo (SE 1,61) que cambia de signo entre P25 y P75. Suprimirlo.
- La recomendación sobre vivienda vacía descansa en un coeficiente de Z×tendencia significativo al 10% y de interpretación dudosa.
- "Pionero", "original", "aportación más original": rebajar el tono en resumen y conclusiones.
- Faltan referencias: Card (2001); Altonji y Card (1991); Goldsmith-Pinkham, Sorkin y Swift (2020); Adão, Kolesár y Morales (2019); Jaeger, Ruist y Stuhler (2018); Montiel Olea y Pflueger (2013); Lee, McCrary, Moreira y Porter (2022); Jofre-Monseny, Martínez-Mazza y Segú (2023); Monràs y Montalvo (2023).
- Describir SERPAVI con precisión (qué mide, cobertura, censura en provincias pequeñas) y cómo se obtienen niveles a partir del índice IPVA.
- Listar los países de origen del instrumento y el tratamiento de orígenes con pocos efectivos en 2001.
- La fila "Constante" de la Tabla 4 no tiene sentido con efectos fijos; eliminar o explicar.
- Unificar "Figura" y "Gráfico", separador decimal y formato de p-valores.
- El "pico anual superior al 4% en Valencia, Alicante o Madrid en 2024" de las conclusiones no aparece en ninguna tabla.

## Análisis adicionales que pediría para una segunda versión

1. Tabla con MCO, forma reducida y 2SLS para cada variable dependiente, con intervalos AR.
2. Tabla completa para 2021-2024 con P_new, P_old y P_total observados del IPVA.
3. Validación de P_new reconstruido contra precios de oferta.
4. Figura leave-one-year-out (9 estimaciones con sus KP-F).
5. Pesos de Rotemberg y tabla de balance del instrumento.
6. Placebo de pre-tendencias.
7. Test formal de β(P25) = β(P75).
8. Robustez a α, a shares de 1991/2011 y a excluir Madrid y Barcelona.
9. Dummy para Cataluña 2020-2022 además de 2024.
