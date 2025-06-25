# 📊 01 - EXTRACCIÓN Y PROCESAMIENTO ACTUAL DE DATOS

## 🎯 PROPÓSITO
Documentación técnica completa sobre cómo funciona actualmente la extracción y procesamiento de datos en el dashboard de Streamlit.

---

## 🔗 CARGA INICIAL DE DATOS

### Estructura de Archivos Actual
```
ARCHIVOS/
├── consolidado_final_CCM_personal.pkl.gz
├── consolidado_final_PRR_personal.pkl.gz
└── EVALUADORES/
    └── BASE.xlsx
```

### Función de Carga Principal
```python
# En modules/data/loader.py
@st.cache_data
def cargar_datos(archivo: str) -> pd.DataFrame:
    """
    PROCESO ACTUAL:
    1. Lee archivo .pkl.gz desde carpeta ARCHIVOS/
    2. Retorna DataFrame con caché de Streamlit
    """
    return pd.read_pickle(f"ARCHIVOS/{archivo}")

def obtener_archivos_proceso() -> Dict[str, str]:
    """
    MAPEO DE ARCHIVOS POR PROCESO:
    - CCM: consolidado_final_CCM_personal.pkl.gz
    - PRR: consolidado_final_PRR_personal.pkl.gz
    """
    return {
        "CCM": "consolidado_final_CCM_personal.pkl.gz",
        "PRR": "consolidado_final_PRR_personal.pkl.gz"
    }
```

### Flujo de Carga en app.py
```python
# En app.py función main()
def main():
    # 1. SIDEBAR - Selección de proceso
    proceso = st.sidebar.selectbox(
        "Selecciona el proceso:",
        ["CCM", "PRR"],
        help="Selecciona CCM o PRR para cargar los datos correspondientes"
    )
    
    # 2. CARGA DE DATOS
    archivos_proceso = obtener_archivos_proceso()
    archivo = archivos_proceso[proceso]
    
    with st.spinner(f"Cargando datos de {proceso}..."):
        df = cargar_datos(archivo)
    
    # 3. INFORMACIÓN EN SIDEBAR
    st.sidebar.success(f"Datos de {proceso} cargados correctamente")
    st.sidebar.info(f"Total de registros: {len(df):,}")
    
    # 4. PESTAÑAS
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "🎯 Dashboard Ejecutivo",
        "📋 Pendientes", 
        "📊 Producción Diaria",
        "📈 Ingresos Diarios",
        "🔮 Proyección de Cierre",
        "📉 Evolución Pendientes"
    ])
```

---

## 📋 ESTRUCTURA DE DATOS

### Columnas Principales en ambos DataFrames (CCM y PRR)
```python
# COLUMNAS CRÍTICAS PRESENTES:
columnas_principales = [
    # IDENTIFICADORES
    'NumeroTramite',        # Número único del trámite
    'NumeroExpendiente',    # Número del expediente
    
    # FECHAS
    'FechaExpendiente',     # Fecha de ingreso del expediente
    'FechaPre',            # Fecha de procesamiento/trabajo
    
    # OPERADORES
    'OPERADOR',            # Operador asignado al expediente
    'OperadorPre',         # Operador que procesó el caso
    
    # ESTADO Y PROCESO
    'EstadoTramite',       # Estado actual: PENDIENTE, TERMINADO, etc.
    'EstadoPre',           # Estado de procesamiento
    'UltimaEtapa',         # Última etapa del proceso
    'EQUIPO',              # Equipo al que pertenece
    
    # TEMPORAL
    'Anio',                # Año del expediente (extraído de fecha)
    'Mes',                 # Mes del expediente
    
    # OTROS
    [campos adicionales específicos por proceso...]
]
```

### Conversiones de Datos Aplicadas
```python
# AUTOMÁTICAMENTE AL CARGAR:
def procesar_datos_basicos(df):
    """
    CONVERSIONES AUTOMÁTICAS:
    1. FechaExpendiente y FechaPre → datetime
    2. OPERADOR nulos → 'Sin asignar'
    3. Manejo de categorías en OPERADOR
    """
    # Fechas
    df['FechaExpendiente'] = pd.to_datetime(df['FechaExpendiente'], errors='coerce')
    df['FechaPre'] = pd.to_datetime(df['FechaPre'], errors='coerce')
    
    # Operadores nulos
    if pd.api.types.is_categorical_dtype(df['OPERADOR']):
        if 'Sin asignar' not in df['OPERADOR'].cat.categories:
            df['OPERADOR'] = df['OPERADOR'].cat.add_categories(['Sin asignar'])
    df['OPERADOR'] = df['OPERADOR'].fillna('Sin asignar')
    
    return df
```

