"""
Módulo centralizado para manejo de errores y logging
"""

import logging
import streamlit as st
import pandas as pd
import functools
from typing import Any, Callable, Optional
from modules.config.settings import LOGGING_CONFIG

# Configurar logging
logging.basicConfig(
    level=LOGGING_CONFIG["level"],
    format=LOGGING_CONFIG["format"],
    datefmt=LOGGING_CONFIG["datefmt"]
)

logger = logging.getLogger(__name__)

# =============================================================================
# DECORADORES PARA MANEJO DE ERRORES
# =============================================================================

def handle_data_errors(func: Callable) -> Callable:
    """
    Decorador para manejar errores relacionados con datos
    
    Args:
        func: Función a decorar
        
    Returns:
        Función decorada con manejo de errores
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except FileNotFoundError as e:
            error_msg = f"Archivo no encontrado en {func.__name__}: {e}"
            logger.error(error_msg)
            st.error("📁 **Error de Archivo**: Archivo de datos no encontrado. Verifica que todos los archivos estén en la carpeta ARCHIVOS/")
            return None
        except pd.errors.EmptyDataError as e:
            error_msg = f"Archivo vacío en {func.__name__}: {e}"
            logger.error(error_msg)
            st.error("📊 **Error de Datos**: El archivo de datos está vacío o no contiene información válida")
            return None
        except pd.errors.ParserError as e:
            error_msg = f"Error de formato en {func.__name__}: {e}"
            logger.error(error_msg)
            st.error("🔧 **Error de Formato**: El archivo de datos tiene un formato incorrecto")
            return None
        except KeyError as e:
            error_msg = f"Columna faltante en {func.__name__}: {e}"
            logger.error(error_msg)
            st.error(f"📋 **Error de Estructura**: Columna requerida no encontrada: {e}")
            return None
        except ValueError as e:
            error_msg = f"Error de valor en {func.__name__}: {e}"
            logger.error(error_msg)
            st.error(f"⚠️ **Error de Datos**: {e}")
            return None
        except Exception as e:
            error_msg = f"Error inesperado en {func.__name__}: {e}"
            logger.error(error_msg)
            st.error(f"🚨 **Error Inesperado**: Ocurrió un error inesperado. Contacta al administrador del sistema.")
            return None
    return wrapper

def handle_calculation_errors(func: Callable) -> Callable:
    """
    Decorador para manejar errores en cálculos y métricas
    
    Args:
        func: Función a decorar
        
    Returns:
        Función decorada con manejo de errores
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ZeroDivisionError as e:
            error_msg = f"División por cero en {func.__name__}: {e}"
            logger.warning(error_msg)
            st.warning("🔢 **Advertencia**: No hay datos suficientes para realizar el cálculo")
            return 0
        except TypeError as e:
            error_msg = f"Error de tipo en {func.__name__}: {e}"
            logger.error(error_msg)
            st.error(f"🔤 **Error de Tipo**: Error en el tipo de datos para el cálculo")
            return None
        except OverflowError as e:
            error_msg = f"Overflow en {func.__name__}: {e}"
            logger.error(error_msg)
            st.error("📈 **Error de Cálculo**: El resultado del cálculo es demasiado grande")
            return None
        except Exception as e:
            error_msg = f"Error en cálculo en {func.__name__}: {e}"
            logger.error(error_msg)
            st.error(f"🧮 **Error de Cálculo**: Error inesperado en el cálculo: {e}")
            return None
    return wrapper

