"""
Funciones de KPIs para el Dashboard Ejecutivo
"""

import streamlit as st

def mostrar_kpis_principales(consolidadas: dict, ccm: dict, prr: dict, tendencias: dict) -> None:
    """
    Muestra los KPIs principales con tooltips detallados y cálculos específicos
    """
    st.subheader("📊 Métricas Principales")
    
    # Primera fila de métricas generales con tooltips detallados
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        # Tooltip detallado para Total Pendientes
        tooltip_pendientes = f"""
        📋 **DESGLOSE TOTAL PENDIENTES:**
        • CCM: {ccm['total_pendientes']:,} casos
        • PRR: {prr['total_pendientes']:,} casos
        • **TOTAL:** {consolidadas['total_pendientes']:,} casos
        
        🧮 **CÁLCULO:**
        CCM ({ccm['total_pendientes']:,}) + PRR ({prr['total_pendientes']:,}) = {consolidadas['total_pendientes']:,}
        """
        
        st.metric(
            "🗂️ Total Pendientes", 
            f"{consolidadas['total_pendientes']:,}",
            help=tooltip_pendientes
        )
    
    with col2:
        # Tooltip detallado para Producción Diaria (15 días)
        tooltip_produccion = f"""
        ⚡ **PRODUCCIÓN DIARIA (Últimos 15 días):**
        • CCM: {ccm['produccion_diaria']:.1f} casos/día
        • PRR: {prr['produccion_diaria']:.1f} casos/día
        • **TOTAL:** {consolidadas['produccion_total']:.1f} casos/día
        
        🧮 **CÁLCULO:**
        CCM ({ccm['produccion_diaria']:.1f}) + PRR ({prr['produccion_diaria']:.1f}) = {consolidadas['produccion_total']:.1f}
        
        📊 **MÉTODO:** Promedio de trámites trabajados en últimos 15 días hábiles
        """
        
        st.metric(
            "⚡ Producción Diaria", 
            f"{consolidadas['produccion_total']:.1f}",
            help=tooltip_produccion
        )
    
    with col3:
        # Tooltip detallado para Operadores Activos (corregido con base de personal)
        tooltip_operadores = f"""
        👥 **OPERADORES ACTIVOS (Con casos asignados):**
        • CCM: {ccm['operadores_activos']} operadores
        • PRR: {prr['operadores_activos']} operadores
        • **TOTAL:** {consolidadas['total_operadores']} operadores
        
        🧮 **CÁLCULO:**
        CCM ({ccm['operadores_activos']}) + PRR ({prr['operadores_activos']}) = {consolidadas['total_operadores']}
        
        ✅ **CRITERIO:** Solo operadores con casos pendientes asignados actualmente
        """
        
        st.metric(
            "👥 Operadores Activos", 
            consolidadas['total_operadores'],
            help=tooltip_operadores
        )
    
    with col4:
        # Tooltip detallado para Eficiencia General (15 días)
        eficiencia_pct = consolidadas['eficiencia_general'] * 100
        tooltip_eficiencia = f"""
        📈 **EFICIENCIA GENERAL (Últimos 15 días):**
        
        🧮 **FÓRMULA:** (Producción Total ÷ Ingresos Total) × 100
        
        📊 **CÁLCULO DETALLADO:**
        • Producción Total: {consolidadas['produccion_total']:.1f}
        • Ingresos Total: {consolidadas['ingresos_total']:.1f}
        • ({consolidadas['produccion_total']:.1f} ÷ {consolidadas['ingresos_total']:.1f}) × 100 = {eficiencia_pct:.1f}%
        
        🎯 **INTERPRETACIÓN:**
        • >100%: Reduciendo pendientes ✅
        • =100%: Equilibrio 🟡
        • <100%: Acumulando pendientes ⚠️
        """
        
        st.metric(
            "📈 Eficiencia General", 
            f"{eficiencia_pct:.1f}%",
            help=tooltip_eficiencia
        )
    
    st.markdown("---")
    
    # Segunda fila de métricas por proceso con tooltips detallados
    st.markdown("##### 🔍 Análisis por Proceso")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        # CCM - Pendientes con desglose detallado
        delta_ccm = int(tendencias['ccm'].get('delta_pendientes', 0))
        tooltip_ccm = f"""
        📋 **CCM - DESGLOSE PENDIENTES:**
        • Asignados: {ccm['asignados']:,} casos
        • Sin Asignar: {ccm['sin_asignar']:,} casos
        • **TOTAL CCM:** {ccm['total_pendientes']:,} casos
        
        🧮 **CÁLCULO:**
        Asignados ({ccm['asignados']:,}) + Sin Asignar ({ccm['sin_asignar']:,}) = {ccm['total_pendientes']:,}
        
        📊 **VARIACIÓN:** {delta_ccm:+d} vs período anterior
        """
        
        st.metric(
            "🔵 CCM - Pendientes", 
            f"{ccm['total_pendientes']:,}",
            delta=delta_ccm if delta_ccm != 0 else None,
            delta_color="inverse" if delta_ccm > 0 else "normal",
            help=tooltip_ccm
        )
    
    with col2:
        # PRR - Pendientes con desglose detallado
        delta_prr = int(tendencias['prr'].get('delta_pendientes', 0))
        tooltip_prr = f"""
        📋 **PRR - DESGLOSE PENDIENTES:**
        • Asignados: {prr['asignados']:,} casos
        • Sin Asignar: {prr['sin_asignar']:,} casos
        • **TOTAL PRR:** {prr['total_pendientes']:,} casos
        
        🧮 **CÁLCULO:**
        Asignados ({prr['asignados']:,}) + Sin Asignar ({prr['sin_asignar']:,}) = {prr['total_pendientes']:,}
        
        📊 **VARIACIÓN:** {delta_prr:+d} vs período anterior
        """
        
        st.metric(
            "🟠 PRR - Pendientes", 
            f"{prr['total_pendientes']:,}",
            delta=delta_prr if delta_prr != 0 else None,
            delta_color="inverse" if delta_prr > 0 else "normal",
            help=tooltip_prr
        )
    
    with col3:
        # Sin asignar con desglose por proceso
        delta_sin_asignar = int(tendencias['ccm']['delta_sin_asignar']) + int(tendencias['prr']['delta_sin_asignar'])
        tooltip_sin_asignar = f"""
        ⚠️ **SIN ASIGNAR - DESGLOSE:**
        • CCM: {ccm['sin_asignar']:,} casos
        • PRR: {prr['sin_asignar']:,} casos
        • **TOTAL:** {consolidadas['total_sin_asignar']:,} casos
        
        🧮 **CÁLCULO:**
        CCM ({ccm['sin_asignar']:,}) + PRR ({prr['sin_asignar']:,}) = {consolidadas['total_sin_asignar']:,}
        
        📊 **VARIACIÓN:** {delta_sin_asignar:+d} vs día anterior
        """
        
        st.metric(
            "⚠️ Sin Asignar Total", 
            f"{consolidadas['total_sin_asignar']:,}",
            delta=delta_sin_asignar if delta_sin_asignar != 0 else None,
            delta_color="inverse" if delta_sin_asignar > 0 else "normal",
            help=tooltip_sin_asignar
        )
    
    with col4:
        # Balance diario con cálculo detallado (15 días)
        balance_diario = float(consolidadas['produccion_total'] - consolidadas['ingresos_total'])
        tooltip_balance = f"""
        ⚖️ **BALANCE DIARIO (Últimos 15 días):**
        
        🧮 **FÓRMULA:** Producción Promedio - Ingresos Promedio
        
        📊 **CÁLCULO DETALLADO:**
        • Producción Total: {consolidadas['produccion_total']:.1f} casos/día
        • Ingresos Total: {consolidadas['ingresos_total']:.1f} casos/día
        • Balance: {consolidadas['produccion_total']:.1f} - {consolidadas['ingresos_total']:.1f} = {balance_diario:+.1f}
        
        🎯 **INTERPRETACIÓN:**
        • Positivo (+): Trabajamos más de lo que ingresa ✅
        • Negativo (-): Ingresa más de lo que trabajamos ⚠️
        • Cero (0): Equilibrio perfecto 🎯
        """
        
        st.metric(
            "⚖️ Balance Diario", 
            f"{balance_diario:+.1f}",
            help=tooltip_balance
        )
        
        # Indicador visual mejorado pero más sutil
        if balance_diario > 5:
            st.success("🟢 **Superávit Alto**")
        elif balance_diario > 0:
            st.info("🔵 **Superávit Moderado**")
        elif balance_diario == 0:
            st.warning("🟡 **Equilibrio**")
        elif balance_diario > -5:
            st.warning("🟠 **Déficit Moderado**")
        else:
            st.error("🔴 **Déficit Alto**") 