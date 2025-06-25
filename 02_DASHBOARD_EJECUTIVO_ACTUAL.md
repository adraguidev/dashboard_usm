# 🎯 02 - DASHBOARD EJECUTIVO ACTUAL

## 📝 PROPÓSITO
Documentación técnica completa del Dashboard Ejecutivo que se carga automáticamente con datos de ambos procesos (CCM y PRR) y muestra métricas consolidadas, KPIs principales y análisis de tendencias.

---

## 🔄 FLUJO DE CARGA AUTOMÁTICA

### Carga Simultánea de Ambos Procesos
```python
# En dashboard_ejecutivo_main.py
def mostrar_dashboard_ejecutivo():
    """
    CARGA AUTOMÁTICA DE AMBOS PROCESOS:
    1. No depende de selección del usuario
    2. Carga CCM y PRR simultáneamente
    3. Consolida métricas de ambos
    4. Actualiza histórico automáticamente
    """
    try:
        # Cargar datos de ambos procesos
        archivos_proceso = obtener_archivos_proceso()
        
        with st.spinner("🔄 Cargando datos..."):
            # CARGA SIMULTÁNEA
            df_ccm = cargar_datos(archivos_proceso["CCM"])
            df_prr = cargar_datos(archivos_proceso["PRR"])
            
            # ACTUALIZAR HISTÓRICO AUTOMÁTICAMENTE
            actualizar_historico_sin_asignar(df_ccm, df_prr)
            
            # CALCULAR MÉTRICAS EXACTAS
            metricas_ccm = calcular_metricas_exactas_ccm(df_ccm)
            metricas_prr = calcular_metricas_exactas_prr(df_prr)
            metricas_consolidadas = consolidar_metricas(metricas_ccm, metricas_prr)
            tendencias = calcular_tendencias_reales(metricas_ccm, metricas_prr)
```

---

## 📊 CÁLCULO DE MÉTRICAS EXACTAS

### Métricas CCM
```python
# En dashboard_ejecutivo_metricas.py
def calcular_metricas_exactas_ccm(df_ccm: pd.DataFrame) -> dict:
    """
    MÉTRICAS ESPECÍFICAS PARA CCM:
    
    FILTROS APLICADOS:
    1. Pendientes: UltimaEtapa='EVALUACIÓN - I' + EstadoPre=null + EstadoTramite='PENDIENTE' + EQUIPO!='VULNERABLE'
    2. Trabajados últimos 20 días: Datos con FechaPre en últimos 20 días
    3. Ingresos últimos 60 días: FechaExpendiente en últimos 60 días
    4. Sin asignar: OPERADOR='Sin asignar' dentro de pendientes
    
    RETORNA:
    - total_pendientes: Cantidad total de pendientes CCM
    - trabajados_20d: Cantidad trabajados en últimos 20 días
    - ingresos_60d: Cantidad de ingresos en últimos 60 días
    - sin_asignar: Cantidad de pendientes sin asignar
    - promedio_diario: Promedio de trabajo diario
    """
    # PENDIENTES CCM
    pendientes_ccm = df_ccm[
        (df_ccm['UltimaEtapa'] == 'EVALUACIÓN - I') &
        (df_ccm['EstadoPre'].isna()) &
        (df_ccm['EstadoTramite'] == 'PENDIENTE') &
        (df_ccm['EQUIPO'] != 'VULNERABLE')
    ]
    
    # TRABAJADOS ÚLTIMOS 20 DÍAS
    fecha_limite_trabajo = pd.Timestamp.now() - pd.Timedelta(days=20)
    trabajados_20d = len(df_ccm[
        (df_ccm['FechaPre'] >= fecha_limite_trabajo) &
        (df_ccm['FechaPre'].notna())
    ])
    
    # INGRESOS ÚLTIMOS 60 DÍAS
    fecha_limite_ingreso = pd.Timestamp.now() - pd.Timedelta(days=60)
    ingresos_60d = len(df_ccm[
        (df_ccm['FechaExpendiente'] >= fecha_limite_ingreso) &
        (df_ccm['FechaExpendiente'].notna())
    ])
    
    # SIN ASIGNAR
    sin_asignar = len(pendientes_ccm[pendientes_ccm['OPERADOR'] == 'Sin asignar'])
    
    # PROMEDIO DIARIO (últimos 20 días)
    promedio_diario = trabajados_20d / 20 if trabajados_20d > 0 else 0
    
    return {
        'proceso': 'CCM',
        'total_pendientes': len(pendientes_ccm),
        'trabajados_20d': trabajados_20d,
        'ingresos_60d': ingresos_60d,
        'sin_asignar': sin_asignar,
        'promedio_diario': round(promedio_diario, 1)
    }
```

