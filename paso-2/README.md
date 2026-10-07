# Paso 2: Análisis de la Fuente de Datos — Guía del Entregable

Este directorio contiene los archivos correspondientes a la **Consigna 2: Paso 2 — Análisis de la Fuente de Datos** de la Metodología HEFESTO v2.

---

## 1. Objetivo Metodológico del Paso 2

En este paso se confrontan los requerimientos teóricos definidos en el Paso 1 contra el archivo de datos real:
1. **Perfil del archivo:** Inspeccionar todas las columnas del dataset, describiendo su significado conceptual y su tipo de dato aparente (texto, entero, decimal, fecha, categoría).
2. **a) Conformar indicadores:** Definir formalmente para cada indicador del Paso 1 las columnas reales que lo componen, su fórmula de cálculo exacta y la función de agregación (`SUM`, `AVG`, `STDDEV`, `COUNT`).
3. **b) Establecer correspondencias:** Construir una matriz de correspondencias que mapee cada perspectiva e indicador conceptual con la columna real del archivo y las transformaciones necesarias.
4. **c) Nivel de granularidad y consistencia:**
   * Definir el grano atómico para cada dimensión (por ejemplo, grano diario para Tiempo).
   * Auditar la calidad y consistencia de los datos textuales (espacios sobrantes, variantes ortográficas de nombres de clubes, valores faltantes o fuera de rango).
5. **d) Modelo Conceptual Ampliado:** Replicar el diagrama conceptual del Paso 1 incorporando debajo de cada perspectiva las columnas elegidas del archivo y debajo de cada indicador su fórmula matemática.

---

## 2. Inventario y Función de Archivos

| Archivo | Tipo | Descripción y Función |
| :--- | :--- | :--- |
| **`entrega_fuente_datos.md`** | **Documento Principal de Entrega** | Informe completo del Paso 2 con el perfil de columnas de `Matches.csv` (48 columnas reales) y `EloRatings.csv`, la justificación de alcance, las fórmulas de indicadores, correspondencias, auditoría de consistencia y el diagrama conceptual ampliado en Mermaid (`graph LR`). |
| **`fuente.md`** | **Documento de Metadatos y Enlaces** | Especifica los links oficiales de descarga en Kaggle y GitHub, el peso aproximado de los archivos, la fecha de descarga y aclara el rol de `Matches.csv` como fuente principal y `EloRatings.csv` como fuente de control. |
| **`verificacion_nombres_equipos.py`** | **Script de Auditoría de Consistencia** | Programa en Python puro que compara los nombres únicos de equipos entre `Matches.csv` y `EloRatings.csv`. Calcula el porcentaje de coincidencia exacta (95,4% en el alcance de 15 ligas) y desglosa las discrepancias por espacios finales o diferencias de escritura. |
| **`README.md`** | **Guía Explicativa Interna** | Este archivo: explica el objetivo metodológico del paso, el contenido de cada archivo y los puntos clave para la defensa. |

---

## 3. Aspectos Clave a Defender ante el Profesor

### A. ¿Qué pasó con `EloRatings.csv` y qué uso se le dio?
* **En el diseño preliminar:** Se pensó que `EloRatings.csv` aportaría el catálogo maestro de clubes, el país y el puntaje Elo.
* **Al auditar los datos reales con `verificacion_nombres_equipos.py`:**
  1. `Matches.csv` ya contiene las columnas `HomeElo` y `AwayElo` en cada fila de partido (calculadas el día del encuentro).
  2. `Matches.csv` contiene el código de liga `Division`, que se traduce de forma unívoca al 100% de los países (`ENG`, `ESP`, etc.).
  3. `EloRatings.csv` solo tiene 984 clubes, no contempla ligas americanas ni asiáticas, y presenta 27 diferencias incluso en las 15 ligas europeas (11 por espacios finales `'Ajax '` y 16 por diferencias ortográficas).
* **Conclusión de ingeniería:** `EloRatings.csv` se utilizó exclusivamente en el Paso 2 como **fuente de control y cotejo** para validar la consistencia de los nombres. **No se carga físicamente en el DW ni en MySQL** porque `Matches.csv` es autosuficiente y previene pérdida innecesaria de registros.

### B. Corrección del Perfil de Datos (48 columnas reales)
* En borradores previos figuraban 26 columnas extra (`GF3Home` a `RestDaysAway`). Se verificó sobre el archivo real que `Matches.csv` termina en la columna 48 (`C_PHB`). Se depuraron esas columnas inexistentes para que el perfil refleje fielmente la realidad del archivo.

### C. Tratamiento de Valores Nulos en Tarjetas
* En el 35 % de los partidos no hay datos de tarjetas. **No se imputa 0**, sino que se mantiene `NULL`. Imputar 0 distorsionaría artificialmente a la baja el promedio de tarjetas de los equipos.

---

## 4. Cómo ejecutar el script de verificación

```powershell
# Ejecutar verificación de consistencia sobre las 15 ligas del alcance
python verificacion_nombres_equipos.py ..\paso-4\datos\Matches.csv ruta\a\EloRatings.csv

# Para auditar sobre las 38 ligas completas del dataset
python verificacion_nombres_equipos.py ..\paso-4\datos\Matches.csv ruta\a\EloRatings.csv --todas
```
