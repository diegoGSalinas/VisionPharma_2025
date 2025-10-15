import os
import cv2
import time
import numpy as np
from flask import Flask, render_template, request, url_for, send_from_directory
from werkzeug.utils import secure_filename

# Importar los módulos del CORE
from src.core.inspection_agent import InspectionAgent

# --- Configuración de Flask ---
app = Flask(__name__, 
            template_folder='src/web_interface/templates', 
            static_folder='static')

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(PROJECT_ROOT, 'static', 'uploads')
RESULTS_FOLDER = os.path.join(PROJECT_ROOT, 'static', 'results')

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['RESULTS_FOLDER'] = RESULTS_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULTS_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Instancia del Agente fuera del request (si es posible)
agent = InspectionAgent() 

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    # Inicializar variables para la plantilla
    step_image_urls = None
    results_data = None
    
    if request.method == 'POST':
        # ... Manejo de archivo y paths (código omitido para brevedad, asume que es el mismo) ...
        if 'file' not in request.files:
             return render_template('upload.html', error="No se encontró el archivo en la solicitud.")
        file = request.files['file']
        if file.filename == '' or not allowed_file(file.filename):
             return render_template('upload.html', error="Formato de archivo no permitido.")
        
        # Generar nombre seguro y único
        filename_base = secure_filename(file.filename)
        timestamp = int(time.time() * 1000)
        filename = f"input_{timestamp}_{filename_base}"
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        file.save(input_path)

        # 1. Leer la imagen con OpenCV
        original_frame = cv2.imread(input_path)

        if original_frame is not None:
            # 2. Ejecutar el Pipeline de Visión, DEVOLVIENDO LOS PASOS
            _, step_images, results_list = agent.process_frame_step_by_step(original_frame)
            
            step_image_urls = {}
            
            # 3. Guardar las imágenes de cada paso y generar sus URLs
            for step_name, img_data in step_images.items():
                
                # Asegurar que las imágenes monocanal (gris/umbralizada) se guarden correctamente
                if img_data.ndim == 2:
                    # Convertir a BGR para guardar como JPG/PNG si es necesario, y para que el navegador lo muestre
                    img_data = cv2.cvtColor(img_data, cv2.COLOR_GRAY2BGR)

                output_filename = f"{step_name}_{timestamp}.jpg"
                output_path = os.path.join(app.config['RESULTS_FOLDER'], output_filename)
                
                cv2.imwrite(output_path, img_data, [cv2.IMWRITE_JPEG_QUALITY, 95])
                
                # Generar la URL estática
                step_image_urls[step_name] = url_for('serve_static', filename=f'results/{output_filename}')
            
            results_data = results_list
            
            # 4. Limpieza de archivo subido
            os.remove(input_path)

    # Pasar ambas variables (URLs de pasos y datos de tabla) a la plantilla
    return render_template('upload.html', step_image_urls=step_image_urls, results_data=results_data)

# Endpoint para servir archivos estáticos (código del anterior paso, necesario)
@app.route('/static/<path:filename>')
def serve_static(filename):
    # Sirve archivos desde la carpeta 'static'
    return send_from_directory(os.path.join(PROJECT_ROOT, 'static'), filename)

if __name__ == '__main__':
    # Para desarrollo.
    app.run(debug=True, port=5000)