### Métricas PRR
```python
def calcular_metricas_exactas_prr(df_prr: pd.DataFrame) -> dict:
    """
    MÉTRICAS ESPECÍFICAS PARA PRR:
    
    FILTROS APLICADOS:
    1. Pendientes: UltimaEtapa IN (8 etapas PRR) + EstadoPre=null + EstadoTramite='PENDIENTE' + EQUIPO!='VULNERABLE'
    2. Trabajados: Misma lógica que CCM
    3. Ingresos: Misma lógica que CCM
    
    ETAPAS PRR VÁLIDAS:
    - 'ACTUALIZAR DATOS BENEFICIARIO - F'
    - 'ACTUALIZAR DATOS BENEFICIARIO - I'
    - 'ASOCIACION BENEFICIARIO - F'
    - 'ASOCIACION BENEFICIARIO - I'
    - 'CONFORMIDAD SUB-DIREC.INMGRA. - I'
    - 'PAGOS, FECHA Y NRO RD. - F'
    - 'PAGOS, FECHA Y NRO RD. - I'
    - 'RECEPCIÓN DINM - F'
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
    
    # PENDIENTES PRR
    pendientes_prr = df_prr[
        (df_prr['UltimaEtapa'].isin(etapas_prr)) &
        (df_prr['EstadoPre'].isna()) &
        (df_prr['EstadoTramite'] == 'PENDIENTE') &
        (df_prr['EQUIPO'] != 'VULNERABLE')
    ]
    
    # MISMA LÓGICA DE CÁLCULO QUE CCM
    fecha_limite_trabajo = pd.Timestamp.now() - pd.Timedelta(days=20)
    trabajados_20d = len(df_prr[
        (df_prr['FechaPre'] >= fecha_limite_trabajo) &
        (df_prr['FechaPre'].notna())
    ])
    
    fecha_limite_ingreso = pd.Timestamp.now() - pd.Timedelta(days=60)
    ingresos_60d = len(df_prr[
        (df_prr['FechaExpendiente'] >= fecha_limite_ingreso) &
        (df_prr['FechaExpendiente'].notna())
    ])
    
    sin_asignar = len(pendientes_prr[pendientes_prr['OPERADOR'] == 'Sin asignar'])
    promedio_diario = trabajados_20d / 20 if trabajados_20d > 0 else 0
    
    return {
        'proceso': 'PRR',
        'total_pendientes': len(pendientes_prr),
        'trabajados_20d': trabajados_20d,
        'ingresos_60d': ingresos_60d,
        'sin_asignar': sin_asignar,
        'promedio_diario': round(promedio_diario, 1)
    }
```

### Consolidación de Métricas
```python
def consolidar_metricas(metricas_ccm: dict, metricas_prr: dict) -> dict:
    """
    CONSOLIDA MÉTRICAS DE AMBOS PROCESOS:
    
    CÁLCULOS:
    - Suma directa de valores numéricos
    - Promedio ponderado para promedios
    - Ratios calculados sobre totales
    """
    return {
        'total_pendientes': metricas_ccm['total_pendientes'] + metricas_prr['total_pendientes'],
        'total_trabajados_20d': metricas_ccm['trabajados_20d'] + metricas_prr['trabajados_20d'],
        'total_ingresos_60d': metricas_ccm['ingresos_60d'] + metricas_prr['ingresos_60d'],
        'total_sin_asignar': metricas_ccm['sin_asignar'] + metricas_prr['sin_asignar'],
        'promedio_diario_consolidado': (metricas_ccm['trabajados_20d'] + metricas_prr['trabajados_20d']) / 20,
        'ratio_sin_asignar': round(
            ((metricas_ccm['sin_asignar'] + metricas_prr['sin_asignar']) / 
             (metricas_ccm['total_pendientes'] + metricas_prr['total_pendientes'])) * 100, 1
        ) if (metricas_ccm['total_pendientes'] + metricas_prr['total_pendientes']) > 0 else 0
    }
```

