"""
Funciones de cálculo de métricas para el Dashboard Ejecutivo
"""

import pandas as pd
from modules.data.loader import (
    procesar_pendientes, crear_tabla_pendientes, calcular_sin_asignar,
    cargar_historico_pendientes, cargar_base_evaluadores
)
from modules.data.historico_sin_asignar import calcular_tendencia_sin_asignar

def calcular_metricas_exactas_ccm(df: pd.DataFrame) -> dict:
    """
    Calcula métricas para CCM con período de 15 días y operadores activos corregido
    """
    # === PENDIENTES (misma función que pestaña Pendientes) ===
    df_filtrado = procesar_pendientes(df, "CCM")
    tabla_pendientes = crear_tabla_pendientes(df_filtrado, "CCM")
    
    # Total = tabla + sin asignar
    tabla_total = int(tabla_pendientes.loc['Total', 'Total']) if 'Total' in tabla_pendientes.index else 0
    sin_asignar = calcular_sin_asignar(df_filtrado)
    total_pendientes = tabla_total + sin_asignar
    asignados = tabla_total
    
    # === OPERADORES ACTIVOS CORREGIDO (usando base de personal real) ===
    # Usar la base real de evaluadores registrados
    df_base_evaluadores = cargar_base_evaluadores("CCM")
    if not df_base_evaluadores.empty:
        # Usar la cantidad real de evaluadores de la base de datos
        operadores_activos = len(df_base_evaluadores)
    else:
        # Fallback al método anterior si no hay base de evaluadores
        operadores_en_tabla = [idx for idx in tabla_pendientes.index if idx != 'Total']
        operadores_activos = len([op for op in operadores_en_tabla if tabla_pendientes.loc[op, 'Total'] > 0])
    
    # === PRODUCCIÓN DIARIA (PERÍODO DE 15 DÍAS) ===
    col_operador = 'OperadorPre' if 'OperadorPre' in df.columns else 'OPERADOR'
    col_fecha = 'FechaPre'
    col_tramite = 'NumeroTramite'
    
    # Preparar fechas
    if not pd.api.types.is_datetime64_any_dtype(df[col_fecha]):
        df[col_fecha] = pd.to_datetime(df[col_fecha], errors='coerce')
    
    # CAMBIO: Últimos 15 días en lugar de 20
    fechas_ordenadas = df[col_fecha].dropna().sort_values().unique()
    ultimos_15_dias = fechas_ordenadas[-15:]
    df_15dias = df[df[col_fecha].isin(ultimos_15_dias)]
    
    # Filtros exactos de producción diaria
    operadores_excluir = [
        "Aponte Sanchez, Paola Lita", 
        "Lucero Martinez, Carlos Martin", 
        "USUARIO DE AGENCIA DIGITAL"
    ]
    
    df_resumen = df_15dias[~df_15dias[col_operador].isin(operadores_excluir)].copy()
    
    # Filtrar operadores con >= 5 trámites (con observed=True)
    totales_operador = df_resumen.groupby(col_operador, observed=True)[col_tramite].count()
    operadores_validos = totales_operador[totales_operador >= 5].index
    df_resumen = df_resumen[df_resumen[col_operador].isin(operadores_validos)]
    
    # Calcular producción diaria promedio (15 días)
    resumen = df_resumen.groupby(col_fecha, observed=True).agg(
        total_trabajados=(col_tramite, 'count')
    )
    produccion_diaria = resumen['total_trabajados'].sum() / len(ultimos_15_dias) if len(ultimos_15_dias) > 0 else 0
    
    # === INGRESOS DIARIOS (PERÍODO DE 15 DÍAS) ===
    df['FechaExpendiente'] = pd.to_datetime(df['FechaExpendiente'], errors='coerce')
    fecha_limite = df['FechaExpendiente'].max() - pd.Timedelta(days=15)
    ingresos_recientes = df[df['FechaExpendiente'] >= fecha_limite]['NumeroTramite'].count()
    ingresos_diarios = ingresos_recientes / 15
    
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

