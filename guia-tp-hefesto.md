# GUÍA DE TRABAJO PRÁCTICO #2 — DATA WAREHOUSE CON METODOLOGÍA HEFESTO

**Temas:** Business Intelligence, Data Warehousing, Metodología HEFESTO

---

## De qué se trata este TP

Este trabajo se resuelve en **grupos de exactamente 4 integrantes**. Cada grupo **elige su propio tema** y construye su propio Data Mart, a partir de un archivo de datos que va a tener que conseguir por su cuenta — típicamente un CSV de algún portal de datos abiertos (datos.gob.ar, Kaggle, un organismo público, etc.).

El trabajo se hace en 4 entregas, una por clase, aplicando cada una un paso de la metodología HEFESTO vista en la clase teórica. Cada entrega **parte del resultado de la anterior** — igual que en el TP integrador, no se puede resolver un paso salteando el anterior.

**Carpeta de entrega:** cada grupo entrega en su carpeta grupal, subcarpeta por paso (`paso-1/`, `paso-2/`, `paso-3/`, `paso-4/`).

---

## Elección del tema y del archivo de datos

Antes de la Consigna 1, cada grupo debe:

1. **Elegir un tema** de interés del grupo (deporte, salud, transporte, comercio, clima, educación, lo que sea), siempre que se pueda plantear como un **proceso de negocio analizable** (algo que ocurre repetidamente y que genera registros: ventas, viajes, consultas médicas, partidos jugados, etc.).
2. **Conseguir un archivo CSV** (o similar: Excel exportable a CSV) con datos reales o realistas sobre ese tema, de algún sitio de datos abiertos. El archivo debe tener:
   - Como mínimo unas cientos de filas (para que tenga sentido calcular indicadores).
   - Al menos una columna que sirva como perspectiva de Tiempo (una fecha).
   - Al menos dos o tres columnas más que sirvan de otras perspectivas (categorías, nombres, ubicaciones, tipos).
   - Al menos una o dos columnas numéricas que sirvan de base para indicadores (montos, cantidades, duraciones).
3. Documentar **de dónde salió el archivo** (nombre del portal, URL, fecha de descarga) — esto va a ser parte de la primera entrega.

**Importante:** no hace falta que el archivo sea perfecto. Si aparecen datos faltantes, inconsistentes o con errores de formato, eso también es parte del trabajo (se trabaja en el Paso 2 y el Paso 4) — es exactamente la situación real que van a encontrar siempre que trabajen con datos de terceros.

---

## Consigna 1: Paso 1 — Análisis de Requerimientos

Aplicar el Paso 1 de HEFESTO al tema elegido:

1. **Presentación del tema y la fuente de datos**: qué proceso de negocio se va a analizar, de dónde salió el archivo (link/portal), y una descripción breve de qué información trae (sin entrar todavía en el detalle de columnas — eso es Paso 2).
2. **a) Identificar preguntas**: formular al menos 5 preguntas de negocio complejas (con variables de análisis), siguiendo el mismo criterio visto en clase — deben reflejar objetivos reales de quien usaría este DW, y tienen que poder responderse con datos que efectivamente estén en el archivo conseguido.
3. **b) Identificar indicadores y perspectivas**: descomponer las preguntas anteriores en su lista de indicadores (valores numéricos a medir) y perspectivas (ejes de análisis). Tiempo debe ser una de ellas.
4. **c) Modelo Conceptual**: el diagrama (perspectivas a la izquierda, relación central, indicadores a la derecha), igual al formato visto en clase.

**Formato de entrega:** un archivo `entrega_requerimientos.md` con las 4 partes de arriba (texto + diagrama en bloque de código, en el mismo formato visto en la clase teórica).

**Entregables de Paso 1:**
1. `entrega_requerimientos.md`: tema elegido, fuente del archivo (link/portal), preguntas de negocio, indicadores, perspectivas y modelo conceptual.

---

## Consigna 2: Paso 2 — Análisis de la fuente de datos

**Punto de partida:** el modelo conceptual y las preguntas de negocio de `entrega_requerimientos.md` (Paso 1). Si algo de eso cambia al confrontarlo con los datos reales del archivo, está bien — es normal y forma parte del proceso (ver más abajo).

Aplicar el Paso 2 de HEFESTO sobre el archivo CSV conseguido:

