# 📋 03 - PESTAÑA PENDIENTES ACTUAL

## 📝 PROPÓSITO
Documentación técnica completa de la pestaña Pendientes que muestra casos sin procesar con filtros avanzados, agrupación temporal y sistema de colores por sub-equipos.

---

## 🔄 FLUJO DE PROCESAMIENTO

### Carga y Filtrado Inicial
```python
# En pendientes.py
def mostrar_pendientes(df: pd.DataFrame, proceso: str) -> None:
    """
    FLUJO PRINCIPAL DE LA PESTAÑA PENDIENTES:
    
    1. Aplicar filtros específicos del proceso
    2. Enriquecer con base de evaluadores  
    3. Crear controles de filtrado
    4. Generar tabla dinámica según agrupación
    5. Aplicar filtros adicionales
    6. Mostrar con colores por sub-equipo
    7. Proporcionar exportación Excel
    """
    st.header("Pendientes")
    
    # PASO 1: PROCESAR PENDIENTES BÁSICOS
    df_pendientes = procesar_pendientes(df, proceso)
    
    # PASO 2: ENRIQUECER CON BASE DE EVALUADORES
    df_enriquecido = enriquecer_pendientes_con_base(df_pendientes, proceso)
    
    # PASO 3: INFORMACIÓN GENERAL
    st.sidebar.info(f"Total pendientes {proceso}: {len(df_pendientes):,}")
    sin_asignar = calcular_sin_asignar(df_pendientes, "anios")
    st.sidebar.warning(f"Sin asignar: {sin_asignar:,} casos")
```

---

## 🔧 FILTROS ESPECÍFICOS POR PROCESO

### Filtros CCM
```python
def procesar_pendientes_ccm(df):
    """
    FILTROS APLICADOS PARA CCM:
    
    CONDICIONES OBLIGATORIAS:
    1. UltimaEtapa == 'EVALUACIÓN - I'
    2. EstadoPre.isna() == True (no tiene estado de procesamiento)
    3. EstadoTramite == 'PENDIENTE'
    4. EQUIPO != 'VULNERABLE' (excluir casos vulnerables)
    
    RESULTADO: Solo casos CCM en etapa EVALUACIÓN - I pendientes de procesar
    """
    return df[
        (df['UltimaEtapa'] == 'EVALUACIÓN - I') &
        (df['EstadoPre'].isna()) &
        (df['EstadoTramite'] == 'PENDIENTE') &
        (df['EQUIPO'] != 'VULNERABLE')
    ]
```

### Filtros PRR
```python
def procesar_pendientes_prr(df):
    """
    FILTROS APLICADOS PARA PRR:
    
    ETAPAS VÁLIDAS (8 etapas específicas):
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
    
    RESULTADO: Solo casos PRR en etapas válidas pendientes de procesar
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

---

## 🎛️ CONTROLES DE USUARIO

### Panel de Filtros en Sidebar
```python
def crear_controles_filtros(df_enriquecido, proceso):
    """
    CONTROLES DISPONIBLES EN SIDEBAR:
    
    1. AGRUPACIÓN TEMPORAL:
       - Años (default)
       - Meses  
       - Trimestres
    
    2. MODO DE VISTA:
       - GENERAL: Evaluadores en base (SUB-EQUIPO != 'OTROS')
       - OTROS: Evaluadores no clasificados (SUB-EQUIPO == 'OTROS')
    
    3. FILTROS ESPECÍFICOS (solo para modo GENERAL):
       - Régimen: CAS, PLANILLA, etc.
       - Turno: MAÑANA, TARDE, COMPLETO
       - Modalidad: PRESENCIAL, REMOTO, MIXTO
       - Sub-equipo: SUB-EQUIPO 1, 2, 3, etc.
    """
    
    # AGRUPACIÓN TEMPORAL
    st.sidebar.subheader("🗓️ Agrupación")
    agrupacion = st.sidebar.selectbox(
        "Selecciona agrupación:",
        ["anios", "meses", "trimestres"],
        index=0,  # Default: años
        help="Determina cómo se agrupan los pendientes en la tabla"
    )
    
    # MODO DE VISTA
    st.sidebar.subheader("👥 Vista")
    modo_vista = st.sidebar.selectbox(
        "Modo de vista:",
        ["GENERAL", "OTROS"],
        help="GENERAL: Evaluadores clasificados | OTROS: No clasificados"
    )
    
    # FILTROS ESPECÍFICOS (solo para GENERAL)
    filtros = {"regimen": "Todos", "turno": "Todos", "modalidad": "Todos", "subequipo": "Todos"}
    
    if modo_vista == "GENERAL":
        st.sidebar.subheader("🔍 Filtros")
        
        # OBTENER OPCIONES DISPONIBLES
        regimenes, turnos, modalidades, subequipos = obtener_opciones_filtros(df_enriquecido, modo_vista)
        
        filtros["regimen"] = st.sidebar.selectbox("Régimen:", regimenes)
        filtros["turno"] = st.sidebar.selectbox("Turno:", turnos)  
        filtros["modalidad"] = st.sidebar.selectbox("Modalidad:", modalidades)
        filtros["subequipo"] = st.sidebar.selectbox("Sub-equipo:", subequipos)
    
    return agrupacion, modo_vista, filtros
