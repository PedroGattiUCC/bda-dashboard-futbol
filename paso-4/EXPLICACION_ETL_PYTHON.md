# Paso 4: Integración de datos con Python + Jupyter — explicación para el grupo

Este documento explica **cómo funciona la carga ETL en Python**, pensado para quien nunca usó Python. Si vieron C++ en clase, van a ver que la lógica es la misma: variables, `if`, `for`, funciones. Lo nuevo es la librería **pandas**, que trabaja con tablas enteras de una sola vez.

---

## 1. Qué es esto y por qué usamos Python + Jupyter

En `paso-4/` implementamos el proceso de integración de datos (ETL) íntegramente en **Python** estructurado en el notebook interactivo `01_carga_dw.ipynb`:
* **Recomendación de la cátedra:** En la clase teórica (*Teorico 16_09.docx*) se recomendó el uso de Python y Jupyter para permitir visualización inmediata, modularidad y trazabilidad celda a celda.
* **Transformación en memoria:** Mediante la librería **pandas**, se auditan los datos crudos, se ejecutan las reglas de limpieza y se estructura el modelo multidimensional antes de impactar en MySQL.
* **Persistencia en el motor:** A través de **SQLAlchemy** y **mysql-connector-python**, el notebook aplica el DDL de `../paso-3/entrega_modelo_logico.sql` e inserta los registros en la base `dw_competencia_futbol`.

| Aspecto | Implementación Oficial (`01_carga_dw.ipynb`) |
| :---- | :---- |
| Dónde se limpian los datos | En memoria, con **pandas** (DataFrame crudo $\rightarrow$ DataFrame limpio) |
| Dónde queda el Data Warehouse | MySQL, base `dw_competencia_futbol` (las 5 tablas creadas por el DDL de Paso 3) |
| Cómo se ejecuta | Abriendo Jupyter Lab / VS Code y ejecutando celda por celda |
| Resultado validado | 132.256 hechos, 577 equipos, 6.321 fechas, 15 divisiones, 10 países |
| Balance de pérdida | 0 filas perdidas (238.858 - 106.602 descartes = 132.256 hechos) |

*(Nota importante: El tablero analítico y las respuestas a las 12 preguntas de negocio se entregan por separado en `../entrega-final/dashboard.md` y `../entrega-final/dashboard.ipynb`).*

---

## 2. Organización del Paso 4 (Integración de Datos)

```text
paso-4/
├── entrega_informe.md        <- informe obligatorio de calidad, balance y actualización
├── 01_carga_dw.ipynb         <- notebook ETL: extracción, calidad, limpieza, modelo estrella y carga
├── EXPLICACION_ETL_PYTHON.md <- este archivo (guía pedagógica)
├── requirements.txt          <- librerías requeridas (pandas, sqlalchemy, mysql-connector-python, jupyterlab)
├── datos/
│   └── Matches.csv           <- dataset de partidos (48 columnas, ~45 MB)
├── mapeos/
│   ├── mapeo_divisiones.csv  <- las 15 ligas del alcance, con su nombre y país
│   └── mapeo_equipos.csv     <- clubes escritos de dos formas -> nombre único
└── README.md                 <- guía del paso y manual de ejecución
```

El notebook usa `../paso-3/entrega_modelo_logico.sql` para crear las tablas en MySQL antes de insertar los datos.

---

## 3. Conceptos básicos (lo mínimo para entender los notebooks)

### 3.1 ¿Qué es Jupyter y qué es un notebook?

Un **notebook** (archivo `.ipynb`) es un documento que mezcla **texto explicativo** y **bloques de código** que se pueden ejecutar de a uno. El resultado de cada bloque (una tabla, un número, un gráfico) aparece justo debajo.

**Jupyter** (o **JupyterLab**) es el programa que abre los notebooks en el navegador. También se pueden abrir con **VS Code**.

Por qué se usa tanto en análisis de datos: podés ir viendo el resultado de cada paso, en vez de correr un programa entero y mirar solo el final. Si algo sale mal en el paso 5, lo ves en el paso 5.

**Cómo se usa:**

