"""
Componente para la pestaña de Pendientes
"""

import streamlit as st
import pandas as pd
from modules.data.loader import (
    procesar_pendientes, crear_tabla_pendientes, calcular_sin_asignar,
    preparar_historico_pendientes, actualizar_historico_pendientes,
    enriquecer_pendientes_con_base
)
from modules.utils.excel_export import to_excel_with_format

def aplicar_filtros_tabla(tabla: pd.DataFrame, modo_vista: str, regimen_filtro: str, turno_filtro: str, 
                         modalidad_filtro: str, subequipo_filtro: str) -> pd.DataFrame:
    """
    Aplica filtros a la tabla de pendientes basados en los criterios seleccionados
    
    Args:
        tabla: DataFrame con pendientes enriquecidos
        modo_vista: "GENERAL" para evaluadores en base, "OTROS" para no clasificados
        regimen_filtro: Filtro por régimen
        turno_filtro: Filtro por turno  
        modalidad_filtro: Filtro por modalidad
        subequipo_filtro: Filtro por sub-equipo
        
    Returns:
        DataFrame filtrado
    """
    tabla_filtrada = tabla.copy()
    
    # Aplicar filtro principal según el modo de vista
    if modo_vista == "GENERAL":
        # Mostrar solo evaluadores que están en la base (no son "OTROS")
        tabla_filtrada = tabla_filtrada[
            (tabla_filtrada['REGIMEN'] != 'OTROS') | 
            (tabla_filtrada['TURNO'] != 'OTROS') | 
            (tabla_filtrada['MODALIDAD'] != 'OTROS') | 
            (tabla_filtrada['SUB-EQUIPO'] != 'OTROS')
        ]
        # Mejor lógica: si alguna columna NO es "OTROS", entonces está en la base
        tabla_filtrada = tabla_filtrada[tabla_filtrada['SUB-EQUIPO'] != 'OTROS']
        
    else:  # modo_vista == "OTROS"
        # Mostrar solo evaluadores que NO están en la base (son "OTROS")
        tabla_filtrada = tabla_filtrada[tabla_filtrada['SUB-EQUIPO'] == 'OTROS']
    
    # Aplicar filtros específicos solo si no es "Todos" y hay datos
    if not tabla_filtrada.empty:
        if regimen_filtro != "Todos" and regimen_filtro in tabla_filtrada['REGIMEN'].values:
            tabla_filtrada = tabla_filtrada[tabla_filtrada['REGIMEN'] == regimen_filtro]
        
        if turno_filtro != "Todos" and turno_filtro in tabla_filtrada['TURNO'].values:
            tabla_filtrada = tabla_filtrada[tabla_filtrada['TURNO'] == turno_filtro]
            
        if modalidad_filtro != "Todos" and modalidad_filtro in tabla_filtrada['MODALIDAD'].values:
            tabla_filtrada = tabla_filtrada[tabla_filtrada['MODALIDAD'] == modalidad_filtro]
            
        if subequipo_filtro != "Todos" and subequipo_filtro in tabla_filtrada['SUB-EQUIPO'].values:
            tabla_filtrada = tabla_filtrada[tabla_filtrada['SUB-EQUIPO'] == subequipo_filtro]
    
    return tabla_filtrada

def obtener_opciones_filtros(tabla_enriquecida: pd.DataFrame, modo_vista: str) -> tuple:
    """
    Obtiene las opciones de filtros según el modo de vista seleccionado
    
    Args:
        tabla_enriquecida: DataFrame completo con información de evaluadores
        modo_vista: "GENERAL" o "OTROS"
        
    Returns:
        Tupla con listas de opciones para cada filtro
    """
    if modo_vista == "GENERAL":
        # Filtrar solo evaluadores que están en la base
        tabla_filtro = tabla_enriquecida[tabla_enriquecida['SUB-EQUIPO'] != 'OTROS']
    else:
        # Filtrar solo evaluadores que NO están en la base
        tabla_filtro = tabla_enriquecida[tabla_enriquecida['SUB-EQUIPO'] == 'OTROS']
    
    if tabla_filtro.empty:
        return (["Todos"], ["Todos"], ["Todos"], ["Todos"])
    
    regimenes = ["Todos"] + sorted([x for x in tabla_filtro['REGIMEN'].unique() if x != 'OTROS'])
    turnos = ["Todos"] + sorted([x for x in tabla_filtro['TURNO'].unique() if x != 'OTROS'])
    modalidades = ["Todos"] + sorted([x for x in tabla_filtro['MODALIDAD'].unique() if x != 'OTROS'])
    subequipos = ["Todos"] + sorted([x for x in tabla_filtro['SUB-EQUIPO'].unique() if x != 'OTROS'])
    
    return regimenes, turnos, modalidades, subequipos