def calcular_metricas_exactas_prr(df: pd.DataFrame) -> dict:
    """
    Calcula métricas para PRR con período de 15 días y operadores activos corregido
    """
    # === PENDIENTES (misma función que pestaña Pendientes) ===
    df_filtrado = procesar_pendientes(df, "PRR")
    tabla_pendientes = crear_tabla_pendientes(df_filtrado, "PRR")
    
    # Total = tabla + sin asignar
    tabla_total = int(tabla_pendientes.loc['Total', 'Total']) if 'Total' in tabla_pendientes.index else 0
    sin_asignar = calcular_sin_asignar(df_filtrado)
    total_pendientes = tabla_total + sin_asignar
    asignados = tabla_total
    
    # === OPERADORES ACTIVOS CORREGIDO (usando base de personal real) ===
    # Usar la base real de evaluadores registrados
    df_base_evaluadores = cargar_base_evaluadores("PRR")
    if not df_base_evaluadores.empty:
        # Usar la cantidad real de evaluadores de la base de datos
        operadores_activos = len(df_base_evaluadores)
    else:
        # Fallback al método anterior si no hay base de evaluadores
        operadores_en_tabla = [idx for idx in tabla_pendientes.index if idx != 'Total']
        operadores_activos = len([op for op in operadores_en_tabla if tabla_pendientes.loc[op, 'Total'] > 0])
    
    # === PRODUCCIÓN DIARIA (PERÍODO DE 15 DÍAS) ===
    col_operador = 'OperadorPre' if 'OperadorPre' in df.columns else 'OPERADOR'
    col_fecha = 'FechaPre'
    col_tramite = 'NumeroTramite'
    
    # Preparar fechas
    if not pd.api.types.is_datetime64_any_dtype(df[col_fecha]):
        df[col_fecha] = pd.to_datetime(df[col_fecha], errors='coerce')
    
    # CAMBIO: Últimos 15 días en lugar de 20
    fechas_ordenadas = df[col_fecha].dropna().sort_values().unique()
    ultimos_15_dias = fechas_ordenadas[-15:]
    df_15dias = df[df[col_fecha].isin(ultimos_15_dias)]
    
    # Filtros exactos de producción diaria
    operadores_excluir = [
        "Aponte Sanchez, Paola Lita", 
        "Lucero Martinez, Carlos Martin", 
        "USUARIO DE AGENCIA DIGITAL"
    ]
    
    df_resumen = df_15dias[~df_15dias[col_operador].isin(operadores_excluir)].copy()
    
    # Filtrar operadores con >= 5 trámites (con observed=True)
    totales_operador = df_resumen.groupby(col_operador, observed=True)[col_tramite].count()
    operadores_validos = totales_operador[totales_operador >= 5].index
    df_resumen = df_resumen[df_resumen[col_operador].isin(operadores_validos)]
    
    # Calcular producción diaria promedio (15 días)
    resumen = df_resumen.groupby(col_fecha, observed=True).agg(
        total_trabajados=(col_tramite, 'count')
    )
    produccion_diaria = resumen['total_trabajados'].sum() / len(ultimos_15_dias) if len(ultimos_15_dias) > 0 else 0
    
    # === INGRESOS DIARIOS (PERÍODO DE 15 DÍAS) ===
    df['FechaExpendiente'] = pd.to_datetime(df['FechaExpendiente'], errors='coerce')
    fecha_limite = df['FechaExpendiente'].max() - pd.Timedelta(days=15)
    ingresos_recientes = df[df['FechaExpendiente'] >= fecha_limite]['NumeroTramite'].count()
    ingresos_diarios = ingresos_recientes / 15
    
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

def consolidar_metricas(metricas_ccm: dict, metricas_prr: dict) -> dict:
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

def calcular_tendencias_reales(metricas_ccm: dict, metricas_prr: dict) -> dict:
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
                        'delta_sin_asignar': tendencias_sin_asignar.get(f'delta_{proceso}', 0)
                    }
                else:
                    # Sin suficientes datos históricos
                    deltas[proceso] = {
                        'delta_pendientes': 0,
                        'delta_operadores': 0,
                        'delta_sin_asignar': tendencias_sin_asignar.get(f'delta_{proceso}', 0)
                    }
            else:
                # Sin datos históricos para este proceso
                deltas[proceso] = {
                    'delta_pendientes': 0,
                    'delta_operadores': 0,
                    'delta_sin_asignar': tendencias_sin_asignar.get(f'delta_{proceso}', 0)
                }
    else:
        # Sin histórico de pendientes
        for proceso in ['ccm', 'prr']:
            deltas[proceso] = {
                'delta_pendientes': 0,
                'delta_operadores': 0,
                'delta_sin_asignar': tendencias_sin_asignar.get(f'delta_{proceso}', 0)
            }
    
    return deltas 