* Cada bloque gris es una **celda de código**. Se ejecuta con **Shift + Enter** (ejecuta y pasa a la siguiente).
* Las celdas con texto (como los títulos y las explicaciones) son **celdas Markdown**; no hacen nada al ejecutarlas.
* **Hay que ejecutarlas en orden, de arriba hacia abajo**, porque cada una usa las variables que crearon las anteriores. Para correr todo junto: menú *Run → Run All Cells*.
* A la izquierda de cada celda aparece `[1]`, `[2]`… con el orden en que se ejecutó. Si aparece `[*]`, todavía se está ejecutando.
* Si algo quedó en un estado raro: *Kernel → Restart Kernel and Run All Cells* (reinicia y corre todo de cero).

### 3.2 Python comparado con C++

| C++ | Python | Comentario |
| :---- | :---- | :---- |
| `#include <iostream>` | `import pandas as pd` | Traer una librería. `as pd` le pone un nombre corto |
| `int x = 5;` | `x = 5` | No se declara el tipo ni se pone `;` |
| `string nombre = "Arsenal";` | `nombre = "Arsenal"` | |
| `cout << "Total: " << x;` | `print("Total:", x)` | |
| `if (x > 5) { ... }` | `if x > 5:` + bloque con sangría | En Python **la sangría (los espacios) marca el bloque**, no las llaves |
| `&&`, `\|\|`, `!` | `and`, `or`, `not` | Para valores sueltos |
| `for (int i = 0; i < n; i++)` | `for elemento in lista:` | Recorre directamente los elementos |
| `int suma(int a, int b) { return a + b; }` | `def suma(a, b): return a + b` | Definir una función |
| `vector<string> v = {"a", "b"};` | `v = ["a", "b"]` | Una **lista** |
| `map<string,string> m;` | `m = {"clave": "valor"}` | Un **diccionario** |
| `// comentario` | `# comentario` | |

### 3.3 pandas: trabajar con tablas

**pandas** es la librería de Python para trabajar con tablas. Una tabla en pandas se llama **DataFrame**, y una columna sola se llama **Series**.

La idea clave: **las operaciones se aplican a toda la columna de una vez**, sin escribir un `for` que recorra fila por fila (parecido a SQL).

| Qué se quiere hacer | SQL | pandas |
| :---- | :---- | :---- |
| Leer un CSV | (se importa a una tabla) | `tabla = pd.read_csv("archivo.csv")` |
| Ver las primeras filas | `SELECT * ... LIMIT 5` | `tabla.head()` |
| Elegir una columna | `SELECT HomeTeam` | `tabla["HomeTeam"]` |
| Filtrar filas | `WHERE goles > 3` | `tabla[tabla["goles"] > 3]` |
| Varias condiciones | `AND` / `OR` / `NOT` | `&` / `\|` / `~` (cada condición entre paréntesis) |
| Valor dentro de una lista | `IN ('E0', 'SP1')` | `.isin(["E0", "SP1"])` |
| Sacar espacios | `TRIM(x)` | `.str.strip()` |
| Dato faltante | `NULL` | `NaN` (se chequea con `.isna()` / `.notna()`) |
| Contar | `COUNT(*)` | `len(tabla)` o `.sum()` sobre una condición |
| Agrupar | `GROUP BY equipo` | `.groupby("equipo").agg(...)` |
| Unir tablas | `JOIN ... ON` | `.merge(otra_tabla, on="columna")` |
| Ordenar | `ORDER BY x DESC` | `.sort_values("x", ascending=False)` |
| Primeros N | `LIMIT 15` | `.head(15)` |
| Sin repetidos | `DISTINCT` | `.drop_duplicates()` |
| Unir filas de dos tablas | `UNION ALL` | `pd.concat([t1, t2])` |

Un truco que se usa mucho: una condición como `tabla["FTHome"] == ""` devuelve `True`/`False` para cada fila, y `.sum()` cuenta los `True` (cada `True` vale 1). Así se cuentan vacíos, errores, etc.

### 3.4 Las otras librerías

* **matplotlib**: hace los gráficos.
* **mysql-connector-python**: conecta Python con MySQL.
* **SQLAlchemy**: lo necesita pandas para guardar un DataFrame en MySQL (`to_sql`) y para leer con `read_sql`.

---

## 4. Cómo correrlo en tu PC

### 4.1 Requisitos

* **Python 3** (en la PC donde se probó: Python 3.14).
* **MySQL 8** funcionando, con el usuario `root` y su contraseña.

### 4.2 Instalar las librerías (una sola vez)

En una consola (PowerShell), parados en la carpeta `paso-4`:

