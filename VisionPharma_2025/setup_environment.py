#!/usr/bin/env python3
"""
Script para configurar el entorno de desarrollo de VisionPharma
"""

import sys
import subprocess
import platform

def check_python_version():
    """Verifica la versión de Python"""
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major == 3 and version.minor >= 14:
        print("ADVERTENCIA: Python 3.14+ puede tener problemas de compatibilidad")
        print("   con algunas librerías científicas como numpy.")
        print("   Se recomienda usar Python 3.11 o 3.12.")
        return False
    elif version.major == 3 and version.minor in [11, 12]:
        print("Versión de Python compatible")
        return True
    else:
        print("Versión de Python no probada")
        return True

def install_packages():
    """Instala los paquetes necesarios"""
    print("\nInstalando paquetes...")
    
    packages = [
        "opencv-python==4.8.1.78",
        "numpy==1.24.3", 
        "pandas==2.0.3",
        "matplotlib==3.7.2",
        "PyQt6==6.5.0",
        "psycopg2-binary==2.9.7"
    ]
    
    for package in packages:
        try:
            print(f"Instalando {package}...")
            subprocess.run([sys.executable, "-m", "pip", "install", package], 
                         check=True, capture_output=True)
            print(f"OK - {package} instalado correctamente")
        except subprocess.CalledProcessError as e:
            print(f"ERROR - Instalando {package}: {e}")
            return False
    
    return True

def main():
    """Función principal"""
    print("Configurando entorno VisionPharma")
    print("=" * 50)
    
    # Verificar versión de Python
    if not check_python_version():
        print("\nRecomendaciones:")
        print("1. Instalar Python 3.11 o 3.12 desde python.org")
        print("2. Crear un nuevo entorno virtual con la versión compatible")
        print("3. Ejecutar este script nuevamente")
        return
    
    # Instalar paquetes
    if install_packages():
        print("\n¡Entorno configurado correctamente!")
        print("Puedes ejecutar tu aplicación con: python main.py")
    else:
        print("\nError en la instalación")
        print("Revisa los mensajes de error anteriores")

if __name__ == "__main__":
    main()
