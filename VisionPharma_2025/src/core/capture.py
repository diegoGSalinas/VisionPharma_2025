import cv2
import numpy as np
import glob
import os

# --- Interfaz Base ---
# Todas las fuentes de imagen (Cámara Real, Archivo Mock) deben tener un método 'read_frame()'
# y un método 'release()'.

class CameraController:
    """Implementa la captura de una cámara real (PB-01)."""
    def __init__(self, camera_index=0):
        self.cap = cv2.VideoCapture(camera_index)
        if not self.cap.isOpened():
            print(f"Advertencia: Cámara real en índice {camera_index} no detectada.")
            self.cap = None

    def read_frame(self) -> np.ndarray:
        """Lee un frame real de la cámara."""
        if self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                return frame
        return None

    def release(self):
        """Libera el recurso de la cámara."""
        if self.cap:
            self.cap.release()
            print("Controlador de cámara real liberado.")


class MockImageReader:
    """
    Simula la captura de imágenes leyendo archivos de una carpeta (Mock-up para desarrollo).
    Procesar imágenes sin hardware real.
    """
    def __init__(self, folder_path='sample_data'):
        # Buscar todas las imágenes JPG y PNG en la carpeta de prueba
        search_path = os.path.join(folder_path, '*.jpg')
        self.image_files = sorted(glob.glob(search_path))
        
        # Añadir archivos PNG
        search_path_png = os.path.join(folder_path, '*.png')
        self.image_files.extend(sorted(glob.glob(search_path_png)))
        
        self.current_index = 0
        if not self.image_files:
            print(f"Error: No se encontraron imágenes en la carpeta '{folder_path}'.")

    def read_frame(self) -> np.ndarray:
        """Lee la siguiente imagen de la lista y regresa al inicio si termina."""
        if not self.image_files:
            return None
            
        file_path = self.image_files[self.current_index]
        # cv2.IMREAD_COLOR asegura que se lea en formato de color (BGR)
        frame = cv2.imread(file_path, cv2.IMREAD_COLOR) 
        
        # Avanzar al siguiente archivo
        self.current_index = (self.current_index + 1) % len(self.image_files)
        
        return frame

    def release(self):
        """No hay recursos de hardware que liberar."""
        print("Controlador Mock liberado (no hay cámara).")