```powershell
cd "C:\PROYECTO BDA\paso-4"
pip install -r requirements.txt
```

### 4.3 Abrir Jupyter

```powershell
jupyter lab
```

Se abre el navegador con la lista de archivos. Doble clic en `01_carga_dw.ipynb`.

Si `jupyter` no se reconoce como comando, probar con `python -m jupyterlab`. **Alternativa:** abrir la carpeta con VS Code (con la extensión *Jupyter* instalada), abrir el `.ipynb` y elegir Python como *kernel* arriba a la derecha.

### 4.4 Ejecutar

1. **`01_carga_dw.ipynb`** → *Run → Run All Cells*. Cuando llega a la parte de MySQL aparece un cuadro para escribir la **contraseña de MySQL** (no queda guardada en el archivo). Tarda alrededor de un minuto.
2. Para ver el tablero y los gráficos de las 12 preguntas de negocio, abrir **`../entrega-final/dashboard.ipynb`** y ejecutar sus celdas.

Si no quieren que pida la contraseña cada vez, antes de `jupyter lab` se puede hacer `$env:MYSQL_PASSWORD = "la_contraseña"` en la misma consola.

> **Atención:** el notebook `01_carga_dw.ipynb` **crea o recrea** las tablas de `dw_competencia_futbol` ejecutando el DDL del Paso 3 (`../paso-3/entrega_modelo_logico.sql`) antes de cargar los datos limpios.

---

## 5. Notebook 1 — `01_carga_dw.ipynb`, paso por paso

### 5.0 Preparación

Se importan las librerías y se definen las rutas de los archivos y los datos de conexión a MySQL. Si en otra PC algo cambia (otra ruta, otro usuario), **se cambia solo en esa celda**.

### 5.1 Extracción

```python
partidos = pd.read_csv(RUTA_CSV, dtype=str, keep_default_na=False)
```

Lee el CSV entero (**238.858 partidos**) y lo guarda en el DataFrame `partidos`. Se lee **todo como texto** a propósito: así podemos revisar los datos tal cual vienen antes de convertirlos. Es el equivalente a la tabla de staging `STG_PARTIDOS` de la versión SQL.

Después nos quedamos con las 13 columnas que usa el modelo del Paso 3 (el archivo trae 48; las cuotas, tiros, córners, etc. ya se habían descartado en el Paso 3) y se leen las dos tablas de mapeo.

### 5.2 Calidad de datos

Son los mismos chequeos de `sql/02_calidad.sql`, uno por celda:

| Chequeo | Cómo se hace en pandas | Qué dio |
| :---- | :---- | :---- |
| Vacíos en columnas clave | `(partidos[col].str.strip() == "").sum()` | 4 partidos sin goles ni resultado en todo el archivo |
| Vacíos de Elo y tarjetas | Igual, con porcentaje | 37 % sin Elo y 47 % sin tarjetas en el archivo completo |
| Formato y rango de fechas | `.str.match(patrón)`, `.min()`, `.max()` | Todas bien, de 2000-07-28 a 2026-09-03 |
| Resultado H/D/A y coherente con goles | Se calcula el resultado con los goles y se compara | 0 errores |
| Valores fuera de rango | Condiciones con `>` y `<` unidas con `\|` | 1 partido: Zaragoza–Oviedo con **9 rojas** |
| Nombres con espacios sobrantes | `equipos != equipos.str.strip()` | 11 equipos (`'Ajax '`, `'Kaiserslautern '`…) |
| Mismo club escrito distinto | Contar las variantes del mapeo | 4 variantes (`Nott'm Forest`, `M'gladbach`, `Roda JC`, `Preußen Münster`) |
| Alcance | `.isin(ligas_del_mapeo)` | 132.257 partidos dentro, 106.601 fuera |
| Vacíos dentro del alcance | Igual que antes, filtrado | 3,1 % sin Elo, 35 % sin tarjetas |
| Duplicados y equipo contra sí mismo | `.duplicated()` | 0 y 0 |

### 5.3 Limpieza

Se crea la tabla `limpio` y se van aplicando las reglas (las mismas de `sql/03_limpieza.sql`). Cada vez que se descartan filas se anota el motivo y la cantidad en la lista `descartes`.