```

### Obtención de Opciones de Filtros
```python
def obtener_opciones_filtros(tabla_enriquecida: pd.DataFrame, modo_vista: str) -> tuple:
    """
    GENERA OPCIONES DE FILTROS DINÁMICAMENTE:
    
    LÓGICA:
    1. Filtrar datos según modo de vista
    2. Extraer valores únicos de cada columna
    3. Ordenar y agregar opción "Todos"
    4. Excluir valores 'OTROS' para modo GENERAL
    
    RETORNA:
    - Lista de regímenes disponibles
    - Lista de turnos disponibles  
    - Lista de modalidades disponibles
    - Lista de sub-equipos disponibles
    """
    if modo_vista == "GENERAL":
        # Solo evaluadores clasificados (SUB-EQUIPO != 'OTROS')
        tabla_filtro = tabla_enriquecida[tabla_enriquecida['SUB-EQUIPO'] != 'OTROS']
    else:
        # Solo evaluadores no clasificados (SUB-EQUIPO == 'OTROS')
        tabla_filtro = tabla_enriquecida[tabla_enriquecida['SUB-EQUIPO'] == 'OTROS']
    
    if tabla_filtro.empty:
        return (["Todos"], ["Todos"], ["Todos"], ["Todos"])
    
    # EXTRAER VALORES ÚNICOS Y FILTRAR
    regimenes = ["Todos"] + sorted([x for x in tabla_filtro['REGIMEN'].unique() if x != 'OTROS'])
    turnos = ["Todos"] + sorted([x for x in tabla_filtro['TURNO'].unique() if x != 'OTROS'])
    modalidades = ["Todos"] + sorted([x for x in tabla_filtro['MODALIDAD'].unique() if x != 'OTROS'])
    subequipos = ["Todos"] + sorted([x for x in tabla_filtro['SUB-EQUIPO'].unique() if x != 'OTROS'])
    
    return regimenes, turnos, modalidades, subequipos
```

---

## 📊 CREACIÓN DE TABLAS DINÁMICAS

### Tabla por Años
```python
def crear_tabla_pendientes_anios(df_filtrado):
    """
    TABLA DINÁMICA: OPERADOR x AÑO
    
    ESTRUCTURA:
    - Filas: OPERADOR (nombres de evaluadores)
    - Columnas: Años (2023, 2024, etc.)
    - Valores: COUNT de NumeroTramite (cantidad de pendientes)
    - Totales: margins=True, margins_name='Total'
    
    RESULTADO: Tabla mostrando pendientes por operador y año
    """
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
```

### Tabla por Meses
```python
def crear_tabla_pendientes_meses(df_filtrado):
    """
    TABLA DINÁMICA: OPERADOR x AÑO-MES
    
    PROCESO:
    1. Crear columna AnioMes combinada (formato: '2024-01')
    2. Crear tabla pivotada con AnioMes como columnas
    3. Contar pendientes por operador y mes
    
    FORMATO COLUMNAS: YYYY-MM (ej: 2024-01, 2024-02)
    """
    df_temp = df_filtrado.copy()
    df_temp['Mes'] = df_temp['Mes'].astype(str).str.zfill(2)  # 01, 02, 03...
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
```

### Tabla por Trimestres
```python
def crear_tabla_pendientes_trimestres(df_filtrado):
    """
    TABLA DINÁMICA: OPERADOR x TRIMESTRE
    
    PROCESO:
    1. Calcular trimestre desde FechaExpendiente
    2. Formato: YYYY-Q1, YYYY-Q2, etc.
    3. Crear tabla pivotada con trimestres como columnas
    
    CÁLCULO TRIMESTRE:
    - Q1: Enero-Marzo (meses 1-3)
    - Q2: Abril-Junio (meses 4-6) 
    - Q3: Julio-Septiembre (meses 7-9)
    - Q4: Octubre-Diciembre (meses 10-12)
    """
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

