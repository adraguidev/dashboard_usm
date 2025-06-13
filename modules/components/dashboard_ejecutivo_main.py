"""
Componente principal para el Dashboard Ejecutivo
"""

import streamlit as st
from modules.data.loader import obtener_archivos_proceso, cargar_datos
from modules.data.historico_sin_asignar import actualizar_historico_sin_asignar
from .dashboard_ejecutivo_metricas import (
    calcular_metricas_exactas_ccm, 
    calcular_metricas_exactas_prr,
    consolidar_metricas,
    calcular_tendencias_reales
)
from .dashboard_ejecutivo_kpis import mostrar_kpis_principales
from .dashboard_ejecutivo_visualizaciones import (
    mostrar_evolucion_pendientes_historica,
    mostrar_evolucion_sin_asignar,
    mostrar_ingresos_vs_trabajados_lineal,
    mostrar_tabla_comparativa
)


def mostrar_dashboard_ejecutivo() -> None:
    """
    Dashboard ejecutivo con diseño limpio y moderno
    """
    # Header principal simple
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                padding: 1.5rem; border-radius: 15px; margin-bottom: 1.5rem;">
        <h1 style="color: white; text-align: center; margin: 0; font-size: 2rem;">
            🎯 Dashboard Ejecutivo
        </h1>
    </div>
    """, unsafe_allow_html=True)
    
    try:
        # Cargar datos
        archivos_proceso = obtener_archivos_proceso()
        
        with st.spinner("🔄 Cargando datos..."):
            # Cargar datasets
            df_ccm = cargar_datos(archivos_proceso["CCM"])
            df_prr = cargar_datos(archivos_proceso["PRR"])
            
            # Actualizar histórico de sin asignar
            actualizar_historico_sin_asignar(df_ccm, df_prr)
            
            # Calcular métricas exactas
            metricas_ccm = calcular_metricas_exactas_ccm(df_ccm)
            metricas_prr = calcular_metricas_exactas_prr(df_prr)
            metricas_consolidadas = consolidar_metricas(metricas_ccm, metricas_prr)
            tendencias = calcular_tendencias_reales(metricas_ccm, metricas_prr)
        

        
        # === KPIs PRINCIPALES ===
        mostrar_kpis_principales(metricas_consolidadas, metricas_ccm, metricas_prr, tendencias)
        
        st.markdown("---")
        
        # === EVOLUCIÓN Y TENDENCIAS ===
        st.markdown("### 📈 Análisis de Tendencias")
        
        # Evolución de pendientes
        mostrar_evolucion_pendientes_historica()
        
        # Evolución de sin asignar
        mostrar_evolucion_sin_asignar()
        
        st.markdown("---")
        
        # === ANÁLISIS DE FLUJO ===
        st.markdown("### 🔄 Análisis de Flujo de Trabajo")
        
        # Ingresos vs trabajados separado por proceso
        mostrar_ingresos_vs_trabajados_lineal(df_ccm, df_prr)
        
        st.markdown("---")
        
        # === COMPARACIÓN DETALLADA ===
        st.markdown("### 🔍 Análisis Comparativo")
        
        # Tabla comparativa
        mostrar_tabla_comparativa(metricas_ccm, metricas_prr)
        
    except Exception as e:
        st.error(f"❌ Error al cargar el dashboard ejecutivo: {str(e)}")
        st.info("🔄 Intenta recargar la página o verifica la conexión de datos") 