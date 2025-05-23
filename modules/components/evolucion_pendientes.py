"""
Componente para la pestaña de Evolución de Pendientes por Operador
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from modules.data.loader import cargar_historico_pendientes
from modules.utils.excel_export import to_excel_matriz
from modules.utils.analytics import (
    agrupar_anios_antiguos, preparar_tabla_operadores_periodo,
    procesar_datos_produccion, procesar_evolucion_pendientes,
    resaltar_criticos
)
from modules.charts.plotting import crear_grafico_totales_tendencia, crear_grafico_dispersión_eficiencia

def mostrar_evolucion_pendientes(df: pd.DataFrame, proceso: str) -> None:
    """
    Muestra la pestaña de evolución de pendientes por operador
    
    Args:
        df: DataFrame con los datos
        proceso: Tipo de proceso ('CCM' o 'PRR')
    """
    st.header("Evolución de Pendientes por Operador")
    
    # Botón de recarga
    recargar = st.button("Recargar solo histórico")
    
    # Cargar datos históricos
    historico = cargar_historico_pendientes()
    
    # Agrupar años antiguos
    historico = agrupar_anios_antiguos(historico)
    
    # Filtros
    anios_disp = historico[historico['Proceso'] == proceso]['Año'].unique().tolist()
    anios_disp = sorted(set(anios_disp), reverse=True, key=lambda x: (x != 'ANTIGUOS', x))
    anios_sel = st.multiselect("Año(s)", options=['Todos'] + anios_disp, default=['Todos'])
    
    # Filtrar datos según selección
    df_filtro = _filtrar_datos_historicos(historico, proceso, anios_sel, anios_disp)
    
    if df_filtro.empty:
        st.warning("No hay datos disponibles para la selección.")
        return
    
    # Crear matriz de evolución
    tabla_matriz = _crear_matriz_evolucion(df_filtro)
    
    # Mostrar tabla
    st.dataframe(tabla_matriz, use_container_width=True, height=500)
    
    # Botón de descarga
    excel_data_matriz = to_excel_matriz(tabla_matriz)
    st.download_button(
        label="Descargar matriz en Excel",
        data=excel_data_matriz,
        file_name=f"evolucion_pendientes_{proceso}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    
    # Gráfico de totales por fecha
    _mostrar_grafico_totales(tabla_matriz)
    
    # Ranking de evolución
    _mostrar_ranking_evolucion(tabla_matriz, df, proceso)

def _filtrar_datos_historicos(historico: pd.DataFrame, proceso: str, anios_sel: list, 
                            anios_disp: list) -> pd.DataFrame:
    """
    Filtra los datos históricos según la selección de años
    """
    if 'Todos' in anios_sel or not anios_sel:
        # Mostrar solo fechas que existen en todos los años
        anios_validos = [a for a in anios_disp if a != 'Todos']
        fechas_por_anio = [
            set(historico[(historico['Proceso'] == proceso) & (historico['Año'] == anio)]['Fecha'].unique()) 
            for anio in anios_validos
        ]
        if fechas_por_anio:
            fechas_comunes = set.intersection(*fechas_por_anio)
        else:
            fechas_comunes = set()
        df_filtro = historico[
            (historico['Proceso'] == proceso) & 
            (historico['Fecha'].isin(fechas_comunes))
        ].copy()
    elif len(anios_sel) > 1:
        # Mostrar solo fechas que existen en todos los años seleccionados
        fechas_por_anio = [
            set(historico[(historico['Proceso'] == proceso) & (historico['Año'] == anio)]['Fecha'].unique()) 
            for anio in anios_sel
        ]
        if fechas_por_anio:
            fechas_comunes = set.intersection(*fechas_por_anio)
        else:
            fechas_comunes = set()
        df_filtro = historico[
            (historico['Proceso'] == proceso) & 
            (historico['Año'].isin(anios_sel)) & 
            (historico['Fecha'].isin(fechas_comunes))
        ].copy()
    else:
        df_filtro = historico[
            (historico['Proceso'] == proceso) & 
            (historico['Año'].isin(anios_sel))
        ].copy()
    
    return df_filtro

def _crear_matriz_evolucion(df_filtro: pd.DataFrame) -> pd.DataFrame:
    """
    Crea la matriz de evolución de pendientes
    """
    # Pivotear: filas=OPERADOR, columnas=Fecha, valores=Pendientes
    tabla_matriz = df_filtro.pivot_table(
        index='OPERADOR',
        columns='Fecha',
        values='Pendientes',
        aggfunc='sum',
        fill_value=0
    )
    
    # Ordenar columnas por fecha
    tabla_matriz = tabla_matriz.reindex(sorted(tabla_matriz.columns), axis=1)
    
    # Ordenar filas de mayor a menor según la última fecha disponible
    if len(tabla_matriz.columns) > 0:
        ultima_fecha = tabla_matriz.columns[-1]
        tabla_matriz = tabla_matriz.sort_values(by=ultima_fecha, ascending=False)
    
    # Agregar fila TOTAL
    total_row = tabla_matriz.sum(axis=0)
    total_row.name = 'TOTAL'
    tabla_matriz = pd.concat([tabla_matriz, pd.DataFrame([total_row])])
    
    return tabla_matriz

def _mostrar_grafico_totales(tabla_matriz: pd.DataFrame) -> None:
    """
    Muestra el gráfico de evolución de totales
    """
    st.subheader("Evolución de los totales de pendientes")
    
    # Obtener fila de totales
    total_row = tabla_matriz.loc['TOTAL']
    totales = total_row.astype(int)
    
    # Crear y mostrar gráfico
    fig_totales = crear_grafico_totales_tendencia(totales)
    st.plotly_chart(fig_totales, use_container_width=True)

def _mostrar_ranking_evolucion(tabla_matriz: pd.DataFrame, df: pd.DataFrame, proceso: str) -> None:
    """
    Muestra el ranking de evolución de pendientes por operador
    """
    st.subheader("Ranking de evolución de pendientes por operador")
    
    # Selector de periodo
    opciones_periodo = [7, 15, 30, 'Todo el periodo']
    periodo_sel = st.selectbox("Periodo de análisis (días)", opciones_periodo, index=1)
    
    # Solo operadores (sin TOTAL)
    tabla_operadores = tabla_matriz.drop('TOTAL', errors='ignore')
    
    if len(tabla_operadores.columns) == 0:
        st.warning("No hay datos disponibles para el periodo seleccionado.")
        return
    
    # Definir periodo
    if periodo_sel == 'Todo el periodo':
        cols_periodo = tabla_operadores.columns
    else:
        cols_periodo = tabla_operadores.columns[-periodo_sel:]
    
    # Preparar datos para análisis
    pendientes_long = preparar_tabla_operadores_periodo(tabla_operadores, periodo_sel, cols_periodo)
    
    if len(pendientes_long) == 0:
        st.warning("No hay datos suficientes para mostrar el ranking.")
        return
    
    # Obtener datos de producción
    col_operador = 'OperadorPre' if 'OperadorPre' in df.columns else 'OPERADOR'
    col_fecha = 'FechaPre'
    col_tramite = 'NumeroTramite'
    
    prod_promedio = procesar_datos_produccion(df, cols_periodo, col_operador, col_fecha, col_tramite)
    
    # Calcular métricas de evolución
    evolucion = procesar_evolucion_pendientes(pendientes_long, prod_promedio, col_operador)
    
    # Mostrar ranking con formato condicional
    st.dataframe(evolucion.style.apply(resaltar_criticos, axis=1), use_container_width=True)
    
    # Gráfico de dispersión
    fig_scatter = crear_grafico_dispersión_eficiencia(evolucion)
    st.plotly_chart(fig_scatter, use_container_width=True)
    
    # Mostrar resumen por estado
    st.subheader("Resumen por Estado")
    resumen_estado = evolucion.groupby('Eficiencia').agg({
        'OPERADOR_NORM': 'count',
        'Pendientes_Final': 'sum',
        'Produccion_Promedio': 'mean'
    }).round(2)
    st.dataframe(resumen_estado, use_container_width=True) 