# Resumen de correcciones, Paso 4 y Entrega Final — para el grupo

Este documento explica todo lo que se revisó, corrigió y estructuró en el proyecto, aclara las decisiones metodológicas clave (incluyendo qué pasó con `EloRatings.csv`) y detalla la **separación estricta entre el Paso 4 (Integración de Datos / ETL) y la Entrega Final (Dashboard sobre el modelo estrella)**.

Todo el proyecto actualizado y depurado se encuentra organizado en la raíz del repositorio. Asimismo, **el Paso 4 se consolidó exclusivamente en Python**, eliminando la versión en scripts SQL puros (`cargar_dw.py` y carpeta `sql/`).

```text
PROYECTO BDA/
├── RESUMEN_PARA_EL_GRUPO.md          <- este archivo (hoja de ruta integral)
├── paso-1/                           <- PASO 1: Requerimientos
│   ├── README.md                     <- guía explicativa del paso y sus requerimientos
│   └── entrega_requerimientos.md
├── paso-2/                           <- PASO 2: Análisis de la Fuente de Datos
│   ├── README.md                     <- guía explicativa del paso, perfiles y scripts
│   ├── entrega_fuente_datos.md       <- corregido (48 columnas reales, sin columnas fantasma)
│   ├── fuente.md                     <- links de descarga y especificación de archivos
│   └── verificacion_nombres_equipos.py
├── paso-3/                           <- PASO 3: Modelo Lógico del DW
│   ├── README.md                     <- guía explicativa del modelo estrella y DDL
│   ├── entrega_modelo_logico.md
│   └── entrega_modelo_logico.sql     <- DDL ejecutable en MySQL 8.0
├── paso-4/                           <- PASO 4: Integración de Datos (ETL oficial en Python)
│   ├── README.md                     <- guía explicativa del proceso ETL y ejecución
│   ├── entrega_informe.md            <- informe técnico de calidad, carga y actualización
│   ├── 01_carga_dw.ipynb             <- notebook ETL oficial (pandas + SQLAlchemy + MySQL)
│   ├── EXPLICACION_ETL_PYTHON.md     <- guía pedagógica del ETL para el equipo
│   ├── requirements.txt              <- dependencias de ETL (pandas, sqlalchemy, mysql-connector, jupyterlab)
│   ├── datos/
│   │   └── Matches.csv               <- archivo real de partidos (48 columnas, ~45 MB)
│   └── mapeos/
│       ├── mapeo_divisiones.csv      <- las 15 divisiones del alcance -> liga y país
│       └── mapeo_equipos.csv         <- unificación de variantes de nombres de clubes
└── entrega-final/                    <- ENTREGA FINAL: Dashboard sobre el modelo estrella
    ├── README.md                     <- guía explicativa del tablero y respuestas clave
    ├── dashboard.md                  <- documento formal con las 6 preguntas, SQL, tablas y gráficos
    ├── dashboard.ipynb               <- notebook interactivo del dashboard para clase
    ├── generar_dashboard.py          <- script generador autónomo de tablas y gráficos desde MySQL
    ├── requirements.txt              <- dependencias de visualización (matplotlib, etc.)
    ├── sql/
    │   └── 07_vista_dashboard.sql    <- DDL de la vista analítica V_PARTICIPACION
    ├── graficos/                     <- las imágenes pregunta_01.png a pregunta_06.png
    └── dashboard-dinamico/           <- tablero web dinámico para exposición (Streamlit + Render/Clever Cloud)
```

---

## 1. Separación Estricta de Entregables: Paso 4 vs. Entrega Final

La guía del TP (`guia-tp-hefesto.md`) define claramente dos hitos independientes que no deben mezclarse:

### A) Paso 4 — Integración de Datos (ETL)
* **Objetivo:** Poblar el modelo lógico de Paso 3 con los datos reales del archivo y documentar la calidad y actualización.
* **Carpeta:** `paso-4/`.
* **Entregables obligatorios:**
  1. Notebook oficial de carga ETL ejecutado: `01_carga_dw.ipynb` (desarrollado en Python con pandas y MySQL, según lo solicitado por el docente).
  2. `entrega_informe.md`: informe formal con resultados de calidad de datos, verificación del balance de filas (diferencia 0) y comparación de totales agregados contra el archivo CSV, más las políticas de actualización (inicial vs. incremental).
  * **Cero archivos de dashboard ni gráficos en esta carpeta.**

