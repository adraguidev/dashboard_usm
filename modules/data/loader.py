"""
Módulo para cargar y procesar datos del dashboard
"""

import streamlit as st
import pandas as pd
import datetime
import pytz
from pathlib import Path
from typing import Dict, Optional

@st.cache_data
def cargar_datos(archivo: str) -> pd.DataFrame:
    """
    Carga los datos desde un archivo Excel
    
    Args:
        archivo: Nombre del archivo a cargar
        
    Returns:
        DataFrame con los datos cargados
    """
    return pd.read_excel(f"ARCHIVOS/{archivo}")

def obtener_archivos_proceso() -> Dict[str, str]:
    """
    Retorna el mapeo de procesos a archivos
    
    Returns:
        Diccionario con el mapeo proceso -> archivo
    """
    return {
        "CCM": "consolidado_final_CCM_personal.xlsx",
        "PRR": "consolidado_final_PRR_personal.xlsx"
    }

def filtrar_pendientes_ccm(df: pd.DataFrame) -> pd.DataFrame:
    """
    Filtra los datos para obtener pendientes de CCM
    
    Args:
        df: DataFrame con los datos
        
    Returns:
        DataFrame filtrado con pendientes CCM
    """
    return df[
        (df['UltimaEtapa'] == 'EVALUACIÓN - I') &
        (df['EstadoPre'].isna()) &
        (df['EstadoTramite'] == 'PENDIENTE') &
        (df['EQUIPO'] != 'VULNERABLE')
    ]

def filtrar_pendientes_prr(df: pd.DataFrame) -> pd.DataFrame:
    """
    Filtra los datos para obtener pendientes de PRR
    
    Args:
        df: DataFrame con los datos
        
    Returns:
        DataFrame filtrado con pendientes PRR
    """
    etapas_prr = [
        'ACTUALIZAR DATOS BENEFICIARIO - F',
        'ACTUALIZAR DATOS BENEFICIARIO - I',
        'ASOCIACION BENEFICIARIO - F',
        'ASOCIACION BENEFICIARIO - I',
        'CONFORMIDAD SUB-DIREC.INMGRA. - I',
        'PAGOS, FECHA Y NRO RD. - F',
        'PAGOS, FECHA Y NRO RD. - I',
        'RECEPCIÓN DINM - F'
    ]
    
    return df[
        (df['UltimaEtapa'].isin(etapas_prr)) &
        (df['EstadoPre'].isna()) &
        (df['EstadoTramite'] == 'PENDIENTE') &
        (df['EQUIPO'] != 'VULNERABLE')
    ]

def procesar_pendientes(df: pd.DataFrame, proceso: str) -> pd.DataFrame:
    """
    Procesa los datos para obtener pendientes según el proceso
    
    Args:
        df: DataFrame con los datos
        proceso: Tipo de proceso ('CCM' o 'PRR')
        
    Returns:
        DataFrame procesado con pendientes
    """
    # Filtrar según el proceso
    if proceso == "CCM":
        df_filtrado = filtrar_pendientes_ccm(df)
    else:
        df_filtrado = filtrar_pendientes_prr(df)
    
    # Reemplazar nulos en OPERADOR por 'Sin asignar'
    df_filtrado = df_filtrado.copy()
    df_filtrado['OPERADOR'] = df_filtrado['OPERADOR'].fillna('Sin asignar')
    
    return df_filtrado

def crear_tabla_pendientes(df_filtrado: pd.DataFrame, proceso: str) -> pd.DataFrame:
    """
    Crea la tabla dinámica de pendientes
    
    Args:
        df_filtrado: DataFrame filtrado con pendientes
        proceso: Tipo de proceso ('CCM' o 'PRR')
        
    Returns:
        Tabla dinámica de pendientes por operador y año
    """
    # Crear tabla dinámica sin totales automáticos
    tabla = pd.pivot_table(
        df_filtrado,
        index='OPERADOR',
        columns='Anio',
        values='NumeroTramite',
        aggfunc='count',
        fill_value=0
    )
    
    # Calcular columna Total manualmente
    tabla['Total'] = tabla.sum(axis=1)
    
    # Excluir operadores específicos
    if proceso == "CCM":
        operadores_excluir = ["MAURICIO ROMERO, HUGO", "Sin asignar"]
        tabla = tabla.drop(operadores_excluir, errors='ignore')
    elif proceso == "PRR":
        tabla = tabla.drop(["Sin asignar"], errors='ignore')
    
    # Ordenar por Total descendente
    tabla = tabla.sort_values(by=('Total'), ascending=False)
    
    # Recalcular la fila Total después de filtrar
    total_row = tabla.sum(axis=0)
    total_row.name = 'Total'
    tabla = pd.concat([tabla, pd.DataFrame([total_row])])
    
    return tabla

def calcular_sin_asignar(df_filtrado: pd.DataFrame) -> int:
    """
    Calcula el total de casos sin asignar en los últimos 2 años
    
    Args:
        df_filtrado: DataFrame filtrado con pendientes
        
    Returns:
        Número de casos sin asignar
    """
    anios = sorted(df_filtrado['Anio'].dropna().unique())
    ultimos_2_anios = anios[-2:] if len(anios) >= 2 else anios
    
    return df_filtrado[
        (df_filtrado['OPERADOR'] == 'Sin asignar') &
        (df_filtrado['Anio'].isin(ultimos_2_anios))
    ]['NumeroTramite'].count()

