import cv2
import sys
import os
from src.core.inspection_agent import InspectionAgent
from src.core.capture import CameraController, MockImageReader

# --- CONFIGURACIÓN DE LA FUENTE ---
USE_CAMERA_REAL = False 
CAMERA_INDEX = 0 
SAMPLE_FOLDER = 'sample_data' 

def get_image_source():
    """Selecciona la fuente de imagen basada en la configuración."""
    if USE_CAMERA_REAL:
        print("Modo: Usando Cámara Real.")
        return CameraController(CAMERA_INDEX)
    else:
        print(f"Modo: Usando Imágenes Mock de la carpeta '{SAMPLE_FOLDER}'.")
        return MockImageReader(SAMPLE_FOLDER)


def main():
    """
    Punto de entrada de la aplicación.
    """
    if not os.path.exists(SAMPLE_FOLDER):
        os.makedirs(SAMPLE_FOLDER)
        print(f"Carpeta '{SAMPLE_FOLDER}' creada. Agrega imágenes de blísters aquí para la prueba Mock.")
    
    # 1. Inyectar la fuente de imagen deseada
    image_source = get_image_source()
    agent = InspectionAgent(image_source) # Inyección de Dependencias
    
    print("--- VisionPharma 2025: Prueba de Prototipo ---")
    print("Presiona 'q' para salir. Si usas Mock, las imágenes rotarán.")

    try:
        while True:
            # Ejecutar el pipeline de Visión
            # Desempaquetamos 4 valores, usando '_' para descartar el diccionario de pasos y la lista de resultados.
            final_frame_display, _, _, success = agent.run_pipeline_step()

            if success:
                # Mostrar el resultado final del pipeline (contornos dibujados)
                cv2.imshow("VisionPharma 2025 - Resultado Final (Escritorio)", final_frame_display)
            else:
                print("No se pudo obtener el frame de la fuente seleccionada.")
                break
            
            # Condición de salida
            wait_time = 1 if USE_CAMERA_REAL else 1000 
            if cv2.waitKey(wait_time) & 0xFF == ord('q'):
                break

    except KeyboardInterrupt:
        print("\nPrueba interrumpida.")
        
    finally:
        agent.release_resources()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()