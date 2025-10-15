import os
import cv2
import time
import numpy as np
from flask import Flask, render_template, request, url_for, send_from_directory, jsonify
from werkzeug.utils import secure_filename
from src.data.local_storage import LocalStorage
from src.core.inspection_agent import InspectionAgent
from src.core.capture import CameraController, MockImageReader

# --- CONFIGURACIÓN DE RUTAS ---
# Rutas relativas a donde se ejecuta el script (D:\git\VisionPharma_2025)
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

# --- VARIABLES DE ESTADO (Para el control de modo) ---
USE_CAMERA_REAL = False 
CAMERA_INDEX = 0
AGENT_VERSION = "1.0.1"

# --- CONFIGURACIÓN DE FLASK ---
app = Flask(__name__, 
            # ⬇️ CORRECCIÓN: Apunta directamente a la subcarpeta 'src/web_interface/templates' ⬇️
            template_folder=os.path.join(PROJECT_ROOT, 'src', 'web_interface', 'templates'), 
            
            # La carpeta estática está en la raíz
            static_folder=os.path.join(PROJECT_ROOT, 'static'))

UPLOAD_FOLDER = os.path.join(PROJECT_ROOT, 'static', 'uploads')
RESULTS_FOLDER = os.path.join(PROJECT_ROOT, 'static', 'results')

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['RESULTS_FOLDER'] = RESULTS_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULTS_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# Instancias globales
agent = InspectionAgent() 
storage = LocalStorage() 

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ----------------------------------------------------------------------
# ENDPOINTS WEB Y DE PROCESAMIENTO
# ----------------------------------------------------------------------

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    # Inicialización para evitar NameError en GET
    step_image_urls = None
    results_data = None
    error_message = None
    debug_info = None

    if request.method == 'POST':
        # Validación temprana y segura del archivo subido para evitar KeyError
        file = request.files.get('file')
        if not file:
            # DEBUG: imprimir información de la petición para entender por qué falta el archivo
            try:
                print("[DEBUG] request.content_type:", request.content_type)
                print("[DEBUG] request.files keys:", list(request.files.keys()))
                print("[DEBUG] request.form keys:", list(request.form.keys()))
                # también mostrar headers relevantes
                print("[DEBUG] headers Content-Type:", request.headers.get('Content-Type'))
            except Exception:
                pass
            error_message = "Error crítico: El archivo 'file' no fue encontrado en la solicitud POST."
            # Preparar info que mostraremos en la plantilla para debugging en el navegador
            try:
                debug_info = {
                    'content_type': request.content_type,
                    'files_keys': list(request.files.keys()),
                    'form_keys': list(request.form.keys()),
                    'header_content_type': request.headers.get('Content-Type')
                }
            except Exception:
                debug_info = None

            return render_template('index.html', step_image_urls=step_image_urls, results_data=results_data, error=error_message, debug_info=debug_info)

        if file.filename == '':
            error_message = "No se seleccionó ningún archivo."
            return render_template('index.html', step_image_urls=step_image_urls, results_data=results_data, error=error_message, debug_info=None)

        if not allowed_file(file.filename):
            error_message = "Formato de archivo no permitido. Extensiones permitidas: png, jpg, jpeg."
            return render_template('index.html', step_image_urls=step_image_urls, results_data=results_data, error=error_message, debug_info=None)

        if not error_message:
            # Lógica de procesamiento y guardado exitosa
            filename_base = secure_filename(file.filename)
            timestamp = int(time.time() * 1000)
            filename = f"input_{timestamp}_{filename_base}"
            input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(input_path)

            original_frame = cv2.imread(input_path)

            if original_frame is not None:
                try:
                    # 2. Ejecutar el Pipeline de Visión
                    _, step_images, results_list = agent.process_frame_step_by_step(original_frame)
                    storage.save_inspection_batch(results_list)
                    
                    step_image_urls = {}
                    for step_name, img_data in step_images.items():
                        # Asegurarse de que la imagen tenga 3 canales para guardar como JPG
                        if isinstance(img_data, np.ndarray) and img_data.ndim == 2:
                            img_data = cv2.cvtColor(img_data, cv2.COLOR_GRAY2BGR)

                        output_filename = f"{step_name}_{timestamp}.jpg"
                        output_path = os.path.join(app.config['RESULTS_FOLDER'], output_filename)
                        try:
                            ok = cv2.imwrite(output_path, img_data, [cv2.IMWRITE_JPEG_QUALITY, 95])
                        except Exception as write_exc:
                            ok = False
                            print(f"[ERROR] Al guardar imagen {output_path}: {write_exc}")

                        if not ok:
                            print(f"[WARN] cv2.imwrite falló para: {output_path}")
                        else:
                            print(f"[INFO] Imagen guardada: {output_path}")

                        # Usar el endpoint 'static' estándar para construir la URL
                        step_image_urls[step_name] = url_for('static', filename=f'results/{output_filename}')

                    # DEBUG: Mostrar en consola las URLs devueltas a la plantilla
                    try:
                        print(f"[DEBUG] step_image_urls = {step_image_urls}")
                    except Exception:
                        pass
                    
                    results_data = results_list
                    
                except Exception as e:
                    # Log en servidor, pero no exponer stacktrace completo al usuario
                    import traceback
                    traceback.print_exc()
                    error_message = "Error interno durante el procesamiento de la imagen. Revise los logs del servidor." 
                finally:
                    if os.path.exists(input_path):
                        os.remove(input_path)
            else:
                error_message = "No se pudo leer la imagen con OpenCV después de la subida."

    # Retorno final para GET y POST
    return render_template('index.html', 
                           step_image_urls=step_image_urls, 
                           results_data=results_data,
                           error=error_message)

# Endpoint para servir archivos estáticos
@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory(app.static_folder, filename)

# ----------------------------------------------------------------------
# ENDPOINTS DE CONTROL (API)
# ----------------------------------------------------------------------

@app.route('/api/status', methods=['GET'])
def api_status():
    """Devuelve el estado actual del sistema (versión y modo)."""
    return jsonify({
        "status": "Ready",
        "version": AGENT_VERSION,
        "mode": "camera" if USE_CAMERA_REAL else "mock"
    })

@app.route('/api/config/mode', methods=['POST'])
def api_config_mode():
    """API para cambiar el modo entre Cámara Real y Mock."""
    global USE_CAMERA_REAL
    try:
        data = request.get_json()
        use_camera = data.get('use_camera', False)
        
        USE_CAMERA_REAL = bool(use_camera)

        return jsonify({
            "success": True,
            "new_mode": "camera" if USE_CAMERA_REAL else "mock"
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


if __name__ == '__main__':
    app.run(debug=True, port=5000)