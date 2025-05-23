"""
Módulo para el manejo del histórico de casos SIN ASIGNAR
Solo almacena la métrica que no tiene histórico inherente
"""

import pandas as pd
import pytz
import datetime
import os
from modules.data.loader import procesar_pendientes, calcular_sin_asignar

def cargar_historico_sin_asignar() -> pd.DataFrame:
    """
    Carga el histórico de casos sin asignar
    
    Returns:
        DataFrame con el histórico de sin asignar
    """
    ruta_historico = 'ARCHIVOS/historico_sin_asignar.csv'
    try:
        return pd.read_csv(ruta_historico)
    except FileNotFoundError:
        return pd.DataFrame(columns=['fecha', 'proceso', 'sin_asignar'])

def actualizar_historico_sin_asignar(df_ccm: pd.DataFrame, df_prr: pd.DataFrame) -> None:
    """
    Actualiza el histórico de casos sin asignar solo si los datos han cambiado
    
    Args:
        df_ccm: DataFrame de CCM
        df_prr: DataFrame de PRR
    """
    # Obtener fecha local
    tz = pytz.timezone('America/Lima')
    fecha_hoy = datetime.datetime.now(tz).strftime('%Y-%m-%d')
    
    # Calcular sin asignar actuales
    df_ccm_filt = procesar_pendientes(df_ccm, "CCM")
    sin_asignar_ccm = calcular_sin_asignar(df_ccm_filt)
    
    df_prr_filt = procesar_pendientes(df_prr, "PRR")
    sin_asignar_prr = calcular_sin_asignar(df_prr_filt)
    
    # Cargar histórico existente
    historico = cargar_historico_sin_asignar()
    
    # Verificar si ya existe registro para hoy
    if not historico.empty:
        registro_hoy = historico[historico['fecha'] == fecha_hoy]
        if not registro_hoy.empty:
            # Verificar si los valores han cambiado
            ccm_actual = registro_hoy[registro_hoy['proceso'] == 'CCM']['sin_asignar'].iloc[0] if len(registro_hoy[registro_hoy['proceso'] == 'CCM']) > 0 else None
            prr_actual = registro_hoy[registro_hoy['proceso'] == 'PRR']['sin_asignar'].iloc[0] if len(registro_hoy[registro_hoy['proceso'] == 'PRR']) > 0 else None
            
            if ccm_actual == sin_asignar_ccm and prr_actual == sin_asignar_prr:
                # No han cambiado, no actualizar
                return
            else:
                # Han cambiado, eliminar registros de hoy para actualizarlos
                historico = historico[historico['fecha'] != fecha_hoy]
    
    # Crear nuevos registros
    nuevos_registros = [
        {'fecha': fecha_hoy, 'proceso': 'CCM', 'sin_asignar': sin_asignar_ccm},
        {'fecha': fecha_hoy, 'proceso': 'PRR', 'sin_asignar': sin_asignar_prr}
    ]
    
    # Agregar al histórico
    nuevos_df = pd.DataFrame(nuevos_registros)
    historico_actualizado = pd.concat([historico, nuevos_df], ignore_index=True)
    
    # Mantener solo últimos 90 días
    historico_actualizado['fecha'] = pd.to_datetime(historico_actualizado['fecha'])
    fecha_limite = historico_actualizado['fecha'].max() - pd.Timedelta(days=90)
    historico_actualizado = historico_actualizado[historico_actualizado['fecha'] >= fecha_limite]
    
    # Convertir fecha de vuelta a string y guardar
    historico_actualizado['fecha'] = historico_actualizado['fecha'].dt.strftime('%Y-%m-%d')
    
    # Crear directorio si no existe
    os.makedirs('ARCHIVOS', exist_ok=True)
    
    # Guardar
    ruta_historico = 'ARCHIVOS/historico_sin_asignar.csv'
    historico_actualizado.to_csv(ruta_historico, index=False)

def calcular_tendencia_sin_asignar(sin_asignar_actual_ccm: int, sin_asignar_actual_prr: int) -> dict:
    """
    Calcula la tendencia de casos sin asignar basada en el histórico
    
    Args:
        sin_asignar_actual_ccm: Casos sin asignar actuales CCM
        sin_asignar_actual_prr: Casos sin asignar actuales PRR
        
    Returns:
        Diccionario con deltas calculados
    """
    historico = cargar_historico_sin_asignar()
    
    if historico.empty or len(historico) < 2:
        return {'ccm': 0, 'prr': 0}
    
    # Convertir fecha y ordenar
    historico['fecha'] = pd.to_datetime(historico['fecha'])
    historico = historico.sort_values('fecha')
    
    # Obtener valores anteriores (penúltimo registro por proceso)
    resultado = {'ccm': 0, 'prr': 0}
    
    for proceso_key, proceso_name, valor_actual in [('ccm', 'CCM', sin_asignar_actual_ccm), ('prr', 'PRR', sin_asignar_actual_prr)]:
        hist_proceso = historico[historico['proceso'] == proceso_name]
        
        if len(hist_proceso) >= 2:
            # Tomar el penúltimo valor (el anterior al actual)
            valor_anterior = hist_proceso.iloc[-2]['sin_asignar']
            resultado[proceso_key] = valor_actual - valor_anterior
        else:
            resultado[proceso_key] = 0
    
    return resultado 