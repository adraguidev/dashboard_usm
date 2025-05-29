"""
Componente para la pestaña de Ingresos Diarios
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from modules.utils.excel_export import to_excel_matriz

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
    col_fecha_egr = 'FechaPre'
    col_tramite_ing = 'NumeroTramite'
    
    if col_fecha_ing not in df.columns:
        st.warning("No se encontró la columna FechaExpendiente en los datos.")
        return
    
    # Asegurar tipo datetime
    df[col_fecha_ing] = pd.to_datetime(df[col_fecha_ing], errors='coerce')
    if col_fecha_egr in df.columns:
        df[col_fecha_egr] = pd.to_datetime(df[col_fecha_egr], errors='coerce')
    
    # Mostrar gráfico principal de ingresos
    _mostrar_grafico_ingresos_principales(df, col_fecha_ing, col_tramite_ing)
    
    # Mostrar tabla de últimos 15 días
    _mostrar_tabla_ultimos_dias(df, col_fecha_ing, col_tramite_ing)
    
    # Mostrar promedio semanal
    _mostrar_promedio_semanal(df, col_fecha_ing, col_tramite_ing)
    
    # Nueva sección: Cuadros mensuales con descarga (al final)
    _mostrar_cuadros_mensuales(df, col_fecha_ing, col_fecha_egr, col_tramite_ing, proceso)

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

def _mostrar_cuadros_mensuales(df: pd.DataFrame, col_fecha_ing: str, col_fecha_egr: str, 
                              col_tramite_ing: str, proceso: str) -> None:
    """
    Muestra la sección de cuadros mensuales con opción de descarga
    """
    st.write("#### 📊 Cuadros Mensuales de Ingresos y Egresos")
    
    # Obtener meses disponibles
    df_temp = df.copy()
    df_temp[col_fecha_ing] = pd.to_datetime(df_temp[col_fecha_ing], errors='coerce')
    df_temp['AñoMes'] = df_temp[col_fecha_ing].dt.to_period('M')
    meses_disponibles = sorted(df_temp['AñoMes'].dropna().unique(), reverse=True)
    meses_disponibles_str = [str(m) for m in meses_disponibles[:12]]  # Últimos 12 meses
    
    # Selector de mes
    col1, col2 = st.columns([2, 1])
    with col1:
        mes_seleccionado = st.selectbox(
            "Seleccionar mes para generar cuadro:",
            options=meses_disponibles_str,
            index=0 if meses_disponibles_str else None
        )
    
    if not mes_seleccionado:
        st.warning("No hay datos disponibles para generar cuadros.")
        return
    
    # Crear cuadro mensual
    cuadro_mensual = _crear_cuadro_mensual(df, mes_seleccionado, col_fecha_ing, col_fecha_egr, col_tramite_ing)
    
    if cuadro_mensual.empty:
        st.warning(f"No hay datos disponibles para {mes_seleccionado}.")
        return
    
    # Mostrar métricas resumen
    total_ingresos = cuadro_mensual['Ingresos'].sum()
    total_egresos = cuadro_mensual['Egresos'].sum()
    saldo_neto = total_ingresos - total_egresos
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📥 Total Ingresos", f"{total_ingresos:,}")
    with col2:
        st.metric("📤 Total Egresos", f"{total_egresos:,}")
    with col3:
        st.metric("📊 Saldo Neto", f"{saldo_neto:,}")
    with col4:
        color = "🟢" if saldo_neto >= 0 else "🔴"
        st.metric("📈 Tendencia", f"{color}")
    
    # Mostrar tabla
    st.dataframe(cuadro_mensual, use_container_width=True, height=400)
    
    # Botón de descarga
    with col2:
        excel_data = to_excel_matriz(cuadro_mensual)
        st.download_button(
            label=f"📥 Descargar {mes_seleccionado}.xlsx",
            data=excel_data,
            file_name=f"cuadro_ingresos_egresos_{proceso}_{mes_seleccionado}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

def _crear_cuadro_mensual(df: pd.DataFrame, mes_seleccionado: str, col_fecha_ing: str, 
                         col_fecha_egr: str, col_tramite_ing: str) -> pd.DataFrame:
    """
    Crea el cuadro mensual con fecha, ingresos y egresos
    """
    # Convertir mes seleccionado a periodo
    periodo = pd.Period(mes_seleccionado)
    fecha_inicio = periodo.start_time
    fecha_fin = periodo.end_time
    
    # Crear rango de fechas completo del mes
    fechas_mes = pd.date_range(start=fecha_inicio, end=fecha_fin, freq='D')
    cuadro_base = pd.DataFrame({'Fecha': fechas_mes})
    
    # Calcular ingresos diarios (por FechaExpendiente)
    df_ingresos = df.copy()
    df_ingresos[col_fecha_ing] = pd.to_datetime(df_ingresos[col_fecha_ing], errors='coerce')
    ingresos_diarios = df_ingresos[
        (df_ingresos[col_fecha_ing] >= fecha_inicio) & 
        (df_ingresos[col_fecha_ing] <= fecha_fin)
    ].groupby(col_fecha_ing)[col_tramite_ing].count().reset_index()
    ingresos_diarios = ingresos_diarios.rename(columns={col_fecha_ing: 'Fecha', col_tramite_ing: 'Ingresos'})
    
    # Calcular egresos diarios (por FechaPre)
    egresos_diarios = pd.DataFrame({'Fecha': fechas_mes, 'Egresos': 0})
    if col_fecha_egr in df.columns:
        df_egresos = df.copy()
        df_egresos[col_fecha_egr] = pd.to_datetime(df_egresos[col_fecha_egr], errors='coerce')
        egresos_temp = df_egresos[
            (df_egresos[col_fecha_egr] >= fecha_inicio) & 
            (df_egresos[col_fecha_egr] <= fecha_fin)
        ].groupby(col_fecha_egr)[col_tramite_ing].count().reset_index()
        egresos_temp = egresos_temp.rename(columns={col_fecha_egr: 'Fecha', col_tramite_ing: 'Egresos'})
        egresos_diarios = cuadro_base.merge(egresos_temp, on='Fecha', how='left')
        egresos_diarios['Egresos'] = egresos_diarios['Egresos'].fillna(0)
    
    # Combinar ingresos y egresos
    cuadro_mensual = cuadro_base.merge(ingresos_diarios, on='Fecha', how='left')
    cuadro_mensual = cuadro_mensual.merge(egresos_diarios[['Fecha', 'Egresos']], on='Fecha', how='left')
    
    # Llenar valores faltantes con 0
    cuadro_mensual['Ingresos'] = cuadro_mensual['Ingresos'].fillna(0).astype(int)
    cuadro_mensual['Egresos'] = cuadro_mensual['Egresos'].fillna(0).astype(int)
    
    # Calcular saldo diario y acumulado
    cuadro_mensual['Saldo_Diario'] = cuadro_mensual['Ingresos'] - cuadro_mensual['Egresos']
    cuadro_mensual['Saldo_Acumulado'] = cuadro_mensual['Saldo_Diario'].cumsum()
    
    # Formatear fecha para visualización
    cuadro_mensual['Fecha'] = cuadro_mensual['Fecha'].dt.strftime('%d/%m/%Y')
    
    # Añadir día de la semana con nombres en español
    dias_semana = {
        0: 'Lunes', 1: 'Martes', 2: 'Miércoles', 3: 'Jueves', 
        4: 'Viernes', 5: 'Sábado', 6: 'Domingo'
    }
    fechas_dt = pd.to_datetime(cuadro_mensual['Fecha'], format='%d/%m/%Y')
    cuadro_mensual['Día'] = fechas_dt.dt.dayofweek.map(dias_semana)
    
    # Reordenar columnas
    cuadro_mensual = cuadro_mensual[['Fecha', 'Día', 'Ingresos', 'Egresos', 'Saldo_Diario', 'Saldo_Acumulado']]
    
    return cuadro_mensual 