---

## 📈 KPIs PRINCIPALES

### Visualización de KPIs
```python
# En dashboard_ejecutivo_kpis.py
def mostrar_kpis_principales(metricas_consolidadas, metricas_ccm, metricas_prr, tendencias):
    """
    MUESTRA 4 KPIs PRINCIPALES EN COLUMNAS:
    
    KPI 1: Total Pendientes
    - Valor: Suma CCM + PRR
    - Color: Rojo si > umbral, Verde si <= umbral
    - Tooltip: Desglose por proceso
    
    KPI 2: Trabajados (20 días)
    - Valor: Suma de trabajados últimos 20 días
    - Tendencia: Comparación con período anterior
    - Promedio diario calculado
    
    KPI 3: Ingresos (60 días)
    - Valor: Suma de ingresos últimos 60 días
    - Comparación: Balance ingresos vs trabajados
    
    KPI 4: Sin Asignar
    - Valor: Cantidad sin asignar
    - Porcentaje: % sobre total pendientes
    - Alerta: Si ratio > 15%
    """
    col1, col2, col3, col4 = st.columns(4)
    
    # KPI 1: TOTAL PENDIENTES
    with col1:
        total_pendientes = metricas_consolidadas['total_pendientes']
        color_pendientes = "🔴" if total_pendientes > 1000 else "🟢"
        
        st.metric(
            label="📋 Total Pendientes",
            value=f"{total_pendientes:,}",
            delta=tendencias.get('delta_pendientes', 0),
            help=f"CCM: {metricas_ccm['total_pendientes']:,} | PRR: {metricas_prr['total_pendientes']:,}"
        )
        st.markdown(f"{color_pendientes} **Estado General**")
    
    # KPI 2: TRABAJADOS 20 DÍAS
    with col2:
        trabajados = metricas_consolidadas['total_trabajados_20d']
        promedio = metricas_consolidadas['promedio_diario_consolidado']
        
        st.metric(
            label="⚡ Trabajados (20d)",
            value=f"{trabajados:,}",
            delta=tendencias.get('delta_trabajados', 0),
            help=f"Promedio diario: {promedio:.1f} casos"
        )
        st.markdown(f"📊 **{promedio:.1f} diarios**")
    
    # KPI 3: INGRESOS 60 DÍAS
    with col3:
        ingresos = metricas_consolidadas['total_ingresos_60d']
        balance = ingresos - trabajados
        color_balance = "🟢" if balance >= 0 else "🔴"
        
        st.metric(
            label="📈 Ingresos (60d)",
            value=f"{ingresos:,}",
            delta=balance,
            help="Balance: Diferencia entre ingresos y trabajados"
        )
        st.markdown(f"{color_balance} **Balance: {balance:+,}**")
    
    # KPI 4: SIN ASIGNAR
    with col4:
        sin_asignar = metricas_consolidadas['total_sin_asignar']
        ratio = metricas_consolidadas['ratio_sin_asignar']
        color_ratio = "🔴" if ratio > 15 else "🟠" if ratio > 10 else "🟢"
        
        st.metric(
            label="⚠️ Sin Asignar",
            value=f"{sin_asignar:,}",
            delta=f"{ratio}%",
            help="Porcentaje de casos sin asignar sobre total pendientes"
        )
        st.markdown(f"{color_ratio} **{ratio}% del total**")
```

---

## 📊 CÁLCULO DE TENDENCIAS