## 🔍 APLICACIÓN DE FILTROS AVANZADOS

### Filtrado de Tabla Enriquecida
```python
def aplicar_filtros_tabla(tabla: pd.DataFrame, modo_vista: str, regimen_filtro: str, 
                         turno_filtro: str, modalidad_filtro: str, subequipo_filtro: str) -> pd.DataFrame:
    """
    APLICA FILTROS COMPLEJOS A LA TABLA:
    
    PASOS:
    1. Preservar fila 'Total' temporalmente
    2. Aplicar filtro principal según modo_vista
    3. Aplicar filtros específicos si != "Todos"
    4. Filtrar columnas sin datos (Total = 0)
    5. Recalcular fila 'Total' basada en datos filtrados
    6. Retornar tabla final
    """
    tabla_filtrada = tabla.copy()
    
    # PRESERVAR FILA TOTAL
    fila_total = None
    if 'Total' in tabla_filtrada.index:
        fila_total = tabla_filtrada.loc[['Total']].copy()
        tabla_filtrada = tabla_filtrada.drop('Total', errors='ignore')
    
    # FILTRO PRINCIPAL POR MODO DE VISTA
    if modo_vista == "GENERAL":
        # Solo evaluadores clasificados (en la base)
        tabla_filtrada = tabla_filtrada[tabla_filtrada['SUB-EQUIPO'] != 'OTROS']
    else:  # modo_vista == "OTROS"
        # Solo evaluadores no clasificados
        tabla_filtrada = tabla_filtrada[tabla_filtrada['SUB-EQUIPO'] == 'OTROS']
    
    # FILTROS ESPECÍFICOS (solo si no es "Todos")
    if not tabla_filtrada.empty:
        if regimen_filtro != "Todos" and regimen_filtro in tabla_filtrada['REGIMEN'].values:
            tabla_filtrada = tabla_filtrada[tabla_filtrada['REGIMEN'] == regimen_filtro]
        
        if turno_filtro != "Todos" and turno_filtro in tabla_filtrada['TURNO'].values:
            tabla_filtrada = tabla_filtrada[tabla_filtrada['TURNO'] == turno_filtro]
            
        if modalidad_filtro != "Todos" and modalidad_filtro in tabla_filtrada['MODALIDAD'].values:
            tabla_filtrada = tabla_filtrada[tabla_filtrada['MODALIDAD'] == modalidad_filtro]
            
        if subequipo_filtro != "Todos" and subequipo_filtro in tabla_filtrada['SUB-EQUIPO'].values:
            tabla_filtrada = tabla_filtrada[tabla_filtrada['SUB-EQUIPO'] == subequipo_filtro]
    
    # RECALCULAR TOTALES Y FILTRAR COLUMNAS VACÍAS
    if fila_total is not None and not tabla_filtrada.empty:
        # Columnas numéricas (períodos temporales)
        columnas_numericas = [col for col in tabla_filtrada.columns 
                             if col not in ['REGIMEN', 'TURNO', 'MODALIDAD', 'SUB-EQUIPO']]
        
        # Calcular nuevos totales
        nueva_fila_total = tabla_filtrada[columnas_numericas].sum(axis=0)
        
        # FILTRAR COLUMNAS CON TOTAL 0 (sin pendientes)
        columnas_con_datos = [col for col in columnas_numericas if nueva_fila_total[col] > 0]
        
        # Mantener al menos una columna si todas están vacías
        if not columnas_con_datos and columnas_numericas:
            columnas_con_datos = [columnas_numericas[-1]]
        
        # Filtrar tabla para mostrar solo columnas con datos
        columnas_clasificacion = ['REGIMEN', 'TURNO', 'MODALIDAD', 'SUB-EQUIPO']
        columnas_a_mostrar = [col for col in columnas_clasificacion if col in tabla_filtrada.columns] + columnas_con_datos
        tabla_filtrada = tabla_filtrada[columnas_a_mostrar]
        
        # AGREGAR FILA TOTAL RECALCULADA
        nueva_fila_total_filtrada = tabla_filtrada[columnas_con_datos].sum(axis=0)
        nueva_fila_total_df = pd.DataFrame([nueva_fila_total_filtrada])
        
        # Agregar columnas de clasificación para fila Total
        for col in columnas_clasificacion:
            if col in tabla_filtrada.columns:
                nueva_fila_total_df[col] = 'TOTAL'
        
        # Reordenar columnas y concatenar
        columnas_ordenadas = [col for col in columnas_clasificacion if col in nueva_fila_total_df.columns] + columnas_con_datos
        nueva_fila_total_df = nueva_fila_total_df[columnas_ordenadas]
        tabla_filtrada = pd.concat([tabla_filtrada, nueva_fila_total_df])
    
    return tabla_filtrada
```

