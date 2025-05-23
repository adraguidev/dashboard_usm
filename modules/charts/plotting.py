"""
Módulo para generar gráficos y visualizaciones
"""

import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff
import pandas as pd
import numpy as np
from typing import Dict, Any

def crear_grafico_totales_tendencia(totales: pd.Series) -> go.Figure:
    """
    Crea un gráfico de evolución de totales con línea de tendencia
    
    Args:
        totales: Serie con los totales por fecha
        
    Returns:
        Figura de Plotly con el gráfico
    """
    fig_totales = go.Figure()
    
    # Línea principal con etiquetas
    fig_totales.add_trace(go.Scatter(
        x=totales.index,
        y=totales.values,
        mode='lines+markers+text',
        name='Total de pendientes',
        text=[str(v) for v in totales.values],
        textposition="top center"
    ))
    
    # Línea de tendencia sobre los últimos 7 días
    if len(totales) >= 2:
        ultimos_7 = totales[-7:]
        x_numeric = list(range(len(ultimos_7)))
        y = ultimos_7.values
        
        if len(x_numeric) > 1:
            z = np.polyfit(x_numeric, y, 1)
            tendencia = z[0] * np.array(x_numeric) + z[1]
            fig_totales.add_trace(go.Scatter(
                x=ultimos_7.index,
                y=tendencia,
                mode='lines',
                name='Tendencia (últimos 7 días)',
                line=dict(dash='dash', color='orange')
            ))
    
    fig_totales.update_layout(
        title='Total de pendientes por fecha',
        xaxis_title='Fecha',
        yaxis_title='Total de pendientes',
        hovermode='x unified'
    )
    
    return fig_totales

def crear_grafico_dispersión_eficiencia(evolucion: pd.DataFrame) -> go.Figure:
    """
    Crea un gráfico de dispersión de tendencia vs producción promedio
    
    Args:
        evolucion: DataFrame con datos de evolución
        
    Returns:
        Figura de Plotly con el gráfico de dispersión
    """
    fig_scatter = px.scatter(
        evolucion,
        x='Produccion_Promedio',
        y='Tendencia_Diaria',
        hover_name='OPERADOR_NORM',
        color='Eficiencia',
        size='Pendientes_Final',
        title='Tendencia vs Producción Promedio',
        labels={
            'Produccion_Promedio': 'Producción Diaria Promedio',
            'Tendencia_Diaria': 'Tendencia Diaria (pendientes/día)'
        }
    )
    
    return fig_scatter

def crear_grafico_produccion_diaria(df_produccion: pd.DataFrame, proceso: str) -> go.Figure:
    """
    Crea un gráfico de producción diaria
    
    Args:
        df_produccion: DataFrame con datos de producción
        proceso: Tipo de proceso
        
    Returns:
        Figura de Plotly con el gráfico de producción
    """
    # Implementar según los datos específicos de producción diaria
    # Esta función necesitará ser completada según la lógica específica
    pass

def crear_grafico_ingresos_diarios(df_ingresos: pd.DataFrame, proceso: str) -> go.Figure:
    """
    Crea un gráfico de ingresos diarios
    
    Args:
        df_ingresos: DataFrame con datos de ingresos
        proceso: Tipo de proceso
        
    Returns:
        Figura de Plotly con el gráfico de ingresos
    """
    # Implementar según los datos específicos de ingresos diarios
    # Esta función necesitará ser completada según la lógica específica
    pass

def crear_grafico_proyeccion_cierre(datos_proyeccion: Dict[str, Any]) -> go.Figure:
    """
    Crea un gráfico de proyección de cierre
    
    Args:
        datos_proyeccion: Diccionario con datos de proyección
        
    Returns:
        Figura de Plotly con el gráfico de proyección
    """
    # Implementar según los datos específicos de proyección
    # Esta función necesitará ser completada según la lógica específica
    pass 