### B) Entrega Final — Dashboard sobre el modelo estrella
* **Objetivo:** Construir un tablero que responda a las 6 preguntas de negocio seleccionadas planteadas en el Paso 1 con consultas SQL sobre el Data Mart (no sobre el archivo crudo).
* **Carpeta:** `entrega-final/`.
* **Entregables obligatorios:**
  1. `dashboard.md`: cada una de las 6 preguntas con su consulta SQL, su tabla de resultados reales y su gráfico correspondiente.
  2. Recursos del tablero: `dashboard.ipynb` (notebook interactivo acotado a las 6 preguntas), `generar_dashboard.py`, `sql/07_vista_dashboard.sql` y las 6 imágenes en `graficos/`.
  * **Cero scripts de carga ni staging en esta carpeta.**

---

## 2. Qué pasó con el archivo `EloRatings.csv` y cómo explicarlo

Este es un punto fundamental que el profesor puede consultar en la defensa:

### 1. ¿Por qué existen dos archivos en la fuente?
El dataset de Kaggle contiene `Matches.csv` (partidos individuales) y `EloRatings.csv` (ranking histórico de clubes por fecha y país).

### 2. ¿Qué se creía al principio?
En el borrador inicial se supuso que `EloRatings.csv` se utilizaría como catálogo maestro para obtener el nombre canónico de los equipos (`Club`), el país (`Country`) y las clasificaciones Elo.

### 3. ¿Qué descubrimos al auditar los datos reales? (Pedido de corrección P2)
Al ejecutar el script de auditoría `verificacion_nombres_equipos.py` cotejando ambos archivos, se demostró que:
* **`Matches.csv` ya trae el Elo atómico:** Cada partido ya registra `HomeElo` y `AwayElo` correspondientes al día del encuentro.
* **`Matches.csv` ya trae el país:** El campo `Division` (código de liga: `E0`, `SP1`, etc.) se mapea determinísticamente al 100 % de los países. En cambio, `EloRatings.csv` solo tiene país para los clubes que figuran en él.
* **Inconsistencias y omisiones en `EloRatings.csv`:**
  * En el dataset completo (38 ligas), solo el **63,7 %** de los equipos de `Matches.csv` coinciden con `EloRatings.csv` (no incluye ligas de América ni Asia, ni ligas de ascenso).
  * Dentro de las 15 ligas del alcance, de 592 clubes únicos, 27 no coinciden directamente (11 por espacios finales `'Ajax '`, y 16 por diferencias de escritura o ausencia total, como `'Ankaragucu'` vs `'Ankaraguecue'`).

### 4. ¿Cuál fue su uso real en el proyecto?
* **En el Paso 2 (Análisis de Fuentes):** Se utilizó como **fuente auxiliar de control y cotejo de calidad**. Gracias a él se detectaron los espacios sobrantes que requerían `TRIM` y los cambios ortográficos de clubes a lo largo de las temporadas (resueltos con `mapeo_equipos.csv`).
* **En el Paso 3 y Paso 4 (DW y Carga):** **NO se cargó en MySQL ni se utilizó en el ETL.** Intentar unir partidos con `EloRatings.csv` por fecha y nombre hubiera provocado pérdidas de datos, nulos artificiales y una sobrecarga técnica innecesaria, dado que `Matches.csv` ya contiene toda la información de forma íntegra y consistente.

---

## 3. Decisiones clave que cambian y ordenan el trabajo

### a) Lo que se estudia es la **competencia entre equipos**, no el "rendimiento"
Se unificó en todos los documentos y scripts:
* Proceso de negocio central: **COMPETENCIA ENTRE EQUIPOS**.
* Tabla de hechos: `FACT_RENDIMIENTO` → **`FACT_COMPETENCIA`**.
* Base de datos: `dw_rendimiento_futbol` → **`dw_competencia_futbol`**.
* Indicador: **"% de victorias en enfrentamientos directos"**.

### b) Alcance acotado a **15 ligas europeas** (10 países)
El archivo contiene 38 ligas, pero no son comparables:
* Las de América y Asia (Argentina, Brasil, MLS, México, China, Japón) juegan por año calendario y no tienen Elo.
* Ligas europeas menores (Escandinavia, Irlanda, etc.) solo abarcan de 2012 a 2024 y tienen Elo parcial.
* Divisiones de ascenso inglesas y escocesas carecen de Elo en hasta el 96 % de sus partidos.
* **Alcance final:** 15 ligas de 10 países (Inglaterra E0/E1, España SP1/SP2, Italia I1/I2, Alemania D1/D2, Francia F1/F2, Países Bajos N1, Portugal P1, Bélgica B1, Turquía T1, Escocia SC0). Son **132.257 partidos** comparables de 2000 a 2026.

