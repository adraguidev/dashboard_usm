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
    
    # === OPCIONES DE AGRUPACIÓN ===
    st.subheader("🔧 Opciones de Agrupación")
    
    col1, col2 = st.columns([2, 3])
    
    with col1:
        agrupacion = st.selectbox(
            "Agrupar pendientes por:",
            options=["Años", "Trimestres", "Meses"],
            index=0,
            help="Selecciona cómo quieres agrupar temporalmente los pendientes"
        )
    
    with col2:
        st.info(f"📊 **Vista actual:** {agrupacion} - Pendientes agrupados por {agrupacion.lower()}")
    
    st.markdown("---")
    
    # Procesar datos de pendientes
    df_filtrado = procesar_pendientes(df, proceso)
    
    # Crear tabla dinámica según la agrupación seleccionada
    if agrupacion == "Años":
        tabla = crear_tabla_pendientes(df_filtrado, proceso, agrupacion="anios")
        periodo_sin_asignar = "últimos 2 años"
    elif agrupacion == "Trimestres":
        tabla = crear_tabla_pendientes(df_filtrado, proceso, agrupacion="trimestres")
        periodo_sin_asignar = "últimos 6 trimestres"
    else:  # Meses
        tabla = crear_tabla_pendientes(df_filtrado, proceso, agrupacion="meses")
        periodo_sin_asignar = "últimos 12 meses"
    
    # === MÉTRICAS PRINCIPALES ===
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Total de pendientes (excluyendo sin asignar para esta métrica)
        total_asignados = tabla.loc[tabla.index != 'Sin asignar', 'Total'].sum() if 'Sin asignar' not in tabla.index else tabla.loc['Total', 'Total']
        if 'Total' in tabla.index:
            total_asignados = tabla.loc['Total', 'Total']
            if 'Sin asignar' in tabla.index:
                total_asignados -= tabla.loc['Sin asignar', 'Total']
        
        st.metric(
            "📋 Total Asignados", 
            f"{total_asignados:,}",
            help="Total de casos pendientes asignados a operadores"
        )
    
    with col2:
        # Operadores activos (con al menos 1 caso)
        operadores_activos = len([idx for idx in tabla.index if idx not in ['Total', 'Sin asignar'] and tabla.loc[idx, 'Total'] > 0])
        st.metric(
            "👥 Operadores Activos", 
            operadores_activos,
            help="Operadores con al menos 1 caso asignado"
        )
    
    with col3:
        # Promedio por operador
        promedio_operador = total_asignados / operadores_activos if operadores_activos > 0 else 0
        st.metric(
            "📊 Promedio/Operador", 
            f"{promedio_operador:.1f}",
            help="Promedio de casos por operador activo"
        )
    
    # === TABLA PRINCIPAL ===
    st.subheader(f"📋 Tabla de Pendientes por {agrupacion}")
    
    # Mostrar tabla con formato mejorado
    st.dataframe(
        tabla, 
        use_container_width=True, 
        height=500,
        column_config={
            "Total": st.column_config.NumberColumn(
                "Total",
                help="Total de casos pendientes por operador",
                format="%d"
            )
        }
    )
    
    # === MÉTRICAS DE SIN ASIGNAR ===
    st.markdown("---")
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # Mostrar métrica de sin asignar
        total_sin_asignar = calcular_sin_asignar(df_filtrado, agrupacion)
        st.metric(
            f"⚠️ Sin asignar ({periodo_sin_asignar})", 
            f"{total_sin_asignar:,}",
            help=f"Casos sin asignar en el período de {periodo_sin_asignar}"
        )
    
    with col2:
        # Porcentaje de sin asignar
        total_general = total_asignados + total_sin_asignar
        porcentaje_sin_asignar = (total_sin_asignar / total_general * 100) if total_general > 0 else 0
        
        # Color basado en el porcentaje
        if porcentaje_sin_asignar <= 5:
            color = "🟢"
        elif porcentaje_sin_asignar <= 15:
            color = "🟡"
        else:
            color = "🔴"
        
        st.metric(
            f"{color} % Sin Asignar", 
            f"{porcentaje_sin_asignar:.1f}%",
            help="Porcentaje de casos sin asignar del total"
        )
    
    # === DESCARGA Y ACCIONES ===
    st.markdown("---")
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # Botón para descargar Excel
        excel_data = to_excel_with_format(tabla)
        st.download_button(
            label="📥 Descargar tabla en Excel",
            data=excel_data,
            file_name=f"pendientes_{proceso}_{agrupacion.lower()}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
    
    with col2:
        # Información adicional
        st.info(f"💡 **Consejo:** Puedes cambiar la agrupación arriba para ver diferentes perspectivas temporales de los pendientes.")
    
    # === GUARDADO AUTOMÁTICO DEL HISTÓRICO ===
    # Solo guardar histórico para agrupación por años (para mantener compatibilidad)
    if agrupacion == "Años":
        tabla_historico = preparar_historico_pendientes(tabla, proceso)
        actualizar_historico_pendientes(tabla_historico) 