### Tendencias Reales
```python
def calcular_tendencias_reales(metricas_ccm: dict, metricas_prr: dict) -> dict:
    """
    CALCULA TENDENCIAS COMPARANDO CON PERÍODO ANTERIOR:
    
    MÉTODO:
    1. Leer histórico de sin asignar (historico_sin_asignar.csv)
    2. Comparar valores actuales con última medición
    3. Calcular diferencias (deltas)
    4. Retornar tendencias para KPIs
    """
    try:
        # LEER HISTÓRICO
        if os.path.exists('historico_sin_asignar.csv'):
            df_hist = pd.read_csv('historico_sin_asignar.csv')
            df_hist['Fecha'] = pd.to_datetime(df_hist['Fecha'])
            df_hist = df_hist.sort_values('Fecha')
            
            if len(df_hist) >= 2:
                # COMPARAR CON REGISTRO ANTERIOR
                ultimo = df_hist.iloc[-1]
                anterior = df_hist.iloc[-2]
                
                delta_sin_asignar = int(ultimo['Total_SinAsignar'] - anterior['Total_SinAsignar'])
                
                return {
                    'delta_pendientes': 0,  # No se calcula tendencia de pendientes
                    'delta_trabajados': 0,  # No se calcula tendencia de trabajados
                    'delta_sin_asignar': delta_sin_asignar,
                    'fecha_anterior': anterior['Fecha']
                }
        
        return {'delta_pendientes': 0, 'delta_trabajados': 0, 'delta_sin_asignar': 0}
        
    except Exception as e:
        return {'delta_pendientes': 0, 'delta_trabajados': 0, 'delta_sin_asignar': 0}
```

---

## 📈 GRÁFICOS Y VISUALIZACIONES

### 1. Evolución de Pendientes Histórica
```python
# En dashboard_ejecutivo_visualizaciones.py
def mostrar_evolucion_pendientes_historica():
    """
    GRÁFICO: Evolución histórica de pendientes totales
    
    FUENTE: historico_sin_asignar.csv
    COLUMNAS USADAS: Fecha, Total_SinAsignar
    TIPO: Línea temporal con marcadores
    PERÍODO: Todos los datos disponibles
    """
    if os.path.exists('historico_sin_asignar.csv'):
        df_hist = pd.read_csv('historico_sin_asignar.csv')
        df_hist['Fecha'] = pd.to_datetime(df_hist['Fecha'])
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df_hist['Fecha'],
            y=df_hist['Total_SinAsignar'],
            mode='lines+markers',
            name='Sin Asignar',
            line=dict(color='#ff6b6b', width=3),
            marker=dict(size=8)
        ))
        
        fig.update_layout(
            title="📈 Evolución Histórica - Casos Sin Asignar",
            xaxis_title="Fecha",
            yaxis_title="Cantidad de Casos",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
```

### 2. Evolución Sin Asignar por Proceso
```python
def mostrar_evolucion_sin_asignar():
    """
    GRÁFICO: Evolución separada CCM vs PRR
    
    FUENTE: historico_sin_asignar.csv
    COLUMNAS: Fecha, CCM_SinAsignar, PRR_SinAsignar
    TIPO: Líneas múltiples
    COLORES: CCM=#3498db (azul), PRR=#e74c3c (rojo)
    """
    if os.path.exists('historico_sin_asignar.csv'):
        df_hist = pd.read_csv('historico_sin_asignar.csv')
        df_hist['Fecha'] = pd.to_datetime(df_hist['Fecha'])
        
        fig = go.Figure()
        
        # LÍNEA CCM
        fig.add_trace(go.Scatter(
            x=df_hist['Fecha'],
            y=df_hist['CCM_SinAsignar'],
            mode='lines+markers',
            name='CCM Sin Asignar',
            line=dict(color='#3498db', width=2),
            marker=dict(size=6)
        ))
        
        # LÍNEA PRR
        fig.add_trace(go.Scatter(
            x=df_hist['Fecha'],
            y=df_hist['PRR_SinAsignar'],
            mode='lines+markers',
            name='PRR Sin Asignar',
            line=dict(color='#e74c3c', width=2),
            marker=dict(size=6)
        ))
        
        fig.update_layout(
            title="🔄 Evolución Sin Asignar por Proceso",
            xaxis_title="Fecha",
            yaxis_title="Cantidad",
            height=400,
            legend=dict(orientation="h", yanchor="bottom", y=1.02)
        )
        
        st.plotly_chart(fig, use_container_width=True)
```

