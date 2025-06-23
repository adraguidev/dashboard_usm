#!/usr/bin/env python3
"""
Script para ejecutar los tests del proyecto
"""

import subprocess
import sys
import os

def run_tests():
    """
    Ejecuta la suite completa de tests
    """
    print("🧪 Ejecutando tests del Dashboard de Análisis de Procesos")
    print("=" * 60)
    
    # Cambiar al directorio del proyecto
    project_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_dir)
    
    # Comando para ejecutar pytest
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/",
        "--verbose",
        "--tb=short",
        "--cov=modules",
        "--cov-report=html",
        "--cov-report=term-missing"
    ]
    
    try:
        result = subprocess.run(cmd, check=True)
        print("\n✅ Todos los tests pasaron exitosamente!")
        print("📊 Reporte de cobertura generado en htmlcov/index.html")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Algunos tests fallaron (código de salida: {e.returncode})")
        return False
    except FileNotFoundError:
        print("❌ pytest no está instalado. Ejecuta: pip install pytest pytest-cov")
        return False

def run_specific_test(test_file):
    """
    Ejecuta un archivo de test específico
    
    Args:
        test_file: Nombre del archivo de test
    """
    print(f"🧪 Ejecutando {test_file}")
    print("=" * 40)
    
    cmd = [
        sys.executable, "-m", "pytest",
        f"tests/{test_file}",
        "--verbose"
    ]
    
    try:
        subprocess.run(cmd, check=True)
        print(f"\n✅ Tests en {test_file} pasaron exitosamente!")
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Tests en {test_file} fallaron (código de salida: {e.returncode})")

def main():
    """
    Función principal
    """
    if len(sys.argv) > 1:
        # Ejecutar test específico
        test_file = sys.argv[1]
        if not test_file.startswith("test_"):
            test_file = f"test_{test_file}"
        if not test_file.endswith(".py"):
            test_file = f"{test_file}.py"
        
        run_specific_test(test_file)
    else:
        # Ejecutar todos los tests
        run_tests()

if __name__ == "__main__":
    main() 