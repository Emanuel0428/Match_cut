"""
Script para verificar si las dependencias están instaladas correctamente en Vercel
"""
import sys
import importlib

def check_module(module_name):
    try:
        importlib.import_module(module_name)
        print(f"✓ {module_name} instalado correctamente")
        return True
    except ImportError as e:
        print(f"✗ Error al importar {module_name}: {e}")
        return False

def main():
    required_modules = [
        "flask",
        "PIL",
        "numpy",
        "moviepy",
        "matplotlib"
    ]
    
    all_good = True
    print("\n=== VERIFICACIÓN DE DEPENDENCIAS ===\n")
    
    for module in required_modules:
        if not check_module(module):
            all_good = False
    
    print("\n=== VERIFICACIÓN DE RUTAS ===\n")
    import os
    print(f"Directorio actual: {os.getcwd()}")
    print(f"Contenido del directorio:")
    for item in os.listdir():
        print(f"  - {item}")
    
    print("\n=== VARIABLES DE ENTORNO ===\n")
    for key, value in os.environ.items():
        if key.startswith("VERCEL") or key in ["PYTHONPATH", "PATH"]:
            print(f"{key}: {value}")
    
    if all_good:
        print("\n✓ Todas las dependencias están instaladas correctamente.")
        return 0
    else:
        print("\n✗ Algunas dependencias faltan o tienen problemas.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