1. **Alcance:** se descartan los partidos de ligas que no están en `mapeo_divisiones.csv` → **106.601 filas**.
2. **Textos:** `.str.strip()` saca espacios; se corrige un carácter mal codificado; y con un diccionario se unifican los nombres (`Nott'm Forest` → `Nottm Forest`, etc.). Sin esto, Nottingham Forest quedaría partido en dos equipos y la pregunta 1 daría mal.
3. **Tipos:** `pd.to_datetime` para la fecha y `pd.to_numeric` para los números. Lo vacío queda como `NaN`.
4. **Fuera de rango → vacío:** las 9 rojas de Zaragoza–Oviedo pasan a `NaN`; el partido se conserva.
5. **No se rellena con 0:** tarjetas y Elo vacíos quedan vacíos, porque rellenar con 0 bajaría los promedios. pandas saltea los `NaN` cuando calcula promedios.
6. **Descartes por problemas de datos:** sin fecha, sin equipo, **sin goles (1 partido: Bastia–Red Star)**, local igual a visitante, duplicados.
7. **Resultado derivado de los goles:** se recalcula siempre (se corrigieron 0).
8. Se renombran las columnas a los nombres del Paso 3 (`FTHome` → `goles_local`, etc.) y con `.merge` se agrega el nombre de la liga y del país.

**Resultado:** 238.858 filas del archivo = **132.256 limpias** + **106.602 descartadas**. Diferencia **0**.

### 5.4 Transformación: el modelo estrella en memoria

Se arman con pandas las mismas 5 tablas del Paso 3. Cada dimensión recibe una **clave subrogada** (`id_...`) numerada 1, 2, 3… con `range(1, cantidad + 1)`.

| Tabla | Cómo se arma | Filas |
| :---- | :---- | :---- |
| `DIM_TIEMPO` | Fechas distintas; de cada una se sacan año, mes, trimestre, día de la semana y **temporada** (con una función `calcular_temporada` que corta en julio: un partido de marzo de 2022 es de la `2021-2022`) | 6.321 |
| `DIM_EQUIPO` | Locales y visitantes juntos (`pd.concat`), sin repetir y ordenados | 577 |
| `DIM_DIVISION` | Código y nombre de liga, sin repetir | 15 |
| `DIM_PAIS` | Código y nombre de país, sin repetir | 10 |
| `FACT_COMPETENCIA` | Cada partido limpio + las claves de sus dimensiones, que se buscan con `.merge` (igual que un `JOIN`). `DIM_EQUIPO` se une dos veces: una para el local y otra para el visitante. Se calculan los puntos (3/1/0) y las banderas `victoria_local`, `empate`, `victoria_visitante` | 132.256 |

### 5.5 Carga en MySQL

1. **Contraseña:** se toma de la variable `MYSQL_PASSWORD` o se pide con un cuadro (`getpass`). **Nunca se escribe en el notebook**, así se puede compartir sin exponerla.
2. **Crear el modelo (Persistencia en disco):** antes de correr el DDL, el código consulta con `SHOW TABLES` si `FACT_COMPETENCIA` ya existe en MySQL:
   * **Si es la primera vez en la PC:** lee `../paso-3/entrega_modelo_logico.sql` y crea las 5 tablas con sus claves primarias, foráneas e índices.
   * **Si ya existe en la PC (`RECREAR_TABLAS = False`):** **no borra nada**. El Data Warehouse queda guardado en el disco de tu máquina y no se pierde al reiniciar el kernel o cerrar Jupyter.
   * **Recreación forzada opcional:** si alguna vez se necesita resetear la base desde cero, basta con cambiar el flag de la celda de configuración a `RECREAR_TABLAS = True`.
3. **Guardar las tablas (Protección contra duplicados e incremental):**
   * **Carga inicial:** si `FACT_COMPETENCIA` está vacía, inserta las 4 dimensiones y los 132.256 partidos con `if_exists="append"`.
   * **Protección contra duplicados:** si los partidos ya están cargados (ej. al reiniciar el kernel y volver a correr), detecta que ya existen y **no los vuelve a insertar**, evitando errores de claves duplicadas.
   * **Carga incremental:** si el archivo trae partidos nuevos, inserta solo las dimensiones que no existan previamente y agrega únicamente los partidos nuevos a la tabla de hechos.

### 5.6 Verificación

