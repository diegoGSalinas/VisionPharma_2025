import cv2
import numpy as np

# Parámetros (Ajustados para tu imagen de pastillas rojas)
BLISTER_AREA_MIN = 8000     
BLISTER_AREA_MAX = 40000    
CIRCULARITY_THRESHOLD = 0.50 


def detect_and_classify_blister(thresholded_image: np.ndarray, frame_to_draw: np.ndarray) -> tuple[np.ndarray, list]:
    
    # Dependemos ahora del suavizado en 'processing.py' y un filtro estricto de área.
    
    # 1. Detección de Contornos (PB-03)
    
    # Apertura para eliminar pequeños contornos ruidosos
    kernel = np.ones((5,5),np.uint8) 
    processed_thresh = cv2.morphologyEx(thresholded_image, cv2.MORPH_OPEN, kernel)
    
    # cv2.RETR_EXTERNAL: Recupera solo los contornos externos limpios.
    contours, _ = cv2.findContours(processed_thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    inspection_results = []
    output_image = frame_to_draw.copy()

    # 2. Análisis Geométrico y Clasificación (PB-04, PB-05)
    for i, contour in enumerate(contours):
        area = cv2.contourArea(contour)
        is_defective = False
        defect_type = "Aprobado"
        
        # --- FILTRADO CRÍTICO: SOLO CONSIDERAR OBJETOS GRANDES (PASTILLAS) ---
        if area < BLISTER_AREA_MIN:
             if area > 3000:
                # Objeto pequeño pero detectable: Posible Cavidad Vacía o borde sucio
                is_defective = True
                defect_type = "Cavidad Vacía"
             else:
                continue # Ignorar ruido
        
        elif area > BLISTER_AREA_MAX:
             continue # Ignorar el objeto si es demasiado grande
        
        # Clasificación para contornos dentro del rango de área.
        perimeter = cv2.arcLength(contour, closed=True)
        circularity = (4 * np.pi * area) / (perimeter ** 2) if perimeter > 0 else 0

        # CLASIFICACIÓN DE PASTILLA DEFORMADA
        if circularity < CIRCULARITY_THRESHOLD:
            is_defective = True
            defect_type = "Pastilla Deformada"
        
        # 3. Marcado Visual (PB-06)
        if is_defective:
            color = (0, 0, 255) # Rojo BGR
            thickness = 3
        else:
            color = (0, 255, 0) # Verde BGR
            thickness = 3
        
        cv2.drawContours(output_image, [contour], -1, color, thickness)
        
        inspection_results.append({
            'id': i,
            'area': area,
            'circularity': circularity,
            'status': defect_type
        })
    
    return output_image, inspection_results