1. **Perfil del archivo**: listar todas sus columnas, con una breve descripción del significado de cada una (qué representa, qué valores puede tomar) y su tipo de dato aparente (texto, número, fecha, categoría). Si el archivo viene con un diccionario de datos o README, referenciarlo; si no, inferirlo inspeccionando los valores.
2. **a) Conformar indicadores**: para cada indicador del Paso 1, especificar el/los hechos que lo componen (con su fórmula, si es calculado) y la función de agregación (`SUM`, `AVG`, `COUNT`, etc.), usando los nombres reales de columnas del archivo.
3. **b) Establecer correspondencias**: tabla que vincule cada perspectiva e indicador del modelo conceptual con la(s) columna(s) real(es) del archivo que le corresponden.
4. **c) Nivel de granularidad**: para cada perspectiva, qué columnas concretas se van a incluir y por qué (cuáles aportan valor analítico y cuáles no). Para la perspectiva Tiempo, definir explícitamente el nivel de agrupamiento (día/mes/trimestre/año). Además, **revisar la consistencia de los valores de texto** que van a identificar cada perspectiva (por ejemplo, si una misma categoría aparece escrita de más de una forma) — documentar cualquier inconsistencia encontrada y cómo se piensa resolver (normalización de texto, mapeo manual, etc.).
5. **d) Modelo Conceptual ampliado**: el mismo diagrama del Paso 1, agregando debajo de cada perspectiva las columnas elegidas, y debajo de cada indicador su fórmula de cálculo.

**Si al hacer este análisis se dan cuenta de que alguna pregunta o indicador del Paso 1 no se puede responder con los datos disponibles**, está permitido (y es preferible) ajustar el modelo conceptual acá, documentando el cambio y por qué se hizo, antes que forzar un indicador que el archivo no puede sostener.

**Formato de entrega:**
- `entrega_fuente_datos.md` con las 5 partes de arriba.
- El archivo de datos (`dataset.csv`, o el nombre que tenga), o un archivo `fuente.md` con el link de descarga si el archivo pesa demasiado para subir.

**Entregables de Paso 2:**
1. `entrega_fuente_datos.md`: perfil del archivo, indicadores conformados, correspondencias, granularidad (incluyendo problemas de consistencia detectados) y modelo conceptual ampliado.
2. El archivo de datos usado (o el link de descarga).

---

## Consigna 3: Paso 3 — Modelo Lógico del DW

**Punto de partida:** el modelo conceptual ampliado de `entrega_fuente_datos.md` (Paso 2).

Aplicar el Paso 3 de HEFESTO:

1. **a) Tipo de Modelo Lógico**: elegir el tipo de esquema (estrella, copo de nieve o constelación) y justificar la elección en función de las perspectivas relevadas (¿alguna tiene jerarquías internas que ameriten normalizar? ¿hay un solo proceso de negocio o varios que comparten dimensiones?).
2. **b) Tablas de dimensiones**: diseñar una tabla de dimensión por cada perspectiva (nombre de tabla, clave principal nueva, campos renombrados si hace falta).
3. **c) Tablas de hechos**: diseñar la tabla de hechos (nombre, clave primaria compuesta por las claves de las dimensiones relacionadas, un campo por cada indicador).
4. **d) Uniones**: diagrama del modelo lógico final, con todas las tablas de dimensiones unidas a la tabla de hechos por clave foránea.

**Formato de entrega:**
- `entrega_modelo_logico.md`: las 4 partes de arriba, con el diagrama final del modelo (igual al formato visto en el Paso 2).
- `entrega_modelo_logico.sql`: el DDL real (`CREATE TABLE`) de todas las tablas de dimensiones y la tabla de hechos, ejecutable en MySQL.

**Entregables del Paso 3:**
1. `entrega_modelo_logico.md`: tipo de esquema elegido y justificación, diseño de dimensiones y hechos, diagrama de uniones.
2. `entrega_modelo_logico.sql`: DDL ejecutable de todo el modelo lógico (dimensiones + tabla de hechos), corrido al menos una vez contra una base MySQL propia para confirmar que compila sin errores.

---

## Consigna 4: Paso 4 — Integración de Datos

**Punto de partida:** el modelo lógico de `entrega_modelo_logico.sql` (Paso 3), ya creado en una base MySQL propia.