### 3. Ingresos vs Trabajados Lineal
```python
def mostrar_ingresos_vs_trabajados_lineal(df_ccm: pd.DataFrame, df_prr: pd.DataFrame):
    """
    GRÁFICO: Comparación ingresos vs trabajados por proceso
    
    CÁLCULO:
    - Ingresos: Últimos 60 días por FechaExpendiente
    - Trabajados: Últimos 20 días por FechaPre
    - Agrupación: Por día
    
    VISUALIZACIÓN:
    - Barras agrupadas por proceso
    - CCM: Azul, PRR: Rojo
    - Eje Y: Cantidad de casos
    """
    # PREPARAR DATOS CCM
    fecha_limite = pd.Timestamp.now() - pd.Timedelta(days=60)
    
    # INGRESOS CCM (últimos 60 días)
    ingresos_ccm = df_ccm[df_ccm['FechaExpendiente'] >= fecha_limite]
    
    # TRABAJADOS CCM (últimos 20 días)
    fecha_trabajo = pd.Timestamp.now() - pd.Timedelta(days=20)
    trabajados_ccm = df_ccm[df_ccm['FechaPre'] >= fecha_trabajo]
    
    # MISMA LÓGICA PARA PRR
    ingresos_prr = df_prr[df_prr['FechaExpendiente'] >= fecha_limite]
    trabajados_prr = df_prr[df_prr['FechaPre'] >= fecha_trabajo]
    
    # CREAR GRÁFICO DE BARRAS
    fig = go.Figure()
    
    # BARRAS CCM
    fig.add_trace(go.Bar(
        name='Ingresos CCM',
        x=['CCM'],
        y=[len(ingresos_ccm)],
        marker_color='lightblue'
    ))
    
    fig.add_trace(go.Bar(
        name='Trabajados CCM',
        x=['CCM'],
        y=[len(trabajados_ccm)],
        marker_color='darkblue'
    ))
    
    # BARRAS PRR
    fig.add_trace(go.Bar(
        name='Ingresos PRR',
        x=['PRR'],
        y=[len(ingresos_prr)],
        marker_color='lightcoral'
    ))
    
    fig.add_trace(go.Bar(
        name='Trabajados PRR',
        x=['PRR'],
        y=[len(trabajados_prr)],
        marker_color='darkred'
    ))
    
    fig.update_layout(
        title="🔄 Ingresos vs Trabajados por Proceso",
        xaxis_title="Proceso",
        yaxis_title="Cantidad de Casos",
        barmode='group',
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)
```

### 4. Tabla Comparativa
```python
def mostrar_tabla_comparativa(metricas_ccm: dict, metricas_prr: dict):
    """
    TABLA: Comparación detallada de métricas por proceso
    
    COLUMNAS:
    - Métrica: Nombre del indicador
    - CCM: Valor para CCM
    - PRR: Valor para PRR
    - Total: Suma de ambos
    
    MÉTRICAS INCLUIDAS:
    - Total Pendientes
    - Trabajados (20d)
    - Ingresos (60d)
    - Sin Asignar
    - Promedio Diario
    """
    # CREAR DATAFRAME COMPARATIVO
    datos_comparacion = {
        'Métrica': [
            'Total Pendientes',
            'Trabajados (20d)',
            'Ingresos (60d)',
            'Sin Asignar',
            'Promedio Diario'
        ],
        'CCM': [
            f"{metricas_ccm['total_pendientes']:,}",
            f"{metricas_ccm['trabajados_20d']:,}",
            f"{metricas_ccm['ingresos_60d']:,}",
            f"{metricas_ccm['sin_asignar']:,}",
            f"{metricas_ccm['promedio_diario']:.1f}"
        ],
        'PRR': [
            f"{metricas_prr['total_pendientes']:,}",
            f"{metricas_prr['trabajados_20d']:,}",
            f"{metricas_prr['ingresos_60d']:,}",
            f"{metricas_prr['sin_asignar']:,}",
            f"{metricas_prr['promedio_diario']:.1f}"
        ],
        'Total': [
            f"{metricas_ccm['total_pendientes'] + metricas_prr['total_pendientes']:,}",
            f"{metricas_ccm['trabajados_20d'] + metricas_prr['trabajados_20d']:,}",
            f"{metricas_ccm['ingresos_60d'] + metricas_prr['ingresos_60d']:,}",
            f"{metricas_ccm['sin_asignar'] + metricas_prr['sin_asignar']:,}",
            f"{(metricas_ccm['trabajados_20d'] + metricas_prr['trabajados_20d']) / 20:.1f}"
        ]
    }
    
    df_comparacion = pd.DataFrame(datos_comparacion)
    
    # MOSTRAR TABLA CON ESTILO
    st.dataframe(
        df_comparacion,
        use_container_width=True,
        hide_index=True
    )
```

