#!/usr/bin/env python3
"""
Script de prueba para verificar compatibilidad con Streamlit Cloud
"""

import sys
import importlib
import subprocess
import os

def test_imports():
    """Prueba que todas las importaciones funcionen correctamente"""
    print("🔍 Probando importaciones...")
    
    required_modules = [
        'streamlit',
        'pandas', 
        'plotly.graph_objects',
        'plotly.express',
        'openpyxl',
        'numpy',
        'pytz'
    ]
    
    failed_imports = []
    
    for module in required_modules:
        try:
            importlib.import_module(module)
            print(f"  ✅ {module}")
        except ImportError as e:
            print(f"  ❌ {module}: {e}")
            failed_imports.append(module)
    
    return len(failed_imports) == 0

def test_file_structure():
    """Verifica que los archivos necesarios existan"""
    print("\n📁 Verificando estructura de archivos...")
    
    required_files = [
        'app.py',
        'requirements.txt',
        '.streamlit/config.toml',
        'modules/__init__.py',
        'modules/data/loader.py',
        'modules/components/dashboard_ejecutivo.py',
        'ARCHIVOS/'  # Directorio
    ]
    
    missing_files = []
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ {file_path}")
            missing_files.append(file_path)
    
    return len(missing_files) == 0

def test_syntax():
    """Verifica que no haya errores de sintaxis"""
    print("\n🔍 Verificando sintaxis...")
    
    python_files = [
        'app.py',
        'modules/components/dashboard_ejecutivo.py',
        'modules/data/loader.py'
    ]
    
    syntax_errors = []
    
    for file_path in python_files:
        if os.path.exists(file_path):
            try:
                result = subprocess.run([
                    sys.executable, '-m', 'py_compile', file_path
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    print(f"  ✅ {file_path}")
                else:
                    print(f"  ❌ {file_path}: {result.stderr}")
                    syntax_errors.append(file_path)
            except Exception as e:
                print(f"  ❌ {file_path}: {e}")
                syntax_errors.append(file_path)
        else:
            print(f"  ⚠️ {file_path} no encontrado")
    
    return len(syntax_errors) == 0

def test_streamlit_compatibility():
    """Prueba compatibilidad específica con Streamlit"""
    print("\n🚀 Probando compatibilidad con Streamlit...")
    
    try:
        # Importar la función principal
        from modules.components.dashboard_ejecutivo import mostrar_dashboard_ejecutivo
        print("  ✅ Importación de dashboard_ejecutivo exitosa")
        
        # Verificar decoradores de cache
        import streamlit as st
        if hasattr(st, 'cache_data'):
            print("  ✅ st.cache_data disponible")
        else:
            print("  ❌ st.cache_data no disponible - actualizar Streamlit")
            return False
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def main():
    """Función principal de pruebas"""
    print("🧪 PRUEBAS DE COMPATIBILIDAD CON STREAMLIT CLOUD")
    print("=" * 50)
    
    all_tests_passed = True
    
    # Ejecutar pruebas
    tests = [
        ("Importaciones", test_imports),
        ("Estructura de archivos", test_file_structure), 
        ("Sintaxis", test_syntax),
        ("Compatibilidad Streamlit", test_streamlit_compatibility)
    ]
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            if not result:
                all_tests_passed = False
        except Exception as e:
            print(f"❌ Error en {test_name}: {e}")
            all_tests_passed = False
    
    # Resultado final
    print("\n" + "=" * 50)
    if all_tests_passed:
        print("🎉 TODAS LAS PRUEBAS PASARON")
        print("✅ La aplicación debería funcionar en Streamlit Cloud")
    else:
        print("⚠️ ALGUNAS PRUEBAS FALLARON")
        print("❌ Corregir los errores antes del despliegue")
    
    return all_tests_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 