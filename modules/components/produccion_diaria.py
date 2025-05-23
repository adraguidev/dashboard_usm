"""
Componente para la pestaña de Producción Diaria
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from modules.utils.excel_export import to_excel_with_format_prod, to_excel_with_format_weekend, to_excel_resumen

def mostrar_produccion_diaria(df: pd.DataFrame, proceso: str) -> None:
    """
    Muestra la pestaña de producción diaria con tablas y gráficos
    
    Args:
        df: DataFrame con los datos
        proceso: Tipo de proceso ('CCM' o 'PRR')
    """
    st.header("Producción Diaria")
    
    # Determinar columnas según disponibilidad
    col_operador = 'OperadorPre' if 'OperadorPre' in df.columns else 'OPERADOR'
    col_fecha = 'FechaPre'
    col_tramite = 'NumeroTramite'
    
    # Preparar datos de fechas
    if not pd.api.types.is_datetime64_any_dtype(df[col_fecha]):
        df[col_fecha] = pd.to_datetime(df[col_fecha], errors='coerce')
    
    fechas_ordenadas = df[col_fecha].dropna().sort_values().unique()
    ultimos_20_dias = fechas_ordenadas[-20:]
    df_20dias = df[df[col_fecha].isin(ultimos_20_dias)]
    
    # Crear tabla principal de producción
    tabla_prod = _crear_tabla_produccion(df_20dias, col_operador, col_fecha, col_tramite)
    
    # Filtrar y procesar tabla
    tabla_filtrada_corr = _filtrar_tabla_produccion(tabla_prod)
    
    # Mostrar tabla
    st.dataframe(tabla_filtrada_corr, use_container_width=True, height=500)
    
    # Botón de descarga
    excel_data_prod = to_excel_with_format_prod(tabla_filtrada_corr)
    st.download_button(
        label="Descargar tabla de Producción Diaria en Excel",
        data=excel_data_prod,
        file_name=f"produccion_diaria_{proceso}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    
    # Tabla de fines de semana
    _mostrar_tabla_fines_semana(df, col_operador, col_fecha, col_tramite, proceso)
    
    # Resumen diario
    _mostrar_resumen_diario(df_20dias, col_operador, col_fecha, col_tramite, proceso)
    
    # Gráficos
    _mostrar_graficos_produccion(df_20dias, col_fecha, col_operador, col_tramite)

def _crear_tabla_produccion(df_20dias: pd.DataFrame, col_operador: str, 
                          col_fecha: str, col_tramite: str) -> pd.DataFrame:
    """
    Crea la tabla dinámica de producción diaria
    """
    return pd.pivot_table(
        df_20dias,
        index=col_operador,
        columns=col_fecha,
        values=col_tramite,
        aggfunc='count',
        fill_value=0,
        margins=True,
        margins_name='Total'
    )

def _filtrar_tabla_produccion(tabla_prod: pd.DataFrame) -> pd.DataFrame:
    """
    Filtra y procesa la tabla de producción
    """
    operadores_excluir = [
        "Aponte Sanchez, Paola Lita", 
        "Lucero Martinez, Carlos Martin", 
        "USUARIO DE AGENCIA DIGITAL"
    ]
    
    if 'Total' in tabla_prod.index:
        tabla_filtrada = tabla_prod.drop(operadores_excluir, errors='ignore')
        if tabla_filtrada.shape[0] > 1:
            tabla_filtrada = tabla_filtrada[
                (tabla_filtrada['Total'] >= 5) | (tabla_filtrada.index == 'Total')
            ]
    else:
        tabla_filtrada = tabla_prod.drop(operadores_excluir, errors='ignore')
        tabla_filtrada = tabla_filtrada[tabla_filtrada['Total'] >= 5]

    # Recalcular la fila Total después de filtrar
    tabla_sin_total = tabla_filtrada.drop('Total', errors='ignore')
    total_row = tabla_sin_total.sum(numeric_only=True)
    total_row.name = 'Total'
    tabla_filtrada_corr = pd.concat([tabla_sin_total, pd.DataFrame([total_row])])
    
    # Formatear las fechas de las columnas
    fechas_formateadas = [
        f.strftime('%d/%m/%Y') if not isinstance(f, str) and f != 'Total' else f 
        for f in tabla_filtrada_corr.columns
    ]
    tabla_filtrada_corr.columns = fechas_formateadas
    
    # Ordenar por Total descendente
    if 'Total' in tabla_filtrada_corr.index:
        tabla_sin_total = tabla_filtrada_corr.drop('Total')
        tabla_sin_total = tabla_sin_total.sort_values(by='Total', ascending=False)
        tabla_filtrada_corr = pd.concat([tabla_sin_total, tabla_filtrada_corr.loc[['Total']]])
    else:
        tabla_filtrada_corr = tabla_filtrada_corr.sort_values(by='Total', ascending=False)
    
    return tabla_filtrada_corr

def _mostrar_tabla_fines_semana(df: pd.DataFrame, col_operador: str, col_fecha: str, 
                               col_tramite: str, proceso: str) -> None:
    """
    Muestra la tabla de producción de fines de semana
    """
    st.subheader("Producción Fines de Semana (Últimas 5 semanas)")
    
    # Calcular el rango de fechas de las últimas 5 semanas
    fecha_max = df[col_fecha].max()
    fecha_min = fecha_max - pd.Timedelta(weeks=5)
    df_5sem = df[(df[col_fecha] >= fecha_min) & (df[col_fecha] <= fecha_max)]
    
    # Filtrar solo sábados (5) y domingos (6)
    df_5sem = df_5sem[df_5sem[col_fecha].dt.weekday.isin([5, 6])]
    
    # Crear tabla dinámica
    tabla_weekend = pd.pivot_table(
        df_5sem,
        index=col_operador,
        columns=col_fecha,
        values=col_tramite,
        aggfunc='count',
        fill_value=0,
        margins=True,
        margins_name='Total'
    )
    
    # Filtrar tabla de fin de semana
    operadores_excluir = [
        "Aponte Sanchez, Paola Lita", 
        "Lucero Martinez, Carlos Martin", 
        "USUARIO DE AGENCIA DIGITAL"
    ]
    
    if 'Total' in tabla_weekend.index:
        tabla_weekend_filtrada = tabla_weekend.drop(operadores_excluir, errors='ignore')
        if tabla_weekend_filtrada.shape[0] > 1:
            tabla_weekend_filtrada = tabla_weekend_filtrada[
                (tabla_weekend_filtrada['Total'] >= 5) | (tabla_weekend_filtrada.index == 'Total')
            ]
    else:
        tabla_weekend_filtrada = tabla_weekend.drop(operadores_excluir, errors='ignore')
        tabla_weekend_filtrada = tabla_weekend_filtrada[tabla_weekend_filtrada['Total'] >= 5]
    
    # Recalcular la fila Total después de filtrar
    tabla_sin_total_w = tabla_weekend_filtrada.drop('Total', errors='ignore')
    total_row_w = tabla_sin_total_w.sum(numeric_only=True)
    total_row_w.name = 'Total'
    tabla_weekend_filtrada_corr = pd.concat([tabla_sin_total_w, pd.DataFrame([total_row_w])])
    
    # Formatear las fechas de las columnas
    fechas_formateadas_w = [
        f.strftime('%d/%m/%Y') if not isinstance(f, str) and f != 'Total' else f 
        for f in tabla_weekend_filtrada_corr.columns
    ]
    tabla_weekend_filtrada_corr.columns = fechas_formateadas_w
    
    # Ordenar por Total descendente
    if 'Total' in tabla_weekend_filtrada_corr.index:
        tabla_sin_total_w = tabla_weekend_filtrada_corr.drop('Total')
        tabla_sin_total_w = tabla_sin_total_w.sort_values(by='Total', ascending=False)
        tabla_weekend_filtrada_corr = pd.concat([tabla_sin_total_w, tabla_weekend_filtrada_corr.loc[['Total']]])
    else:
        tabla_weekend_filtrada_corr = tabla_weekend_filtrada_corr.sort_values(by='Total', ascending=False)

    st.dataframe(tabla_weekend_filtrada_corr, use_container_width=True, height=400)
    
    # Botón de descarga
    excel_data_weekend = to_excel_with_format_weekend(tabla_weekend_filtrada_corr)
    st.download_button(
        label="Descargar tabla de fines de semana en Excel",
        data=excel_data_weekend,
        file_name=f"produccion_fines_semana_{proceso}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

def _mostrar_resumen_diario(df_20dias: pd.DataFrame, col_operador: str, col_fecha: str, 
                          col_tramite: str, proceso: str) -> None:
    """
    Muestra el resumen diario de producción
    """
    st.subheader("Resumen Diario de Producción")
    
    # Operadores a excluir
    operadores_excluir_resumen = [
        "Aponte Sanchez, Paola Lita", 
        "Lucero Martinez, Carlos Martin", 
        "USUARIO DE AGENCIA DIGITAL"
    ]
    
    # Filtrar el dataframe de los últimos 20 días
    df_resumen = df_20dias[~df_20dias[col_operador].isin(operadores_excluir_resumen)].copy()
    
    # Calcular el total por operador (en los últimos 20 días)
    totales_operador = df_resumen.groupby(col_operador)[col_tramite].count()
    operadores_validos = totales_operador[totales_operador >= 5].index
    df_resumen = df_resumen[df_resumen[col_operador].isin(operadores_validos)]
    
    # Calcular cantidad de operadores y total de trámites por fecha
    resumen = df_resumen.groupby(col_fecha).agg(
        cantidad_operadores=(col_operador, lambda x: x.nunique()),
        total_trabajados=(col_tramite, 'count')
    )
    resumen = resumen.sort_index()
    resumen['promedio_por_operador'] = resumen['total_trabajados'] / resumen['cantidad_operadores']
    
    # Formatear fechas
    resumen.index = [f.strftime('%d/%m/%Y') if not isinstance(f, str) else f for f in resumen.index]
    
    st.dataframe(resumen, use_container_width=True, height=400)
    
    # Botón para descargar Excel
    excel_data_resumen = to_excel_resumen(resumen)
    st.download_button(
        label="Descargar resumen diario en Excel",
        data=excel_data_resumen,
        file_name=f"resumen_diario_{proceso}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

def _mostrar_graficos_produccion(df_20dias: pd.DataFrame, col_fecha: str, 
                               col_operador: str, col_tramite: str) -> None:
    """
    Muestra los gráficos de producción
    """
    # Preparar datos para gráficos
    operadores_excluir_resumen = [
        "Aponte Sanchez, Paola Lita", 
        "Lucero Martinez, Carlos Martin", 
        "USUARIO DE AGENCIA DIGITAL"
    ]
    
    df_resumen = df_20dias[~df_20dias[col_operador].isin(operadores_excluir_resumen)].copy()
    totales_operador = df_resumen.groupby(col_operador)[col_tramite].count()
    operadores_validos = totales_operador[totales_operador >= 5].index
    df_resumen = df_resumen[df_resumen[col_operador].isin(operadores_validos)]
    
    resumen = df_resumen.groupby(col_fecha).agg(
        cantidad_operadores=(col_operador, lambda x: x.nunique()),
        total_trabajados=(col_tramite, 'count')
    )
    resumen = resumen.sort_index()
    resumen['promedio_por_operador'] = resumen['total_trabajados'] / resumen['cantidad_operadores']
    resumen.index = [f.strftime('%d/%m/%Y') if not isinstance(f, str) else f for f in resumen.index]
    
    # Gráfico de días hábiles
    _crear_grafico_dias_habiles(resumen)
    
    # Gráfico de fines de semana
    _crear_grafico_fines_semana(resumen)
    
    # Gráfico de total de trámites
    _crear_grafico_total_tramites(resumen)

def _crear_grafico_dias_habiles(resumen: pd.DataFrame) -> None:
    """
    Crea el gráfico de promedio diario para días hábiles
    """
    st.subheader("Gráfica: Promedio Diario por Operador (Lunes a Viernes)")
    
    resumen_graf_habiles = resumen.copy()
    resumen_graf_habiles.index = pd.to_datetime(resumen_graf_habiles.index, format='%d/%m/%Y')
    dias_habiles = resumen_graf_habiles.index.weekday < 5
    resumen_graf_habiles = resumen_graf_habiles[dias_habiles]
    
    fig_habiles = go.Figure()
    fig_habiles.add_trace(go.Scatter(
        x=resumen_graf_habiles.index,
        y=resumen_graf_habiles['promedio_por_operador'],
        mode='lines+markers+text',
        name='Promedio por Operador (L-V)',
        text=[f"{v:.1f}" for v in resumen_graf_habiles['promedio_por_operador']],
        textposition="top center"
    ))
    
    # Línea de tendencia
    x_numeric = np.arange(len(resumen_graf_habiles.index))
    y = resumen_graf_habiles['promedio_por_operador'].values
    if len(x_numeric) > 1:
        z = np.polyfit(x_numeric, y, 1)
        tendencia = z[0] * x_numeric + z[1]
        fig_habiles.add_trace(go.Scatter(
            x=resumen_graf_habiles.index,
            y=tendencia,
            mode='lines',
            name='Tendencia',
            line=dict(dash='dash', color='orange')
        ))
    
    fig_habiles.update_layout(
        title='Promedio Diario de Trámites por Operador (Lunes a Viernes)',
        xaxis_title='Fecha',
        yaxis_title='Promedio por Operador',
        legend_title='Métrica',
        hovermode='x unified'
    )
    st.plotly_chart(fig_habiles, use_container_width=True)

def _crear_grafico_fines_semana(resumen: pd.DataFrame) -> None:
    """
    Crea el gráfico de promedio diario para fines de semana
    """
    st.subheader("Gráfica: Promedio Diario por Operador (Fines de Semana)")
    
    resumen_graf_fds = resumen.copy()
    resumen_graf_fds.index = pd.to_datetime(resumen_graf_fds.index, format='%d/%m/%Y')
    dias_fds = resumen_graf_fds.index.weekday >= 5
    resumen_graf_fds = resumen_graf_fds[dias_fds]
    
    fig_fds = go.Figure()
    fig_fds.add_trace(go.Scatter(
        x=resumen_graf_fds.index,
        y=resumen_graf_fds['promedio_por_operador'],
        mode='lines+markers+text',
        name='Promedio por Operador (S-D)',
        text=[f"{v:.1f}" for v in resumen_graf_fds['promedio_por_operador']],
        textposition="top center"
    ))
    
    # Línea de tendencia
    x_numeric_fds = np.arange(len(resumen_graf_fds.index))
    y_fds = resumen_graf_fds['promedio_por_operador'].values
    if len(x_numeric_fds) > 1:
        z_fds = np.polyfit(x_numeric_fds, y_fds, 1)
        tendencia_fds = z_fds[0] * x_numeric_fds + z_fds[1]
        fig_fds.add_trace(go.Scatter(
            x=resumen_graf_fds.index,
            y=tendencia_fds,
            mode='lines',
            name='Tendencia',
            line=dict(dash='dash', color='orange')
        ))
    
    fig_fds.update_layout(
        title='Promedio Diario de Trámites por Operador (Fines de Semana)',
        xaxis_title='Fecha',
        yaxis_title='Promedio por Operador',
        legend_title='Métrica',
        hovermode='x unified'
    )
    st.plotly_chart(fig_fds, use_container_width=True)

def _crear_grafico_total_tramites(resumen: pd.DataFrame) -> None:
    """
    Crea el gráfico de total de trámites diarios
    """
    st.subheader("Gráfica: Total de Trámites Diarios")
    
    resumen_graf_total = resumen.copy()
    resumen_graf_total.index = pd.to_datetime(resumen_graf_total.index, format='%d/%m/%Y')
    
    fig_total = go.Figure()
    fig_total.add_trace(go.Scatter(
        x=resumen_graf_total.index,
        y=resumen_graf_total['total_trabajados'],
        mode='lines+markers+text',
        name='Total de Trámites',
        text=[str(v) for v in resumen_graf_total['total_trabajados']],
        textposition="top center"
    ))
    
    # Línea de tendencia
    x_numeric_total = np.arange(len(resumen_graf_total.index))
    y_total = resumen_graf_total['total_trabajados'].values
    if len(x_numeric_total) > 1:
        z_total = np.polyfit(x_numeric_total, y_total, 1)
        tendencia_total = z_total[0] * x_numeric_total + z_total[1]
        fig_total.add_trace(go.Scatter(
            x=resumen_graf_total.index,
            y=tendencia_total,
            mode='lines',
            name='Tendencia',
            line=dict(dash='dash', color='orange')
        ))
    
    fig_total.update_layout(
        title='Total de Trámites Diarios',
        xaxis_title='Fecha',
        yaxis_title='Total de Trámites',
        legend_title='Métrica',
        hovermode='x unified'
    )
    st.plotly_chart(fig_total, use_container_width=True) 