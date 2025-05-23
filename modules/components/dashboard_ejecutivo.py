"""
Componente para el Dashboard Ejecutivo
Dashboard de alto nivel usando históricos existentes y solo almacenando sin asignar
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from modules.data.loader import (
    cargar_datos, obtener_archivos_proceso, 
    procesar_pendientes, crear_tabla_pendientes, calcular_sin_asignar,
    cargar_historico_pendientes
)
from modules.data.historico_sin_asignar import (
    actualizar_historico_sin_asignar, calcular_tendencia_sin_asignar
)

def mostrar_dashboard_ejecutivo() -> None:
    """
    Muestra el dashboard ejecutivo con KPIs y métricas consolidadas
    """
    st.header("📊 Dashboard Ejecutivo")
    st.markdown("*Vista consolidada para toma de decisiones estratégicas*")
    
    # Cargar datos de ambos procesos
    try:
        archivos = obtener_archivos_proceso()
        df_ccm = cargar_datos(archivos["CCM"])
        df_prr = cargar_datos(archivos["PRR"])
    except Exception as e:
        st.error(f"Error al cargar datos: {str(e)}")
        return
    
    # Calcular métricas usando las mismas funciones que cada pestaña
    metricas_ccm = _calcular_metricas_exactas_ccm(df_ccm)
    metricas_prr = _calcular_metricas_exactas_prr(df_prr)
    metricas_consolidadas = _consolidar_metricas(metricas_ccm, metricas_prr)
    
    # Actualizar histórico solo de sin asignar (si los datos cambiaron)
    actualizar_historico_sin_asignar(df_ccm, df_prr)
    
    # Calcular tendencias usando históricos existentes
    tendencias = _calcular_tendencias_reales(metricas_ccm, metricas_prr)
    
    # === LAYOUT PRINCIPAL ORGANIZADO ===
    st.markdown("---")
    
    # SECCIÓN 1: KPIs PRINCIPALES CON TENDENCIAS
    _mostrar_kpis_principales(metricas_consolidadas, metricas_ccm, metricas_prr, tendencias)
    
    st.markdown("---")
    
    # SECCIÓN 2: GRÁFICOS DE TENDENCIAS (LADO A LADO)
    col_left, col_right = st.columns(2)
    
    with col_left:
        # Evolución de Pendientes (gráfico de líneas histórico)
        _mostrar_evolucion_pendientes_historica()
    
    with col_right:
        # Semáforos de estado y alertas (sin carga promedio)
        _mostrar_panel_control_estado(metricas_consolidadas, metricas_ccm, metricas_prr)
    
    st.markdown("---")
    
    # SECCIÓN 3: ANÁLISIS COMPARATIVO DE PROCESOS
    col_left2, col_right2 = st.columns(2)
    
    with col_left2:
        # Ingresos vs Trabajados (líneas por proceso)
        _mostrar_ingresos_vs_trabajados_lineal(df_ccm, df_prr)
    
    with col_right2:
        # Tabla comparativa (sin gráfico de eficiencia)
        _mostrar_tabla_comparativa(metricas_ccm, metricas_prr)

def _calcular_metricas_exactas_ccm(df: pd.DataFrame) -> dict:
    """
    Calcula métricas para CCM usando exactamente las mismas funciones que cada pestaña
    """
    # === PENDIENTES (misma función que pestaña Pendientes) ===
    df_filtrado = procesar_pendientes(df, "CCM")
    tabla_pendientes = crear_tabla_pendientes(df_filtrado, "CCM")
    
    # Total = tabla + sin asignar
    tabla_total = int(tabla_pendientes.loc['Total', 'Total']) if 'Total' in tabla_pendientes.index else 0
    sin_asignar = calcular_sin_asignar(df_filtrado)
    total_pendientes = tabla_total + sin_asignar
    asignados = tabla_total
    
    # Operadores activos (de la tabla, excluyendo 'Total')
    operadores_en_tabla = [idx for idx in tabla_pendientes.index if idx != 'Total']
    operadores_activos = len(operadores_en_tabla)
    
    # === PRODUCCIÓN DIARIA (misma lógica que pestaña Producción Diaria) ===
    col_operador = 'OperadorPre' if 'OperadorPre' in df.columns else 'OPERADOR'
    col_fecha = 'FechaPre'
    col_tramite = 'NumeroTramite'
    
    # Preparar fechas
    if not pd.api.types.is_datetime64_any_dtype(df[col_fecha]):
        df[col_fecha] = pd.to_datetime(df[col_fecha], errors='coerce')
    
    fechas_ordenadas = df[col_fecha].dropna().sort_values().unique()
    ultimos_20_dias = fechas_ordenadas[-20:]
    df_20dias = df[df[col_fecha].isin(ultimos_20_dias)]
    
    # Filtros exactos de producción diaria
    operadores_excluir = [
        "Aponte Sanchez, Paola Lita", 
        "Lucero Martinez, Carlos Martin", 
        "USUARIO DE AGENCIA DIGITAL"
    ]
    
    df_resumen = df_20dias[~df_20dias[col_operador].isin(operadores_excluir)].copy()
    
    # Filtrar operadores con >= 5 trámites
    totales_operador = df_resumen.groupby(col_operador)[col_tramite].count()
    operadores_validos = totales_operador[totales_operador >= 5].index
    df_resumen = df_resumen[df_resumen[col_operador].isin(operadores_validos)]
    
    # Calcular producción diaria igual que en la pestaña
    resumen = df_resumen.groupby(col_fecha).agg(
        total_trabajados=(col_tramite, 'count')
    )
    produccion_diaria = resumen['total_trabajados'].sum() / len(ultimos_20_dias) if len(ultimos_20_dias) > 0 else 0
    
    # Ingresos diarios (últimos 30 días)
    df['FechaExpendiente'] = pd.to_datetime(df['FechaExpendiente'], errors='coerce')
    fecha_limite = df['FechaExpendiente'].max() - pd.Timedelta(days=30)
    ingresos_recientes = df[df['FechaExpendiente'] >= fecha_limite]['NumeroTramite'].count()
    ingresos_diarios = ingresos_recientes / 30
    
    return {
        'proceso': 'CCM',
        'total_pendientes': total_pendientes,
        'sin_asignar': sin_asignar,
        'asignados': asignados,
        'operadores_activos': operadores_activos,
        'produccion_diaria': produccion_diaria,
        'ingresos_diarios': ingresos_diarios,
        'promedio_por_operador': asignados / operadores_activos if operadores_activos > 0 else 0
    }

def _calcular_metricas_exactas_prr(df: pd.DataFrame) -> dict:
    """
    Calcula métricas para PRR usando exactamente las mismas funciones que cada pestaña
    """
    # === PENDIENTES (misma función que pestaña Pendientes) ===
    df_filtrado = procesar_pendientes(df, "PRR")
    tabla_pendientes = crear_tabla_pendientes(df_filtrado, "PRR")
    
    # Total = tabla + sin asignar
    tabla_total = int(tabla_pendientes.loc['Total', 'Total']) if 'Total' in tabla_pendientes.index else 0
    sin_asignar = calcular_sin_asignar(df_filtrado)
    total_pendientes = tabla_total + sin_asignar
    asignados = tabla_total
    
    # Operadores activos (de la tabla, excluyendo 'Total')
    operadores_en_tabla = [idx for idx in tabla_pendientes.index if idx != 'Total']
    operadores_activos = len(operadores_en_tabla)
    
    # === PRODUCCIÓN DIARIA (misma lógica que pestaña Producción Diaria) ===
    col_operador = 'OperadorPre' if 'OperadorPre' in df.columns else 'OPERADOR'
    col_fecha = 'FechaPre'
    col_tramite = 'NumeroTramite'
    
    # Preparar fechas
    if not pd.api.types.is_datetime64_any_dtype(df[col_fecha]):
        df[col_fecha] = pd.to_datetime(df[col_fecha], errors='coerce')
    
    fechas_ordenadas = df[col_fecha].dropna().sort_values().unique()
    ultimos_20_dias = fechas_ordenadas[-20:]
    df_20dias = df[df[col_fecha].isin(ultimos_20_dias)]
    
    # Filtros exactos de producción diaria
    operadores_excluir = [
        "Aponte Sanchez, Paola Lita", 
        "Lucero Martinez, Carlos Martin", 
        "USUARIO DE AGENCIA DIGITAL"
    ]
    
    df_resumen = df_20dias[~df_20dias[col_operador].isin(operadores_excluir)].copy()
    
    # Filtrar operadores con >= 5 trámites
    totales_operador = df_resumen.groupby(col_operador)[col_tramite].count()
    operadores_validos = totales_operador[totales_operador >= 5].index
    df_resumen = df_resumen[df_resumen[col_operador].isin(operadores_validos)]
    
    # Calcular producción diaria igual que en la pestaña
    resumen = df_resumen.groupby(col_fecha).agg(
        total_trabajados=(col_tramite, 'count')
    )
    produccion_diaria = resumen['total_trabajados'].sum() / len(ultimos_20_dias) if len(ultimos_20_dias) > 0 else 0
    
    # Ingresos diarios (últimos 30 días)
    df['FechaExpendiente'] = pd.to_datetime(df['FechaExpendiente'], errors='coerce')
    fecha_limite = df['FechaExpendiente'].max() - pd.Timedelta(days=30)
    ingresos_recientes = df[df['FechaExpendiente'] >= fecha_limite]['NumeroTramite'].count()
    ingresos_diarios = ingresos_recientes / 30
    
    return {
        'proceso': 'PRR',
        'total_pendientes': total_pendientes,
        'sin_asignar': sin_asignar,
        'asignados': asignados,
        'operadores_activos': operadores_activos,
        'produccion_diaria': produccion_diaria,
        'ingresos_diarios': ingresos_diarios,
        'promedio_por_operador': asignados / operadores_activos if operadores_activos > 0 else 0
    }

def _consolidar_metricas(metricas_ccm: dict, metricas_prr: dict) -> dict:
    """
    Consolida métricas de ambos procesos
    """
    return {
        'total_pendientes': metricas_ccm['total_pendientes'] + metricas_prr['total_pendientes'],
        'total_sin_asignar': metricas_ccm['sin_asignar'] + metricas_prr['sin_asignar'],
        'total_asignados': metricas_ccm['asignados'] + metricas_prr['asignados'],
        'total_operadores': metricas_ccm['operadores_activos'] + metricas_prr['operadores_activos'],
        'produccion_total': metricas_ccm['produccion_diaria'] + metricas_prr['produccion_diaria'],
        'ingresos_total': metricas_ccm['ingresos_diarios'] + metricas_prr['ingresos_diarios'],
        'eficiencia_general': (metricas_ccm['produccion_diaria'] + metricas_prr['produccion_diaria']) / 
                            (metricas_ccm['ingresos_diarios'] + metricas_prr['ingresos_diarios']) if 
                            (metricas_ccm['ingresos_diarios'] + metricas_prr['ingresos_diarios']) > 0 else 0
    }

def _calcular_tendencias_reales(metricas_ccm: dict, metricas_prr: dict) -> dict:
    """
    Calcula tendencias reales usando los históricos existentes
    """
    # Tendencias de sin asignar (único histórico nuevo)
    tendencias_sin_asignar = calcular_tendencia_sin_asignar(
        metricas_ccm['sin_asignar'], 
        metricas_prr['sin_asignar']
    )
    
    # Para pendientes totales: usar histórico existente
    historico_pendientes = cargar_historico_pendientes()
    
    deltas = {'ccm': {}, 'prr': {}}
    
    if not historico_pendientes.empty:
        # Calcular tendencias de pendientes desde histórico real
        historico_pendientes['Fecha'] = pd.to_datetime(historico_pendientes['Fecha'])
        
        for proceso, datos_proceso in [('ccm', 'CCM'), ('prr', 'PRR')]:
            hist_proceso = historico_pendientes[historico_pendientes['Proceso'] == datos_proceso]
            
            if len(hist_proceso) >= 2:
                # Obtener últimos dos registros por fecha
                hist_proceso = hist_proceso.sort_values('Fecha')
                ultimas_fechas = hist_proceso['Fecha'].unique()[-2:]
                
                if len(ultimas_fechas) >= 2:
                    pendientes_anterior = hist_proceso[hist_proceso['Fecha'] == ultimas_fechas[0]]['Pendientes'].sum()
                    pendientes_actual = hist_proceso[hist_proceso['Fecha'] == ultimas_fechas[1]]['Pendientes'].sum()
                    delta_pendientes = pendientes_actual - pendientes_anterior
                    
                    # Calcular delta de operadores (simplificado)
                    operadores_anterior = hist_proceso[hist_proceso['Fecha'] == ultimas_fechas[0]]['Pendientes'].count()
                    operadores_actual = hist_proceso[hist_proceso['Fecha'] == ultimas_fechas[1]]['Pendientes'].count()
                    delta_operadores = operadores_actual - operadores_anterior
                    
                    deltas[proceso] = {
                        'delta_pendientes': delta_pendientes,
                        'delta_operadores': delta_operadores,
                        'delta_sin_asignar': tendencias_sin_asignar[proceso],
                        'delta_produccion': 0  # Se puede calcular si hay histórico de producción
                    }
                else:
                    deltas[proceso] = {
                        'delta_pendientes': 0,
                        'delta_operadores': 0,
                        'delta_sin_asignar': tendencias_sin_asignar[proceso],
                        'delta_produccion': 0
                    }
            else:
                deltas[proceso] = {
                    'delta_pendientes': 0,
                    'delta_operadores': 0,
                    'delta_sin_asignar': tendencias_sin_asignar[proceso],
                    'delta_produccion': 0
                }
    else:
        # Sin histórico, solo sin asignar
        for proceso in ['ccm', 'prr']:
            deltas[proceso] = {
                'delta_pendientes': 0,
                'delta_operadores': 0,
                'delta_sin_asignar': tendencias_sin_asignar[proceso],
                'delta_produccion': 0
            }
    
    return deltas

def _mostrar_kpis_principales(consolidadas: dict, ccm: dict, prr: dict, tendencias: dict) -> None:
    """
    Muestra los KPIs principales con tendencias reales basadas en histórico
    """
    st.subheader("🎯 KPIs Principales")
    
    # Primera fila de métricas generales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Pendientes", 
            f"{consolidadas['total_pendientes']:,}",
            help="Incluye sin asignar + asignados"
        )
    
    with col2:
        st.metric(
            "Producción Diaria", 
            f"{consolidadas['produccion_total']:.1f}",
            help="Promedio últimos 20 días"
        )
    
    with col3:
        st.metric(
            "Operadores Activos", 
            consolidadas['total_operadores'],
            help="Con casos asignados"
        )
    
    with col4:
        eficiencia_pct = consolidadas['eficiencia_general'] * 100
        st.metric(
            "Eficiencia General", 
            f"{eficiencia_pct:.1f}%",
            help="Producción/Ingresos"
        )
    
    # Segunda fila de métricas CON TENDENCIAS por proceso
    st.markdown("##### Métricas por Proceso")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        # CCM - Pendientes CON DELTA
        delta_ccm = tendencias['ccm'].get('delta_pendientes', 0)
        st.metric(
            "CCM - Pendientes", 
            f"{ccm['total_pendientes']:,}",
            delta=delta_ccm,
            delta_color="inverse",
            help="Cambio vs período anterior"
        )
    
    with col2:
        # PRR - Pendientes CON DELTA
        delta_prr = tendencias['prr'].get('delta_pendientes', 0)
        st.metric(
            "PRR - Pendientes", 
            f"{prr['total_pendientes']:,}",
            delta=delta_prr,
            delta_color="inverse",
            help="Cambio vs período anterior"
        )
    
    with col3:
        # Sin asignar con tendencia real
        delta_sin_asignar = tendencias['ccm']['delta_sin_asignar'] + tendencias['prr']['delta_sin_asignar']
        st.metric(
            "Sin Asignar Total", 
            f"{consolidadas['total_sin_asignar']:,}",
            delta=delta_sin_asignar,
            delta_color="inverse",
            help="Cambio vs día anterior"
        )
    
    with col4:
        balance_diario = consolidadas['produccion_total'] - consolidadas['ingresos_total']
        st.metric(
            "Balance Diario", 
            f"{balance_diario:+.1f}",
            help="Producción - Ingresos"
        )
        
        # Indicador visual de superávit/déficit
        if balance_diario > 0:
            st.markdown("🟢 **SUPERÁVIT** ⬆️")
        elif balance_diario < 0:
            st.markdown("🔴 **DÉFICIT** ⬇️")
        else:
            st.markdown("🟡 **EQUILIBRIO** ➡️")

def _mostrar_evolucion_pendientes_historica() -> None:
    """
    Muestra gráfico de evolución de pendientes usando histórico existente (omitiendo valores 0)
    """
    st.subheader("📈 Evolución de Pendientes")
    
    # Usar histórico de pendientes existente
    historico = cargar_historico_pendientes()
    
    if not historico.empty:
        # Preparar datos del histórico para gráfico
        historico['Fecha'] = pd.to_datetime(historico['Fecha'])
        
        # Últimos 60 días para ver tendencia
        historico_reciente = historico[historico['Fecha'] >= (historico['Fecha'].max() - pd.Timedelta(days=60))]
        
        if not historico_reciente.empty:
            # Agrupar por fecha y proceso para mostrar totales
            totales_por_fecha = historico_reciente.groupby(['Fecha', 'Proceso'])['Pendientes'].sum().reset_index()
            
            fig = go.Figure()
            
            # Líneas por proceso (OMITIENDO VALORES 0)
            for proceso in ['CCM', 'PRR']:
                datos_proceso = totales_por_fecha[totales_por_fecha['Proceso'] == proceso]
                if not datos_proceso.empty:
                    # FILTRAR VALORES 0
                    datos_filtrados = datos_proceso[datos_proceso['Pendientes'] > 0]
                    
                    if not datos_filtrados.empty:
                        fig.add_trace(go.Scatter(
                            x=datos_filtrados['Fecha'],
                            y=datos_filtrados['Pendientes'],
                            mode='lines+markers',
                            name=f'{proceso} - Pendientes',
                            line=dict(width=3),
                            text=[f"{v:,}" for v in datos_filtrados['Pendientes']],
                            textposition="top center",
                            connectgaps=True  # Conecta a través de valores omitidos
                        ))
            
            # Total combinado (OMITIENDO VALORES 0)
            totales_fecha = totales_por_fecha.groupby('Fecha')['Pendientes'].sum().reset_index()
            totales_filtrados = totales_fecha[totales_fecha['Pendientes'] > 0]
            
            if not totales_filtrados.empty:
                fig.add_trace(go.Scatter(
                    x=totales_filtrados['Fecha'],
                    y=totales_filtrados['Pendientes'],
                    mode='lines+markers',
                    name='Total Combinado',
                    line=dict(width=4, dash='dash', color='purple'),
                    text=[f"{v:,}" for v in totales_filtrados['Pendientes']],
                    textposition="top center",
                    connectgaps=True
                ))
            
            fig.update_layout(
                title="Evolución de Pendientes (Últimos 60 días - Sin valores 0)",
                xaxis_title="Fecha",
                yaxis_title="Total Pendientes",
                hovermode='x unified',
                height=400,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                )
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Datos históricos insuficientes para gráfico de tendencias")
    else:
        st.info("No hay datos históricos disponibles")

def _mostrar_panel_control_estado(consolidadas: dict, ccm: dict, prr: dict) -> None:
    """
    Panel de control con semáforos y alertas (SIN carga promedio)
    """
    st.subheader("🚦 Panel de Control")
    
    # Semáforos de estado
    st.markdown("**Estados Generales**")
    
    # Eficiencia General
    eficiencia = consolidadas['eficiencia_general']
    if eficiencia >= 1.1:
        color, status = "🟢", "Excelente"
    elif eficiencia >= 0.9:
        color, status = "🟡", "Aceptable"
    else:
        color, status = "🔴", "Crítico"
    
    st.markdown(f"**Eficiencia General** {color}")
    st.markdown(f"*{status}* - {eficiencia*100:.1f}%")
    
    # Sin Asignar
    porcentaje_sin_asignar = (consolidadas['total_sin_asignar'] / consolidadas['total_pendientes']) * 100 if consolidadas['total_pendientes'] > 0 else 0
    if porcentaje_sin_asignar <= 5:
        color, status = "🟢", "Excelente"
    elif porcentaje_sin_asignar <= 15:
        color, status = "🟡", "Aceptable"
    else:
        color, status = "🔴", "Crítico"
    
    st.markdown(f"**Casos Sin Asignar** {color}")
    st.markdown(f"*{status}* - {porcentaje_sin_asignar:.1f}%")
    
    st.markdown("---")
    
    # Alertas críticas (SIN alertas de sobrecarga)
    st.markdown("**⚠️ Alertas Activas**")
    
    alertas = []
    
    # Verificar alertas CCM
    if ccm['sin_asignar'] > ccm['total_pendientes'] * 0.15:
        alertas.append(f"🔴 CCM: {ccm['sin_asignar']} casos sin asignar (>15%)")
    
    # Verificar alertas PRR
    if prr['sin_asignar'] > prr['total_pendientes'] * 0.15:
        alertas.append(f"🔴 PRR: {prr['sin_asignar']} casos sin asignar (>15%)")
    
    # Alertas de eficiencia
    if ccm['produccion_diaria'] < ccm['ingresos_diarios'] * 0.8:
        alertas.append("🔴 CCM: Producción muy baja vs ingresos")
    
    if prr['produccion_diaria'] < prr['ingresos_diarios'] * 0.8:
        alertas.append("🔴 PRR: Producción muy baja vs ingresos")
    
    if alertas:
        for alerta in alertas:
            st.markdown(alerta)
    else:
        st.markdown("✅ **Sin alertas críticas**")
        st.markdown("*Todos los indicadores dentro de rangos normales*")

def _mostrar_ingresos_vs_trabajados_lineal(df_ccm: pd.DataFrame, df_prr: pd.DataFrame) -> None:
    """
    Muestra gráfico de líneas comparando ingresos vs trabajados por proceso
    """
    st.subheader("📊 Ingresos vs Trabajados (Tendencia)")
    
    # Calcular datos para CCM
    ccm_data = _calcular_datos_ingresos_trabajados(df_ccm, "CCM")
    prr_data = _calcular_datos_ingresos_trabajados(df_prr, "PRR")
    
    fig = go.Figure()
    
    # Líneas de ingresos
    if not ccm_data.empty:
        fig.add_trace(go.Scatter(
            x=ccm_data['fecha'],
            y=ccm_data['ingresos'],
            mode='lines+markers',
            name='CCM - Ingresos',
            line=dict(color='#e74c3c', width=3),
            yaxis='y'
        ))
        
        fig.add_trace(go.Scatter(
            x=ccm_data['fecha'],
            y=ccm_data['trabajados'],
            mode='lines+markers',
            name='CCM - Trabajados',
            line=dict(color='#e74c3c', width=3, dash='dash'),
            yaxis='y'
        ))
    
    if not prr_data.empty:
        fig.add_trace(go.Scatter(
            x=prr_data['fecha'],
            y=prr_data['ingresos'],
            mode='lines+markers',
            name='PRR - Ingresos',
            line=dict(color='#3498db', width=3),
            yaxis='y'
        ))
        
        fig.add_trace(go.Scatter(
            x=prr_data['fecha'],
            y=prr_data['trabajados'],
            mode='lines+markers',
            name='PRR - Trabajados',
            line=dict(color='#3498db', width=3, dash='dash'),
            yaxis='y'
        ))
    
    fig.update_layout(
        title="Evolución Diaria: Ingresos vs Trabajados por Proceso",
        xaxis_title="Fecha",
        yaxis_title="Cantidad de Trámites",
        hovermode='x unified',
        height=400,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Mostrar resumen
    if not ccm_data.empty and not prr_data.empty:
        col1, col2 = st.columns(2)
        with col1:
            balance_ccm = ccm_data['trabajados'].mean() - ccm_data['ingresos'].mean()
            st.metric("Balance Promedio CCM", f"{balance_ccm:+.1f}", help="Trabajados - Ingresos promedio")
        
        with col2:
            balance_prr = prr_data['trabajados'].mean() - prr_data['ingresos'].mean()
            st.metric("Balance Promedio PRR", f"{balance_prr:+.1f}", help="Trabajados - Ingresos promedio")

def _calcular_datos_ingresos_trabajados(df: pd.DataFrame, proceso: str) -> pd.DataFrame:
    """
    Calcula datos de ingresos vs trabajados para un proceso (últimos 30 días)
    """
    try:
        # Preparar fechas
        df['FechaExpendiente'] = pd.to_datetime(df['FechaExpendiente'], errors='coerce')
        df['FechaPre'] = pd.to_datetime(df['FechaPre'], errors='coerce')
        
        # Últimos 30 días
        fecha_max = max(df['FechaExpendiente'].max(), df['FechaPre'].max())
        fecha_min = fecha_max - pd.Timedelta(days=30)
        
        # Calcular ingresos por día
        ingresos_df = df[df['FechaExpendiente'] >= fecha_min]
        ingresos_por_dia = ingresos_df.groupby('FechaExpendiente')['NumeroTramite'].count().reset_index()
        ingresos_por_dia.columns = ['fecha', 'ingresos']
        
        # Calcular trabajados por día
        trabajados_df = df[df['FechaPre'] >= fecha_min]
        trabajados_por_dia = trabajados_df.groupby('FechaPre')['NumeroTramite'].count().reset_index()
        trabajados_por_dia.columns = ['fecha', 'trabajados']
        
        # Combinar datos
        datos_combinados = pd.merge(ingresos_por_dia, trabajados_por_dia, on='fecha', how='outer')
        datos_combinados = datos_combinados.fillna(0)
        datos_combinados = datos_combinados.sort_values('fecha')
        
        return datos_combinados
    except Exception:
        return pd.DataFrame()

def _mostrar_tabla_comparativa(ccm: dict, prr: dict) -> None:
    """
    Muestra tabla comparativa entre procesos (SIN gráfico de eficiencia)
    """
    st.subheader("⚖️ Comparación Detallada")
    
    # Crear tabla comparativa
    data_comparativa = {
        'Métrica': [
            'Pendientes Totales', 
            'Sin Asignar', 
            'Operadores Activos', 
            'Producción Diaria',
            'Ingresos Diarios',
            'Promedio/Operador'
        ],
        'CCM': [
            f"{ccm['total_pendientes']:,}", 
            f"{ccm['sin_asignar']:,}", 
            ccm['operadores_activos'], 
            f"{ccm['produccion_diaria']:.1f}",
            f"{ccm['ingresos_diarios']:.1f}",
            f"{ccm['promedio_por_operador']:.1f}"
        ],
        'PRR': [
            f"{prr['total_pendientes']:,}", 
            f"{prr['sin_asignar']:,}", 
            prr['operadores_activos'], 
            f"{prr['produccion_diaria']:.1f}",
            f"{prr['ingresos_diarios']:.1f}",
            f"{prr['promedio_por_operador']:.1f}"
        ]
    }
    
    df_comparativo = pd.DataFrame(data_comparativa)
    st.dataframe(df_comparativo, use_container_width=True, hide_index=True)
    
    # Leyenda explicativa para Promedio/Operador
    st.markdown("---")
    st.markdown("**📋 Leyenda Promedio/Operador:**")
    st.markdown("*Representa el promedio de casos pendientes asignados por operador activo en el momento actual. Es una instantánea de la carga de trabajo presente, no un promedio temporal.*") 