---

## 🔧 FILTROS BASE POR PROCESO

### Filtros para CCM
```python
def procesar_pendientes_ccm(df):
    """
    FILTROS ESPECÍFICOS CCM:
    
    CONDICIONES OBLIGATORIAS:
    1. UltimaEtapa == 'EVALUACIÓN - I'
    2. EstadoPre.isna() == True (no procesado)
    3. EstadoTramite == 'PENDIENTE'
    4. EQUIPO != 'VULNERABLE' (excluir vulnerables)
    """
    return df[
        (df['UltimaEtapa'] == 'EVALUACIÓN - I') &
        (df['EstadoPre'].isna()) &
        (df['EstadoTramite'] == 'PENDIENTE') &
        (df['EQUIPO'] != 'VULNERABLE')
    ]
```

### Filtros para PRR
```python
def procesar_pendientes_prr(df):
    """
    FILTROS ESPECÍFICOS PRR:
    
    ETAPAS VÁLIDAS (8 etapas):
    1. 'ACTUALIZAR DATOS BENEFICIARIO - F'
    2. 'ACTUALIZAR DATOS BENEFICIARIO - I'
    3. 'ASOCIACION BENEFICIARIO - F'
    4. 'ASOCIACION BENEFICIARIO - I'
    5. 'CONFORMIDAD SUB-DIREC.INMGRA. - I'
    6. 'PAGOS, FECHA Y NRO RD. - F'
    7. 'PAGOS, FECHA Y NRO RD. - I'
    8. 'RECEPCIÓN DINM - F'
    
    CONDICIONES:
    - UltimaEtapa IN (etapas_prr)
    - EstadoPre.isna() == True
    - EstadoTramite == 'PENDIENTE'
    - EQUIPO != 'VULNERABLE'
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
```

### Función Unificada de Procesamiento
```python
def procesar_pendientes(df: pd.DataFrame, proceso: str) -> pd.DataFrame:
    """
    FUNCIÓN MAESTRA PARA PROCESAR PENDIENTES
    
    PASOS:
    1. Aplicar filtros específicos del proceso
    2. Manejar operadores nulos
    3. Crear copia para evitar warnings
    4. Retornar DataFrame procesado
    """
    # Filtros según proceso
    if proceso == "CCM":
        df_filtrado = procesar_pendientes_ccm(df)
    elif proceso == "PRR":
        df_filtrado = procesar_pendientes_prr(df)
    else:
        raise ValueError(f"Proceso no válido: {proceso}")
    
    # Crear copia y manejar operadores
    df_filtrado = df_filtrado.copy()
    
    # Manejo categórico de OPERADOR
    if pd.api.types.is_categorical_dtype(df_filtrado['OPERADOR']):
        if 'Sin asignar' not in df_filtrado['OPERADOR'].cat.categories:
            df_filtrado['OPERADOR'] = df_filtrado['OPERADOR'].cat.add_categories(['Sin asignar'])
    
    df_filtrado['OPERADOR'] = df_filtrado['OPERADOR'].fillna('Sin asignar')
    
    return df_filtrado
```

---

## 🚫 OPERADORES EXCLUIDOS

### Lista de Operadores Excluidos por Proceso
```python
def obtener_operadores_excluidos(proceso: str) -> list:
    """
    OPERADORES EXCLUIDOS SEGÚN PROCESO:
    
    DIFERENCIA CRÍTICA:
    - CCM: Incluye "MAURICIO ROMERO, HUGO"
    - PRR: NO incluye "MAURICIO ROMERO, HUGO"
    """
    operadores_comunes = [
        "Sin asignar",
        "Aponte Sanchez, Paola Lita",
        "Lucero Martinez, Carlos Martin", 
        "USUARIO DE AGENCIA DIGITAL"
    ]
    
    if proceso == "CCM":
        return operadores_comunes + ["MAURICIO ROMERO, HUGO"]
    elif proceso == "PRR":
        return operadores_comunes
    else:
        return operadores_comunes
```

