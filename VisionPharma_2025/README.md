# VisionPharma 2025

Sistema de inspección farmacéutica con visión artificial.

## Configuración del Entorno

### Requisitos Previos

- **Python 3.11 o 3.12** (recomendado)
- Python 3.14 puede tener problemas de compatibilidad con numpy y otras librerías científicas

### Instalación Rápida

1. **Crear entorno virtual:**
   ```bash
   python -m venv venv
   ```

2. **Activar entorno virtual:**
   - Windows PowerShell: `.\venv\Scripts\Activate.ps1`
   - Windows CMD: `venv\Scripts\activate.bat`
   - Linux/Mac: `source venv/bin/activate`

3. **Instalar dependencias:**
   ```bash
   pip install -r requeriments.txt
   ```

### Solución de Problemas

Si tienes problemas con Python 3.14:

1. **Instalar Python 3.11 o 3.12** desde [python.org](https://python.org)
2. **Crear nuevo entorno virtual** con la versión compatible
3. **Ejecutar el script de configuración:**
   ```bash
   python setup_environment.py
   ```

### Estructura del Proyecto

```
VisionPharma_2025/
├── src/
│   ├── core/          # Módulos principales
│   ├── data/          # Gestión de datos
│   └── ui/            # Interfaz de usuario
├── config/            # Configuraciones
├── data/              # Base de datos y reportes
├── tests/             # Pruebas unitarias
└── main.py           # Punto de entrada
```

### Ejecutar la Aplicación

#### Opción 1: Comandos Manuales
```bash
# Activar entorno virtual
.\venv311\Scripts\Activate.ps1

# Ejecutar aplicación web
python app.py
```

#### Opción 2: Script Automático
```bash
# Windows (doble clic o desde terminal)
start_app.bat

# PowerShell
.\start_app.ps1
```

#### Acceso a la Aplicación
- **Interfaz Web**: http://localhost:5000
- **Aplicación de Escritorio**: `python main.py`

## Desarrollo

Para contribuir al proyecto, asegúrate de:

1. Usar Python 3.11 o 3.12
2. Activar el entorno virtual
3. Instalar las dependencias de desarrollo
4. Ejecutar las pruebas antes de hacer commit

## Dependencias Principales

- **OpenCV**: Procesamiento de imágenes
- **NumPy**: Cálculos numéricos
- **Pandas**: Manipulación de datos
- **Matplotlib**: Visualización
- **PyQt6**: Interfaz gráfica
- **psycopg2**: Conexión a PostgreSQL