def cargar_historico_pendientes() -> pd.DataFrame:
    """
    Carga el histórico de pendientes por operador
    
    Returns:
        DataFrame con el histórico de pendientes
    """
    ruta_historico = 'ARCHIVOS/historico_pendientes_operador.csv'
    try:
        return pd.read_csv(ruta_historico, dtype={'Año': str})
    except FileNotFoundError:
        return pd.DataFrame(columns=['Fecha', 'Proceso', 'OPERADOR', 'Año', 'Pendientes'])

def preparar_historico_pendientes(tabla: pd.DataFrame, proceso: str) -> pd.DataFrame:
    """
    Prepara los datos del histórico de pendientes para guardar
    
    Args:
        tabla: Tabla de pendientes actual
        proceso: Tipo de proceso
        
    Returns:
        DataFrame preparado para guardar en el histórico
    """
    # Quitar la fila 'Total' para el histórico
    tabla_historico = tabla.drop('Total', errors='ignore').copy()
    
    # Quitar la columna 'Total' para el histórico
    if 'Total' in tabla_historico.columns:
        tabla_historico = tabla_historico.drop(columns=['Total'])
    
    # Asegurar que 'OPERADOR' sea columna
    if 'OPERADOR' not in tabla_historico.columns:
        tabla_historico = tabla_historico.reset_index().rename(
            columns={tabla_historico.index.name or 'index': 'OPERADOR'}
        )
    
    # Convertir a formato largo
    tabla_historico = tabla_historico.melt(
        id_vars=['OPERADOR'],
        var_name='Año',
        value_name='Pendientes'
    )
    
    # Agregar columnas de fecha local y proceso
    tz = pytz.timezone('America/Lima')
    fecha_hoy_local = datetime.datetime.now(tz).strftime('%Y-%m-%d')
    tabla_historico['Fecha'] = fecha_hoy_local
    tabla_historico['Proceso'] = proceso
    
    # Reordenar columnas
    tabla_historico = tabla_historico[['Fecha', 'Proceso', 'OPERADOR', 'Año', 'Pendientes']]
    
    # Normalizar claves para evitar duplicados por diferencias de formato
    tabla_historico['OPERADOR'] = tabla_historico['OPERADOR'].str.strip().str.upper()
    tabla_historico['Año'] = tabla_historico['Año'].astype(str)
    
    return tabla_historico

def actualizar_historico_pendientes(tabla_historico: pd.DataFrame) -> None:
    """
    Actualiza el archivo histórico de pendientes
    
    Args:
        tabla_historico: Datos del histórico a guardar
    """
    ruta_historico = 'ARCHIVOS/historico_pendientes_operador.csv'
    
    # Leer histórico existente si existe
    try:
        historico_existente = pd.read_csv(ruta_historico, dtype=str)
        historico_existente['OPERADOR'] = historico_existente['OPERADOR'].str.strip().str.upper()
        historico_existente['Año'] = historico_existente['Año'].astype(str)
    except FileNotFoundError:
        historico_existente = pd.DataFrame(columns=tabla_historico.columns)

    # Nueva lógica: solo actualizar si los valores de pendientes realmente cambiaron
    claves = ['Fecha', 'Proceso', 'OPERADOR', 'Año']
    
    if not historico_existente.empty:
        # Hacer merge para comparar valores existentes y nuevos
        comparacion = tabla_historico.merge(
            historico_existente,
            on=claves,
            suffixes=('_nuevo', '_existente'),
            how='outer',
            indicator=True
        )
        
        # Identificar registros que son nuevos o han cambiado
        nuevos_o_cambiados = comparacion[
            (comparacion['_merge'] == 'left_only') |
            ((comparacion['_merge'] == 'both') & 
             (comparacion['Pendientes_nuevo'] != comparacion['Pendientes_existente']))
        ]
        
        if not nuevos_o_cambiados.empty:
            # Actualizar solo los que cambiaron
            for _, row in nuevos_o_cambiados.iterrows():
                mask = (
                    (historico_existente['Fecha'] == row['Fecha']) &
                    (historico_existente['Proceso'] == row['Proceso']) &
                    (historico_existente['OPERADOR'] == row['OPERADOR']) &
                    (historico_existente['Año'] == row['Año'])
                )
                
                if mask.any():
                    historico_existente.loc[mask, 'Pendientes'] = row['Pendientes_nuevo']
                else:
                    # Es un registro nuevo
                    nuevo_registro = {
                        'Fecha': row['Fecha'],
                        'Proceso': row['Proceso'],
                        'OPERADOR': row['OPERADOR'],
                        'Año': row['Año'],
                        'Pendientes': row['Pendientes_nuevo']
                    }
                    historico_existente = pd.concat([
                        historico_existente, 
                        pd.DataFrame([nuevo_registro])
                    ], ignore_index=True)
            
            # Guardar el histórico actualizado
            historico_existente.to_csv(ruta_historico, index=False)
    else:
        # Si no existe histórico, guardar directamente
        tabla_historico.to_csv(ruta_historico, index=False) 