Aplicar el Paso 4 de HEFESTO: poblar el modelo lógico con los datos reales del archivo, y definir cómo se actualizaría. Esto se puede resolver de la forma que cada grupo prefiera (scripts SQL, un script Python que se conecte a MySQL, una herramienta ETL, o cualquier combinación) — lo que se evalúa es que el resultado cumpla lo siguiente, sea cual sea el camino elegido:

1. **Los datos del archivo quedan volcados en la base**, en algún punto intermedio, de forma tal que se puedan revisar y limpiar antes de pasar a las tablas finales del modelo.
2. **Se hizo al menos un chequeo de calidad de datos** (nulos en columnas clave, valores fuera de rango, inconsistencias de texto detectadas en el Paso 2) y quedó documentado qué se encontró y cómo se resolvió (se descartan filas, se corrigen valores, se completan con un valor por defecto, etc.).
3. **Cada tabla de dimensión queda poblada** con los valores únicos correspondientes del archivo, con su clave nueva generada.
4. **La tabla de hechos queda poblada**, resolviendo para cada fila del archivo a qué fila le corresponde en cada dimensión, y agregando los indicadores según la granularidad definida en el Paso 2.
5. **La carga quedó verificada**: conteos de filas en cada tabla (dimensiones y hechos), y al menos una comparación entre un total agregado del DW y el mismo total calculado directamente sobre el archivo original, para confirmar que no se perdieron ni duplicaron datos.
6. **Están definidas las políticas de actualización**: aunque para este TP la carga sea única, describir cómo se plantearía la actualización si este archivo se recibiera periódicamente (qué se recargaría completo, qué de forma incremental, con qué frecuencia).

**Formato de entrega:**
- El o los scripts/programas usados para la carga (lo que corresponda según la herramienta elegida), organizados de forma que se entienda el orden en que se ejecutan.
- `entrega_informe.md`: resultados reales de calidad de datos, verificación de la carga, y la descripción de la política de actualización.

**Entregables del Paso 4:**
1. El o los scripts/programas de carga, ejecutados al menos una vez contra el modelo lógico de Paso 3.
2. `entrega_informe.md`: calidad de datos, verificación de la carga y política de actualización propuesta.

---

## Entrega final: Dashboard sobre el modelo estrella

Una vez cargado el Data Mart, construir un **tablero** que responda, con datos reales extraídos del modelo estrella (no del archivo original), cada una de las preguntas de negocio planteadas en el Paso 1.

- Por cada pregunta de negocio, escribir la consulta SQL que la responde y armar un gráfico que represente visualmente el resultado obtenido.
- El tablero puede resolverse como corresponda según las herramientas de cada grupo: una serie de consultas SQL con sus resultados y gráficos documentados en un informe o aplicación desarrollada por ustedes mismos, o conectando alguna herramienta de visualización (Metabase, Power BI, Python con `matplotlib`/`plotly`, etc.) directamente contra el Data Mart en MySQL.
- Lo importante no es la herramienta, sino que **cada pregunta original del Paso 1 tenga una respuesta concreta, con datos reales y con su gráfico correspondiente, trazable hasta el modelo estrella** que se construyó a lo largo de los 4 pasos.

**Formato de entrega:** `dashboard.md` con cada pregunta de negocio, su consulta SQL, el resultado obtenido (tabla) y su gráfico correspondiente (imagen o captura de pantalla), entregado junto con el Paso 4.

**Entregable:**
- `dashboard.md`: respuesta a cada pregunta de negocio del Paso 1, con su consulta SQL, resultado real y gráfico.

Con esta entrega se cierra el ciclo completo de HEFESTO aplicado al tema elegido por cada grupo.

---

## Resumen de entregables por paso

| Paso | Nombre | Archivos a entregar |
|---|---|---|
| 1 | Análisis de Requerimientos | `entrega_requerimientos.md` |
| 2 | Análisis de la fuente de datos | `entrega_fuente_datos.md`, archivo de datos (o link) |
| 3 | Modelo Lógico del DW | `entrega_modelo_logico.md`, `entrega_modelo_logico.sql` |
| 4 | Integración de Datos | Script(s)/programa(s) de carga (SQL, Python, u otro), `entrega_informe.md`, `dashboard.md` |
