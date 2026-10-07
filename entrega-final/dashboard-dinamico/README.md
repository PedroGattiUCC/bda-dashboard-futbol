# Dashboard Dinámico para la Exposición Final en Clase

Esta carpeta contiene la implementación interactiva del **Dashboard sobre el Modelo Estrella** preparada especialmente para la **defensa oral presencial** y el despliegue en la nube mediante **Render** y **Clever Cloud**, según las instrucciones del docente.

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
   *(Por defecto incluye la base local offline de contingencia con los 132.256 partidos reales).*

---

### Opción 2: Despliegue en la Nube (Clever Cloud + Render)
1. **Base de Datos (Clever Cloud MySQL):** Crear el add-on MySQL gratuito y migrar los datos corriendo:
   ```bash
   python migrar_a_clevercloud.py --host <HOST> --user <USER> --password <PASSWORD> --database <DB>
   ```
2. **Servidor Web (Render):** Crear un nuevo **Web Service** conectado a tu GitHub con:
   - **Build Command:** `pip install -r entrega-final/dashboard-dinamico/requirements.txt`
   - **Start Command:** `cd entrega-final/dashboard-dinamico && streamlit run app.py --server.port $PORT --server.address 0.0.0.0 --server.headless true`
   - **Variables de Entorno:** Configurar `MYSQL_HOST`, `MYSQL_PORT`, `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_DATABASE`.

---

## 📚 Documentación Completa para la Defensa

Para leer la explicación detallada de la arquitectura, el paso a paso de configuración y el **guión para responder las preguntas del profesor en vivo al frente del aula**, consultar:

👉 **[`MANUAL_EXPOSICION_Y_DESPLIEGUE.md`](MANUAL_EXPOSICION_Y_DESPLIEGUE.md)**

---

## 📁 Archivos de esta Carpeta

- **`app.py`**: Tablero dinámico interactivo con controles en tiempo real, editor SQL en vivo y generación automática de gráficos.
- **`consultas_base.py`**: Definición de las 12 preguntas de negocio oficiales, plantillas ad-hoc y diccionario de datos del DW.
- **`conexion.py`**: Administrador de conexiones multientorno (Clever Cloud MySQL, MySQL local y SQLite offline).
- **`migrar_a_clevercloud.py`**: Script de migración en lotes a la base remota de Clever Cloud.
- **`exportar_dump_sql.py`**: Exportador de dump SQL compatible con phpMyAdmin.
- **`generar_sqlite_contingencia.py`**: Generador del respaldo local autónomo de 132.256 partidos.
- **`requirements.txt`**: Librerías necesarias para Render y entorno local.
- **`render.yaml`** y **`Procfile`**: Archivos de infraestructura como código para Render.
- **`MANUAL_EXPOSICION_Y_DESPLIEGUE.md`**: Guía pedagógica y táctica para la exposición oral.
