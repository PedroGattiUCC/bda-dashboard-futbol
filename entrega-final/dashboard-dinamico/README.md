# Dashboard Dinámico para la Exposición Final en Clase
## Aplicación Web Interactiva en Streamlit + Plotly (Render & Clever Cloud MySQL)

Esta carpeta contiene la implementación del **Tablero Analítico Dinámico sobre el Modelo Estrella**, desarrollado específicamente para la **defensa oral presencial** ante la cátedra y desplegado en la nube con **Render** y **Clever Cloud**, conforme a lo solicitado por el docente.

---

## ⚡ Inicio Rápido (En 2 Minutos)

### Opción 1: Ejecución Local en tu Computadora
1. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```
2. Iniciar el servidor web:
   ```bash
   streamlit run app.py
   ```
3. La aplicación se abrirá automáticamente en tu navegador (`http://localhost:8501`).  
   *(Por defecto inicia en Modo Contingencia Offline con los 132.256 partidos reales).*

---

### Opción 2: Despliegue en la Nube (Clever Cloud + Render)
1. **Base de Datos (Clever Cloud MySQL):** Crear el add-on MySQL gratuito en [clever-cloud.com](https://www.clever-cloud.com/).
2. **Servidor Web (Render):** Crear un nuevo **Web Service** conectado a tu GitHub (`PedroGattiUCC/bda-dashboard-futbol`) con:
   - **Root Directory:** `entrega-final/dashboard-dinamico`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `streamlit run app.py --server.port $PORT --server.address 0.0.0.0 --server.headless true`
   - **Variables de Entorno (Environment Variables):**
     - `MYSQL_HOST`: Host de Clever Cloud (ej: `bxxxx-mysql.services.clever-cloud.com`)
     - `MYSQL_PORT`: `3306`
     - `MYSQL_USER`: Usuario de Clever Cloud (ej: `uxxxxxxxx`)
     - `MYSQL_PASSWORD`: Contraseña de Clever Cloud
     - `MYSQL_DATABASE`: Nombre de la base de datos de Clever Cloud (ej: `bxxxxxxxx`)

---

## 🚨 Solución al Error de Clever Cloud en Render

Si en Render seleccionás **Clever Cloud MySQL** y te arroja error, se debe a una de las siguientes razones:

### 1. La Base de Datos en Clever Cloud está vacía (Aún no tiene las tablas)
- **Causa:** Creaste la base en Clever Cloud pero todavía no creaste las tablas ni cargaste los partidos. Al consultar, MySQL arroja: `Table 'FACT_COMPETENCIA' doesn't exist`.
- **Solución con 1 Clic desde la propia Web:**
  1. En la barra lateral, seleccioná **☁️ Clever Cloud MySQL**.
  2. Hacé clic en **"⚡ Test Conexión"**.
  3. La app detectará la conexión y te mostrará el botón: **"🚀 Cargar Data Mart en Clever Cloud (1 Clic)"**.
  4. Hacé clic: la aplicación en Render tomará los datos del archivo local y poblará las tablas e índices en Clever Cloud en vivo con una barra de progreso.

### 2. Nombre de Base de Datos Incorrecto
- **Causa:** En Clever Cloud la base **no se llama `dw_competencia_futbol`**. Clever Cloud genera un nombre automático tipo `bxxxxxxxx` (ej: `b8q3j7kf...`).
- **Solución:** Copiá el nombre exacto de la base desde el panel de Clever Cloud y configuralo en las credenciales.

### 3. Plan B: Modo Contingencia Offline
Si la red de la facultad bloquea el puerto 3306 o no tenés internet en el proyector:
- En la barra lateral, seleccioná **`🛡️ Contingencia Offline (SQLite Local)`**.
- La app conmuta al instante y corre sobre el archivo `dw_contingencia.sqlite` (que contiene los 132.256 partidos reales), garantizando una exposición 100 % fluida.

---

## 🔄 ¿Cómo Trabaja Render Tras Bambalinas al Filtrar o Cambiar Consultas?

Render aloja la aplicación en un contenedor Linux en la nube. Cuando un usuario interactúa con la aplicación (mueve un slider, elige un equipo o edita una consulta SQL), el ciclo de trabajo es el siguiente:

```
[Navegador del Usuario] 
      │ (1) Mueve un slider o modifica código SQL
      ▼ 
[Túnel WebSocket] ──────────► [Servidor Render (Streamlit)]
                                    │ (2) Se activa el "Rerun" reactivo de app.py
                                    │ (3) consultas_base.py genera la sentencia SQL
                                    ▼
                             [Motor de Base de Datos]
                             • Clever Cloud (TCP/SSL Puerto 3306)
                             • SQLite Local (Filesystem del contenedor)
                                    │ (4) Ejecuta SELECT sobre FACT_COMPETENCIA / V_PARTICIPACION
                                    ▼
                             [DataFrame en Memoria (Pandas)]
                                    │ (5) Calcula KPIs y deltas
                                    ▼
                             [Motor Gráfico (Plotly)]
                                    │ (6) Compila gráficos en objetos JSON / WebGL
                                    ▼
[Navegador del Usuario] ◄─── [Deltas WebSocket] (Renderiza gráficos y tablas en ms)
```

1. **Interacción:** El navegador no recarga la página; envía el nuevo estado por WebSocket.
2. **Re-ejecución reactiva:** Streamlit re-ejecuta `app.py` inyectando los parámetros del widget.
3. **Generación SQL:** `consultas_base.py` ensambla la consulta sobre el modelo estrella (`FACT_COMPETENCIA` o `V_PARTICIPACION`).
4. **Consulta a la base:** Se ejecuta en milisegundos en Clever Cloud o SQLite.
5. **Generación de gráficos:** Plotly genera múltiples visualizaciones interactivas (curvas con bandas min-max, barras apiladas, matrices cuadrantes).
6. **Respuesta en pantalla:** Los gráficos y tablas se actualizan fluidamente frente a la audiencia.

---

## 📖 Cómo Usar el Tablero en la Exposición Frente al Profesor

1. **Abrir la aplicación en pantalla completa.**
2. **Verificar el indicador verde de conexión** en la esquina superior derecha.
3. **Navegar por las 6 Preguntas Oficiales:**
   - **P1 (Evolución Elo):** Mostrá cómo creció Nottingham Forest (+314 pts). Si el profe pide otro club, escribí `Arsenal` o `Real Madrid` y cambiá la ventana de años frente a él.
   - **P2 (Clásicos):** Mostrá los derbis europeos. Activá `Comparar enfrentamiento libre entre 2 clubes` para comparar cualquier par de clubes en vivo.
   - **P3 (Ventaja de Localía):** Mostrá el ranking de ventaja en puntos porcentuales, la comparativa de goles local vs visitante y la dona continental.
   - **P4 (Paridad de Ligas):** Mostrá el ranking de desvío de brecha Elo y el cuadrante de paridad que demuestra por qué las segundas divisiones son más parejas.
   - **P5 (Tarjetas):** Mostrá el ranking de amarillas/rojas y el clúster disciplinario de la península ibérica vs Inglaterra y Alemania.
   - **P6 (Mejores Visitantes):** Mostrá el ranking de efectividad a domicilio de Porto, PSV y Celtic, y la matriz de goles fuera de casa.
4. **Modificación de SQL en Vivo:** En la pestaña `💻 Consulta SQL en Vivo`, activá el editor, modificá una cláusula ante el docente y re-ejecutá para mostrar que los datos son dinámicos y trazables al modelo estrella.
5. **Consola SQL Libre:** Si el profesor pide una consulta libre fuera de las 6, cambias al modo *Consola SQL Libre* y usás el diccionario de tablas y el constructor de gráficos al vuelo.

---

## 📁 Archivos de esta Carpeta

- **`app.py`**: Aplicación web principal en Streamlit con interfaz reactiva, KPIs y gráficos Plotly.
- **`consultas_base.py`**: Catálogo de preguntas de negocio, constructores dinámicos de SQL y diccionario del DW.
- **`conexion.py`**: Motor de conexión con soporte seguro para Clever Cloud (URL.create), SQLite y migración en 1 clic.
- **`migrar_a_clevercloud.py`**: Script de migración por terminal a Clever Cloud MySQL.
- **`exportar_dump_sql.py`**: Generador de dump SQL para phpMyAdmin.
- **`dw_contingencia.sqlite`**: Base local con los 132.256 partidos reales para contingencia sin internet.
- **`MANUAL_EXPOSICION_Y_DESPLIEGUE.md`**: Guía pedagógica y manual táctico de defensa oral.
- **`requirements.txt`**: Dependencias para Render.
- **`render.yaml`** y **`Procfile`**: Configuración de despliegue en la nube.