### c) Depuración del perfil del Paso 2 (48 columnas reales)
* Se eliminaron del documento `entrega_fuente_datos.md` las 26 columnas que figuraban en borradores previos (`GF3Home` a `RestDaysAway`).
* **Se comprobó físicamente:** el archivo real `Matches.csv` provisto en el proyecto tiene **48 columnas**, finalizando en `C_PHB`.
* El diagrama conceptual ampliado se normalizó a `graph LR` para mantener total simetría visual y metodológica con el Paso 1.

---

## 4. Estado de los 4 Pasos de Hefesto v2

| Paso | Estado | Aspectos destacados |
| :--- | :--- | :--- |
| **Paso 1: Requerimientos** | **Aprobado** | 12 preguntas de negocio numeradas; indicadores conceptuales sin fórmulas prematuras; proceso central `COMPETENCIA ENTRE EQUIPOS`; diagrama `graph LR`. |
| **Paso 2: Análisis de Fuentes** | **Aprobado** | Perfil fiel de 48 columnas reales; rol de `EloRatings.csv` aclarado; fórmulas analíticas de indicadores; correspondencias; auditoría de consistencia de nombres; diagrama ampliado `graph LR`. |
| **Paso 3: Modelo Lógico** | **Aprobado** | Esquema estrella puro; dimensiones con claves subrogadas autoincrementales (`DIM_TIEMPO`, `DIM_EQUIPO` con rol local/visitante, `DIM_DIVISION`, `DIM_PAIS`); hechos con PK compuesta en `FACT_COMPETENCIA`; DDL probado en MySQL 8.0.45. |
| **Paso 4: Integración (ETL)** | **Aprobado** | Implementación oficial en Python (`01_carga_dw.ipynb`) con pandas y SQLAlchemy; staging en memoria; 15 chequeos de calidad ejecutados; balance perfecto: 238.858 filas = 132.256 hechos + 106.602 descartes (**diferencia 0**); totales agregados (348.954 goles y 18.356 rojas) idénticos al CSV original; política de actualización definida (semanal / ventana 30 días). |
| **Entrega Final: Dashboard** | **Aprobado** | 12 consultas SQL directas contra el modelo estrella; tablas de resultados comprobadas; 12 gráficos generados en `graficos/`; respuestas directas documentadas en `dashboard.md`. |

---

## 5. Implementación Oficial del Paso 4 en Python (Jupyter Notebook)

Siguiendo la indicación de la cátedra en la clase teórica (*Teorico 16_09.docx*), el proceso ETL se estandarizó exclusivamente en **Python + Jupyter (`01_carga_dw.ipynb`)**, eliminando la versión previa en scripts SQL puros (`cargar_dw.py` y `sql/`):

* **Por qué Python + pandas:** Permite inspección inmediata de los datos crudos, trazabilidad celda a celda en el notebook y manipulación vectorizada de tablas de forma mucho más flexible y didáctica que scripts procedurales extensos.
* **Orquestación del DDL y persistencia:** El notebook lee y ejecuta el script DDL oficial de Paso 3 (`../paso-3/entrega_modelo_logico.sql`) para crear la base `dw_competencia_futbol` y sus restricciones relacionales, y luego inserta los DataFrames mediante SQLAlchemy (`append`).
* **Verificación cruzada con diferencia 0:** El notebook recalcula en memoria partidos, goles y tarjetas directamente sobre el archivo `Matches.csv` y los contrasta contra las tablas del Data Mart en MySQL, certificando que no existe pérdida ni alteración de registros.

---

## 6. Lista de tareas y guía para la defensa

1. **Fecha de descarga:** En `paso-2/fuente.md` figura como fecha `2026-09-29`. Si se les consulta, el dataset se descargó a fines de septiembre de 2026 del repositorio actualizado del autor.
2. **Explicación de `EloRatings.csv`:** Recordar los 4 puntos del apartado 2: sirvió como fuente de cotejo en P2, pero no se cargó en MySQL porque `Matches.csv` es autosuficiente y previene pérdida de datos.
3. **Separación de entregas (sin duplicados ni redundancias):**
   * Cuando pidan el **Paso 4 (Integración de Datos)**, se entrega únicamente la carpeta `paso-4/` con su notebook `01_carga_dw.ipynb` y su informe técnico `entrega_informe.md`.
   * Cuando pidan la **Entrega Final (Dashboard)**, se entrega la carpeta `entrega-final/` con `dashboard.md`, `dashboard.ipynb` y `graficos/`.
4. **Respuestas clave del Dashboard:**
   * *Nottingham Forest:* +314 puntos de Elo en 5 años (+21,4 %).
   * *Ventaja de local:* El local gana el 45 % de los partidos frente al 28 % del visitante.
   * *Liga más pareja:* Las segundas divisiones europeas (Segunda División española, Ligue 2, Serie B).
   * *Disciplina:* Portugal y España presentan el mayor promedio de tarjetas por partido.
