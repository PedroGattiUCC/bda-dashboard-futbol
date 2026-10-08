# 📖 Guía Completa de Uso: Tablero Analítico Dinámico en Render
## Data Mart de Competencia de Fútbol — Metodología HEFESTO v2

> **Documento oficial para la Defensa Oral Presencial ante la Cátedra de Bases de Datos Avanzadas.**  
> Este manual explica **cómo operar el dashboard en vivo**, **qué hace cada funcionalidad**, **cómo trabaja Render tras bambalinas**, y **cómo configurar y migrar Clever Cloud MySQL sin errores**.

---

## 📑 Índice de Contenidos
1. [¿Para qué sirve este Tablero Dinámico?](#1-para-qué-sirve-este-tablero-dinámico)
2. [¿Cómo se Usa la Aplicación Paso a Paso?](#2-cómo-se-usa-la-aplicación-paso-a-paso)
   - [Modo 1: Las 6 Preguntas Oficiales de Negocio](#modo-1-las-6-preguntas-oficiales-de-negocio)
   - [Navegación de Pestañas (Gráficos, Tablas, SQL y Conclusión)](#navegación-de-pestañas-en-cada-pregunta)
   - [Modo 2: Consola SQL Libre (Preguntas Sorpresa del Profesor)](#modo-2-consola-sql-libre-preguntas-del-docente)
   - [Modo 3: Explorador Multidimensional del Data Mart](#modo-3-explorador-del-data-mart)
3. [¿Cómo Trabaja Render Tras Bambalinas al Filtrar o Cambiar Consultas?](#3-cómo-trabaja-render-tras-bambalinas-al-filtrar-o-cambiar-consultas)
4. [Solución Definitiva y Conexión con Clever Cloud MySQL](#4-solución-definitiva-y-conexión-con-clever-cloud-mysql)
   - [¿Por qué daba error al elegir Clever Cloud y cómo se corrigió?](#por-qué-daba-error-al-elegir-clever-cloud)
   - [Cómo obtener tus credenciales en Clever Cloud](#dónde-obtener-las-credenciales-en-clever-cloud)
   - [Método A: Configuración automática en Render (Recomendado)](#método-a-variables-de-entorno-en-render-100-automático)
   - [Método B: Configuración en vivo desde el navegador web](#método-b-formulario-en-vivo-en-la-barra-lateral)
   - [Carga del Data Mart en Clever Cloud con 1 Clic](#cómo-poblar-la-base-si-está-vacía-migración-en-1-clic)
   - [El Mecanismo de Failsafe (Contingencia Offline Indestructible)](#el-mecanismo-de-failsafe-y-contingencia-offline)
5. [Guion de Defensa Oral Sugerido (10 Minutos Frente al Docente)](#5-guion-de-defensa-oral-sugerido-10-minutos)

---

## 1. ¿Para qué sirve este Tablero Dinámico?

En la entrega estándar de la cátedra se solicitan consultas SQL y gráficos estáticos. Sin embargo, para la **exposición oral frente al curso**, el profesor evalúa la capacidad de **adaptar las respuestas en vivo** a preguntas que él mismo formule en el momento (por ejemplo: *"¿Y qué pasa si en vez del Nottingham Forest analizamos al Arsenal o al Real Madrid?", "¿Y si cambiamos el umbral de tarjetas?", "¿Podemos comparar dos equipos que yo les diga?"*).

Para responder a este requerimiento con máxima excelencia técnica, se construyó este tablero sobre las siguientes bases:
- **Metodología:** HEFESTO v2 (Data Mart enfocado en el proceso de negocio *"Competencia entre Equipos"*).
- **Volumen de Datos:** **132.256 partidos oficiales** disputados a lo largo de 10 temporadas en Europa.
- **Granularidad:** 1 fila por partido en `FACT_COMPETENCIA`.
- **Arquitectura Nube:** Desplegado en **Render** (Servidor Web Python / Streamlit) conectado a **Clever Cloud** (Base de datos relacional MySQL remota) con **fallback automático de contingencia local** en SQLite.

---

## 2. ¿Cómo se Usa la Aplicación Paso a Paso?

Al ingresar a la URL de Render (o en tu máquina local con `streamlit run app.py`), la pantalla se divide en dos secciones principales:
- **Barra Lateral Izquierda (Menú):** Selección del modo de exposición, configuración del origen de datos (Clever Cloud / SQLite) y filtros globales.
- **Área Principal de Trabajo:** Visualizaciones interactivas, métricas KPI, tablas de datos, código SQL y conclusiones.

---

### Modo 1: Las 6 Preguntas Oficiales de Negocio

Este es el modo principal con el que debés iniciar la exposición. En la parte superior verás un selector desplegable con las **6 Preguntas Oficiales Seleccionadas**:

1. **Pregunta 1 (Evolución de Rendimiento):** ¿Cómo evolucionó el rendimiento histórico (Elo) de un club a lo largo de las temporadas?
2. **Pregunta 2 (Dominio en Clásicos / Derbis):** ¿Existe paridad o dominancia histórica en los clásicos europeos y enfrentamientos directos?
3. **Pregunta 3 (Efecto Localía):** ¿Qué divisiones presentan mayor ventaja de jugar de local y cómo impacta en los goles?
4. **Pregunta 4 (Paridad Competitiva):** ¿Cuáles son las ligas más parejas y competitivas del continente según la dispersión de Elo?
5. **Pregunta 5 (Comportamiento Disciplinario):** ¿Cuáles son las ligas con mayor tasa de tarjetas amarillas y rojas por partido?
6. **Pregunta 6 (Fortaleza de Visitante):** ¿Cuáles son los clubes con mayor efectividad y volumen de puntos jugando fuera de casa?

#### 🎛️ Filtros Rápidos Dinámicos en Vivo
Debajo del título de cada pregunta hay controles interactivos que podés manipular frente al profesor:
- **En la Pregunta 1:** Escribí en el campo *"Club a analizar"* cualquier equipo (ej: `Arsenal`, `Real Madrid`, `Barcelona`, `Liverpool`, `Milan`) y mové el control deslizante de *Ventana de años* (de 1 a 10 años). Al instante se recalculan todas las métricas.
- **En la Pregunta 2:** Activá el checkbox *"Comparar enfrentamiento libre entre 2 clubes"* para enfrentar a cualquier par de equipos que pida el docente (ej: `Chelsea` vs `Tottenham` o `Inter` vs `Milan`).
- **En la Pregunta 3:** Modificá el deslizador de *Ligas a visualizar* para ordenar de mayor a menor ventaja de localía.
- **En la Pregunta 4:** Modificá el *% mínimo de partidos con Elo* (filtro de calidad de datos).
- **En la Pregunta 5:** Alterná el ordenamiento del ranking entre *Amarillas por partido* o *Rojas por partido*.
- **En la Pregunta 6:** Cambiá el umbral de *Partidos mínimos de visitante* y la ventana de años.

---

### Navegación de Pestañas en Cada Pregunta

Debajo de los filtros dinámicos, cada una de las 6 preguntas organiza la información en **4 pestañas intuitivas**:

#### 📊 Pestaña 1: Visualizaciones y KPIs
- **Fila de Tarjetas KPI:** Cuadros métricos destacados en la parte superior que resumen la respuesta ejecutiva en números claros (ej: Elo Inicial, Elo Final, Tasa de Crecimiento %, Total de Partidos).
- **Múltiples Gráficos Plotly Interactivos:**
  - *Gráfico 1 (Principal):* Curvas temporales con bandas de volatilidad min-max, barras horizontales de ventaja o rankings.
  - *Gráfico 2 (Complementario):* Distribución de resultados, volumen de partidos por categoría o gráficos de dona.
  - *Gráfico 3 (Avanzado):* Matrices cuadrantes de dispersión (Scatter Plot) o comparativas agrupadas de goles a favor vs goles en contra.
- **Interactividad en los Gráficos:** Podés pasar el cursor sobre cualquier punto (hover tooltip), hacer zoom en áreas específicas, descargar el gráfico como imagen PNG en alta resolución o hacer clic en la leyenda para aislar una serie.

#### 📋 Pestaña 2: Datos Tabulados
- Muestra el **DataFrame completo** obtenido de la ejecución de la consulta SQL.
- Podés ordenar por cualquier columna haciendo clic en su encabezado, redimensionar columnas o buscar registros específicos.

#### 💻 Pestaña 3: Consulta SQL en Vivo
- Muestra el código SQL exacto que se está ejecutando sobre el modelo estrella (`FACT_COMPETENCIA` y dimensiones `DIM_*`).
- **Editor en Vivo:** Marcando el casillero *"✏️ Abrir Editor SQL para modificar la consulta en vivo ante el docente"*, se habilita un cuadro de texto donde podés alterar cláusulas `WHERE`, `GROUP BY` o `ORDER BY` y presionar **"🚀 Re-ejecutar SQL Modificado"** para ver el resultado de la nueva consulta en milisegundos.

#### 💡 Pestaña 4: Conclusión de Negocio
- Presenta la **interpretación de negocio bajo la metodología HEFESTO v2**:
  - Indicadores y perspectivas involucradas.
  - Justificación analítica de los resultados.
  - Recomendación de toma de decisiones para sponsors deportivos, gerencias de clubes o comités organizadores de torneos.

---

### Modo 2: Consola SQL Libre (Preguntas del Docente)

Si el profesor dice: *"Quiero que me muestren cuántos goles se hicieron en el año 2021 en España"*, cambiá en el menú lateral a:  
👉 **`💻 Consola SQL Libre (Preguntas del Docente)`**.

Esta sección ofrece:
1. **Plantillas Rápidas de 1 Clic:** Un menú desplegable con consultas típicas preparadas:
   - Partidos por temporada y goles promedio.
   - Top 10 goleadores locales de la historia.
   - Distribución de tarjetas por división.
   - Efectividad por día de la semana.
   - Hacé clic en *"Cargar Plantilla al Editor"* y la consulta aparecerá lista para ejecutar.
2. **Editor SQL Abierto:** Podés redactar cualquier sentencia SQL desde cero sobre `FACT_COMPETENCIA` o la vista auxiliar `V_PARTICIPACION`.
3. **Diccionario de Tablas Desplegable:** Un acordeón lateral con los nombres de todas las tablas y sus columnas principales para tener a mano el esquema exacto.
4. **Generador Rápido de Gráficos:** Si la consulta arroja al menos 2 columnas, el sistema te permite elegir el Eje X, el Eje Y y el Tipo de Gráfico (Barras Horizontales, Barras Verticales, Líneas o Dona) para graficar en vivo la respuesta a la pregunta del profesor.

---

### Modo 3: Explorador del Data Mart

Diseñado para demostrar la integridad de la base de datos y la arquitectura multidimensional:
- Permite seleccionar cualquier dimensión (`DIM_TIEMPO`, `DIM_EQUIPO`, `DIM_DIVISION`, `DIM_PAIS`), la tabla de hechos (`FACT_COMPETENCIA`) o la vista analítica (`V_PARTICIPACION`).
- Muestra el **conteo total de registros auditado** (ej: 132.256 partidos en hechos) y una vista previa de las primeras 25 filas con todas sus columnas.

---

## 3. ¿Cómo Trabaja Render Tras Bambalinas al Filtrar o Cambiar Consultas?

Es muy común que el docente pregunte:  
> *"¿Cómo funciona la arquitectura de esto? ¿Qué pasa en el servidor cuando ustedes mueven un filtro o editan una consulta?"*

Acá tenés la explicación técnica exacta:

```
[Navegador del Usuario] 
      │ (1) El usuario mueve un slider, escribe un club o presiona un botón
      ▼ 
[Túnel WebSocket wss://] ──► [Servidor Render (Contenedor Docker Linux)]
                                    │ (2) El motor de Streamlit detecta el cambio de estado
                                    │     y dispara un "Rerun" reactivo desde la línea 1.
                                    │ (3) consultas_base.py inyecta los parámetros limpios
                                    │     en la plantilla SQL del Data Mart.
                                    ▼
                             [Motor de Base de Datos Seleccionado]
                             ┌──────────────────────────────────────┐
                             │ • Clever Cloud MySQL (vía SSL:3306)  │
                             │ • SQLite Local (Memoria / Contenedor)│
                             └──────────────────────────────────────┘
                                    │ (4) El motor ejecuta el plan de ejecución relacional
                                    │     utilizando los índices primarios y secundarios.
                                    ▼
                             [Pandas DataFrame en Memoria RAM]
                                    │ (5) Transforma los registros en series vectorizadas,
                                    │     calcula deltas y métricas porcentuales.
                                    ▼
                             [Motor Gráfico Plotly]
                                    │ (6) Serializa las figuras en estructuras JSON declarativas
                                    │     optimizadas para renderizado con WebGL en el cliente.
                                    ▼
[Navegador del Usuario] ◄─── [Deltas WebSocket] (Actualiza el DOM en pantalla sin recargar la página)
```

### Detalle de cada fase técnica:
1. **Comunicación Bidireccional:** El frontend y el backend en Render están conectados permanentemente mediante un túnel **WebSocket**. No hay recargas de página (`F5`).
2. **Ejecución Reactiva:** Streamlit mantiene el diccionario `st.session_state`. Cuando cualquier widget cambia de valor, Streamlit reevalúa el script pasando únicamente las variables modificadas.
3. **Construcción Segura de Consultas:** `consultas_base.py` toma los argumentos (ej: `anios=5`, `equipo='Arsenal'`) y genera el SQL estándar compatible tanto con MySQL 8.0 como con SQLite.
4. **Ejecución Relacional:**
   - Si está seleccionado **Clever Cloud**, la consulta viaja por la red mediante SQLAlchemy y `mysql-connector-python` con cifrado SSL al puerto 3306 del cluster de Clever Cloud.
   - Si está en **Modo SQLite de Contingencia**, la consulta se resuelve localmente en menos de **15 milisegundos**.
5. **Procesamiento de Datos:** Pandas estructura la salida y aplica agregaciones rápidas para alimentar las tarjetas KPI.
6. **Renderizado en el Cliente:** Plotly genera gráficos vectoriales interactivos que se dibujan en la GPU del navegador mediante Canvas y WebGL.

---

## 4. Solución Definitiva y Conexión con Clever Cloud MySQL

### ¿Por qué daba error al elegir Clever Cloud?
El error original ocurría por dos factores típicos en entornos de nube:
1. **Variables de entorno ausentes en Render:** Si Render no tenía cargadas las variables `MYSQL_HOST`, `MYSQL_USER`, etc., el sistema intentaba por defecto conectarse a `localhost:3306`. Como Render es un contenedor Linux aislado sin servidor MySQL propio en localhost, la conexión era rechazada de inmediato (`Connection refused`).
2. **Base de datos recién creada vacía:** Al crear un add-on MySQL nuevo en Clever Cloud, la base de datos se crea con 0 tablas. Cuando la app ejecutaba `SELECT ... FROM FACT_COMPETENCIA`, MySQL devolvía el error `Table doesn't exist`.

### ¿Cómo se solucionó esto en el código?
Implementamos **tres capas de blindaje**:
1. **Detección inteligente de credenciales:** Si Clever Cloud está seleccionado pero no se ingresaron las credenciales reales de la nube, la aplicación **NO intenta conectarse a localhost**. En su lugar, despliega automáticamente el formulario de configuración para que ingreses los datos.
2. **Mecanismo de Failsafe (Fallback Automático):** Si Clever Cloud no está configurado, las credenciales son erróneas o la base está vacía, **LA APLICACIÓN NUNCA SE ROMPE NI MUESTRA UNA PANTALLA ROJA DE ERROR**. Automáticamente consulta los datos de respaldo local (SQLite), muestra un cartel informativo explicando la situación, y **dibuja todos los gráficos, KPIs y conclusiones normalmente**.
3. **Migración en 1 Clic desde la Web:** Si la base en Clever Cloud está vacía, la propia aplicación web ofrece un botón para crear las tablas y migrar los 132.256 partidos en vivo con una barra de progreso.

---

### Dónde obtener las credenciales en Clever Cloud
1. Iniciá sesión en [clever-cloud.com](https://www.clever-cloud.com/).
2. Entrá a tu organización y hacé clic en tu add-on de base de datos **MySQL**.
3. En la pestaña **Information**, verás los siguientes datos:
   - **Host:** Tiene un formato similar a `bxxxxxx-mysql.services.clever-cloud.com`
   - **Port:** `3306`
   - **Database name:** Un código alfanumérico generado por Clever Cloud (ej: `b8q3j7kfa4...`). *(¡Atención! No se llama `dw_competencia_futbol`)*.
   - **User:** Un código generado por Clever Cloud (ej: `uq8w9...`). *(¡Atención! No es `root`)*.
   - **Password:** Tu contraseña alfanumérica asignada.

---

### Método A: Variables de Entorno en Render (100% Automático)
Esta es la mejor forma porque queda guardada para siempre en la nube:
1. Abrí tu panel de control en [dashboard.render.com](https://dashboard.render.com/).
2. Hacé clic en tu Web Service (`bda-dashboard-futbol`).
3. En el menú de la izquierda, seleccioná **Environment**.
4. Hacé clic en **Add Environment Variable** y agregá estas 5 variables con los datos de Clever Cloud:
   - `MYSQL_HOST` = Tu host de Clever Cloud
   - `MYSQL_PORT` = `3306`
   - `MYSQL_USER` = Tu usuario de Clever Cloud
   - `MYSQL_PASSWORD` = Tu contraseña de Clever Cloud
   - `MYSQL_DATABASE` = Tu nombre de base de datos de Clever Cloud
5. Hacé clic en **Save Changes**. Render reiniciará la app automáticamente y desde ese momento iniciará conectada a Clever Cloud en verde.

---

### Método B: Formulario en Vivo en la Barra Lateral
Si no querés entrar a Render o estás probando en vivo:
1. En la aplicación web, en la barra lateral izquierda, seleccioná en *Origen de Datos:* **`☁️ Clever Cloud MySQL (Nube)`**.
2. Verás un panel desplegable titulado: **`☁️ Configurar Clever Cloud MySQL`**.
3. Pegá allí los 5 datos (Host, Puerto 3306, Usuario, Contraseña y Base de Datos).
4. Presioná el botón: **`💾 Guardar y Conectar`**.
5. La app validará la conexión en vivo:
   - Si todo es correcto, aparecerá el cartel verde: `✓ Conexión exitosa a Clever Cloud`.
   - Si la base aún no tiene las tablas, te mostrará la opción de migrar en 1 clic.

---

### Cómo poblar la base si está vacía (Migración en 1 Clic)
Si acabás de crear la base en Clever Cloud y nunca le cargaste las tablas ni los partidos:
1. En la barra lateral, presioná **`⚡ Test Conexión`**.
2. La app detectará que conectó pero que la tabla `FACT_COMPETENCIA` no existe, y mostrará el botón amarillo:  
   👉 **`🚀 Cargar Data Mart en Clever Cloud (1 Clic)`**.
3. Hacé clic en el botón.
4. Una barra de progreso en vivo creará:
   - Las 4 dimensiones (`DIM_TIEMPO`, `DIM_EQUIPO`, `DIM_DIVISION`, `DIM_PAIS`).
   - La tabla de hechos `FACT_COMPETENCIA` con sus índices.
   - Cargará los **132.256 partidos reales**.
   - Creará la vista analítica `V_PARTICIPACION`.
5. Al finalizar, la app se recargará y el indicador superior cambiará a:  
   🟢 **`Clever Cloud MySQL (Nube)`**.

---

### El Mecanismo de Failsafe y Contingencia Offline
> [!IMPORTANT]
> **Tranquilidad absoluta para la exposición:**  
> Si el día de la presentación el WiFi de la universidad funciona lento, Clever Cloud tarda en responder o la red bloquea el puerto 3306:
> 1. El tablero **nunca se colgará ni mostrará un error**.
> 2. Conmutará automáticamente o podés seleccionar en el menú lateral:  
>    **`🛡️ Contingencia Offline (SQLite Local)`**.
> 3. En modo offline, el dashboard corre sobre el archivo `dw_contingencia.sqlite` empaquetado en el contenedor, que contiene **exactamente los mismos 132.256 partidos** y responde en menos de 10 milisegundos.

---

## 5. Guion de Defensa Oral Sugerido (10 Minutos)

Para estructurar una exposición brillante frente al profesor:

| Minuto | Acción en Pantalla | Qué decir |
|---|---|---|
| **00:00 - 02:00** | Abrir la app en Render en pantalla completa. Mostrar el badge verde de Clever Cloud / SQLite. | *"Buenas tardes profesor. Para la defensa final desplegamos nuestro Data Mart multidimensional bajo la metodología HEFESTO v2 en la nube utilizando Render y Clever Cloud MySQL. El modelo almacena 132.256 partidos con granularidad de un partido por fila en FACT_COMPETENCIA."* |
| **02:00 - 05:00** | Recorrer Pregunta 1 (Evolución Elo) y Pregunta 2 (Clásicos). Cambiar los filtros de club en vivo. | *"Nuestra Pregunta 1 analiza la evolución de rendimiento. Aquí vemos al Nottingham Forest con sus bandas de Elo máximo y mínimo. Si queremos ver qué pasó con el Arsenal o el Real Madrid, simplemente cambiamos el filtro y en milisegundos Render recompila la consulta SQL y Plotly dibuja las curvas."* |
| **05:00 - 07:00** | Mostrar Pregunta 3 (Localía) y Pregunta 4 (Paridad de Ligas). Mostrar la Pestaña "Consulta SQL en Vivo". | *"La Pregunta 3 demuestra empíricamente la ventaja de jugar de local en Europa (45% vs 28%). Si abrimos la pestaña de Consulta SQL, podemos auditar la sentencia que se ejecuta directamente sobre el modelo estrella y modificarla en vivo."* |
| **07:00 - 09:00** | Pasar al **Modo 2: Consola SQL Libre**. Pedirle al profesor una consulta sorpresa. | *"Profesor, diseñamos una Consola SQL Libre pensada específicamente para responder cualquier pregunta ad-hoc que usted desee hacernos. Si nos indica cualquier club, liga o rango temporal, redactamos la consulta al frente y generamos el gráfico en tiempo real."* |
| **09:00 - 10:00** | Ir a la pestaña **Conclusión de Negocio** de la Pregunta 6 o Explorador. Cierre. | *"Como conclusión metodológica, el modelo HEFESTO v2 nos permitió estructurar la toma de decisiones para sponsors y clubes con alta velocidad analítica y total resiliencia técnica. Quedamos a disposición para sus preguntas."* |

---

✅ **Repositorio GitHub Oficial:** `https://github.com/PedroGattiUCC/bda-dashboard-futbol`  
✅ **Despliegue Web en Render:** Conectado a la rama `main` del repositorio.
