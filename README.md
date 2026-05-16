# LinProd - Simulador de Línea de Producción

Un simulador interactivo de sistemas de producción en tiempo real, construido con Python y tecnologías web modernas. Permite modelar, configurar y analizar líneas de producción complejas con múltiples procesos y tareas.

## 📋 Descripción

**LinProd** es una herramienta educativa y de análisis que simula el comportamiento de una línea de producción industrial. Permite:

- **Crear procesos** con múltiples tareas encadenadas
- **Configurar parámetros** de tiempo de procesamiento
- **Ejecutar simulaciones** con control en tiempo real (play/pausa)
- **Analizar estadísticas** detalladas de rendimiento y cuellos de botella
- **Visualizar dinámicamente** el estado de cada proceso y tarea
- **Reconfigurar la cantidad** de productos a procesar

## ✨ Características

### Funcionalidades Principales
- 🏭 **Gestión de Procesos**: Crear y reordenar procesos en la línea de producción
- 📊 **Simulación en Tiempo Real**: Ejecución con visualización instantánea
- ⏸️ **Control de Simulación**: Play, pausa y reinicio de simulaciones
- 📈 **Análisis Estadístico**: Métricas detalladas de cada tarea
- 🎯 **Identificación de Cuellos de Botella**: Detecta tareas con mayores tiempos de espera
- 🔄 **Tareas Encadenadas**: Soporte para múltiples tareas por proceso

### Métricas Disponibles
- Tiempo del primer producto salido de la línea
- Tiempo del último producto
- Tiempo promedio de salida
- Tiempo de espera promedio por tarea
- Máximo tiempo de espera
- Cuello de botella de la línea de producción

## 🚀 Instalación y Puesta en Marcha

### Requisitos Previos
- **Python 3.8+**
- **pip** (gestor de paquetes de Python)

### Pasos de Instalación

1. **Clona o descarga el repositorio**
   ```bash
   cd /ruta/al/proyecto/proyecto-2-modelacion
   ```

2. **Crea un entorno virtual** (recomendado)
   ```bash
   python3 -m venv venv
   ```

3. **Activa el entorno virtual**
   
   En Linux/Mac:
   ```bash
   source venv/bin/activate
   ```
   
   En Windows:
   ```bash
   venv\Scripts\activate
   ```

4. **Instala las dependencias**
   ```bash
   pip install flask flask-socketio python-socketio python-engineio
   ```

   O usa este comando si existe un `requirements.txt`:
   ```bash
   pip install -r requirements.txt
   ```

### Ejecución de la Aplicación

**Para desarrollo:**
```bash
python app.py
```

**Para producción:**
```bash
python prod.py
```

La aplicación estará disponible en: **http://localhost:5000**

## 📖 Guía de Uso

### 1. Accede a la Aplicación
Abre tu navegador en `http://localhost:5000`

### 2. Crear un Proceso
- Ve a la sección **"Procesos"**
- Ingresa el nombre del proceso
- Define la cantidad inicial de productos
- Añade tareas especificando el tiempo de procesamiento para cada una
- Haz clic en "Crear Proceso"

### 3. Configurar Tareas
- Desde la sección **"Tareas"** puedes:
  - Ver todas las tareas configuradas
  - Modificar tiempos de procesamiento
  - Ver qué proceso contiene cada tarea

### 4. Ejecutar la Simulación
- Ve a **"Simulación"**
- Presiona **"Iniciar"** para comenzar
- Usa **"Pausar"** para detener temporalmente
- Usa **"Reiniciar"** para ejecutar nuevamente con la misma configuración
- Usa **"Reset"** para limpiar toda la línea de producción

### 5. Analizar Resultados
- Una vez finalizada la simulación, ve a **"Estadísticas"**
- Visualiza:
  - Tiempos de salida de productos
  - Tiempos de espera por tarea
  - Identificación del cuello de botella
  - Estadísticas completas por proceso

## 📁 Estructura del Proyecto

```
proyecto-2-modelacion/
├── app.py                 # Aplicación Flask principal
├── prod.py               # Lógica de simulación y estructuras de datos
├── templates/            # Plantillas HTML
│   ├── base.html         # Plantilla base
│   ├── index.html        # Página principal
│   ├── procesos.html     # Gestión de procesos
│   ├── tareas.html       # Gestión de tareas
│   ├── simulacion.html   # Control de simulación
│   └── estadisticas.html # Visualización de resultados
├── static/               # Archivos estáticos
│   ├── css/
│   │   └── style.css     # Estilos de la aplicación
│   └── js/
│       ├── main.js       # Lógica principal del frontend
│       ├── procesos.js   # Lógica de gestión de procesos
│       ├── tareas.js     # Lógica de gestión de tareas
│       ├── procesos-config.js  # Configuración de procesos
│       └── estadisticas.js     # Visualización de estadísticas
```

## 🏗️ Arquitectura Técnica

### Backend (Python)
- **Framework**: Flask
- **Comunicación en Tiempo Real**: Flask-SocketIO
- **Concurrencia**: Threading de Python
- **Estructuras de Datos**: Listas enlazadas personalizadas

### Frontend
- **HTML5** para estructura
- **CSS** para estilos
- **JavaScript** para interactividad
- **WebSockets** (SocketIO) para comunicación bidireccional

## 🔧 API REST

### Endpoints Principales

**Procesos:**
- `POST /api/crear-proceso` - Crear nuevo proceso
- `GET /api/procesos-creados` - Obtener lista de procesos
- `POST /api/mover-proceso` - Reordenar procesos

**Simulación:**
- `POST /api/iniciar` - Iniciar simulación
- `POST /api/pausar` - Pausar/reanudar simulación
- `POST /api/reiniciar` - Reiniciar simulación
- `POST /api/reset-linea` - Limpiar la línea de producción
- `GET /api/estado` - Obtener estado actual

**Tareas:**
- `POST /api/actualizar-tarea` - Modificar tiempo de procesamiento
- `GET /api/estadisticas` - Obtener estadísticas finales

## 🎯 Ejemplo de Uso

1. **Crea una línea de producción simple:**
   - Proceso 1: "Corte" con 1 tarea (5 segundos)
   - Proceso 2: "Ensamble" con 1 tarea (8 segundos)
   - Proceso 3: "Empaque" con 1 tarea (3 segundos)
   - Cantidad de productos: 10

2. **Ejecuta la simulación** y observa cómo los productos avanzan

3. **Revisa las estadísticas** para identificar dónde se concentran los retrasos

## 📝 Notas Técnicas

- La simulación utiliza **threading** para ejecutar tareas en paralelo
- Cada proceso y tarea se ejecuta en su propio thread
- La comunicación entre cliente y servidor es bidireccional mediante WebSockets