---

## 🎨 SISTEMA DE COLORES

### Generación de Tabla Solo con Pendientes
```python
def generar_tabla_con_colores(tabla_filtrada: pd.DataFrame) -> pd.DataFrame:
    """
    GENERA TABLA FINAL PARA MOSTRAR:
    
    PROCESO:
    1. Extraer solo columnas numéricas (pendientes por período)
    2. Asegurar columna 'Total' al final
    3. Convertir valores a enteros para mejor visualización
    4. Retornar tabla preparada para aplicar colores
    
    RESULTADO: Tabla solo con números de pendientes (sin columnas de clasificación)
    """
    # Solo columnas numéricas (períodos + Total)
    columnas_numericas = [col for col in tabla_filtrada.columns 
                         if col not in ['REGIMEN', 'TURNO', 'MODALIDAD', 'SUB-EQUIPO']]
    
    tabla_display = tabla_filtrada[columnas_numericas].copy()
    
    # ASEGURAR QUE 'Total' ESTÉ AL FINAL
    if 'Total' in tabla_display.columns:
        cols = [col for col in tabla_display.columns if col != 'Total']
        cols.append('Total')
        tabla_display = tabla_display[cols]
    
    # CONVERTIR A ENTEROS
    for col in tabla_display.columns:
        if tabla_display[col].dtype in ['float64', 'float32']:
            tabla_display[col] = tabla_display[col].astype(int)
    
    return tabla_display
```

