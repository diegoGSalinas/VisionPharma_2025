import cv2
import numpy as np

class ContadorContornos:
    @staticmethod
    def contar_contornos_coloreados(imagen_procesada):
        """
        Cuenta los contornos coloreados en una imagen procesada.
        
        Args:
            imagen_procesada: Imagen con contornos coloreados (BGR)
            
        Returns:
            tuple: (imagen_con_contornos, total_contornos)
        """
        # Convertir a escala de grises
        gris = cv2.cvtColor(imagen_procesada, cv2.COLOR_BGR2GRAY)
        
        # Aplicar umbral para aislar los contornos coloreados
        _, umbral = cv2.threshold(gris, 10, 255, cv2.THRESH_BINARY)
        
        # Encontrar contornos
        contornos, _ = cv2.findContours(umbral, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Crear una copia para dibujar los contornos encontrados
        imagen_contornos = imagen_procesada.copy()
        
        # Dibujar rectángulos alrededor de los contornos
        for i, cnt in enumerate(contornos, 1):
            x, y, w, h = cv2.boundingRect(cnt)
            # Dibujar rectángulo rojo alrededor de cada contorno
            cv2.rectangle(imagen_contornos, (x, y), (x+w, y+h), (0, 0, 255), 2)
            # Mostrar número del contorno
            cv2.putText(imagen_contornos, str(i), (x, y-5), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        
        return imagen_contornos, len(contornos)