| Control | Cómo | Resultado esperado |
| :---- | :---- | :---- |
| Conteo por tabla | `SELECT COUNT(*)` en MySQL contra `len()` del DataFrame | Iguales en las 5 tablas |
| Balance de filas | archivo − hechos − descartes | **0** |
| Totales contra el archivo original | Se recalculan partidos, goles y rojas **desde el CSV sin limpiar** con los mismos criterios, y se comparan con un `SELECT SUM(...)` en MySQL | 132.256 partidos, 348.954 goles, 18.356 rojas → **OK** |
| Integridad | `LEFT JOIN` de los hechos con cada dimensión | 0 claves huérfanas |
| Coherencia | Cada partido tiene exactamente una bandera en 1 | 0 incoherentes |

La **política de actualización** es la misma de la versión SQL (`../paso-4/entrega_informe.md`, sección 7).

---

## 6. Explotación Analítica — Notebook del Dashboard (en `../entrega-final/dashboard.ipynb`)

### 6.1 Preparación (igual para todas las preguntas)

1. **Leer el modelo desde MySQL** con `pd.read_sql("SELECT * FROM FACT_COMPETENCIA", motor)` y lo mismo para las 4 dimensiones. El dashboard usa **solo el modelo estrella**, nunca el CSV, que es lo que pide la metodología.
2. **Convertir el Elo y las tarjetas a número** (`astype(float)`), porque MySQL devuelve las columnas `DECIMAL` con un tipo especial.
3. **Unir hechos + dimensiones** con `.merge` en una sola tabla `partidos` (una fila por partido, con fecha, temporada, liga, país y nombres de los equipos).
4. **Tabla `participacion`:** cada partido aparece **dos veces**, una desde el punto de vista del local y otra desde el visitante. Así, para cualquier pregunta "por equipo", los goles a favor son siempre `goles_favor`, las victorias siempre `victoria`, etc. Es lo mismo que la vista `V_PARTICIPACION` de SQL. Se arma con dos DataFrames y `pd.concat`.
5. **Fechas de referencia:** "últimos 5 años" se cuenta desde el último partido cargado (2026-09-03), con `pd.DateOffset(years=5)`.
6. **Función `grafico_barras`:** dibuja un gráfico de barras horizontales y lo guarda en `graficos/`. Se define una vez y se usa en 9 preguntas, para no repetir el mismo código.

### 6.2 Las 12 preguntas

Cada pregunta tiene: el indicador y las perspectivas del Paso 1, una explicación de cómo se calcula, la tabla de resultados, el gráfico y la **respuesta escrita**.

| # | Pregunta | Cómo se calcula en pandas | Respuesta |
| :---- | :---- | :---- | :---- |
| 1 | ¿Cuánto mejoró un equipo en 5 años? (Nottingham Forest) | Filtro por equipo y fecha; `groupby("anio")` para el Elo por año; primer y último partido con `.iloc[0]` y `.iloc[-1]` | +314 puntos de Elo (+21,4 %) |
| 2 | ¿Quién gana más en un clásico? | `for` sobre 6 clásicos; se filtra `equipo == A` y `rival == B` y se suman victorias, empates y derrotas | Arsenal sobre Tottenham 47 % vs 20 %; Barcelona sobre Real Madrid 46 % vs 33 % |
| 3 | ¿Existe ventaja de local? | Promedio de la bandera `victoria_local` (promedio de 1 y 0 = proporción); `groupby("liga")` | Sí: el local gana 45,0 %, el visitante 28,1 % |
| 4 | ¿Qué liga es más pareja? | Desvío estándar (`std`) de `elo_local − elo_visitante` por liga; solo ligas con Elo en ≥ 80 % de los partidos | Las segundas divisiones (Segunda, Ligue 2, Serie B) |
| 5 | ¿Qué liga tiene más tarjetas? | Promedio de amarillas y rojas por liga, solo partidos con dato (≥ 1000) | Primeira Liga (5,09 amarillas por partido) y La Liga (5,02) |
| 6 | Mejores visitantes (5 años) | `participacion` filtrada por `condicion == "Visitante"`; % de victorias por equipo; ≥ 60 partidos | Porto 71,8 %, PSV 70,9 %, Celtic 70,7 % |
| 7 | % de victorias por equipo (5 años) | `groupby("equipo")`, promedio de `victoria`; ≥ 120 partidos | Celtic 76,9 %, PSV 76,0 % |
| 8 | Promedio de goles por equipo (5 años) | La misma tabla de la 7, ordenada por `goles_favor` | Bayern Munich 2,98 goles por partido |
| 9 | ¿El equipo es consistente? | División principal de cada equipo por temporada; `.shift(1)` para comparar con la temporada anterior y contar ascensos/descensos | Menos consistente: Metz (15 cambios). Más: Lyon, Athletic Bilbao |
| 10 | Mayor incremento de Elo (3 años) | Primer y último Elo de cada equipo con `agg("first")` / `agg("last")`; condiciones para que la comparación sea justa | Como +327, Paris FC +239 |
| 11 | Más rojas (fair play) | Promedio de `rojas` por equipo; ≥ 200 partidos con dato | Boavista 0,213 rojas por partido |
| 12 | Países con equipos de mayor Elo (2025-2026) | Elo máximo por equipo y después por país; gráfico de puntos | Inglaterra (Arsenal 2029), España, Francia, Alemania, Italia |