### Aplicación de Colores por Sub-Equipo
```python
def aplicar_estilo_subequipo(tabla_display, tabla_filtrada, base_evaluadores):
    """
    APLICA COLORES DE FONDO SEGÚN SUB-EQUIPO:
    
    MAPEO DE COLORES:
    - SUB-EQUIPO 1: #90EE90 (Verde claro)
    - SUB-EQUIPO 2: #FFB347 (Naranja claro)
    - SUB-EQUIPO 3: #87CEEB (Azul cielo)
    - SUB-EQUIPO 4: #DDA0DD (Ciruela)
    - SUB-EQUIPO 5: #F0E68C (Caqui)
    - SUB-EQUIPO 6: #FFA07A (Salmón claro)
    - OTROS: #FFFFFF (Blanco)
    - INACTIVOS: #D3D3D3 (Gris claro)
    
    LÓGICA:
    1. Crear mapa operador → sub-equipo desde base
    2. Para cada fila, obtener sub-equipo del operador
    3. Aplicar color correspondiente a toda la fila
    4. NO colorear fila 'Total'
    """
    if base_evaluadores.empty:
        return tabla_display.style
    
    # CREAR MAPA OPERADOR → SUB-EQUIPO
    mapa_subequipos = dict(zip(base_evaluadores['OPERADOR'], base_evaluadores['SUB-EQUIPO']))
    
    def colorear_fila(row):
        # NO COLOREAR FILA 'Total'
        if row.name == 'Total':
            return [''] * len(row)
        
        # OBTENER SUB-EQUIPO DEL OPERADOR
        operador = str(row.name)
        subequipo = mapa_subequipos.get(operador, 'OTROS')
        
        # OBTENER COLOR CORRESPONDIENTE
        colores_subequipos = {
            'SUB-EQUIPO 1': '#90EE90',  # Verde claro
            'SUB-EQUIPO 2': '#FFB347',  # Naranja claro
            'SUB-EQUIPO 3': '#87CEEB',  # Azul cielo
            'SUB-EQUIPO 4': '#DDA0DD',  # Ciruela
            'SUB-EQUIPO 5': '#F0E68C',  # Caqui
            'SUB-EQUIPO 6': '#FFA07A',  # Salmón claro
            'OTROS': '#FFFFFF'          # Blanco
        }
        
        color = colores_subequipos.get(subequipo, '#D3D3D3')  # Gris por defecto
        
        return [f'background-color: {color}'] * len(row)
    
    return tabla_display.style.apply(colorear_fila, axis=1)
```

### Leyenda de Colores
```python
def crear_leyenda_colores(modo_vista: str):
    """
    MUESTRA LEYENDA DE COLORES SEGÚN MODO DE VISTA:
    
    MODO GENERAL:
    - Muestra colores de todos los sub-equipos activos
    - 4 columnas con colores y nombres
    
    MODO OTROS:
    - Solo muestra color blanco para no clasificados
    """
    st.markdown("### 📋 Leyenda de Colores")
    
    if modo_vista == "GENERAL":
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown('<div style="background-color: #90EE90; padding: 5px; border-radius: 5px; text-align: center;">SUB-EQUIPO 1</div>', unsafe_allow_html=True)
            st.markdown('<div style="background-color: #FFB347; padding: 5px; border-radius: 5px; text-align: center;">SUB-EQUIPO 2</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div style="background-color: #87CEEB; padding: 5px; border-radius: 5px; text-align: center;">SUB-EQUIPO 3</div>', unsafe_allow_html=True)
            st.markdown('<div style="background-color: #DDA0DD; padding: 5px; border-radius: 5px; text-align: center;">SUB-EQUIPO 4</div>', unsafe_allow_html=True)
        
        with col3:
            st.markdown('<div style="background-color: #F0E68C; padding: 5px; border-radius: 5px; text-align: center;">SUB-EQUIPO 5</div>', unsafe_allow_html=True)
            st.markdown('<div style="background-color: #FFA07A; padding: 5px; border-radius: 5px; text-align: center;">SUB-EQUIPO 6</div>', unsafe_allow_html=True)
        
        with col4:
            st.markdown('<div style="background-color: #FFFFFF; border: 1px solid #ccc; padding: 5px; border-radius: 5px; text-align: center;">SIN CLASIFICAR</div>', unsafe_allow_html=True)
            st.markdown('<div style="background-color: #D3D3D3; padding: 5px; border-radius: 5px; text-align: center;">INACTIVOS</div>', unsafe_allow_html=True)
    
    else:  # modo_vista == "OTROS"
        st.markdown('<div style="background-color: #FFFFFF; border: 1px solid #ccc; padding: 10px; border-radius: 5px; text-align: center; max-width: 200px;">Evaluadores no clasificados</div>', unsafe_allow_html=True)
```

---

## 📤 EXPORTACIÓN A EXCEL

### Funcionalidad de Descarga
```python
def exportar_a_excel(tabla_final, proceso, agrupacion):
    """
    GENERA ARCHIVO EXCEL PARA DESCARGA:
    
    CARACTERÍSTICAS:
    - Formato Excel (.xlsx)
    - Nombre archivo: pendientes_{proceso}_{agrupacion}.xlsx
    - Incluye todos los datos filtrados
    - Mantiene estructura de tabla con totales
    
    USO:
    st.download_button() con datos generados
    """
    from modules.utils.excel_export import to_excel_with_format
    
    # GENERAR DATOS EXCEL
    excel_data = to_excel_with_format(tabla_final)
    
    # NOMBRE DE ARCHIVO
    nombre_archivo = f"pendientes_{proceso}_{agrupacion}.xlsx"
    
    # BOTÓN DE DESCARGA
    st.download_button(
        label="📥 Descargar tabla de Pendientes en Excel",
        data=excel_data,
        file_name=nombre_archivo,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
```