### Aplicación de Filtros de Operadores
```python
def filtrar_operadores_validos(df: pd.DataFrame, proceso: str, umbral_minimo: int = 5):
    """
    FILTROS APLICADOS:
    1. Excluir operadores de la lista
    2. Mantener solo operadores con >= umbral_minimo casos
    3. Preservar fila 'Total' si existe
    """
    operadores_excluir = obtener_operadores_excluidos(proceso)
    operadores_excluir_lower = [op.lower() for op in operadores_excluir]
    
    # Filtrar operadores excluidos (case-insensitive)
    if isinstance(df.index, pd.Index):
        # Para tablas pivotadas
        indices_a_excluir = [
            idx for idx in df.index 
            if str(idx).lower() in operadores_excluir_lower
        ]
        df_filtrado = df.drop(indices_a_excluir, errors='ignore')
        
        # Aplicar umbral mínimo (excepto 'Total')
        if 'Total' in df_filtrado.columns:
            mask = (df_filtrado['Total'] >= umbral_minimo) | (df_filtrado.index == 'Total')
            df_filtrado = df_filtrado[mask]
    else:
        # Para DataFrames normales
        mask = ~df['OPERADOR'].str.lower().isin(operadores_excluir_lower)
        df_filtrado = df[mask]
    
    return df_filtrado
```

---

## 📊 BASE DE EVALUADORES

### Carga de Base de Evaluadores
```python
@st.cache_data
def cargar_base_evaluadores(proceso: str) -> pd.DataFrame:
    """
    CARGA ARCHIVO: ARCHIVOS/EVALUADORES/BASE.xlsx
    
    COLUMNAS ESPERADAS:
    - OPERADOR: Nombre del evaluador
    - REGIMEN: CAS, PLANILLA, etc.
    - TURNO: MAÑANA, TARDE, COMPLETO
    - MODALIDAD: PRESENCIAL, REMOTO, MIXTO
    - SUB-EQUIPO: Clasificación por colores
    """
    try:
        ruta_base = Path("ARCHIVOS/EVALUADORES/BASE.xlsx")
        if not ruta_base.exists():
            st.warning(f"❌ Archivo de base no encontrado: {ruta_base}")
            return pd.DataFrame()
        
        df_base = pd.read_excel(ruta_base)
        
        # Validar columnas requeridas
        columnas_requeridas = ['OPERADOR', 'REGIMEN', 'TURNO', 'MODALIDAD', 'SUB-EQUIPO']
        if not all(col in df_base.columns for col in columnas_requeridas):
            st.warning(f"❌ Columnas faltantes en base de evaluadores")
            return pd.DataFrame()
        
        # Limpiar datos
        df_base = df_base.dropna(subset=['OPERADOR'])
        df_base['OPERADOR'] = df_base['OPERADOR'].astype(str).str.strip()
        
        return df_base
        
    except Exception as e:
        st.warning(f"❌ Error al cargar base de evaluadores: {str(e)}")
        return pd.DataFrame()
```

### Enriquecimiento de Datos
```python
def enriquecer_pendientes_con_base(df_pendientes: pd.DataFrame, proceso: str) -> pd.DataFrame:
    """
    ENRIQUECE PENDIENTES CON INFORMACIÓN DE BASE
    
    PROCESO:
    1. Cargar base de evaluadores
    2. LEFT JOIN con datos de pendientes
    3. Llenar valores faltantes con 'OTROS'
    4. Retornar DataFrame enriquecido
    """
    base_evaluadores = cargar_base_evaluadores(proceso)
    
    if base_evaluadores.empty:
        # Si no hay base, llenar con 'OTROS'
        df_enriquecido = df_pendientes.copy()
        df_enriquecido['REGIMEN'] = 'OTROS'
        df_enriquecido['TURNO'] = 'OTROS'
        df_enriquecido['MODALIDAD'] = 'OTROS'
        df_enriquecido['SUB-EQUIPO'] = 'OTROS'
        return df_enriquecido
    
    # LEFT JOIN para mantener todos los operadores
    df_enriquecido = df_pendientes.merge(
        base_evaluadores[['OPERADOR', 'REGIMEN', 'TURNO', 'MODALIDAD', 'SUB-EQUIPO']], 
        on='OPERADOR', 
        how='left'
    )
    
    # Llenar valores faltantes con 'OTROS'
    columnas_clasificacion = ['REGIMEN', 'TURNO', 'MODALIDAD', 'SUB-EQUIPO']
    for col in columnas_clasificacion:
        df_enriquecido[col] = df_enriquecido[col].fillna('OTROS')
    
    return df_enriquecido
```

