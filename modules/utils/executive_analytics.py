"""
Módulo para análisis ejecutivos avanzados
Funciones especializadas para el Dashboard Ejecutivo
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from datetime import datetime, timedelta

def calcular_kpis_ejecutivos(df_ccm: pd.DataFrame, df_prr: pd.DataFrame) -> Dict:
    """
    Calcula KPIs ejecutivos consolidados
    
    Args:
        df_ccm: DataFrame de CCM
        df_prr: DataFrame de PRR
        
    Returns:
        Diccionario con KPIs ejecutivos
    """
    # Métricas por proceso
    kpis_ccm = _calcular_kpis_proceso(df_ccm, "CCM")
    kpis_prr = _calcular_kpis_proceso(df_prr, "PRR")
    
    # Consolidación
    kpis_consolidados = {
        'pendientes_total': kpis_ccm['pendientes'] + kpis_prr['pendientes'],
        'produccion_total': kpis_ccm['produccion_diaria'] + kpis_prr['produccion_diaria'],
        'ingresos_total': kpis_ccm['ingresos_diarios'] + kpis_prr['ingresos_diarios'],
        'operadores_total': kpis_ccm['operadores_activos'] + kpis_prr['operadores_activos'],
        'eficiencia_general': _calcular_eficiencia_consolidada(kpis_ccm, kpis_prr),
        'ccm': kpis_ccm,
        'prr': kpis_prr
    }
    
    return kpis_consolidados

def generar_alertas_criticas(kpis: Dict) -> List[Dict]:
    """
    Genera alertas críticas basadas en umbrales ejecutivos
    
    Args:
        kpis: Diccionario con KPIs calculados
        
    Returns:
        Lista de alertas con nivel de criticidad
    """
    alertas = []
    
    # Alertas de pendientes
    if kpis['pendientes_total'] > 2000:
        alertas.append({
            'nivel': 'critico',
            'tipo': 'pendientes',
            'mensaje': f"Pendientes totales críticos: {kpis['pendientes_total']:,}",
            'icono': '🔴'
        })
    elif kpis['pendientes_total'] > 1500:
        alertas.append({
            'nivel': 'warning',
            'tipo': 'pendientes',
            'mensaje': f"Pendientes totales elevados: {kpis['pendientes_total']:,}",
            'icono': '🟡'
        })
    
    # Alertas de eficiencia
    if kpis['eficiencia_general'] < 0.8:
        alertas.append({
            'nivel': 'critico',
            'tipo': 'eficiencia',
            'mensaje': f"Eficiencia crítica: {kpis['eficiencia_general']*100:.1f}%",
            'icono': '🔴'
        })
    elif kpis['eficiencia_general'] < 0.9:
        alertas.append({
            'nivel': 'warning',
            'tipo': 'eficiencia',
            'mensaje': f"Eficiencia baja: {kpis['eficiencia_general']*100:.1f}%",
            'icono': '🟡'
        })
    
    # Alertas por proceso individual
    for proceso in ['ccm', 'prr']:
        datos = kpis[proceso]
        if datos['sin_asignar'] > datos['pendientes'] * 0.2:
            alertas.append({
                'nivel': 'warning',
                'tipo': 'asignacion',
                'mensaje': f"{proceso.upper()}: {datos['sin_asignar']} casos sin asignar",
                'icono': '🟡'
            })
    
    return alertas

def calcular_semaforos_estado(kpis: Dict) -> Dict:
    """
    Calcula estados de semáforo para indicadores clave
    
    Args:
        kpis: Diccionario con KPIs
        
    Returns:
        Diccionario con estados de semáforos
    """
    def obtener_estado_semaforo(valor: float, umbrales: Dict) -> Tuple[str, str]:
        """Determina estado del semáforo basado en umbrales"""
        if valor >= umbrales['verde']:
            return "🟢", "Excelente"
        elif valor >= umbrales['amarillo']:
            return "🟡", "Aceptable"
        else:
            return "🔴", "Crítico"
    
    # Definir umbrales
    umbrales_eficiencia = {'verde': 1.1, 'amarillo': 0.9}
    umbrales_carga = {'verde': 70, 'amarillo': 50}  # Invertido: menos carga es mejor
    umbrales_asignacion = {'verde': 95, 'amarillo': 85}  # % de casos asignados
    
    # Calcular estados
    eficiencia = kpis['eficiencia_general']
    carga_promedio = kpis['pendientes_total'] / kpis['operadores_total'] if kpis['operadores_total'] > 0 else 100
    porcentaje_asignado = ((kpis['pendientes_total'] - kpis['ccm']['sin_asignar'] - kpis['prr']['sin_asignar']) / 
                          kpis['pendientes_total'] * 100) if kpis['pendientes_total'] > 0 else 100
    
    semaforos = {
        'eficiencia': {
            'valor': eficiencia,
            'estado': obtener_estado_semaforo(eficiencia, umbrales_eficiencia),
            'descripcion': f"{eficiencia*100:.1f}%"
        },
        'carga': {
            'valor': carga_promedio,
            'estado': obtener_estado_semaforo(100-carga_promedio, umbrales_carga),
            'descripcion': f"{carga_promedio:.1f} casos/operador"
        },
        'asignacion': {
            'valor': porcentaje_asignado,
            'estado': obtener_estado_semaforo(porcentaje_asignado, umbrales_asignacion),
            'descripcion': f"{porcentaje_asignado:.1f}% asignados"
        }
    }
    
    return semaforos

def generar_tendencias_ejecutivas(df_ccm: pd.DataFrame, df_prr: pd.DataFrame, 
                                 periodo_dias: int = 30) -> Dict:
    """
    Genera datos de tendencias para gráficos ejecutivos
    
    Args:
        df_ccm: DataFrame de CCM
        df_prr: DataFrame de PRR
        periodo_dias: Número de días para análisis
        
    Returns:
        Diccionario con datos de tendencias
    """
    # Fechas del período
    fecha_fin = datetime.now()
    fecha_inicio = fecha_fin - timedelta(days=periodo_dias)
    fechas = pd.date_range(start=fecha_inicio, end=fecha_fin, freq='D')
    
    # Simular tendencias basadas en datos reales
    tendencias = {
        'fechas': fechas,
        'pendientes_ccm': _simular_tendencia_pendientes(df_ccm, fechas, 'CCM'),
        'pendientes_prr': _simular_tendencia_pendientes(df_prr, fechas, 'PRR'),
        'produccion_diaria': _simular_tendencia_produccion(df_ccm, df_prr, fechas),
        'ingresos_diarios': _simular_tendencia_ingresos(df_ccm, df_prr, fechas)
    }
    
    return tendencias

def calcular_metricas_comparativas(kpis: Dict) -> Dict:
    """
    Calcula métricas comparativas entre CCM y PRR
    
    Args:
        kpis: Diccionario con KPIs
        
    Returns:
        Diccionario con métricas comparativas
    """
    ccm = kpis['ccm']
    prr = kpis['prr']
    
    comparativas = {
        'pendientes': {
            'ccm': ccm['pendientes'],
            'prr': prr['pendientes'],
            'diferencia': ccm['pendientes'] - prr['pendientes'],
            'porcentaje_ccm': (ccm['pendientes'] / (ccm['pendientes'] + prr['pendientes']) * 100) 
                             if (ccm['pendientes'] + prr['pendientes']) > 0 else 0
        },
        'productividad': {
            'ccm': ccm['produccion_diaria'],
            'prr': prr['produccion_diaria'],
            'ratio': ccm['produccion_diaria'] / prr['produccion_diaria'] if prr['produccion_diaria'] > 0 else 0
        },
        'eficiencia': {
            'ccm': ccm['produccion_diaria'] / ccm['ingresos_diarios'] if ccm['ingresos_diarios'] > 0 else 0,
            'prr': prr['produccion_diaria'] / prr['ingresos_diarios'] if prr['ingresos_diarios'] > 0 else 0
        },
        'carga_operadores': {
            'ccm': ccm['pendientes'] / ccm['operadores_activos'] if ccm['operadores_activos'] > 0 else 0,
            'prr': prr['pendientes'] / prr['operadores_activos'] if prr['operadores_activos'] > 0 else 0
        }
    }
    
    return comparativas

def _calcular_kpis_proceso(df: pd.DataFrame, proceso: str) -> Dict:
    """Calcula KPIs para un proceso específico"""
    # Implementación similar a la del dashboard ejecutivo pero más robusta
    if proceso == "CCM":
        df_pendientes = df[
            (df['UltimaEtapa'] == 'EVALUACIÓN - I') &
            (df['EstadoPre'].isna()) &
            (df['EstadoTramite'] == 'PENDIENTE') &
            (df['EQUIPO'] != 'VULNERABLE')
        ]
    else:
        etapas_prr = [
            'ACTUALIZAR DATOS BENEFICIARIO - F', 'ACTUALIZAR DATOS BENEFICIARIO - I',
            'ASOCIACION BENEFICIARIO - F', 'ASOCIACION BENEFICIARIO - I',
            'CONFORMIDAD SUB-DIREC.INMGRA. - I', 'PAGOS, FECHA Y NRO RD. - F',
            'PAGOS, FECHA Y NRO RD. - I', 'RECEPCIÓN DINM - F'
        ]
        df_pendientes = df[
            (df['UltimaEtapa'].isin(etapas_prr)) &
            (df['EstadoPre'].isna()) &
            (df['EstadoTramite'] == 'PENDIENTE') &
            (df['EQUIPO'] != 'VULNERABLE')
        ]
    
    # Cálculos básicos
    pendientes = len(df_pendientes)
    sin_asignar = df_pendientes['OPERADOR'].isna().sum()
    operadores_activos = df_pendientes['OPERADOR'].dropna().nunique()
    
    # Productividad (últimos 15 días)
    col_fecha = 'FechaPre'
    df[col_fecha] = pd.to_datetime(df[col_fecha], errors='coerce')
    fecha_limite = df[col_fecha].max() - timedelta(days=15)
    produccion_reciente = df[df[col_fecha] >= fecha_limite]
    produccion_diaria = len(produccion_reciente) / 15 if len(produccion_reciente) > 0 else 0
    
    # Ingresos (últimos 30 días)
    df['FechaExpendiente'] = pd.to_datetime(df['FechaExpendiente'], errors='coerce')
    fecha_limite_ing = df['FechaExpendiente'].max() - timedelta(days=30)
    ingresos_recientes = df[df['FechaExpendiente'] >= fecha_limite_ing]
    ingresos_diarios = len(ingresos_recientes) / 30 if len(ingresos_recientes) > 0 else 0
    
    return {
        'pendientes': pendientes,
        'sin_asignar': sin_asignar,
        'operadores_activos': operadores_activos,
        'produccion_diaria': produccion_diaria,
        'ingresos_diarios': ingresos_diarios,
        'promedio_por_operador': pendientes / operadores_activos if operadores_activos > 0 else 0
    }

def _calcular_eficiencia_consolidada(kpis_ccm: Dict, kpis_prr: Dict) -> float:
    """Calcula eficiencia general consolidada"""
    produccion_total = kpis_ccm['produccion_diaria'] + kpis_prr['produccion_diaria']
    ingresos_total = kpis_ccm['ingresos_diarios'] + kpis_prr['ingresos_diarios']
    
    return produccion_total / ingresos_total if ingresos_total > 0 else 0

def _simular_tendencia_pendientes(df: pd.DataFrame, fechas: pd.DatetimeIndex, proceso: str) -> List[int]:
    """Simula tendencia de pendientes basada en datos reales"""
    base = len(df) // 2  # Valor base aproximado
    tendencia = []
    
    for i, fecha in enumerate(fechas):
        # Simulación con variación realista
        variacion = np.random.normal(0, base * 0.1)  # 10% de variación
        valor = max(0, int(base + variacion + (i * np.random.normal(0, 5))))
        tendencia.append(valor)
    
    return tendencia

def _simular_tendencia_produccion(df_ccm: pd.DataFrame, df_prr: pd.DataFrame, 
                                fechas: pd.DatetimeIndex) -> List[float]:
    """Simula tendencia de producción diaria"""
    base_ccm = len(df_ccm) // 60  # Aproximación de producción diaria
    base_prr = len(df_prr) // 60
    base_total = base_ccm + base_prr
    
    tendencia = []
    for fecha in fechas:
        # Variación según día de la semana
        factor_dia = 0.7 if fecha.weekday() >= 5 else 1.0  # Menor producción en fines de semana
        variacion = np.random.normal(1, 0.2)  # 20% de variación
        valor = max(0, base_total * factor_dia * variacion)
        tendencia.append(valor)
    
    return tendencia

def _simular_tendencia_ingresos(df_ccm: pd.DataFrame, df_prr: pd.DataFrame, 
                              fechas: pd.DatetimeIndex) -> List[float]:
    """Simula tendencia de ingresos diarios"""
    base_total = (len(df_ccm) + len(df_prr)) // 90  # Aproximación de ingresos diarios
    
    tendencia = []
    for fecha in fechas:
        variacion = np.random.normal(1, 0.15)  # 15% de variación
        valor = max(0, base_total * variacion)
        tendencia.append(valor)
    
    return tendencia 