---

## 📊 INFORMACIÓN ADICIONAL MOSTRADA

### Métricas en Sidebar
```python
def mostrar_metricas_sidebar(df_pendientes, proceso):
    """
    INFORMACIÓN MOSTRADA EN SIDEBAR:
    
    1. Total pendientes: Cantidad total filtrada
    2. Sin asignar: Casos con OPERADOR = 'Sin asignar'  
    3. Rango de fechas: Fecha mínima y máxima de expedientes
    4. Última actualización: Timestamp de carga
    """
    # TOTAL PENDIENTES
    total_pendientes = len(df_pendientes)
    st.sidebar.info(f"Total pendientes {proceso}: {total_pendientes:,}")
    
    # SIN ASIGNAR
    sin_asignar = len(df_pendientes[df_pendientes['OPERADOR'] == 'Sin asignar'])
    porcentaje_sin_asignar = (sin_asignar / total_pendientes * 100) if total_pendientes > 0 else 0
    st.sidebar.warning(f"Sin asignar: {sin_asignar:,} casos ({porcentaje_sin_asignar:.1f}%)")
    
    # RANGO DE FECHAS
    if 'FechaExpendiente' in df_pendientes.columns:
        fecha_min = df_pendientes['FechaExpendiente'].min()
        fecha_max = df_pendientes['FechaExpendiente'].max()
        if pd.notna(fecha_min) and pd.notna(fecha_max):
            st.sidebar.info(f"Rango: {fecha_min.strftime('%d/%m/%Y')} - {fecha_max.strftime('%d/%m/%Y')}")
    
    # ÚLTIMA ACTUALIZACIÓN
    st.sidebar.success(f"Actualizado: {pd.Timestamp.now().strftime('%d/%m/%Y %H:%M')}")
```

---

## 📋 RESUMEN DE FUNCIONAMIENTO

### Características Principales
1. **FILTROS ESPECÍFICOS**: Diferentes filtros para CCM vs PRR
2. **AGRUPACIÓN TEMPORAL**: Años, meses o trimestres
3. **MODOS DE VISTA**: GENERAL (clasificados) vs OTROS (sin clasificar)
4. **FILTROS AVANZADOS**: Por régimen, turno, modalidad y sub-equipo
5. **COLORES DINÁMICOS**: Sistema de colores por sub-equipo
6. **EXPORTACIÓN**: Descarga en Excel con formato
7. **TOTALES INTELIGENTES**: Recalculo automático de totales tras filtros

### Flujo de Ejecución
```
1. Cargar datos según proceso seleccionado
   ↓
2. Aplicar filtros específicos CCM/PRR
   ↓
3. Enriquecer con base de evaluadores
   ↓
4. Mostrar controles de filtrado en sidebar
   ↓
5. Crear tabla dinámica según agrupación temporal
   ↓
6. Aplicar filtros adicionales (modo, régimen, etc.)
   ↓
7. Filtrar columnas sin datos (Total = 0)
   ↓
8. Recalcular totales basados en datos filtrados
   ↓
9. Aplicar colores por sub-equipo
   ↓
10. Mostrar tabla final con leyenda de colores
   ↓
11. Proporcionar botón de descarga Excel
```

### Operadores Excluidos por Proceso
- **CCM**: "Sin asignar", "Aponte Sanchez, Paola Lita", "Lucero Martinez, Carlos Martin", "USUARIO DE AGENCIA DIGITAL", **"MAURICIO ROMERO, HUGO"**
- **PRR**: "Sin asignar", "Aponte Sanchez, Paola Lita", "Lucero Martinez, Carlos Martin", "USUARIO DE AGENCIA DIGITAL" (NO incluye Mauricio Romero) 