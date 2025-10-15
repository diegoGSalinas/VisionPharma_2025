import numpy as np
import cv2
from .processing import preprocess_image
from .detection import detect_and_classify_blister
from .capture import CameraController, MockImageReader
from .ContadorContornos import ContadorContornos  # Importar la nueva clase

class InspectionAgent:
    """
    Compatible con el modo Web (sin fuente inyectada) y modo Escritorio (con fuente inyectada).
    """
    
    def __init__(self, image_source=None):
        self.image_source = image_source
        
    def process_frame_step_by_step(self, frame_original: np.ndarray) -> tuple[np.ndarray, dict, list]:
        """
        Ejecuta el pipeline de visión y devuelve las imágenes clave en cada paso.
        """
        if frame_original is None:
            return None, {}, []

        step_images = {'original': frame_original.copy()}

        # 1. Convertir a escala de grises
        frame_gray = cv2.cvtColor(frame_original, cv2.COLOR_BGR2GRAY)
        step_images['grayscale'] = cv2.cvtColor(frame_gray, cv2.COLOR_GRAY2BGR)
        
        # 2. Procesamiento y umbralización
        frame_procesado = preprocess_image(frame_original)
        
        if frame_procesado is not None and frame_procesado.size > 0:
            # Crear una imagen de fondo negro
            thresh_vis = np.zeros((frame_original.shape[0], frame_original.shape[1], 3), dtype=np.uint8)
            
            # Aplicar un umbral más bajo para capturar más detalles
            _, thresh = cv2.threshold(frame_procesado, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # Encontrar contornos
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Dibujar contornos en verde
            cv2.drawContours(thresh_vis, contours, -1, (0, 255, 0), 2)
            
            # Rellenar los contornos con un verde semi-transparente
            for cnt in contours:
                area = cv2.contourArea(cnt)
                if 300 < area < 50000:  # Ajustar según el tamaño esperado
                    mask = np.zeros_like(thresh)
                    cv2.drawContours(mask, [cnt], -1, 255, -1)
                    thresh_vis[mask > 0] = [0, 100, 0]  # Verde oscuro para el relleno
            
            # Mezclar con la imagen original para mejor contexto
            alpha = 0.7
            beta = 1 - alpha
            blended = cv2.addWeighted(cv2.cvtColor(frame_gray, cv2.COLOR_GRAY2BGR), alpha, 
                                    thresh_vis, beta, 0)
            
            step_images['thresholded'] = blended
            thresh = cv2.cvtColor(thresh_vis, cv2.COLOR_BGR2GRAY)
        else:
            step_images['thresholded'] = np.zeros((frame_original.shape[0], frame_original.shape[1], 3), 
                                                dtype=np.uint8)

        # 3. Detección y Clasificación
        frame_para_dibujo = frame_original.copy()
        frame_salida_final, results = detect_and_classify_blister(thresh, frame_para_dibujo)
        
        # Usar el contador de contornos
        imagen_con_contornos, total_contornos = ContadorContornos.contar_contornos_coloreados(frame_salida_final)
        print(f"[DEBUG] Contornos detectados: {total_contornos}")
        
        # Invertir colores para mejor visualización
        frame_final = cv2.bitwise_not(imagen_con_contornos)
        step_images['final_contours'] = frame_final

        # Asegurarse de que los resultados estén en el formato correcto
        formatted_results = []
        for i, result in enumerate(results):
            formatted_results.append({
                'id': i + 1,
                'area': round(float(result.get('area', 0)), 2),
                'circularity': round(float(result.get('circularity', 0)), 4),
                'status': result.get('status', 'Desconocido')
            })
        
        # Ordenar resultados por área (de mayor a menor)
        formatted_results.sort(key=lambda x: x['area'], reverse=True)
        
        return frame_final, step_images, formatted_results

    def run_pipeline_step(self) -> tuple[np.ndarray, dict, list, bool]:
        """
        Captura un frame de la fuente de imagen y ejecuta el pipeline.
        Usado principalmente por la aplicación de escritorio.
        """
        if self.image_source is None:
            return None, {}, [], False
            
        frame = self.image_source.capture()
        if frame is None:
            return None, {}, [], False
            
        frame_result, step_images, results = self.process_frame_step_by_step(frame)
        return frame_result, step_images, results, True