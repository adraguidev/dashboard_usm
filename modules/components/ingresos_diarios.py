"""
Componente para la pestaña de Ingresos Diarios
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np

def mostrar_ingresos_diarios(df: pd.DataFrame, proceso: str) -> None:
    """
    Muestra la pestaña de ingresos diarios con gráficos y análisis
    
    Args:
        df: DataFrame con los datos
        proceso: Tipo de proceso ('CCM' o 'PRR')
    """
    st.header("Ingreso de Expedientes")
    
    # Determinar columna de fecha
    col_fecha_ing = 'FechaExpendiente'
    col_tramite_ing = 'NumeroTramite'
    
    if col_fecha_ing not in df.columns:
        st.warning("No se encontró la columna FechaExpendiente en los datos.")
        return
    
    # Asegurar tipo datetime
    df[col_fecha_ing] = pd.to_datetime(df[col_fecha_ing], errors='coerce')
    
    # Mostrar gráfico principal de ingresos
    _mostrar_grafico_ingresos_principales(df, col_fecha_ing, col_tramite_ing)
    
    # Mostrar tabla de últimos 15 días
    _mostrar_tabla_ultimos_dias(df, col_fecha_ing, col_tramite_ing)
    
    # Mostrar promedio semanal
    _mostrar_promedio_semanal(df, col_fecha_ing, col_tramite_ing)

def _mostrar_grafico_ingresos_principales(df: pd.DataFrame, col_fecha_ing: str, 
                                        col_tramite_ing: str) -> None:
    """
    Muestra el gráfico principal de ingresos de los últimos 60 días
    """
    # Filtrar últimos 60 días
    fecha_max = df[col_fecha_ing].max()
    fecha_min = fecha_max - pd.Timedelta(days=60)
    df_60dias = df[(df[col_fecha_ing] >= fecha_min) & (df[col_fecha_ing] <= fecha_max)]
    
    # Agrupar por fecha y contar NumeroTramite
    ingresos_diarios = df_60dias.groupby(col_fecha_ing)[col_tramite_ing].count().reset_index()
    ingresos_diarios = ingresos_diarios.sort_values(col_fecha_ing)
    
    # Crear gráfico
    fig = go.Figure()
    
    # Línea y puntos
    fig.add_trace(go.Scatter(
        x=ingresos_diarios[col_fecha_ing],
        y=ingresos_diarios[col_tramite_ing],
        mode='lines+markers+text',
        name='NumeroTramite',
        text=[str(v) for v in ingresos_diarios[col_tramite_ing]],
        textposition="top center",
        line=dict(color='royalblue'),
        fill='tozeroy',
        fillcolor='rgba(65,105,225,0.1)'
    ))
    
    # Línea de tendencia
    x_numeric = np.arange(len(ingresos_diarios))
    y_vals = ingresos_diarios[col_tramite_ing].values
    if len(x_numeric) > 1:
        z = np.polyfit(x_numeric, y_vals, 1)
        tendencia = z[0] * x_numeric + z[1]
        fig.add_trace(go.Scatter(
            x=ingresos_diarios[col_fecha_ing],
            y=tendencia,
            mode='lines',
            name='Tendencia',
            line=dict(dash='dash', color='red', width=3)
        ))
    
    # Formato de fechas en eje X
    fig.update_xaxes(
        tickformat="%d %b",
        tickangle=0
    )
    fig.update_layout(
        title='',
        xaxis_title='',
        yaxis_title='',
        legend_title='',
        hovermode='x unified',
        margin=dict(l=20, r=20, t=40, b=20)
    )
    st.plotly_chart(fig, use_container_width=True)

def _mostrar_tabla_ultimos_dias(df: pd.DataFrame, col_fecha_ing: str, 
                               col_tramite_ing: str) -> None:
    """
    Muestra la tabla de ingresos de los últimos 15 días
    """
    st.write("#### Ingresos diarios - últimos 15 días")
    
    # Filtrar últimos 60 días para obtener la serie completa
    fecha_max = df[col_fecha_ing].max()
    fecha_min = fecha_max - pd.Timedelta(days=60)
    df_60dias = df[(df[col_fecha_ing] >= fecha_min) & (df[col_fecha_ing] <= fecha_max)]
    
    # Agrupar por fecha
    ingresos_diarios = df_60dias.groupby(col_fecha_ing)[col_tramite_ing].count().reset_index()
    ingresos_diarios = ingresos_diarios.sort_values(col_fecha_ing)
    
    # Tomar últimos 15 días
    tabla_15 = ingresos_diarios.tail(15).copy()
    tabla_15['FechaExpendiente'] = tabla_15['FechaExpendiente'].dt.strftime('%d/%m/%Y')
    tabla_15 = tabla_15.rename(columns={'FechaExpendiente': 'Fecha', 'NumeroTramite': 'Ingresos'})
    
    st.dataframe(tabla_15, use_container_width=True)

def _mostrar_promedio_semanal(df: pd.DataFrame, col_fecha_ing: str, 
                            col_tramite_ing: str) -> None:
    """
    Muestra el gráfico de promedio semanal de ingresos
    """
    st.write("#### Promedio semanal de ingresos diarios")
    
    if col_fecha_ing not in df.columns:
        st.warning("No se encontró la columna FechaExpendiente en los datos.")
        return
    
    # Preparar datos del último año
    df_sem = df.copy()
    df_sem[col_fecha_ing] = pd.to_datetime(df_sem[col_fecha_ing], errors='coerce')
    fecha_max_sem = df_sem[col_fecha_ing].max()
    fecha_min_sem = fecha_max_sem - pd.Timedelta(days=365)
    df_sem = df_sem[(df_sem[col_fecha_ing] >= fecha_min_sem) & (df_sem[col_fecha_ing] <= fecha_max_sem)]
    
    # Agrupar por semana
    df_sem['Semana'] = df_sem[col_fecha_ing].dt.to_period('W').dt.start_time
    ingresos_diarios_semanal = df_sem.groupby('Semana')[col_tramite_ing].count().reset_index()
    ingresos_diarios_semanal = ingresos_diarios_semanal.rename(columns={col_tramite_ing: 'Total ingresos'})
    ingresos_diarios_semanal['Promedio semanal'] = ingresos_diarios_semanal['Total ingresos'] / 7
    ingresos_diarios_semanal['Fecha'] = ingresos_diarios_semanal['Semana'].dt.strftime('%d/%m/%Y')
    ingresos_diarios_semanal['Rango de fechas'] = (
        ingresos_diarios_semanal['Semana'].dt.strftime('%d/%m/%Y') + ' - ' + 
        (ingresos_diarios_semanal['Semana'] + pd.Timedelta(days=6)).dt.strftime('%d/%m/%Y')
    )
    
    # Marcar semana actual
    semana_actual = pd.Timestamp.today().to_period('W').start_time
    ingresos_diarios_semanal['Es semana actual'] = ingresos_diarios_semanal['Semana'] == semana_actual
    
    # Crear gráfico
    fig_sem = px.line(
        ingresos_diarios_semanal,
        x='Fecha',
        y='Promedio semanal',
        title='Promedio semanal de ingresos diarios (último año)',
        labels={'Fecha': 'Fecha', 'Promedio semanal': 'Promedio semanal de ingresos'},
        hover_data={'Rango de fechas': True}
    )
    
    fig_sem.update_traces(
        mode='lines+markers', 
        marker=dict(
            color=ingresos_diarios_semanal['Es semana actual'].map({True: 'red', False: 'blue'})
        )
    )
    
    # Línea de tendencia para el año actual
    anio_actual = pd.Timestamp.today().year
    mask_anio = ingresos_diarios_semanal['Semana'].dt.year == anio_actual
    sem_actual = ingresos_diarios_semanal[mask_anio].reset_index(drop=True)
    
    if len(sem_actual) > 1:
        x_numeric_sem = np.arange(len(sem_actual))
        y_vals_sem = sem_actual['Promedio semanal'].values
        z_sem = np.polyfit(x_numeric_sem, y_vals_sem, 1)
        tendencia_sem = z_sem[0] * x_numeric_sem + z_sem[1]
        fig_sem.add_scatter(
            x=sem_actual['Fecha'],
            y=tendencia_sem,
            mode='lines',
            name='Tendencia año en curso',
            line=dict(dash='dash', color='orange')
        )
    
    fig_sem.update_xaxes(tickangle=45)
    st.plotly_chart(fig_sem, use_container_width=True)
    
    # Explicación
    st.write("""**¿Qué muestra este gráfico?**
- Permite ver si el tiempo promedio para pretrabajar un expediente ha mejorado o empeorado a lo largo del año.
- Una tendencia descendente indica mayor eficiencia; una ascendente, posibles cuellos de botella o sobrecarga.""") 