import numpy as np
import cv2 # Para el tipo de dato np.ndarray
from .processing import preprocess_image
from .detection import detect_and_classify_blister

class InspectionAgent:
    """
    Orquesta el pipeline completo de Visión Artificial, devolviendo pasos intermedios.
    """
    def __init__(self):
        # Inicialización
        pass
        
    def process_frame_step_by_step(self, frame_original: np.ndarray) -> tuple[np.ndarray, dict, list]:
        """
        Ejecuta el pipeline de visión y devuelve las imágenes clave en cada paso.
        
        Returns:
            tuple: (frame_final, dict_imagenes_pasos, lista_resultados)
        """
        if frame_original is None:
            return None, {}, []

        # Diccionario para almacenar las imágenes de cada paso
        step_images = {'original': frame_original.copy()}

        # 1. Procesamiento (PB-02)
        frame_procesado = preprocess_image(frame_original)
        step_images['grayscale_filtered'] = frame_procesado
        
        # 2. Detección y Clasificación (PB-03, PB-04, PB-05)
        
        # * Paso Intermedio: Umbralización *
        # Se necesita la Umbralización (Segmentation) para la detección de contornos.
        # La implementamos para aislar el paso visualmente.
        _, thresh_image = cv2.threshold(frame_procesado, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        step_images['thresholded'] = thresh_image

        # 3. Detección y Clasificación
        # Nota: La función detect_and_classify_blister no toma el frame_procesado, sino el umbralizado.
        # detection.py recibe el umbralizado.
        
        # Copia del original para el frame final (donde se dibujan los contornos)
        frame_para_dibujo = frame_original.copy()
        
        # **Llamada a la Detección**
        frame_salida_final, results = detect_and_classify_blister(thresh_image, frame_para_dibujo)
        
        step_images['final_contours'] = frame_salida_final
        
        return frame_salida_final, step_images, results