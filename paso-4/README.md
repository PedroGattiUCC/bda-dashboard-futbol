# Paso 4: Integración de Datos (ETL) — Guía del Entregable

Este directorio contiene los archivos correspondientes a la **Consigna 4: Paso 4 — Integración de Datos** de la Metodología HEFESTO v2.

---

## 1. Objetivo Metodológico del Paso 4

El hito de Integración de Datos (ETL) materializa la carga física del Data Warehouse a partir de los datos crudos del archivo:
1. **Área Intermedia (Staging Area):** Volcar los datos crudos en una zona intermedia dentro de la base de datos para inspección, aseguramiento de calidad y trazabilidad.
2. **Chequeos de Calidad de Datos:** Identificar inconsistencias, valores nulos, registros fuera de rango o variantes ortográficas sobre el 100% del archivo fuente y registrar las decisiones de limpieza.
3. **Población de Dimensiones:** Cargar los valores únicos de cada perspectiva generando sus claves subrogadas autoincrementales.
4. **Población de Hechos:** Mapear cada partido a sus correspondientes claves foráneas en las dimensiones e insertar las métricas y banderas calculadas en `FACT_COMPETENCIA`.
5. **Verificación de la Carga:** Demostrar con evidencia matemática que no hubo pérdida ni duplicación de registros mediante balance de filas (diferencia 0) y comparación de métricas agregadas contra el CSV original.
6. **Políticas de Actualización:** Diseñar la estrategia de refresco periódico del Data Warehouse (cargas iniciales, incrementales y ventanas de reproceso).

> **Aclaración importante:** En estricto apego a la consigna oficial, esta carpeta contiene **exclusivamente el proceso ETL**. El tablero analítico y las respuestas a las 12 preguntas de negocio se presentan de forma independiente en la carpeta `../entrega-final/`.

---

## 2. Inventario y Función de Archivos

| Archivo / Carpeta | Tipo | Descripción y Función |
| :--- | :--- | :--- |
| **`entrega_informe.md`** | **Documento Principal de Entrega** | Informe técnico exigido por la cátedra: describe la arquitectura del staging en memoria, los 15 chequeos de calidad, el balance de carga, la verificación contra el CSV y la política de actualización. |
| **`01_carga_dw.ipynb`** | **Notebook ETL Oficial (Python + Jupyter)** | Implementación oficial en Jupyter Lab recomendada por la cátedra (`Teorico 16_09.docx`). Ejecuta extracción masiva, auditoría de calidad, limpieza con pandas, creación de tablas y persistencia en MySQL. |
| **`EXPLICACION_ETL_PYTHON.md`** | **Guía Pedagógica del Notebook** | Explicación detallada orientada a quienes no dominan Python o pandas, explicando cada celda y su lógica análoga a SQL/C++. |
| **`requirements.txt`** | **Dependencias de Software** | Lista de librerías Python necesarias para ejecutar el proceso ETL (`mysql-connector-python`, `pandas`, `sqlalchemy`, `jupyterlab`). |
| **`datos/Matches.csv`** | **Dataset Fuente** | Archivo CSV real de partidos (~45 MB, 48 columnas reales, 238.858 registros históricos). |
| **`mapeos/`** | **Tablas de Homologación** | Tablas maestras auxiliares en CSV:<br>• `mapeo_divisiones.csv`: Códigos de liga $\rightarrow$ nombre oficial y país.<br>• `mapeo_equipos.csv`: Variantes temporales de nombres de clubes $\rightarrow$ nombre canónico unificado. |
| **`README.md`** | **Guía Explicativa Interna** | Este archivo: mapa del paso y guía de ejecución. |

---

## 3. Instrucciones de Ejecución del ETL (Python + Jupyter)

El proceso de integración de datos se ejecuta de forma interactiva y trazable a través del cuaderno Jupyter:

1. **Instalar dependencias necesarias:**
   ```powershell
   pip install -r requirements.txt
   ```
2. **Iniciar el entorno Jupyter:**
   ```powershell
   jupyter lab
   ```
   *(También puede abrirse directamente con Visual Studio Code seleccionando el intérprete de Python como kernel).*

3. **Ejecutar el cuaderno:**
   * Abrir `01_carga_dw.ipynb`.
   * Ejecutar las celdas secuencialmente o presionar **Run → Run All Cells**.
   * Al llegar al bloque de persistencia en MySQL, ingresar la contraseña del usuario `root` de forma interactiva (o definir previamente `$env:MYSQL_PASSWORD = "..."` en la terminal).
   * El proceso tomará ~60 segundos, dejando la base `dw_competencia_futbol` completamente cargada y validada contra el CSV original.

---

## 4. Resultados de Verificación y Balance

* **Partidos analizados en el archivo crudo:** 238.858 filas.
* **Descartes documentados:** 106.602 filas (106.601 por corresponder a ligas fuera del alcance de las 15 seleccionadas y 1 partido sin resultado).
* **Partidos limpios cargados en `FACT_COMPETENCIA`:** 132.256 filas.
* **Balance de filas:** $238.858 - 106.602 - 132.256 = \mathbf{0}$ (Cero pérdida de datos).
* **Total de goles agregados:** 348.954 (Idéntico entre CSV y Data Warehouse).
* **Total de tarjetas rojas:** 18.356 (Idéntico entre CSV y Data Warehouse).
