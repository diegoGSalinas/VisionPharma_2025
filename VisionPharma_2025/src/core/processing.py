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
    Implementa la segmentación usando HSV y devuelve una máscara binaria.
    """
    if frame is None:
        return None

    # 1. Conversión a espacio de color HSV
    hsv_image = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    # 2. Creación de Máscaras de Color (Segmentación por Tono/Saturación)
    
    # Máscaras de colores vivos (Rojo/Naranja/Amarillo)
    mask_rojo = cv2.inRange(hsv_image, RANGO_ROJO_MIN, RANGO_ROJO_MAX)
    mask_naranja = cv2.inRange(hsv_image, RANGO_NARANJA_MIN, RANGO_NARANJA_MAX)
    mask_amarillo = cv2.inRange(hsv_image, RANGO_AMARILLO_MIN, RANGO_AMARILLO_MAX)
    
    # Máscara para blancos (baja saturación, alta luminosidad)
    mask_blanco = cv2.inRange(hsv_image, RANGO_BLANCO_MIN, RANGO_BLANCO_MAX)
    
    # 3. Fusionar todas las máscaras con OR (lógico)
    # Esto aísla todas las píldoras de colores/brillos específicos.
    combined_mask = cv2.bitwise_or(mask_rojo, cv2.bitwise_or(mask_naranja, cv2.bitwise_or(mask_amarillo, mask_blanco)))

    # 4. Operaciones Morfológicas para limpiar la máscara (eliminar ruido y unir partes)
    kernel = np.ones((3,3),np.uint8) # Kernel pequeño para limpieza fina
    
    # Cierre: Dilatación seguida de Erosión (cierra pequeños agujeros en las píldoras)
    cleaned_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_CLOSE, kernel)
    
    # Apertura: Erosión seguida de Dilatación (elimina puntos pequeños de ruido)
    cleaned_mask = cv2.morphologyEx(cleaned_mask, cv2.MORPH_OPEN, kernel)
    
    # La imagen final es la MÁSCARA BINARIA LIMPIA (sin necesidad de umbralización posterior)
    return cleaned_mask