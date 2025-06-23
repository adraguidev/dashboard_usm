"""
Dashboard de Análisis de Procesos
Aplicación principal de Streamlit
"""

import streamlit as st
from modules.data.loader import cargar_datos, obtener_archivos_proceso
from modules.config.settings import STREAMLIT_CONFIG, inicializar_configuracion
from modules.utils.error_handler import ErrorHandler, log_user_action
from modules.components.dashboard_ejecutivo_main import mostrar_dashboard_ejecutivo
from modules.components.pendientes import mostrar_pendientes
from modules.components.produccion_diaria import mostrar_produccion_diaria
from modules.components.ingresos_diarios import mostrar_ingresos_diarios
from modules.components.proyeccion_cierre import mostrar_proyeccion_cierre
from modules.components.evolucion_pendientes import mostrar_evolucion_pendientes

def main():
    """
    Función principal de la aplicación
    """
    # Inicializar configuración
    if not inicializar_configuracion():
        st.error("❌ Error en la configuración inicial. Verifica los archivos de datos.")
        st.stop()
    
    # Configuración de la página usando configuración centralizada
    st.set_page_config(**STREAMLIT_CONFIG)
    
    # Título principal
    st.title("📊 Dashboard de Análisis de Procesos")
    
    # Selector de proceso en la barra lateral
    st.sidebar.header("Configuración")
    proceso = st.sidebar.selectbox(
        "Selecciona el proceso:",
        ["CCM", "PRR"],
        help="Selecciona CCM o PRR para cargar los datos correspondientes"
    )
    
    # Log de acción del usuario
    log_user_action("Selección de proceso", {"proceso": proceso})
    
    # Cargar datos con manejo de errores mejorado
    with ErrorHandler(f"Carga de datos {proceso}"):
        archivos_proceso = obtener_archivos_proceso()
        archivo = archivos_proceso[proceso]
        
        with st.spinner(f"Cargando datos de {proceso}..."):
            df = cargar_datos(archivo)
        
        st.sidebar.success(f"Datos de {proceso} cargados correctamente")
        st.sidebar.info(f"Total de registros: {len(df):,}")
    
    # Navegación por pestañas
    tab0, tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🎯 Dashboard Ejecutivo",
        "📋 Pendientes",
        "📈 Producción Diaria", 
        "📥 Ingresos Diarios",
        "🎯 Proyección de Cierre",
        "📊 Evolución Pendientes"
    ])
    
    # Pestaña 0: Dashboard Ejecutivo
    with tab0:
        mostrar_dashboard_ejecutivo()
    
    # Pestaña 1: Pendientes
    with tab1:
        mostrar_pendientes(df, proceso)
    
    # Pestaña 2: Producción Diaria
    with tab2:
        mostrar_produccion_diaria(df, proceso)
    
    # Pestaña 3: Ingresos Diarios
    with tab3:
        mostrar_ingresos_diarios(df, proceso)
    
    # Pestaña 4: Proyección de Cierre
    with tab4:
        mostrar_proyeccion_cierre(df, proceso)
    
    # Pestaña 5: Evolución de Pendientes
    with tab5:
        mostrar_evolucion_pendientes(df, proceso)

if __name__ == "__main__":
    main() 