---

## 🎨 SISTEMA DE COLORES POR SUB-EQUIPO

### Colores Definidos
```python
def obtener_color_subequipo(subequipo: str) -> str:
    """
    COLORES HEXADECIMALES POR SUB-EQUIPO:
    
    SUB-EQUIPOS ACTIVOS (con datos):
    - SUB-EQUIPO 1: #90EE90 (Verde claro)
    - SUB-EQUIPO 2: #FFB347 (Naranja claro)  
    - SUB-EQUIPO 3: #87CEEB (Azul cielo)
    - SUB-EQUIPO 4: #DDA0DD (Ciruela)
    - SUB-EQUIPO 5: #F0E68C (Caqui)
    - SUB-EQUIPO 6: #FFA07A (Salmón claro)
    
    OTROS CASOS:
    - OTROS (no en base): #FFFFFF (Blanco)
    - Sin datos/inactivos: #D3D3D3 (Gris claro)
    """
    colores_subequipos = {
        'SUB-EQUIPO 1': '#90EE90',  # Verde claro
        'SUB-EQUIPO 2': '#FFB347',  # Naranja claro
        'SUB-EQUIPO 3': '#87CEEB',  # Azul cielo
        'SUB-EQUIPO 4': '#DDA0DD',  # Ciruela
        'SUB-EQUIPO 5': '#F0E68C',  # Caqui
        'SUB-EQUIPO 6': '#FFA07A',  # Salmón claro
        'OTROS': '#FFFFFF'          # Blanco para no clasificados
    }
    
    return colores_subequipos.get(subequipo, '#D3D3D3')  # Gris por defecto
```

### Aplicación de Colores en Tablas
```python
def aplicar_colores_tabla(tabla: pd.DataFrame, base_evaluadores: pd.DataFrame):
    """
    APLICA COLORES A FILAS DE TABLA SEGÚN SUB-EQUIPO
    
    LÓGICA:
    1. Crear mapa operador → sub-equipo
    2. Aplicar color de fondo a cada fila
    3. No colorear fila 'Total'
    4. Usar colores hex específicos
    """
    if base_evaluadores.empty:
        return tabla.style
    
    # Crear mapa operador → sub-equipo
    mapa_subequipos = dict(zip(base_evaluadores['OPERADOR'], base_evaluadores['SUB-EQUIPO']))
    
    def colorear_fila(row):
        # No colorear la fila "Total"
        if row.name == 'Total':
            return [''] * len(row)
        
        operador = str(row.name)
        subequipo = mapa_subequipos.get(operador, 'OTROS')
        color = obtener_color_subequipo(subequipo)
        
        return [f'background-color: {color}'] * len(row)
    
    return tabla.style.apply(colorear_fila, axis=1)
```

---

## 📈 CREACIÓN DE TABLAS DINÁMICAS

### Tabla Dinámica Base
```python
def crear_tabla_pendientes(df_filtrado: pd.DataFrame, agrupacion: str = "anios") -> pd.DataFrame:
    """
    CREA TABLA DINÁMICA OPERADOR x PERÍODO
    
    AGRUPACIONES DISPONIBLES:
    - "anios": Operador x Año
    - "meses": Operador x Año-Mes  
    - "trimestres": Operador x Trimestre
    
    SIEMPRE:
    - margins=True (agregar totales)
    - margins_name='Total'
    - fill_value=0 (llenar vacíos con 0)
    - aggfunc='count' (contar trámites)
    """
    if agrupacion == "anios":
        return pd.pivot_table(
            df_filtrado, 
            index='OPERADOR', 
            columns='Anio', 
            values='NumeroTramite',
            aggfunc='count', 
            fill_value=0, 
            margins=True, 
            margins_name='Total'
        )
    
    elif agrupacion == "meses":
        # Crear columna Año-Mes
        df_temp = df_filtrado.copy()
        df_temp['Mes'] = df_temp['Mes'].astype(str).str.zfill(2)
        df_temp['AnioMes'] = df_temp['Anio'].astype(str) + '-' + df_temp['Mes']
        
        return pd.pivot_table(
            df_temp, 
            index='OPERADOR', 
            columns='AnioMes', 
            values='NumeroTramite',
            aggfunc='count', 
            fill_value=0, 
            margins=True, 
            margins_name='Total'
        )
    
    elif agrupacion == "trimestres":
        # Usar FechaExpendiente para calcular trimestres
        df_temp = df_filtrado.copy()
        df_temp['Trimestre'] = df_temp['FechaExpendiente'].dt.to_period('Q').astype(str)
        
        return pd.pivot_table(
            df_temp, 
            index='OPERADOR', 
            columns='Trimestre', 
            values='NumeroTramite',
            aggfunc='count', 
            fill_value=0, 
            margins=True, 
            margins_name='Total'
        )
```

