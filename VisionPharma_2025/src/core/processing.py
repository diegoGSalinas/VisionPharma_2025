import cv2
import numpy as np

# RANGOS DE COLOR HSV (Ajustados para la imagen de Múltiples Blísters)
# El objetivo es crear una máscara que sea BLANCA donde haya pastillas/cápsulas y NEGRA en el fondo del blíster.

# --- Rango 1: Pastillas Rojas/Naranjas (Cápsulas) ---
# El color Rojo se encuentra entre 0 y 180 en el círculo de Tono (Hue) en OpenCV.
# Capturamos el rojo/naranja fuerte.
RANGO_ROJO_MIN = np.array([0, 100, 100])
RANGO_ROJO_MAX = np.array([10, 255, 255])
RANGO_NARANJA_MIN = np.array([10, 100, 100])
RANGO_NARANJA_MAX = np.array([25, 255, 255])

# --- Rango 2: Pastillas Amarillas/Verdes (Pastillas circulares) ---
RANGO_AMARILLO_MIN = np.array([20, 100, 100])
RANGO_AMARILLO_MAX = np.array([40, 255, 255])

# --- Rango 3: Pastillas/Cápsulas Blancas/Grises Claras (Segmentación por Luminosidad) ---
# Las pastillas blancas/grises tienen baja Saturación (S) y Alto Valor (V).
RANGO_BLANCO_MIN = np.array([0, 0, 180])
RANGO_BLANCO_MAX = np.array([180, 50, 255]) # Baja Saturación (0-50) y Alto Valor (180-255)


def preprocess_image(frame: np.ndarray, blur_kernel_size: tuple = (5, 5)) -> np.ndarray:
    """
    Preprocesamiento mejorado para detección de pastillas.
    Devuelve una máscara binaria optimizada para detección de contornos.
    """
    try:
        if frame is None or frame.size == 0:
            raise ValueError("La imagen de entrada está vacía o es inválida")
        
        # 1. Reducción de ruido preservando bordes
        denoised = cv2.bilateralFilter(frame, 9, 75, 75)
        
        # 2. Mejora de contraste local (CLAHE en el canal L de LAB)
        lab = cv2.cvtColor(denoised, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        cl = clahe.apply(l)
        enhanced_lab = cv2.merge((cl, a, b))
        enhanced = cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2BGR)
        
        # 3. Conversión a escala de grises
        # (Mayor peso al canal verde que suele tener mejor contraste)
        gray = cv2.cvtColor(enhanced, cv2.COLOR_BGR2GRAY)
        
        # 4. Aplicar desenfoque gaussiano para reducir ruido
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # 5. Ecualización del histograma adaptativa
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        equalized = clahe.apply(blurred)
        
        # 6. Umbralización adaptativa con parámetros optimizados
        thresh = cv2.adaptiveThreshold(
            equalized, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV, 31, 7  # Aumentado el tamaño del bloque
        )
        
        # 7. Operaciones morfológicas mejoradas
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
        
        # Apertura agresiva para eliminar ruido
        cleaned = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=2)
        
        # Cierre para unir regiones cercanas
        cleaned = cv2.morphologyEx(cleaned, cv2.MORPH_CLOSE, kernel, iterations=3)
        
        # Eliminar pequeños objetos de ruido
        cleaned = cv2.erode(cleaned, None, iterations=1)
        cleaned = cv2.dilate(cleaned, None, iterations=2)
        
        # 8. Rellenar regiones y filtrar por forma
        contours, _ = cv2.findContours(cleaned, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        final_mask = np.zeros_like(cleaned)
        
        for cnt in contours:
            area = cv2.contourArea(cnt)
            # Filtros más estrictos
            if 1000 < area < 20000:  # Rango de área más específico
                # Calcular circularidad
                perimeter = cv2.arcLength(cnt, True)
                if perimeter > 0:
                    circularity = 4 * np.pi * area / (perimeter * perimeter)
                    # Filtrar por circularidad (valores cercanos a 1 son más circulares)
                    if 0.6 < circularity < 1.4:  # Aceptar formas aproximadamente circulares
                        # Rellenar el contorno
                        cv2.drawContours(final_mask, [cnt], -1, 255, -1)
        
        # 8. Suavizado final para bordes más limpios
        final_mask = cv2.medianBlur(final_mask, 3)
        
        return final_mask
        
    except Exception as e:
        print(f"Error en preprocesamiento: {str(e)}")
        if frame is not None and frame.size > 0:
            return np.zeros((frame.shape[0], frame.shape[1]), dtype=np.uint8)
        return np.zeros((100, 100), dtype=np.uint8)