import cv2
import numpy as np

def detect_and_classify_blister(thresholded_image: np.ndarray, frame_to_draw: np.ndarray) -> tuple[np.ndarray, list]:
    # Asegurarnos de que la imagen esté en escala de grises
    if len(thresholded_image.shape) == 3:
        gray = cv2.cvtColor(thresholded_image, cv2.COLOR_BGR2GRAY)
    else:
        gray = thresholded_image
    
    # 1. Aplicar umbral simple ya que la imagen esta procesada
    _, thresh = cv2.threshold(gray, 1, 255, cv2.THRESH_BINARY)
    
    # 2. Encontrar contornos
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    print(f"\n[DEBUG] Total de contornos encontrados: {len(contours)}")
    
    inspection_results = []
    output_image = frame_to_draw.copy()
    
    # 3. Procesar cada contorno
    for idx, contour in enumerate(contours, 1):
        # Calcular área
        area = cv2.contourArea(contour)
        
        # Si el área es muy pequeña, ignorar
        if area < 50:  # Ajustar según sea necesario
            continue
            
        # Dibujar contorno en verde
        cv2.drawContours(output_image, [contour], -1, (0, 255, 0), 2)
        
        # Calcular centroide para el texto
        M = cv2.moments(contour)
        if M["m00"] != 0:
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
            cv2.putText(output_image, str(idx), (cX-10, cY), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Agregar a resultados
        inspection_results.append({
            'id': idx,
            'area': round(float(area), 2),
            'status': 'Aprobado'
        })
    
    print(f"[DEBUG] Contornos válidos: {len(inspection_results)}")
    return output_image, inspection_results