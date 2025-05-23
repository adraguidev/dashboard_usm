"""
Componente para la pestaña de Pendientes
"""

import streamlit as st
import pandas as pd
from modules.data.loader import (
    procesar_pendientes, crear_tabla_pendientes, calcular_sin_asignar,
    preparar_historico_pendientes, actualizar_historico_pendientes
)
from modules.utils.excel_export import to_excel_with_format

def mostrar_pendientes(df: pd.DataFrame, proceso: str) -> None:
    """
    Muestra la pestaña de pendientes con tabla y métricas
    
    Args:
        df: DataFrame con los datos
        proceso: Tipo de proceso ('CCM' o 'PRR')
    """
    st.header(f"Pendientes {proceso}")
    
    # Procesar datos de pendientes
    df_filtrado = procesar_pendientes(df, proceso)
    
    # Crear tabla dinámica
    tabla = crear_tabla_pendientes(df_filtrado, proceso)
    
    # Mostrar tabla
    st.dataframe(tabla, use_container_width=True, height=500)
    
    # Mostrar métrica de sin asignar
    total_sin_asignar = calcular_sin_asignar(df_filtrado)
    st.metric("Sin asignar (últimos 2 años)", total_sin_asignar)
    
    # Botón para descargar Excel
    excel_data = to_excel_with_format(tabla)
    st.download_button(
        label="Descargar tabla en Excel",
        data=excel_data,
        file_name=f"pendientes_{proceso}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    
    # Guardado automático del histórico
    tabla_historico = preparar_historico_pendientes(tabla, proceso)
    actualizar_historico_pendientes(tabla_historico) 