Las decisiones de cada pregunta (mínimos de partidos, ventanas de tiempo, clásicos elegidos) están debidamente documentadas en `../entrega-final/dashboard.md`.

---

## 7. Cómo se comprobó que funciona

* Toda la parte de pandas (extracción, calidad, limpieza, dimensiones, hechos y verificación) **se ejecutó completa con el `Matches.csv` real**:
  * 132.256 hechos, 106.602 descartes, 6.321 / 577 / 15 / 10 filas en las dimensiones.
  * 348.954 goles, 18.356 rojas, 337.275 amarillas: totales idénticos y balance exacto con diferencia 0.
  * Las tablas y gráficos de resultados de las 12 preguntas coinciden rigurosamente con los valores del Data Mart.
* El DDL del Paso 3 se valida y ejecuta: 17 sentencias para crear la base, tablas e índices.
* La verificación de claves primarias y foráneas garantiza cero registros huérfanos.

---

## 8. Errores comunes y cómo resolverlos

| Error | Causa | Solución |
| :---- | :---- | :---- |
| `ModuleNotFoundError: No module named 'pandas'` (u otra librería) | Falta instalar dependencias | `pip install -r requirements.txt` |
| `FileNotFoundError: datos/Matches.csv` | El CSV no está en `datos/` o Jupyter se abrió desde otra carpeta | Verificar que el CSV esté en `datos/Matches.csv` y abrir `jupyter lab` en `paso-4` |
| `NameError: name 'limpio' is not defined` | Se ejecutó una celda sin ejecutar las anteriores | *Run → Run All Cells*, o ejecutar desde arriba hacia abajo |
| `Access denied for user 'root'` | Contraseña incorrecta | Reiniciar el kernel y volver a escribir la contraseña correcta |
| `Can't connect to MySQL server` | El servicio MySQL no está iniciado | Iniciar el servicio MySQL80 (desde Servicios de Windows o MySQL Workbench) |
| `Unknown database 'dw_competencia_futbol'` en el dashboard | Todavía no se ejecutó la carga del DW | Correr primero `01_carga_dw.ipynb` |
| `jupyter` no se reconoce como comando | La carpeta de scripts de Python no está en el PATH | Usar `python -m jupyterlab` |

---

## 9. Pautas para la defensa grupal

1. **Ejecución previa:** Alguien con MySQL instalado corre `01_carga_dw.ipynb` completo y valida que en la etapa 6 todo da **OK** y las diferencias dan **0**. Conviene guardar el notebook con los outputs visibles para la entrega.
2. **Entregable oficial:** Paso 4 se entrega exclusivamente con la solución en **Python (`01_carga_dw.ipynb`)**, fundamentado en la sugerencia del docente de la cátedra para optimizar trazabilidad y visualización.
3. **Conceptos clave que cada integrante debe dominar:**
   * Qué es un DataFrame y en qué se parece a una tabla SQL.
   * Qué hacen `.groupby()` y `.merge()` y cuáles son sus equivalentes (`GROUP BY`, `JOIN`).
   * Por qué los valores faltantes en tarjetas y Elo quedan como `NaN` en vez de rellenar con 0 (para no alterar los promedios reales).
   * Por qué se unifican variantes ortográficas de nombres de clubes (ej. Nottingham Forest).
   * Cómo se demuestra matemáticamente que no hubo pérdida de datos (balance: $238.858 - 106.602 = 132.256$).
4. Si `datos/Matches.csv` resulta muy pesado para el campus virtual (~45 MB), se puede adjuntar o descargar según el enlace documentado en `../paso-2/fuente.md`.
