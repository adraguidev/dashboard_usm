"""
Componente para la pestaña de Proyección de Cierre
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from typing import Dict, Any

def mostrar_proyeccion_cierre(df: pd.DataFrame, proceso: str) -> None:
    """
    Muestra la pestaña de proyección de cierre y equilibrio
    
    Args:
        df: DataFrame con los datos
        proceso: Tipo de proceso ('CCM' o 'PRR')
    """
    st.header("Proyección de Cierre y Equilibrio")
    
    # Calcular métricas base
    metricas = _calcular_metricas_base(df, proceso)
    
    # Input del usuario
    personal_simulacion = _mostrar_configuracion_simulacion(metricas['num_operadores_activos_defecto'])
    
    # Calcular proyecciones
    proyecciones = _calcular_proyecciones(metricas, personal_simulacion)
    
    # Mostrar resumen
    _mostrar_resumen_proyeccion(metricas, proyecciones, personal_simulacion)
    
    # Mostrar gráfico
    _mostrar_grafico_proyeccion(metricas, proyecciones)

def _calcular_metricas_base(df: pd.DataFrame, proceso: str) -> Dict[str, Any]:
    """
    Calcula las métricas base para la proyección
    """
    # Pendientes actuales
    if proceso == "CCM":
        df_pend_calc = df[
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
        df_pend_calc = df[
            (df['UltimaEtapa'].isin(etapas_prr)) &
            (df['EstadoPre'].isna()) &
            (df['EstadoTramite'] == 'PENDIENTE') &
            (df['EQUIPO'] != 'VULNERABLE')
        ]
    
    pendientes_actuales_totales = len(df_pend_calc)
    pendientes_sin_asignar_actuales = df_pend_calc['OPERADOR'].isna().sum()
    pendientes_asignados_actuales = pendientes_actuales_totales - pendientes_sin_asignar_actuales
    
    # Ingresos diarios promedio (últimos 60 días)
    df_copy = df.copy()
    df_copy['FechaExpendiente'] = pd.to_datetime(df_copy['FechaExpendiente'], errors='coerce')
    fecha_max_ingresos = df_copy['FechaExpendiente'].max()
    fecha_min_ingresos = fecha_max_ingresos - pd.Timedelta(days=60)
    ingresos_ultimos_60d = df_copy[
        (df_copy['FechaExpendiente'] >= fecha_min_ingresos) & 
        (df_copy['FechaExpendiente'] <= fecha_max_ingresos)
    ]
    ingresos_diarios_promedio = ingresos_ultimos_60d.groupby(
        df_copy['FechaExpendiente'].dt.date
    )['NumeroTramite'].count().mean()
    
    if pd.isna(ingresos_diarios_promedio):
        ingresos_diarios_promedio = 0
    
    # Productividad individual promedio
    productividad_individual_promedio = _calcular_productividad_individual(df_copy)
    
    # Personal activo por defecto
    operadores_con_pendientes = df_pend_calc.groupby('OPERADOR').size()
    operadores_con_min_pendientes = operadores_con_pendientes[operadores_con_pendientes >= 5]
    num_operadores_activos_defecto = len(operadores_con_min_pendientes)
    if num_operadores_activos_defecto == 0:
        num_operadores_activos_defecto = 1
    
    return {
        'pendientes_actuales_totales': pendientes_actuales_totales,
        'pendientes_sin_asignar_actuales': pendientes_sin_asignar_actuales,
        'pendientes_asignados_actuales': pendientes_asignados_actuales,
        'ingresos_diarios_promedio': ingresos_diarios_promedio,
        'productividad_individual_promedio': productividad_individual_promedio,
        'num_operadores_activos_defecto': num_operadores_activos_defecto
    }

def _calcular_productividad_individual(df: pd.DataFrame) -> float:
    """
    Calcula la productividad individual promedio
    """
    col_operador_prod = 'OperadorPre' if 'OperadorPre' in df.columns else 'OPERADOR'
    col_fecha_prod = 'FechaPre'
    col_tramite_prod = 'NumeroTramite'
    
    if not pd.api.types.is_datetime64_any_dtype(df[col_fecha_prod]):
        df[col_fecha_prod] = pd.to_datetime(df[col_fecha_prod], errors='coerce')
    
    fechas_ordenadas_prod = df[col_fecha_prod].dropna().sort_values().unique()
    ultimos_20_dias_prod = fechas_ordenadas_prod[-20:]
    df_20dias_prod = df[df[col_fecha_prod].isin(ultimos_20_dias_prod)]
    
    operadores_excluir_prod = [
        "Aponte Sanchez, Paola Lita", "Lucero Martinez, Carlos Martin",
        "USUARIO DE AGENCIA DIGITAL", "MAURICIO ROMERO, HUGO", "Sin asignar"
    ]
    df_20dias_prod = df_20dias_prod[~df_20dias_prod[col_operador_prod].isin(operadores_excluir_prod)]
    
    totales_operador_prod = df_20dias_prod.groupby(col_operador_prod)[col_tramite_prod].count()
    operadores_validos_prod = totales_operador_prod[totales_operador_prod >= 5].index
    df_20dias_prod = df_20dias_prod[df_20dias_prod[col_operador_prod].isin(operadores_validos_prod)]
    
    resumen_prod_diaria = df_20dias_prod.groupby(df[col_fecha_prod].dt.date).agg(
        cantidad_operadores=(col_operador_prod, lambda x: x.nunique()),
        total_trabajados=(col_tramite_prod, 'count')
    )
    
    if (not resumen_prod_diaria.empty and 
        'cantidad_operadores' in resumen_prod_diaria and 
        'total_trabajados' in resumen_prod_diaria):
        resumen_prod_diaria = resumen_prod_diaria[resumen_prod_diaria['cantidad_operadores'] > 0]
        resumen_prod_diaria['promedio_por_operador'] = (
            resumen_prod_diaria['total_trabajados'] / resumen_prod_diaria['cantidad_operadores']
        )
        productividad_individual_promedio = resumen_prod_diaria['promedio_por_operador'].mean()
    else:
        productividad_individual_promedio = 0
    
    if pd.isna(productividad_individual_promedio) or productividad_individual_promedio == 0:
        productividad_individual_promedio = 1
        st.warning(
            "No se pudo calcular la productividad individual promedio o es cero. "
            "Se usará un valor de 1 para cálculos. Revise los datos de producción."
        )
    
    return productividad_individual_promedio

def _mostrar_configuracion_simulacion(num_operadores_activos_defecto: int) -> int:
    """
    Muestra la configuración de la simulación
    """
    st.write("### Configure la Simulación")
    return st.number_input(
        "Cantidad de personal activo para la simulación:",
        min_value=1, max_value=100, value=num_operadores_activos_defecto, step=1
    )

def _calcular_proyecciones(metricas: Dict[str, Any], personal_simulacion: int) -> Dict[str, Any]:
    """
    Calcula las proyecciones basadas en las métricas y personal configurado
    """
    cierres_estimados_diarios_simulacion = (
        metricas['productividad_individual_promedio'] * personal_simulacion
    )
    balance_diario_proyectado = (
        cierres_estimados_diarios_simulacion - metricas['ingresos_diarios_promedio']
    )
    
    # Calcular días para cero pendientes
    if balance_diario_proyectado > 0:
        dias_para_cero_pendientes = metricas['pendientes_actuales_totales'] / balance_diario_proyectado
    else:
        dias_para_cero_pendientes = float('inf')
    
    # Personal para equilibrio
    if metricas['productividad_individual_promedio'] > 0:
        personal_eq_flujo = np.ceil(
            metricas['ingresos_diarios_promedio'] / metricas['productividad_individual_promedio']
        )
    else:
        personal_eq_flujo = 0
    
    return {
        'cierres_estimados_diarios_simulacion': cierres_estimados_diarios_simulacion,
        'balance_diario_proyectado': balance_diario_proyectado,
        'dias_para_cero_pendientes': dias_para_cero_pendientes,
        'personal_eq_flujo': personal_eq_flujo
    }

def _mostrar_resumen_proyeccion(metricas: Dict[str, Any], proyecciones: Dict[str, Any], 
                              personal_simulacion: int) -> None:
    """
    Muestra el resumen de la proyección
    """
    st.write("### Resumen de Proyección")
    
    data_resumen = {
        'Métrica': [
            "**SITUACIÓN ACTUAL**",
            "Pendientes Totales Actuales",
            "Pendientes Asignados",
            "Pendientes Sin Asignar",
            "Ingresos Diarios Promedio (últimos 60 días)",
            "Productividad Individual Promedio (cierres/persona/día, últimos 20 días)",
            "**SIMULACIÓN CON PERSONAL CONFIGURADO**",
            "Personal Activo en Simulación",
            "Cierres Diarios Estimados (total equipo)",
            "Balance Diario Proyectado (Cierres Estimados - Ingresos Promedio)",
            "Proyección de Agotamiento de Pendientes Actuales",
            "**ANÁLISIS DE EQUILIBRIO DE FLUJO (Ingresos = Cierres)**",
            "Personal Necesario para Equilibrio de Flujo (aprox.)"
        ],
        'Valor': [
            "",  # Separador
            f"{metricas['pendientes_actuales_totales']}",
            f"{metricas['pendientes_asignados_actuales']}",
            f"{metricas['pendientes_sin_asignar_actuales']}",
            f"{metricas['ingresos_diarios_promedio']:.2f}",
            f"{metricas['productividad_individual_promedio']:.2f}",
            "",  # Separador
            f"{personal_simulacion}",
            f"{proyecciones['cierres_estimados_diarios_simulacion']:.2f}",
            "",  # Llenado dinámico
            "",  # Llenado dinámico
            "",  # Separador
            ""   # Llenado dinámico
        ]
    }
    
    # Llenado dinámico de Balance Diario
    balance = proyecciones['balance_diario_proyectado']
    if balance > 0:
        data_resumen['Valor'][9] = (
            f"Superávit de {balance:.2f} expedientes/día. (Pendientes tienden a disminuir)"
        )
    elif balance < 0:
        data_resumen['Valor'][9] = (
            f"Déficit de {abs(balance):.2f} expedientes/día. (Pendientes tienden a aumentar)"
        )
    else:
        data_resumen['Valor'][9] = (
            "Equilibrio: 0 expedientes/día. (Pendientes tienden a mantenerse estables)"
        )
    
    # Llenado dinámico de Días para Cero Pendientes
    if proyecciones['dias_para_cero_pendientes'] != float('inf'):
        data_resumen['Valor'][10] = (
            f"{proyecciones['dias_para_cero_pendientes']:.1f} días (si el ritmo se mantiene)"
        )
    else:
        data_resumen['Valor'][10] = "No se agotarán los pendientes actuales con este ritmo."
    
    # Llenado dinámico de Personal para Equilibrio
    if proyecciones['personal_eq_flujo'] > 0:
        data_resumen['Valor'][12] = f"{int(proyecciones['personal_eq_flujo'])} personas"
    else:
        data_resumen['Valor'][12] = "No calculable (productividad individual es cero o no disponible)"
    
    resumen_df = pd.DataFrame(data_resumen)
    st.dataframe(resumen_df, use_container_width=True, hide_index=True)
    
    st.write("""
    **Interpretación del Resumen:**
    - **Situación Actual:** Muestra el estado actual de pendientes, ingresos y la capacidad de cierre individual.
    - **Simulación:** Proyecta el impacto del personal configurado. El "Balance Diario" es clave:
        - *Superávit*: Se cierran más expedientes de los que ingresan diariamente.
        - *Déficit*: Ingresan más expedientes de los que se cierran diariamente.
        - *Equilibrio*: Los cierres diarios igualan a los ingresos.
    - **Análisis de Equilibrio de Flujo:** Indica cuántas personas se necesitarían para que la cantidad de expedientes cerrados por día iguale la cantidad de expedientes que ingresan por día. Este es el punto donde el *stock* de pendientes dejaría de crecer.
    """)

def _mostrar_grafico_proyeccion(metricas: Dict[str, Any], proyecciones: Dict[str, Any]) -> None:
    """
    Muestra el gráfico de proyección de pendientes
    """
    st.write("### Gráfico de Proyección de Pendientes")
    
    max_dias_grafico = 180
    if (proyecciones['balance_diario_proyectado'] > 0 and 
        proyecciones['dias_para_cero_pendientes'] != float('inf')):
        max_dias_grafico = min(max_dias_grafico, int(proyecciones['dias_para_cero_pendientes']) + 30)
    
    dias_proy = list(range(0, max_dias_grafico + 1))
    
    # Calcular pendientes proyectados
    pendientes_proyectados_graf = [
        max(0, metricas['pendientes_actuales_totales'] - 
            proyecciones['balance_diario_proyectado'] * d) 
        for d in dias_proy
    ]
    
    fig_proy = go.Figure()
    fig_proy.add_trace(go.Scatter(
        x=dias_proy,
        y=pendientes_proyectados_graf,
        mode='lines+markers',
        name='Pendientes Proyectados'
    ))
    
    fig_proy.update_layout(
        title='Evolución Estimada del Total de Pendientes',
        xaxis_title='Días desde Hoy',
        yaxis_title='Cantidad de Pendientes',
        hovermode='x unified'
    )
    
    st.plotly_chart(fig_proy, use_container_width=True)
    
    st.write(f"""
    **Interpretación del Gráfico:**
    - El gráfico muestra cómo se proyecta que evolucione el **stock total de pendientes** día a día, considerando:
        - El total de pendientes actuales.
        - Los ingresos diarios promedio estimados ({metricas['ingresos_diarios_promedio']:.2f}).
        - Los cierres diarios estimados con el personal configurado ({proyecciones['cierres_estimados_diarios_simulacion']:.2f}).
    - **Si la línea desciende:** Los cierres superan a los ingresos. El punto donde cruza el eje X (cero pendientes) es la estimación de días para agotar los pendientes actuales.
    - **Si la línea asciende:** Los ingresos superan a los cierres. Los pendientes aumentarán.
    - **Si la línea es horizontal:** Los ingresos igualan a los cierres. El stock de pendientes se mantendría estable.
    Este gráfico asume que los promedios de ingresos y la productividad individual se mantienen constantes durante el período de proyección.
    """) 