---

## 🔄 ACTUALIZACIÓN AUTOMÁTICA DE HISTÓRICOS

### Proceso de Actualización
```python
# En modules/data/historico_sin_asignar.py
def actualizar_historico_sin_asignar(df_ccm: pd.DataFrame, df_prr: pd.DataFrame):
    """
    ACTUALIZACIÓN AUTOMÁTICA AL CARGAR DASHBOARD:
    
    PROCESO:
    1. Calcular métricas actuales
    2. Verificar si ya existe registro para hoy
    3. Si no existe, agregar nueva fila
    4. Guardar archivo actualizado
    
    ESTRUCTURA ARCHIVO:
    - Fecha: YYYY-MM-DD
    - CCM_SinAsignar: Entero
    - PRR_SinAsignar: Entero  
    - Total_SinAsignar: Entero
    """
    from modules.data.loader import procesar_pendientes
    
    # CALCULAR MÉTRICAS ACTUALES
    pendientes_ccm = procesar_pendientes(df_ccm, "CCM")
    pendientes_prr = procesar_pendientes(df_prr, "PRR")
    
    sin_asignar_ccm = len(pendientes_ccm[pendientes_ccm['OPERADOR'] == 'Sin asignar'])
    sin_asignar_prr = len(pendientes_prr[pendientes_prr['OPERADOR'] == 'Sin asignar'])
    total_sin_asignar = sin_asignar_ccm + sin_asignar_prr
    
    # REGISTRO ACTUAL
    fecha_hoy = pd.Timestamp.now().strftime('%Y-%m-%d')
    nuevo_registro = {
        'Fecha': fecha_hoy,
        'CCM_SinAsignar': sin_asignar_ccm,
        'PRR_SinAsignar': sin_asignar_prr,
        'Total_SinAsignar': total_sin_asignar
    }
    
    # ACTUALIZAR ARCHIVO
    archivo = 'historico_sin_asignar.csv'
    
    try:
        if os.path.exists(archivo):
            df_historico = pd.read_csv(archivo)
        else:
            df_historico = pd.DataFrame(columns=['Fecha', 'CCM_SinAsignar', 'PRR_SinAsignar', 'Total_SinAsignar'])
        
        # VERIFICAR SI YA EXISTE REGISTRO PARA HOY
        if fecha_hoy not in df_historico['Fecha'].values:
            # AGREGAR NUEVO REGISTRO
            df_historico = pd.concat([df_historico, pd.DataFrame([nuevo_registro])], ignore_index=True)
            df_historico.to_csv(archivo, index=False)
            st.sidebar.success("✅ Histórico actualizado")
        else:
            st.sidebar.info("ℹ️ Histórico ya actualizado hoy")
            
    except Exception as e:
        st.sidebar.warning(f"⚠️ Error al actualizar histórico: {str(e)}")
```

---

## 📋 RESUMEN DE FUNCIONAMIENTO

### Características Principales
1. **CARGA AUTOMÁTICA**: No requiere selección de proceso, carga ambos automáticamente
2. **MÉTRICAS CONSOLIDADAS**: Suma y consolida métricas de CCM y PRR
3. **ACTUALIZACIÓN HISTÓRICA**: Actualiza archivo CSV automáticamente cada día
4. **KPIs VISUALES**: 4 KPIs principales con colores y tendencias
5. **GRÁFICOS INTERACTIVOS**: 3 gráficos con datos históricos
6. **TABLA COMPARATIVA**: Desglose detallado por proceso

### Flujo de Ejecución
```
1. Carga Dashboard Ejecutivo
   ↓
2. Carga automática CCM + PRR (sin selección usuario)
   ↓  
3. Actualiza historico_sin_asignar.csv
   ↓
4. Calcula métricas exactas por proceso
   ↓
5. Consolida métricas
   ↓
6. Calcula tendencias (si hay histórico)
   ↓
7. Muestra KPIs principales (4 columnas)
   ↓
8. Muestra gráficos de evolución
   ↓
9. Muestra análisis de flujo
   ↓
10. Muestra tabla comparativa final
```

### Archivos Generados/Actualizados
- **historico_sin_asignar.csv**: Actualizado automáticamente cada día con métricas actuales
- **Caché Streamlit**: DataFrames cacheados para optimizar rendimiento 