---

## 📋 HISTÓRICOS AUTOMÁTICOS

### Actualización de Histórico Sin Asignar
```python
def actualizar_historico_sin_asignar(df_ccm: pd.DataFrame, df_prr: pd.DataFrame):
    """
    ACTUALIZA ARCHIVO: historico_sin_asignar.csv
    
    PROCESO:
    1. Calcular pendientes sin asignar por proceso
    2. Leer histórico existente
    3. Agregar nueva fila con fecha actual
    4. Guardar archivo actualizado
    
    ESTRUCTURA CSV:
    - Fecha: Fecha de la medición
    - CCM_SinAsignar: Cantidad CCM sin asignar
    - PRR_SinAsignar: Cantidad PRR sin asignar
    - Total_SinAsignar: Suma de ambos procesos
    """
    # Calcular pendientes actuales
    pendientes_ccm = procesar_pendientes(df_ccm, "CCM")
    pendientes_prr = procesar_pendientes(df_prr, "PRR")
    
    sin_asignar_ccm = len(pendientes_ccm[pendientes_ccm['OPERADOR'] == 'Sin asignar'])
    sin_asignar_prr = len(pendientes_prr[pendientes_prr['OPERADOR'] == 'Sin asignar'])
    total_sin_asignar = sin_asignar_ccm + sin_asignar_prr
    
    # Crear registro actual
    nuevo_registro = {
        'Fecha': pd.Timestamp.now().strftime('%Y-%m-%d'),
        'CCM_SinAsignar': sin_asignar_ccm,
        'PRR_SinAsignar': sin_asignar_prr,
        'Total_SinAsignar': total_sin_asignar
    }
    
    # Actualizar histórico
    archivo_historico = "historico_sin_asignar.csv"
    
    try:
        if os.path.exists(archivo_historico):
            df_historico = pd.read_csv(archivo_historico)
        else:
            df_historico = pd.DataFrame()
        
        # Agregar nuevo registro si no existe para hoy
        fecha_hoy = nuevo_registro['Fecha']
        if df_historico.empty or fecha_hoy not in df_historico['Fecha'].values:
            df_historico = pd.concat([df_historico, pd.DataFrame([nuevo_registro])], ignore_index=True)
            df_historico.to_csv(archivo_historico, index=False)
            
    except Exception as e:
        st.warning(f"No se pudo actualizar histórico: {str(e)}")
```

### Preparación de Histórico de Pendientes
```python
def preparar_historico_pendientes(proceso: str) -> pd.DataFrame:
    """
    CREA/LEE ARCHIVO: historico_pendientes_operador.csv
    
    ESTRUCTURA:
    - Fecha: Fecha de la medición  
    - OPERADOR: Nombre del operador
    - Proceso: CCM o PRR
    - Pendientes: Cantidad de pendientes
    
    PROPÓSITO: Histórico para análisis evolutivo por operador
    """
    archivo = "ARCHIVOS/historico_pendientes_operador.csv"
    
    try:
        if os.path.exists(archivo):
            df_historico = pd.read_csv(archivo)
            df_historico['Fecha'] = pd.to_datetime(df_historico['Fecha'])
            
            # Filtrar por proceso
            df_proceso = df_historico[df_historico['Proceso'] == proceso]
            return df_proceso
        else:
            return pd.DataFrame()
            
    except Exception as e:
        st.warning(f"Error al cargar histórico: {str(e)}")
        return pd.DataFrame()
``` 