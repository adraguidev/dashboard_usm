"""
Módulo para análisis y cálculos de eficiencia
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any

def calcular_eficiencia_v2(row: pd.Series) -> str:
    """
    Calcula la eficiencia de un operador basada en producción y tendencia de pendientes
    
    Args:
        row: Serie con los datos del operador
        
    Returns:
        Categoría de eficiencia
    """
    eficiencia_real = row['Produccion_Promedio'] - row['Tendencia_Diaria']  # Cuánto reduce neto
    produccion_promedio_minima_alta = 5
    produccion_promedio_minima_media = 3
    aumento_peligroso_pendientes = 1

    if eficiencia_real > 0 and row['Produccion_Promedio'] >= produccion_promedio_minima_alta:
        return 'Muy Alta'
    elif eficiencia_real > 0 and row['Produccion_Promedio'] >= produccion_promedio_minima_media:
        return 'Alta'
    elif eficiencia_real > 0:  # Producción baja pero reduce neto
        return 'Mejorando'
    elif eficiencia_real == 0 and row['Produccion_Promedio'] > 0:  # Se mantiene, pero produce
        return 'Estable'
    # Casos donde los pendientes aumentan (eficiencia_real <= 0)
    elif (row['Tendencia_Diaria'] > aumento_peligroso_pendientes and 
          row['Produccion_Promedio'] < row['Tendencia_Diaria']):
        return 'En Observación'  # ESTOS SE MARCARÁN EN ROJO
    elif (eficiencia_real < 0 and row['Produccion_Promedio'] > 0 and 
          row['Produccion_Promedio'] > abs(row['Tendencia_Diaria'])):
        return 'Conteniendo'
    elif eficiencia_real < 0 and row['Produccion_Promedio'] > 0:
        return 'Conteniendo'  # Produce, pero no lo suficiente para bajar pendientes netos
    else:  # No produce o produce muy poco y los pendientes aumentan o no bajan
        return 'Baja'

def resaltar_criticos(row: pd.Series) -> List[str]:
    """
    Resalta en rojo los operadores en observación
    
    Args:
        row: Serie con los datos del operador
        
    Returns:
        Lista de estilos CSS para cada columna
    """
    color = 'red' if row['Eficiencia'] == 'En Observación' else ''
    return [f'background-color: {color}'] * len(row)

def calcular_cambio_porcentual(row: pd.Series) -> float:
    """
    Calcula el cambio porcentual evitando divisiones por cero
    
    Args:
        row: Serie con pendientes inicial y cambio
        
    Returns:
        Cambio porcentual calculado
    """
    if row['Pendientes_Inicial'] != 0:
        return round((row['Cambio'] / row['Pendientes_Inicial'] * 100), 1)
    else:
        return np.sign(row['Cambio']) * 100.0 if row['Cambio'] != 0 else 0.0

def procesar_evolucion_pendientes(pendientes_long: pd.DataFrame, prod_promedio: pd.DataFrame, 
                                col_operador: str) -> pd.DataFrame:
    """
    Procesa los datos de evolución de pendientes y calcula métricas
    
    Args:
        pendientes_long: DataFrame con pendientes en formato largo
        prod_promedio: DataFrame con producción promedio por operador
        col_operador: Nombre de la columna del operador
        
    Returns:
        DataFrame con métricas de evolución calculadas
    """
    # Agrupar por operador y calcular métricas de pendientes
    evolucion = pendientes_long.groupby('OPERADOR_NORM').agg({
        'Pendientes': ['first', 'last', 'count']
    }).reset_index()
    
    evolucion.columns = ['OPERADOR_NORM', 'Pendientes_Inicial', 'Pendientes_Final', 'Dias']
    evolucion['Cambio'] = evolucion['Pendientes_Final'] - evolucion['Pendientes_Inicial']
    
    # Calcular cambio porcentual evitando inf
    evolucion['Cambio_Porcentual'] = evolucion.apply(calcular_cambio_porcentual, axis=1)
    evolucion['Tendencia_Diaria'] = (evolucion['Cambio'] / evolucion['Dias']).round(2)
    
    # Unir métricas de pendientes con producción
    evolucion = evolucion.merge(
        prod_promedio,
        left_on='OPERADOR_NORM',
        right_on=col_operador,
        how='left'
    ).drop(columns=[col_operador])
    
    # Calcular eficiencia
    evolucion['Eficiencia'] = evolucion.apply(calcular_eficiencia_v2, axis=1)
    
    return evolucion

def procesar_datos_produccion(df: pd.DataFrame, cols_periodo: pd.Index, 
                            col_operador: str, col_fecha: str, col_tramite: str) -> pd.DataFrame:
    """
    Procesa los datos de producción para un periodo específico
    
    Args:
        df: DataFrame con los datos
        cols_periodo: Columnas del periodo
        col_operador: Nombre de la columna del operador
        col_fecha: Nombre de la columna de fecha
        col_tramite: Nombre de la columna de trámite
        
    Returns:
        DataFrame con producción promedio por operador
    """
    # Convertir fechas a datetime si no lo son
    if not pd.api.types.is_datetime64_any_dtype(df[col_fecha]):
        df[col_fecha] = pd.to_datetime(df[col_fecha], errors='coerce')
    
    # Filtrar por el periodo seleccionado
    fecha_min = pd.to_datetime(cols_periodo[0])
    fecha_max = pd.to_datetime(cols_periodo[-1])
    df_prod = df[(df[col_fecha] >= fecha_min) & (df[col_fecha] <= fecha_max)]
    
    # Calcular producción diaria por operador SOLO para el periodo seleccionado
    fechas_periodo = set([str(f) for f in cols_periodo])
    prod_diaria = df_prod.groupby([col_operador, col_fecha])[col_tramite].count().reset_index()
    prod_diaria[col_operador] = prod_diaria[col_operador].str.strip().str.upper()
    prod_diaria[col_fecha] = prod_diaria[col_fecha].dt.strftime('%Y-%m-%d')
    
    # Filtrar solo fechas del periodo seleccionado
    prod_diaria = prod_diaria[prod_diaria[col_fecha].isin(fechas_periodo)]
    
    # Calcular producción promedio y días de producción solo en el periodo
    prod_promedio = prod_diaria.groupby(col_operador)[col_tramite].agg(['mean', 'count']).reset_index()
    prod_promedio.columns = [col_operador, 'Produccion_Promedio', 'Dias_Produccion']
    prod_promedio[col_operador] = prod_promedio[col_operador].str.strip().str.upper()
    
    return prod_promedio

def preparar_tabla_operadores_periodo(tabla_operadores: pd.DataFrame, periodo_sel: Any, 
                                    cols_periodo: pd.Index) -> pd.DataFrame:
    """
    Prepara la tabla de operadores para el periodo seleccionado
    
    Args:
        tabla_operadores: DataFrame con operadores
        periodo_sel: Periodo seleccionado
        cols_periodo: Columnas del periodo
        
    Returns:
        DataFrame preparado para análisis
    """
    # Asegurarnos que OPERADOR sea una columna
    tabla_operadores = tabla_operadores.reset_index()
    if tabla_operadores.columns[0] != 'OPERADOR':
        tabla_operadores = tabla_operadores.rename(
            columns={tabla_operadores.columns[0]: 'OPERADOR'}
        )
    
    tabla_operadores_periodo = tabla_operadores[['OPERADOR'] + cols_periodo.tolist()]
    tabla_operadores_filtrada = tabla_operadores_periodo[
        tabla_operadores_periodo[cols_periodo[-1]] >= 5
    ]
    
    # Realizar el melt con la estructura correcta
    pendientes_long = tabla_operadores_filtrada.melt(
        id_vars=['OPERADOR'],
        value_vars=cols_periodo,
        var_name='Fecha',
        value_name='Pendientes'
    )
    
    # Normalizar operador y fecha
    pendientes_long['OPERADOR_NORM'] = pendientes_long['OPERADOR'].str.strip().str.upper()
    pendientes_long['Fecha'] = pd.to_datetime(
        pendientes_long['Fecha'], errors='coerce'
    ).dt.strftime('%Y-%m-%d')
    
    return pendientes_long

def agrupar_anios_antiguos(historico: pd.DataFrame) -> pd.DataFrame:
    """
    Agrupa años menores a 2024 como 'ANTIGUOS'
    
    Args:
        historico: DataFrame con el histórico
        
    Returns:
        DataFrame con años agrupados
    """
    historico = historico.copy()
    historico['Año'] = historico['Año'].apply(
        lambda x: 'ANTIGUOS' if (x.isdigit() and int(x) < 2024) or x == 'ANTIGUOS' else x
    )
    return historico 