def handle_streamlit_errors(func: Callable) -> Callable:
    """
    Decorador para manejar errores específicos de Streamlit
    
    Args:
        func: Función a decorar
        
    Returns:
        Función decorada con manejo de errores
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except st.StreamlitAPIException as e:
            error_msg = f"Error de Streamlit en {func.__name__}: {e}"
            logger.error(error_msg)
            st.error("🖥️ **Error de Interfaz**: Error en la interfaz de usuario")
            return None
        except Exception as e:
            error_msg = f"Error general en componente {func.__name__}: {e}"
            logger.error(error_msg)
            st.error(f"🔧 **Error de Componente**: Error al cargar el componente")
            return None
    return wrapper

# =============================================================================
# CLASES DE EXCEPCIÓN PERSONALIZADAS
# =============================================================================

class DashboardError(Exception):
    """Excepción base para errores del dashboard"""
    pass

class DataValidationError(DashboardError):
    """Error de validación de datos"""
    pass

class ConfigurationError(DashboardError):
    """Error de configuración"""
    pass

class CalculationError(DashboardError):
    """Error en cálculos"""
    pass

# =============================================================================
# FUNCIONES DE VALIDACIÓN
# =============================================================================

def validar_dataframe(df: pd.DataFrame, columnas_requeridas: list, nombre_df: str = "DataFrame") -> bool:
    """
    Valida que un DataFrame tenga las columnas requeridas
    
    Args:
        df: DataFrame a validar
        columnas_requeridas: Lista de columnas que deben existir
        nombre_df: Nombre descriptivo del DataFrame
        
    Returns:
        True si es válido
        
    Raises:
        DataValidationError: Si la validación falla
    """
    if df is None or df.empty:
        raise DataValidationError(f"{nombre_df} está vacío o es None")
    
    columnas_faltantes = [col for col in columnas_requeridas if col not in df.columns]
    
    if columnas_faltantes:
        raise DataValidationError(
            f"{nombre_df} no tiene las columnas requeridas: {columnas_faltantes}"
        )
    
    logger.info(f"✅ {nombre_df} validado correctamente")
    return True

def validar_fechas(df: pd.DataFrame, columna_fecha: str) -> bool:
    """
    Valida que una columna de fechas sea válida
    
    Args:
        df: DataFrame con la columna de fecha
        columna_fecha: Nombre de la columna de fecha
        
    Returns:
        True si es válida
        
    Raises:
        DataValidationError: Si la validación falla
    """
    if columna_fecha not in df.columns:
        raise DataValidationError(f"Columna de fecha '{columna_fecha}' no encontrada")
    
    # Intentar convertir a datetime
    try:
        fechas_convertidas = pd.to_datetime(df[columna_fecha], errors='coerce')
        fechas_nulas = fechas_convertidas.isna().sum()
        
        if fechas_nulas > 0:
            logger.warning(f"⚠️ {fechas_nulas} fechas inválidas encontradas en {columna_fecha}")
        
        if fechas_nulas == len(df):
            raise DataValidationError(f"Todas las fechas en '{columna_fecha}' son inválidas")
        
        logger.info(f"✅ Columna de fecha '{columna_fecha}' validada")
        return True
        
    except Exception as e:
        raise DataValidationError(f"Error validando fechas en '{columna_fecha}': {e}")

# =============================================================================
# FUNCIONES DE LOGGING ESPECÍFICAS
# =============================================================================

def log_data_load(archivo: str, num_registros: int, proceso: str):
    """
    Log específico para carga de datos
    
    Args:
        archivo: Nombre del archivo cargado
        num_registros: Número de registros cargados
        proceso: Proceso (CCM/PRR)
    """
    logger.info(f"📊 Datos cargados - Archivo: {archivo}, Registros: {num_registros:,}, Proceso: {proceso}")

def log_calculation(nombre_calculo: str, resultado: Any, tiempo_ejecucion: Optional[float] = None):
    """
    Log específico para cálculos
    
    Args:
        nombre_calculo: Nombre del cálculo realizado
        resultado: Resultado del cálculo
        tiempo_ejecucion: Tiempo de ejecución en segundos
    """
    mensaje = f"🧮 Cálculo realizado - {nombre_calculo}: {resultado}"
    if tiempo_ejecucion:
        mensaje += f" (Tiempo: {tiempo_ejecucion:.2f}s)"
    logger.info(mensaje)

def log_user_action(accion: str, parametros: dict = None):
    """
    Log específico para acciones del usuario
    
    Args:
        accion: Descripción de la acción
        parametros: Parámetros de la acción
    """
    mensaje = f"👤 Acción del usuario - {accion}"
    if parametros:
        mensaje += f" - Parámetros: {parametros}"
    logger.info(mensaje)

# =============================================================================
# FUNCIONES DE UTILIDAD PARA STREAMLIT
# =============================================================================

def mostrar_error_amigable(mensaje: str, tipo: str = "error"):
    """
    Muestra un mensaje de error amigable en Streamlit
    
    Args:
        mensaje: Mensaje a mostrar
        tipo: Tipo de mensaje ('error', 'warning', 'info')
    """
    iconos = {
        "error": "🚨",
        "warning": "⚠️", 
        "info": "ℹ️"
    }
    
    icono = iconos.get(tipo, "📢")
    
    if tipo == "error":
        st.error(f"{icono} {mensaje}")
    elif tipo == "warning":
        st.warning(f"{icono} {mensaje}")
    else:
        st.info(f"{icono} {mensaje}")

def crear_expander_debug(titulo: str, contenido: str):
    """
    Crea un expander para información de debug
    
    Args:
        titulo: Título del expander
        contenido: Contenido a mostrar
    """
    with st.expander(f"🔧 Debug: {titulo}"):
        st.code(contenido)

# =============================================================================
# CONTEXT MANAGER PARA MANEJO DE ERRORES
# =============================================================================

class ErrorHandler:
    """Context manager para manejo centralizado de errores"""
    
    def __init__(self, operacion: str, mostrar_en_streamlit: bool = True):
        self.operacion = operacion
        self.mostrar_en_streamlit = mostrar_en_streamlit
    
    def __enter__(self):
        logger.info(f"🚀 Iniciando: {self.operacion}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            error_msg = f"❌ Error en {self.operacion}: {exc_val}"
            logger.error(error_msg)
            
            if self.mostrar_en_streamlit:
                if issubclass(exc_type, (FileNotFoundError, pd.errors.EmptyDataError)):
                    mostrar_error_amigable("Error al cargar los datos. Verifica que los archivos estén disponibles.", "error")
                elif issubclass(exc_type, (ValueError, KeyError)):
                    mostrar_error_amigable(f"Error de datos: {exc_val}", "error") 
                else:
                    mostrar_error_amigable("Error inesperado. Contacta al administrador.", "error")
            
            return False  # No suprimir la excepción
        else:
            logger.info(f"✅ Completado: {self.operacion}")
            return True 