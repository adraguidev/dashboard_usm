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
    Carga los datos desde un archivo pickle comprimido (.pkl.gz)
    
    Args:
        archivo: Nombre del archivo a cargar
        
    Returns:
        DataFrame con los datos cargados
    """
    return pd.read_pickle(f"ARCHIVOS/{archivo}")

def obtener_archivos_proceso() -> Dict[str, str]:
    """
    Retorna el mapeo de procesos a archivos
    
    Returns:
        Diccionario con el mapeo proceso -> archivo
    """
    return {
        "CCM": "consolidado_final_CCM_personal.pkl.gz",
        "PRR": "consolidado_final_PRR_personal.pkl.gz"
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
    
    # Manejar columnas categóricas: convertir a string primero si es necesario
    if pd.api.types.is_categorical_dtype(df_filtrado['OPERADOR']):
        # Si es categórica, agregar 'Sin asignar' a las categorías primero
        if 'Sin asignar' not in df_filtrado['OPERADOR'].cat.categories:
            df_filtrado['OPERADOR'] = df_filtrado['OPERADOR'].cat.add_categories(['Sin asignar'])
    
    df_filtrado['OPERADOR'] = df_filtrado['OPERADOR'].fillna('Sin asignar')
    
    return df_filtrado

def crear_tabla_pendientes(df_filtrado: pd.DataFrame, proceso: str, agrupacion: str = "anios") -> pd.DataFrame:
    """
    Crea la tabla dinámica de pendientes
    
    Args:
        df_filtrado: DataFrame filtrado con pendientes
        proceso: Tipo de proceso ('CCM' o 'PRR')
        agrupacion: Tipo de agrupación ('anios', 'trimestres', 'meses')
        
    Returns:
        Tabla dinámica de pendientes por operador y período
    """
    df_filtrado = df_filtrado.copy()
    
    # Usar columnas existentes o crear nuevas según la agrupación
    if agrupacion == "anios":
        # Usar columna 'Anio' existente
        if 'Anio' not in df_filtrado.columns:
            raise ValueError("La columna 'Anio' no está disponible en los datos")
        col_name = 'Anio'
        
    elif agrupacion == "meses":
        # Combinar año y mes para crear etiquetas descriptivas como "2023-01", "2024-02"
        if 'Mes' not in df_filtrado.columns or 'Anio' not in df_filtrado.columns:
            raise ValueError("Las columnas 'Mes' y 'Anio' son requeridas para agrupar por meses")
        
        # Crear columna combinada Año-Mes
        df_filtrado['Mes'] = df_filtrado['Mes'].astype(str).str.zfill(2)  # Asegurar formato 01, 02, etc.
        df_filtrado['AnioMes'] = df_filtrado['Anio'].astype(str) + '-' + df_filtrado['Mes']
        col_name = 'AnioMes'
        
    else:  # trimestres
        # Para trimestres necesitamos crear la columna usando FechaExpendiente
        if 'FechaExpendiente' not in df_filtrado.columns:
            raise ValueError("La columna 'FechaExpendiente' es requerida para agrupar por trimestres")
        
        # Convertir a datetime si no lo está
        df_filtrado['FechaExpendiente'] = pd.to_datetime(df_filtrado['FechaExpendiente'], errors='coerce')
        
        # Crear columna de trimestre
        df_filtrado['Trimestre'] = (
            df_filtrado['FechaExpendiente'].dt.year.astype(str) + 
            "-T" + 
            df_filtrado['FechaExpendiente'].dt.quarter.astype(str)
        )
        col_name = 'Trimestre'
    
    # Crear tabla dinámica sin totales automáticos
    tabla = pd.pivot_table(
        df_filtrado,
        index='OPERADOR',
        columns=col_name,
        values='NumeroTramite',
        aggfunc='count',
        fill_value=0,
        observed=False  # Para evitar warnings de pandas
    )
    
    # Eliminar columnas con total 0 (excepto 'Total' que se calculará después)
    columnas_periodicas = [col for col in tabla.columns if col != 'Total']
    columnas_con_datos = []
    
    for col in columnas_periodicas:
        if tabla[col].sum() > 0:  # Solo mantener columnas que tengan al menos 1 caso
            columnas_con_datos.append(col)
    
    # Mantener solo columnas con datos
    tabla = tabla[columnas_con_datos]
    
    # Calcular columna Total manualmente después de filtrar columnas
    tabla['Total'] = tabla.sum(axis=1)
    
    # Aplicar filtros de operadores según el proceso (insensible a mayúsculas/minúsculas)
    if proceso == "CCM":
        # Excluir operadores específicos para CCM
        operadores_excluir_nombres = [
            "MAURICIO ROMERO, HUGO", 
            "Sin asignar",
            "Aponte Sanchez, Paola Lita",
            "Lucero Martinez, Carlos Martin", 
            "USUARIO DE AGENCIA DIGITAL"
        ]
        
    elif proceso == "PRR":
        # Excluir operadores específicos para PRR
        operadores_excluir_nombres = [
            "Sin asignar",
            "Aponte Sanchez, Paola Lita",
            "Lucero Martinez, Carlos Martin", 
            "USUARIO DE AGENCIA DIGITAL"
        ]
    
    # Filtrar operadores de forma insensible a mayúsculas/minúsculas
    operadores_excluir_lower = [op.lower() for op in operadores_excluir_nombres]
    indices_a_excluir = [
        idx for idx in tabla.index 
        if idx.lower() in operadores_excluir_lower
    ]
    tabla = tabla.drop(indices_a_excluir, errors='ignore')
    
    # Filtrar operadores con menos de 1 pendiente total
    tabla = tabla[tabla['Total'] >= 1]
    
    # Ordenar por Total descendente
    tabla = tabla.sort_values(by=('Total'), ascending=False)
    
    # Recalcular la fila Total después de filtrar (solo columnas numéricas)
    columnas_numericas = [col for col in tabla.columns if col != 'Total']
    total_row = tabla[columnas_numericas + ['Total']].sum(axis=0)
    total_row.name = 'Total'
    
    # Asegurar que el total sea correcto
    total_row['Total'] = total_row[columnas_numericas].sum()
    
    tabla = pd.concat([tabla, pd.DataFrame([total_row])])
    
    return tabla

def calcular_sin_asignar(df_filtrado: pd.DataFrame, agrupacion: str = "anios") -> int:
    """
    Calcula el total de casos sin asignar según el tipo de agrupación
    
    Args:
        df_filtrado: DataFrame filtrado con pendientes
        agrupacion: Tipo de agrupación ('anios', 'trimestres', 'meses')
        
    Returns:
        Número de casos sin asignar en el período correspondiente
    """
    # Filtrar solo casos sin asignar
    sin_asignar_df = df_filtrado[df_filtrado['OPERADOR'] == 'Sin asignar'].copy()
    
    if sin_asignar_df.empty:
        return 0
    
    # Filtrar según el tipo de agrupación
    if agrupacion == "anios":
        # Usar columna 'Anio' existente - últimos 2 años
        if 'Anio' not in sin_asignar_df.columns:
            return 0
        anios = sorted(sin_asignar_df['Anio'].dropna().unique())
        ultimos_periodos = anios[-2:] if len(anios) >= 2 else anios
        mask = sin_asignar_df['Anio'].isin(ultimos_periodos)
        
    elif agrupacion == "meses":
        # Usar columnas 'Mes' y 'Anio' combinadas - últimos 12 meses
        if 'Mes' not in sin_asignar_df.columns or 'Anio' not in sin_asignar_df.columns:
            return 0
        
        # Crear columna combinada igual que en crear_tabla_pendientes
        sin_asignar_df['Mes'] = sin_asignar_df['Mes'].astype(str).str.zfill(2)
        sin_asignar_df['AnioMes'] = sin_asignar_df['Anio'].astype(str) + '-' + sin_asignar_df['Mes']
        meses = sorted(sin_asignar_df['AnioMes'].dropna().unique())
        ultimos_periodos = meses[-12:] if len(meses) >= 12 else meses
        mask = sin_asignar_df['AnioMes'].isin(ultimos_periodos)
        
    else:  # trimestres
        # Para trimestres crear la columna usando FechaExpendiente - últimos 6 trimestres
        if 'FechaExpendiente' not in sin_asignar_df.columns:
            return 0
        
        # Convertir fecha si no lo está
        sin_asignar_df['FechaExpendiente'] = pd.to_datetime(sin_asignar_df['FechaExpendiente'], errors='coerce')
        
        # Crear columna de trimestre
        sin_asignar_df['Trimestre'] = (
            sin_asignar_df['FechaExpendiente'].dt.year.astype(str) + 
            "-T" + 
            sin_asignar_df['FechaExpendiente'].dt.quarter.astype(str)
        )
        trimestres = sorted(sin_asignar_df['Trimestre'].dropna().unique())
        ultimos_periodos = trimestres[-6:] if len(trimestres) >= 6 else trimestres
        mask = sin_asignar_df['Trimestre'].isin(ultimos_periodos)
    
    return sin_asignar_df[mask]['NumeroTramite'].count()

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

@st.cache_data
def cargar_base_evaluadores(proceso: str) -> pd.DataFrame:
    """
    Carga la base de evaluadores desde BASE.xlsx según el proceso
    
    Args:
        proceso: Tipo de proceso ('CCM' o 'PRR')
        
    Returns:
        DataFrame con la información de los evaluadores del proceso específico
    """
    try:
        # Leer la pestaña específica del proceso
        df_base = pd.read_excel("ARCHIVOS/EVALUADORES/BASE.xlsx", sheet_name=proceso)
        # Renombrar columnas para facilitar el uso
        df_base = df_base.rename(columns={
            'NOMBRE EN BASE': 'OPERADOR',
            'NOMBRES Y APELLIDOS': 'NOMBRE_COMPLETO'
        })
        return df_base
    except Exception as e:
        st.warning(f"No se pudo cargar la base de evaluadores para {proceso}: {str(e)}")
        # Retornar DataFrame vacío con las columnas esperadas
        return pd.DataFrame(columns=['OPERADOR', 'NOMBRE_COMPLETO', 'REGIMEN', 'TURNO', 'MODALIDAD', 'SUB-EQUIPO'])

def enriquecer_pendientes_con_base(df_pendientes: pd.DataFrame, proceso: str) -> pd.DataFrame:
    """
    Enriquece los datos de pendientes con información de la base de evaluadores
    
    Args:
        df_pendientes: DataFrame con pendientes por operador
        proceso: Tipo de proceso ('CCM' o 'PRR')
        
    Returns:
        DataFrame enriquecido con información adicional de evaluadores
    """
    df_base = cargar_base_evaluadores(proceso)
    
    if df_base.empty:
        # Si no hay base, agregar columnas con valores por defecto
        df_pendientes = df_pendientes.copy()
        df_pendientes['REGIMEN'] = 'OTROS'
        df_pendientes['TURNO'] = 'OTROS'
        df_pendientes['MODALIDAD'] = 'OTROS'
        df_pendientes['SUB-EQUIPO'] = 'OTROS'
        return df_pendientes
    
    # Hacer merge con la base de evaluadores
    df_enriquecido = df_pendientes.merge(
        df_base[['OPERADOR', 'REGIMEN', 'TURNO', 'MODALIDAD', 'SUB-EQUIPO']], 
        left_index=True, 
        right_on='OPERADOR', 
        how='left'
    )
    
    # Llenar valores nulos con "OTROS" para operadores no encontrados en la base
    df_enriquecido['REGIMEN'] = df_enriquecido['REGIMEN'].fillna('OTROS')
    df_enriquecido['TURNO'] = df_enriquecido['TURNO'].fillna('OTROS')
    df_enriquecido['MODALIDAD'] = df_enriquecido['MODALIDAD'].fillna('OTROS')
    df_enriquecido['SUB-EQUIPO'] = df_enriquecido['SUB-EQUIPO'].fillna('OTROS')
    
    # Restaurar el índice como OPERADOR si se perdió
    if 'OPERADOR' in df_enriquecido.columns and df_enriquecido.index.name != 'OPERADOR':
        df_enriquecido = df_enriquecido.set_index('OPERADOR')
    
    return df_enriquecido 