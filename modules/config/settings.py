"""
Configuración centralizada del proyecto
"""

import os
from typing import Dict, List

# =============================================================================
# CONFIGURACIÓN DE ARCHIVOS Y DATOS
# =============================================================================

# Mapeo de procesos a archivos
DATABASE_CONFIG: Dict[str, str] = {
    "CCM": "consolidado_final_CCM_personal.pkl.gz",
    "PRR": "consolidado_final_PRR_personal.pkl.gz"
}

# Directorio de archivos
ARCHIVOS_DIR = "ARCHIVOS"

# Archivos de histórico
HISTORICO_PENDIENTES_FILE = "historico_pendientes_operador.csv"
HISTORICO_SIN_ASIGNAR_FILE = "historico_sin_asignar.csv"

# Base de evaluadores
BASE_EVALUADORES_FILE = "EVALUADORES/BASE.xlsx"

# =============================================================================
# FILTROS DE OPERADORES
# =============================================================================

# Operadores a excluir del análisis (común para ambos procesos)
OPERADORES_EXCLUIR_COMUN: List[str] = [
    "Sin asignar",
    "Aponte Sanchez, Paola Lita",
    "Lucero Martinez, Carlos Martin", 
    "USUARIO DE AGENCIA DIGITAL"
]

# Operadores específicos por proceso
OPERADORES_EXCLUIR_CCM: List[str] = OPERADORES_EXCLUIR_COMUN + [
    "MAURICIO ROMERO, HUGO"
]

OPERADORES_EXCLUIR_PRR: List[str] = OPERADORES_EXCLUIR_COMUN.copy()

# =============================================================================
# CONFIGURACIÓN DE ETAPAS POR PROCESO
# =============================================================================

# Etapas válidas para CCM
ETAPAS_CCM = {
    "etapa_principal": "EVALUACIÓN - I",
    "estado_pre": None,  # Debe ser nulo
    "estado_tramite": "PENDIENTE",
    "equipo_excluir": "VULNERABLE"
}

# Etapas válidas para PRR
ETAPAS_PRR: List[str] = [
    'ACTUALIZAR DATOS BENEFICIARIO - F',
    'ACTUALIZAR DATOS BENEFICIARIO - I',
    'ASOCIACION BENEFICIARIO - F',
    'ASOCIACION BENEFICIARIO - I',
    'CONFORMIDAD SUB-DIREC.INMGRA. - I',
    'PAGOS, FECHA Y NRO RD. - F',
    'PAGOS, FECHA Y NRO RD. - I',
    'RECEPCIÓN DINM - F'
]

# =============================================================================
# CONFIGURACIÓN DE MÉTRICAS Y UMBRALES
# =============================================================================

# Umbrales para clasificación de eficiencia
UMBRALES_EFICIENCIA = {
    "produccion_promedio_minima_alta": 5,
    "produccion_promedio_minima_media": 3,
    "aumento_peligroso_pendientes": 1
}

# Configuración de análisis de tendencias
CONFIGURACION_TENDENCIAS = {
    "dias_analisis_produccion": 15,  # Días hábiles para calcular promedio
    "dias_analisis_ingresos": 60,    # Días para análisis de ingresos
    "dias_tabla_ingresos": 15,       # Días para tabla de ingresos
    "dias_proyeccion": 30            # Días para proyecciones
}

# =============================================================================
# CONFIGURACIÓN DE STREAMLIT
# =============================================================================

# Configuración de la página
STREAMLIT_CONFIG = {
    "page_title": "Dashboard de Análisis de Procesos",
    "page_icon": "📊",
    "layout": "wide",
    "initial_sidebar_state": "expanded"
}

# Configuración de cache
CACHE_CONFIG = {
    "ttl_datos_base": 3600,      # 1 hora para datos base
    "ttl_metricas": 300,         # 5 minutos para métricas
    "ttl_historico": 1800        # 30 minutos para datos históricos
}

# =============================================================================
# CONFIGURACIÓN DE VISUALIZACIONES
# =============================================================================

# Colores del dashboard
COLORES = {
    "primary": "#667eea",
    "secondary": "#764ba2", 
    "success": "#28a745",
    "warning": "#ffc107",
    "danger": "#dc3545",
    "info": "#17a2b8"
}

# Configuración de gráficos
GRAFICOS_CONFIG = {
    "altura_default": 400,
    "altura_pequeña": 300,
    "altura_grande": 500,
    "mostrar_toolbar": False,
    "responsive": True
}

# =============================================================================
# CONFIGURACIÓN DE EXPORTACIÓN
# =============================================================================

# Configuración de Excel export
EXCEL_CONFIG = {
    "sheet_name_pendientes": "Pendientes",
    "sheet_name_produccion": "Producción",
    "sheet_name_resumen": "Resumen",
    "formato_fecha": "%Y-%m-%d",
    "formato_numero": "#,##0"
}

# =============================================================================
# CONFIGURACIÓN DE DESARROLLO
# =============================================================================

# Variables de entorno
DEBUG = os.getenv("DEBUG", "False").lower() == "true"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Configuración de logging
LOGGING_CONFIG = {
    "level": LOG_LEVEL,
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "datefmt": "%Y-%m-%d %H:%M:%S"
}

# =============================================================================
# VALIDACIÓN DE CONFIGURACIÓN
# =============================================================================

def validar_configuracion() -> bool:
    """
    Valida que la configuración sea correcta
    
    Returns:
        True si la configuración es válida
    """
    try:
        # Verificar que existan los archivos necesarios
        archivos_requeridos = list(DATABASE_CONFIG.values())
        
        for archivo in archivos_requeridos:
            ruta_completa = os.path.join(ARCHIVOS_DIR, archivo)
            if not os.path.exists(ruta_completa):
                print(f"⚠️ Archivo no encontrado: {ruta_completa}")
                return False
        
        print("✅ Configuración validada correctamente")
        return True
        
    except Exception as e:
        print(f"❌ Error validando configuración: {e}")
        return False

# =============================================================================
# FUNCIÓN DE CONFIGURACIÓN INICIAL
# =============================================================================

def inicializar_configuracion():
    """
    Inicializa la configuración del proyecto
    """
    if DEBUG:
        print("🔧 Modo DEBUG activado")
        print(f"📁 Directorio de archivos: {ARCHIVOS_DIR}")
        print(f"📊 Procesos configurados: {list(DATABASE_CONFIG.keys())}")
    
    # Validar configuración
    return validar_configuracion() 