def generar_tabla_con_colores(tabla_filtrada: pd.DataFrame) -> pd.DataFrame:
    """
    Genera la tabla final solo con las columnas de pendientes y aplica estilos de color
    
    Args:
        tabla_filtrada: DataFrame filtrado con información completa
        
    Returns:
        DataFrame solo con columnas de pendientes preparado para mostrar
    """
    # Obtener solo las columnas numéricas (pendientes por período) y Total
    columnas_numericas = [col for col in tabla_filtrada.columns 
                         if col not in ['REGIMEN', 'TURNO', 'MODALIDAD', 'SUB-EQUIPO']]
    
    tabla_display = tabla_filtrada[columnas_numericas].copy()
    
    # Asegurar que la columna Total esté presente y al final
    if 'Total' in tabla_display.columns:
        cols = [col for col in tabla_display.columns if col != 'Total']
        cols.append('Total')
        tabla_display = tabla_display[cols]
    
    # Convertir valores numéricos a enteros para mejor visualización
    for col in tabla_display.columns:
        if tabla_display[col].dtype in ['float64', 'float32']:
            tabla_display[col] = tabla_display[col].astype(int)
    
    return tabla_display

def crear_leyenda_colores(modo_vista: str):
    """
    Crea la leyenda de colores para los sub-equipos según el modo de vista
    """
    st.markdown("### 📋 Leyenda de Colores")
    
    if modo_vista == "GENERAL":
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(
                '<div style="display: flex; align-items: center; margin-bottom: 10px;">'
                '<div style="width: 20px; height: 20px; background-color: #4caf50; '
                'border-radius: 3px; margin-right: 10px;"></div>'
                '<span><strong>Verde:</strong> RESPONSABLE</span>'
                '</div>', 
                unsafe_allow_html=True
            )
        
        with col2:
            st.markdown(
                '<div style="display: flex; align-items: center; margin-bottom: 10px;">'
                '<div style="width: 20px; height: 20px; background-color: #ff9800; '
                'border-radius: 3px; margin-right: 10px;"></div>'
                '<span><strong>Naranja:</strong> REASIGNADOS</span>'
                '</div>', 
                unsafe_allow_html=True
            )
            
        with col3:
            st.markdown(
                '<div style="display: flex; align-items: center; margin-bottom: 10px;">'
                '<div style="width: 20px; height: 20px; background-color: white; '
                'border: 1px solid #ccc; border-radius: 3px; margin-right: 10px;"></div>'
                '<span><strong>Blanco:</strong> OTROS ACTIVOS</span>'
                '</div>', 
                unsafe_allow_html=True
            )
            
        with col4:
            st.markdown(
                '<div style="display: flex; align-items: center; margin-bottom: 10px;">'
                '<div style="width: 20px; height: 20px; background-color: #9e9e9e; '
                'border-radius: 3px; margin-right: 10px;"></div>'
                '<span><strong>Gris:</strong> INACTIVOS</span>'
                '</div>', 
                unsafe_allow_html=True
            )
    
    else:  # OTROS
        st.markdown(
            '<div style="display: flex; align-items: center; margin-bottom: 10px;">'
            '<div style="width: 20px; height: 20px; background-color: #9e9e9e; '
            'border-radius: 3px; margin-right: 10px;"></div>'
            '<span><strong>Gris:</strong> Evaluadores sin clasificar en la base</span>'
            '</div>', 
            unsafe_allow_html=True
        )

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
    
    # Enriquecer tabla con información de la base de evaluadores
    tabla_enriquecida = enriquecer_pendientes_con_base(tabla, proceso)
    
    # === TOGGLE PRINCIPAL PARA VISTA ===
    st.subheader("🔍 Selector de Vista de Evaluadores")
    
    col_toggle, col_info = st.columns([1, 2])
    
    with col_toggle:
        modo_vista = st.radio(
            "Seleccionar vista:",
            options=["GENERAL", "OTROS"],
            index=0,
            horizontal=True,
            help="GENERAL: Evaluadores en la base de datos | OTROS: Evaluadores no clasificados"
        )
    
    with col_info:
        if modo_vista == "GENERAL":
            st.info("📋 **Vista GENERAL**: Mostrando evaluadores que están en la base de datos con sus clasificaciones")
        else:
            st.info("❓ **Vista OTROS**: Mostrando evaluadores que NO están clasificados en la base de datos")
    
    # === FILTROS POR EVALUADORES ===
    st.subheader("🎯 Filtros Específicos")
    
    # Obtener opciones de filtros según el modo de vista
    regimenes, turnos, modalidades, subequipos = obtener_opciones_filtros(tabla_enriquecida, modo_vista)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        regimen_filtro = st.selectbox(
            "Régimen:",
            options=regimenes,
            index=0,
            help="Filtrar por tipo de régimen laboral",
            disabled=(modo_vista == "OTROS")  # Deshabilitar para OTROS si no hay opciones
        )
    
    with col2:
        turno_filtro = st.selectbox(
            "Turno:",
            options=turnos,
            index=0,
            help="Filtrar por turno de trabajo",
            disabled=(modo_vista == "OTROS")
        )
    
    with col3:
        modalidad_filtro = st.selectbox(
            "Modalidad:",
            options=modalidades,
            index=0,
            help="Filtrar por modalidad de trabajo",
            disabled=(modo_vista == "OTROS")
        )
    
    with col4:
        subequipo_filtro = st.selectbox(
            "Sub-Equipo:",
            options=subequipos,
            index=0,
            help="Filtrar por clasificación de sub-equipo",
            disabled=(modo_vista == "OTROS")
        )
    
    # Aplicar filtros
    tabla_filtrada = aplicar_filtros_tabla(tabla_enriquecida, modo_vista, regimen_filtro, turno_filtro, 
                                          modalidad_filtro, subequipo_filtro)
    
    st.markdown("---")
    
    # === MÉTRICAS PRINCIPALES ===
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Total de pendientes (excluyendo sin asignar para esta métrica)
        total_asignados = tabla_filtrada.loc[tabla_filtrada.index != 'Sin asignar', 'Total'].sum() if 'Sin asignar' not in tabla_filtrada.index else 0
        if 'Total' in tabla_filtrada.index:
            total_asignados = tabla_filtrada.loc['Total', 'Total']
            if 'Sin asignar' in tabla_filtrada.index:
                total_asignados -= tabla_filtrada.loc['Sin asignar', 'Total']
        
        st.metric(
            "📋 Total Asignados", 
            f"{total_asignados:,}",
            help="Total de casos pendientes asignados a operadores (filtrados)"
        )
    
    with col2:
        # Operadores activos (con al menos 1 caso)
        operadores_activos = len([idx for idx in tabla_filtrada.index if idx not in ['Total', 'Sin asignar'] and tabla_filtrada.loc[idx, 'Total'] > 0])
        st.metric(
            "👥 Operadores Activos", 
            operadores_activos,
            help="Operadores con al menos 1 caso asignado (filtrados)"
        )
    
    with col3:
        # Promedio por operador
        promedio_operador = total_asignados / operadores_activos if operadores_activos > 0 else 0
        st.metric(
            "📊 Promedio/Operador", 
            f"{promedio_operador:.1f}",
            help="Promedio de casos por operador activo (filtrados)"
        )
    
    # === LEYENDA DE COLORES ===
    crear_leyenda_colores(modo_vista)
    
    # === TABLA PRINCIPAL ===
    st.subheader(f"📋 Tabla de Pendientes por {agrupacion}")
    
    # Generar tabla para mostrar (solo columnas numéricas)
    tabla_display = generar_tabla_con_colores(tabla_filtrada)
    
    # Aplicar colores según SUB-EQUIPO
    def aplicar_estilo_subequipo(row):
        """Aplica color de fondo según el sub-equipo"""
        if row.name in tabla_filtrada.index:
            subequipo = tabla_filtrada.loc[row.name, 'SUB-EQUIPO'] if 'SUB-EQUIPO' in tabla_filtrada.columns else 'OTROS'
            if subequipo == 'RESPONSABLE':
                return ['background-color: #4caf50; color: white; font-weight: bold;'] * len(row)  # Verde
            elif subequipo == 'REASIGNADOS':
                return ['background-color: #ff9800; color: white; font-weight: bold;'] * len(row)  # Naranja
            elif subequipo == 'OTROS' and row.name != 'Total':
                # Verificar si está en la base (blanco) o no está (gris)
                if 'SUB-EQUIPO' in tabla_filtrada.columns and not pd.isna(tabla_filtrada.loc[row.name, 'SUB-EQUIPO']):
                    return ['background-color: white; color: black; font-weight: bold;'] * len(row)  # Blanco (activo)
                else:
                    return ['background-color: #9e9e9e; color: white; font-weight: bold;'] * len(row)  # Gris (inactivo)
            else:
                return ['background-color: white; color: black; font-weight: bold;'] * len(row)  # Blanco por defecto
        return [''] * len(row)
    
    # Mostrar tabla con estilos
    styled_table = tabla_display.style.apply(aplicar_estilo_subequipo, axis=1)
    
    st.dataframe(
        styled_table,
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
        # Mostrar métrica de sin asignar (usar datos originales sin filtrar)
        total_sin_asignar = calcular_sin_asignar(df_filtrado, agrupacion)
        st.metric(
            f"⚠️ Sin asignar ({periodo_sin_asignar})", 
            f"{total_sin_asignar:,}",
            help=f"Casos sin asignar en el período de {periodo_sin_asignar} (sin filtros aplicados)"
        )
    
    with col2:
        # Porcentaje de sin asignar (usar totales originales)
        total_general_original = tabla.loc['Total', 'Total'] if 'Total' in tabla.index else tabla['Total'].sum()
        porcentaje_sin_asignar = (total_sin_asignar / total_general_original * 100) if total_general_original > 0 else 0
        
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
            help="Porcentaje de casos sin asignar del total general"
        )
    
    # === DESCARGA Y ACCIONES ===
    st.markdown("---")
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # Botón para descargar Excel (tabla filtrada)
        excel_data = to_excel_with_format(tabla_display)
        filtros_aplicados = f"_{modo_vista.lower()}"
        if modo_vista == "GENERAL" and any([
            regimen_filtro != "Todos", turno_filtro != "Todos", 
            modalidad_filtro != "Todos", subequipo_filtro != "Todos"
        ]):
            filtros_aplicados += f"_{regimen_filtro}_{turno_filtro}_{modalidad_filtro}_{subequipo_filtro}"
        
        st.download_button(
            label="📥 Descargar tabla filtrada en Excel",
            data=excel_data,
            file_name=f"pendientes_{proceso}_{agrupacion.lower()}{filtros_aplicados}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
    
    with col2:
        # Información adicional
        st.info(f"💡 **Consejo:** Usa el toggle y filtros para personalizar la vista de evaluadores")
    
    # === GUARDADO AUTOMÁTICO DEL HISTÓRICO ===
    # Solo guardar histórico para agrupación por años (para mantener compatibilidad)
    if agrupacion == "Años":
        tabla_historico = preparar_historico_pendientes(tabla, proceso)  # Usar tabla original, no filtrada
        actualizar_historico_pendientes(tabla_historico) 