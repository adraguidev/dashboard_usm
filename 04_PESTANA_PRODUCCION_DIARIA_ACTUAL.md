# 📊 04 - PESTAÑA PRODUCCIÓN DIARIA ACTUAL

## 📝 PROPÓSITO
Documentación técnica completa de la pestaña Producción Diaria que analiza el trabajo realizado en los últimos 20 días, tablas de fines de semana y gráficos de tendencias.

---

## 🔄 FLUJO PRINCIPAL

### Análisis de Últimos 20 Días
```python
# En produccion_diaria.py
def mostrar_produccion_diaria(df: pd.DataFrame, proceso: str) -> None:
    """
    FLUJO PRINCIPAL DE PRODUCCIÓN DIARIA:
    
    1. Determinar columnas según disponibilidad
    2. Filtrar últimos 20 días de trabajo (FechaPre)
    3. Crear tabla dinámica principal
    4. Aplicar filtros y ordenamiento
    5. Mostrar tabla con colores por sub-equipo
    6. Tabla de fines de semana (últimas 5 semanas)
    7. Resumen diario con 3 descargas Excel
    8. 3 gráficos de análisis de tendencias
    """
    st.header("Producción Diaria")
    
    # DETERMINAR COLUMNAS DISPONIBLES
    col_operador = 'OperadorPre' if 'OperadorPre' in df.columns else 'OPERADOR'
    col_fecha = 'FechaPre'  # SIEMPRE fecha de procesamiento
    col_tramite = 'NumeroTramite'
    
    # PREPARAR FECHAS
    if not pd.api.types.is_datetime64_any_dtype(df[col_fecha]):
        df[col_fecha] = pd.to_datetime(df[col_fecha], errors='coerce')
    
    # FILTRAR ÚLTIMOS 20 DÍAS
    fechas_ordenadas = df[col_fecha].dropna().sort_values().unique()
    ultimos_20_dias = fechas_ordenadas[-20:]  # Las 20 fechas más recientes
    df_20dias = df[df[col_fecha].isin(ultimos_20_dias)]
```

---

## 📊 TABLA PRINCIPAL DE PRODUCCIÓN

### Creación de Tabla Dinámica
```python
def _crear_tabla_produccion(df_20dias: pd.DataFrame, col_operador: str, 
                          col_fecha: str, col_tramite: str) -> pd.DataFrame:
    """
    TABLA DINÁMICA: OPERADOR x FECHA (Últimos 20 días)
    
    ESTRUCTURA:
    - Filas: Operadores (OperadorPre o OPERADOR)
    - Columnas: Fechas de procesamiento (últimos 20 días)
    - Valores: COUNT de NumeroTramite (casos trabajados)
    - Totales: margins=True, margins_name='Total'
    
    RESULTADO: Tabla con cantidad de casos trabajados por operador por día
    """
    return pd.pivot_table(
        df_20dias,
        index=col_operador,        # Filas: Operadores
        columns=col_fecha,         # Columnas: Fechas
        values=col_tramite,        # Valores: Número de trámites
        aggfunc='count',           # Función: Contar casos
        fill_value=0,              # Llenar vacíos con 0
        margins=True,              # Agregar totales
        margins_name='Total'       # Nombre de fila/columna total
    )
```

### Filtrado y Procesamiento
```python
def _filtrar_tabla_produccion(tabla_prod: pd.DataFrame) -> pd.DataFrame:
    """
    APLICAR FILTROS A TABLA DE PRODUCCIÓN:
    
    OPERADORES EXCLUIDOS (MISMOS PARA CCM Y PRR):
    - "Aponte Sanchez, Paola Lita"
    - "Lucero Martinez, Carlos Martin" 
    - "USUARIO DE AGENCIA DIGITAL"
    
    UMBRAL MÍNIMO: >= 5 casos trabajados en total
    
    PROCESAMIENTO:
    1. Excluir operadores de la lista
    2. Filtrar operadores con menos de 5 casos totales
    3. Recalcular fila 'Total' tras filtros
    4. Formatear fechas de columnas (DD/MM/YYYY)
    5. Ordenar por Total descendente
    """
    operadores_excluir = [
        "Aponte Sanchez, Paola Lita", 
        "Lucero Martinez, Carlos Martin", 
        "USUARIO DE AGENCIA DIGITAL"
    ]
    
    # EXCLUIR OPERADORES
    if 'Total' in tabla_prod.index:
        tabla_filtrada = tabla_prod.drop(operadores_excluir, errors='ignore')
        if tabla_filtrada.shape[0] > 1:
            # APLICAR UMBRAL MÍNIMO (excepto fila Total)
            tabla_filtrada = tabla_filtrada[
                (tabla_filtrada['Total'] >= 5) | (tabla_filtrada.index == 'Total')
            ]
    else:
        tabla_filtrada = tabla_prod.drop(operadores_excluir, errors='ignore')
        tabla_filtrada = tabla_filtrada[tabla_filtrada['Total'] >= 5]

    # RECALCULAR FILA TOTAL
    tabla_sin_total = tabla_filtrada.drop('Total', errors='ignore')
    total_row = tabla_sin_total.sum(numeric_only=True)
    total_row.name = 'Total'
    tabla_filtrada_corr = pd.concat([tabla_sin_total, pd.DataFrame([total_row])])
    
    # FORMATEAR FECHAS DE COLUMNAS
    fechas_formateadas = [
        f.strftime('%d/%m/%Y') if not isinstance(f, str) and f != 'Total' else f 
        for f in tabla_filtrada_corr.columns
    ]
    tabla_filtrada_corr.columns = fechas_formateadas
    
    # ORDENAR POR TOTAL DESCENDENTE
    if 'Total' in tabla_filtrada_corr.index:
        tabla_sin_total = tabla_filtrada_corr.drop('Total')
        tabla_sin_total = tabla_sin_total.sort_values(by='Total', ascending=False)
        tabla_filtrada_corr = pd.concat([tabla_sin_total, tabla_filtrada_corr.loc[['Total']]])
    else:
        tabla_filtrada_corr = tabla_filtrada_corr.sort_values(by='Total', ascending=False)
    
    return tabla_filtrada_corr
```

---

## 🎨 SISTEMA DE COLORES

### Aplicación de Colores por Sub-Equipo
```python
def _aplicar_colores_tabla(tabla: pd.DataFrame, base_evaluadores: pd.DataFrame):
    """
    APLICA COLORES SEGÚN SUB-EQUIPO DEL EVALUADOR:
    
    COLORES ESPECÍFICOS:
    - SUB-EQUIPO 1: #90EE90 (Verde claro)
    - SUB-EQUIPO 2: #FFB347 (Naranja claro)
    - SUB-EQUIPO 3: #87CEEB (Azul cielo)
    - SUB-EQUIPO 4: #DDA0DD (Ciruela)
    - SUB-EQUIPO 5: #F0E68C (Caqui)
    - SUB-EQUIPO 6: #FFA07A (Salmón claro)
    - OTROS: #FFFFFF (Blanco)
    - NO EN BASE: #D3D3D3 (Gris claro)
    
    LÓGICA:
    1. Crear mapa operador → sub-equipo
    2. Para cada fila, buscar sub-equipo del operador
    3. Aplicar color correspondiente a toda la fila
    4. NO colorear fila 'Total'
    """
    if base_evaluadores.empty:
        return tabla.style
    
    # CREAR MAPA OPERADOR → SUB-EQUIPO
    mapa_subequipos = dict(zip(base_evaluadores['OPERADOR'], base_evaluadores['SUB-EQUIPO']))
    
    def colorear_fila(row):
        # NO COLOREAR FILA "Total"
        if row.name == 'Total':
            return [''] * len(row)
        
        operador = str(row.name)
        subequipo = mapa_subequipos.get(operador, 'OTROS')
        
        # MAPEO DE COLORES
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
    
    return tabla.style.apply(colorear_fila, axis=1)
```

### Leyenda de Colores
```python
def _mostrar_leyenda_colores(base_evaluadores: pd.DataFrame) -> None:
    """
    MUESTRA LEYENDA DE COLORES:
    
    LAYOUT: 4 columnas con colores y etiquetas
    - Verde: SUB-EQUIPO 1
    - Naranja: SUB-EQUIPO 2  
    - Azul: SUB-EQUIPO 3
    - Ciruela: SUB-EQUIPO 4
    - Caqui: SUB-EQUIPO 5
    - Salmón: SUB-EQUIPO 6
    - Blanco: OTROS
    - Gris: INACTIVOS
    """
    st.markdown("### 📋 Leyenda de Colores")
    
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
        st.markdown('<div style="background-color: #FFFFFF; border: 1px solid #ccc; padding: 5px; border-radius: 5px; text-align: center;">OTROS</div>', unsafe_allow_html=True)
        st.markdown('<div style="background-color: #D3D3D3; padding: 5px; border-radius: 5px; text-align: center;">INACTIVOS</div>', unsafe_allow_html=True)
```

---

## 📅 TABLA DE FINES DE SEMANA

### Producción Fines de Semana (Últimas 5 Semanas)
```python
def _mostrar_tabla_fines_semana(df: pd.DataFrame, col_operador: str, col_fecha: str, 
                               col_tramite: str, proceso: str, base_evaluadores: pd.DataFrame) -> None:
    """
    TABLA ESPECÍFICA PARA FINES DE SEMANA:
    
    PERÍODO: Últimas 5 semanas desde fecha máxima
    DÍAS INCLUIDOS: Sábados (weekday=5) y Domingos (weekday=6)
    
    PROCESO:
    1. Calcular rango de 5 semanas hacia atrás
    2. Filtrar solo sábados y domingos
    3. Crear tabla dinámica Operador x Fecha
    4. Aplicar mismos filtros que tabla principal
    5. Aplicar colores por sub-equipo
    6. Proporcionar descarga Excel específica
    """
    st.subheader("Producción Fines de Semana (Últimas 5 semanas)")
    
    # CALCULAR RANGO DE 5 SEMANAS
    fecha_max = df[col_fecha].max()
    fecha_min = fecha_max - pd.Timedelta(weeks=5)
    df_5sem = df[(df[col_fecha] >= fecha_min) & (df[col_fecha] <= fecha_max)]
    
    # FILTRAR SOLO SÁBADOS (5) Y DOMINGOS (6)
    df_5sem = df_5sem[df_5sem[col_fecha].dt.weekday.isin([5, 6])]
    
    # CREAR TABLA DINÁMICA
    tabla_weekend = pd.pivot_table(
        df_5sem,
        index=col_operador,
        columns=col_fecha,
        values=col_tramite,
        aggfunc='count',
        fill_value=0,
        margins=True,
        margins_name='Total'
    )
    
    # APLICAR MISMOS FILTROS QUE TABLA PRINCIPAL
    operadores_excluir = [
        "Aponte Sanchez, Paola Lita", 
        "Lucero Martinez, Carlos Martin", 
        "USUARIO DE AGENCIA DIGITAL"
    ]
    
    if 'Total' in tabla_weekend.index:
        tabla_weekend_filtrada = tabla_weekend.drop(operadores_excluir, errors='ignore')
        if tabla_weekend_filtrada.shape[0] > 1:
            tabla_weekend_filtrada = tabla_weekend_filtrada[
                (tabla_weekend_filtrada['Total'] >= 5) | (tabla_weekend_filtrada.index == 'Total')
            ]
    else:
        tabla_weekend_filtrada = tabla_weekend.drop(operadores_excluir, errors='ignore')
        tabla_weekend_filtrada = tabla_weekend_filtrada[tabla_weekend_filtrada['Total'] >= 5]
    
    # RECALCULAR TOTALES Y FORMATEAR
    tabla_sin_total_w = tabla_weekend_filtrada.drop('Total', errors='ignore')
    total_row_w = tabla_sin_total_w.sum(numeric_only=True)
    total_row_w.name = 'Total'
    tabla_weekend_filtrada_corr = pd.concat([tabla_sin_total_w, pd.DataFrame([total_row_w])])
    
    # FORMATEAR FECHAS
    fechas_formateadas_w = [
        f.strftime('%d/%m/%Y') if not isinstance(f, str) and f != 'Total' else f 
        for f in tabla_weekend_filtrada_corr.columns
    ]
    tabla_weekend_filtrada_corr.columns = fechas_formateadas_w
    
    # ORDENAR POR TOTAL
    if 'Total' in tabla_weekend_filtrada_corr.index:
        tabla_sin_total_w = tabla_weekend_filtrada_corr.drop('Total')
        tabla_sin_total_w = tabla_sin_total_w.sort_values(by='Total', ascending=False)
        tabla_weekend_filtrada_corr = pd.concat([tabla_sin_total_w, tabla_weekend_filtrada_corr.loc[['Total']]])
    else:
        tabla_weekend_filtrada_corr = tabla_weekend_filtrada_corr.sort_values(by='Total', ascending=False)

    # APLICAR COLORES Y MOSTRAR
    tabla_weekend_styled = _aplicar_colores_tabla(tabla_weekend_filtrada_corr, base_evaluadores)
    st.dataframe(tabla_weekend_styled, use_container_width=True)
    
    # DESCARGA EXCEL ESPECÍFICA
    excel_data_weekend = to_excel_with_format_weekend(tabla_weekend_filtrada_corr)
    st.download_button(
        label="Descargar tabla de Fines de Semana en Excel",
        data=excel_data_weekend,
        file_name=f"fines_semana_{proceso}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
```

---

## 📈 RESUMEN DIARIO

### Cálculo de Métricas Diarias
```python
def _mostrar_resumen_diario(df_20dias: pd.DataFrame, col_operador: str, col_fecha: str, 
                          col_tramite: str, proceso: str) -> None:
    """
    RESUMEN DIARIO CON MÉTRICAS AGREGADAS:
    
    CÁLCULOS POR DÍA:
    1. Cantidad de operadores únicos activos
    2. Total de trámites trabajados
    3. Promedio de trámites por operador
    
    FILTROS APLICADOS:
    - Excluir mismos operadores que tabla principal
    - Solo operadores con >= 5 casos totales
    
    RESULTADO: Tabla con métricas diarias + descarga Excel
    """
    st.subheader("Resumen Diario")
    
    # APLICAR FILTROS
    operadores_excluir_resumen = [
        "Aponte Sanchez, Paola Lita", 
        "Lucero Martinez, Carlos Martin", 
        "USUARIO DE AGENCIA DIGITAL"
    ]
    
    df_resumen = df_20dias[~df_20dias[col_operador].isin(operadores_excluir_resumen)].copy()
    
    # FILTRAR OPERADORES CON >= 5 CASOS TOTALES
    totales_operador = df_resumen.groupby(col_operador)[col_tramite].count()
    operadores_validos = totales_operador[totales_operador >= 5].index
    df_resumen = df_resumen[df_resumen[col_operador].isin(operadores_validos)]
    
    # CALCULAR MÉTRICAS POR DÍA
    resumen = df_resumen.groupby(col_fecha).agg(
        cantidad_operadores=(col_operador, lambda x: x.nunique()),  # Operadores únicos
        total_trabajados=(col_tramite, 'count')                     # Total trámites
    )
    resumen = resumen.sort_index()
    
    # CALCULAR PROMEDIO POR OPERADOR
    resumen['promedio_por_operador'] = resumen['total_trabajados'] / resumen['cantidad_operadores']
    
    # FORMATEAR FECHAS DEL ÍNDICE
    resumen.index = [f.strftime('%d/%m/%Y') if not isinstance(f, str) else f for f in resumen.index]
    
    # RENOMBRAR COLUMNAS PARA MEJOR VISUALIZACIÓN
    resumen.columns = ['Cantidad Operadores', 'Total Trabajados', 'Promedio por Operador']
    
    # MOSTRAR TABLA
    st.dataframe(resumen, use_container_width=True)
    
    # DESCARGA EXCEL
    excel_data_resumen = to_excel_resumen(resumen)
    st.download_button(
        label="Descargar resumen diario en Excel",
        data=excel_data_resumen,
        file_name=f"resumen_diario_{proceso}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
```

---

## 📊 GRÁFICOS DE ANÁLISIS

### 1. Gráfico Días Hábiles (Lunes a Viernes)
```python
def _crear_grafico_dias_habiles(resumen: pd.DataFrame) -> None:
    """
    GRÁFICO: Promedio diario por operador (L-V)
    
    DATOS:
    - Eje X: Fechas (solo lunes a viernes, weekday < 5)
    - Eje Y: Promedio de trámites por operador
    - Línea principal: Valores reales con marcadores
    - Línea tendencia: Regresión lineal (línea punteada naranja)
    - Etiquetas: Valores numéricos en cada punto
    
    CARACTERÍSTICAS:
    - Filtro automático de días hábiles
    - Línea de tendencia calculada con np.polyfit
    - Hover interactivo unificado
    """
    st.subheader("Gráfica: Promedio Diario por Operador (Lunes a Viernes)")
    
    # FILTRAR DÍAS HÁBILES
    resumen_graf_habiles = resumen.copy()
    resumen_graf_habiles.index = pd.to_datetime(resumen_graf_habiles.index, format='%d/%m/%Y')
    dias_habiles = resumen_graf_habiles.index.weekday < 5  # 0=Lunes, 4=Viernes
    resumen_graf_habiles = resumen_graf_habiles[dias_habiles]
    
    # CREAR GRÁFICO
    fig_habiles = go.Figure()
    
    # LÍNEA PRINCIPAL CON DATOS
    fig_habiles.add_trace(go.Scatter(
        x=resumen_graf_habiles.index,
        y=resumen_graf_habiles['promedio_por_operador'],
        mode='lines+markers+text',
        name='Promedio por Operador (L-V)',
        text=[f"{v:.1f}" for v in resumen_graf_habiles['promedio_por_operador']],
        textposition="top center"
    ))
    
    # LÍNEA DE TENDENCIA
    x_numeric = np.arange(len(resumen_graf_habiles.index))
    y = resumen_graf_habiles['promedio_por_operador'].values
    if len(x_numeric) > 1:
        z = np.polyfit(x_numeric, y, 1)  # Regresión lineal
        tendencia = z[0] * x_numeric + z[1]
        fig_habiles.add_trace(go.Scatter(
            x=resumen_graf_habiles.index,
            y=tendencia,
            mode='lines',
            name='Tendencia',
            line=dict(dash='dash', color='orange')
        ))
    
    # CONFIGURACIÓN DEL GRÁFICO
    fig_habiles.update_layout(
        title='Promedio Diario de Trámites por Operador (Lunes a Viernes)',
        xaxis_title='Fecha',
        yaxis_title='Promedio por Operador',
        legend_title='Métrica',
        hovermode='x unified'
    )
    st.plotly_chart(fig_habiles, use_container_width=True)
```

### 2. Gráfico Fines de Semana (Sábado y Domingo)
```python
def _crear_grafico_fines_semana(resumen: pd.DataFrame) -> None:
    """
    GRÁFICO: Promedio diario por operador (S-D)
    
    DATOS:
    - Eje X: Fechas (solo sábados y domingos, weekday >= 5)
    - Eje Y: Promedio de trámites por operador
    - Misma estructura que gráfico días hábiles
    - Línea de tendencia independiente
    
    DIFERENCIAS:
    - Filtro para weekday >= 5 (5=Sábado, 6=Domingo)
    - Datos típicamente más dispersos que días hábiles
    """
    st.subheader("Gráfica: Promedio Diario por Operador (Fines de Semana)")
    
    # FILTRAR FINES DE SEMANA
    resumen_graf_fds = resumen.copy()
    resumen_graf_fds.index = pd.to_datetime(resumen_graf_fds.index, format='%d/%m/%Y')
    dias_fds = resumen_graf_fds.index.weekday >= 5  # 5=Sábado, 6=Domingo
    resumen_graf_fds = resumen_graf_fds[dias_fds]
    
    # CREAR GRÁFICO (misma estructura que días hábiles)
    fig_fds = go.Figure()
    
    fig_fds.add_trace(go.Scatter(
        x=resumen_graf_fds.index,
        y=resumen_graf_fds['promedio_por_operador'],
        mode='lines+markers+text',
        name='Promedio por Operador (S-D)',
        text=[f"{v:.1f}" for v in resumen_graf_fds['promedio_por_operador']],
        textposition="top center"
    ))
    
    # LÍNEA DE TENDENCIA PARA FINES DE SEMANA
    x_numeric_fds = np.arange(len(resumen_graf_fds.index))
    y_fds = resumen_graf_fds['promedio_por_operador'].values
    if len(x_numeric_fds) > 1:
        z_fds = np.polyfit(x_numeric_fds, y_fds, 1)
        tendencia_fds = z_fds[0] * x_numeric_fds + z_fds[1]
        fig_fds.add_trace(go.Scatter(
            x=resumen_graf_fds.index,
            y=tendencia_fds,
            mode='lines',
            name='Tendencia',
            line=dict(dash='dash', color='orange')
        ))
    
    fig_fds.update_layout(
        title='Promedio Diario de Trámites por Operador (Fines de Semana)',
        xaxis_title='Fecha',
        yaxis_title='Promedio por Operador',
        legend_title='Métrica',
        hovermode='x unified'
    )
    st.plotly_chart(fig_fds, use_container_width=True)
```

### 3. Gráfico Total de Trámites Diarios
```python
def _crear_grafico_total_tramites(resumen: pd.DataFrame) -> None:
    """
    GRÁFICO: Total de trámites diarios
    
    DATOS:
    - Eje X: Fechas (todos los días de la semana)
    - Eje Y: Total de trámites trabajados por día
    - Línea principal: Total diario con marcadores
    - Línea tendencia: Regresión lineal general
    - Etiquetas: Valores enteros en cada punto
    
    PROPÓSITO:
    - Ver volumen total de trabajo diario
    - Identificar días de mayor/menor actividad
    - Tendencia general de productividad
    """
    st.subheader("Gráfica: Total de Trámites Diarios")
    
    # PREPARAR DATOS (todos los días)
    resumen_graf_total = resumen.copy()
    resumen_graf_total.index = pd.to_datetime(resumen_graf_total.index, format='%d/%m/%Y')
    
    # CREAR GRÁFICO
    fig_total = go.Figure()
    
    # LÍNEA DE TOTAL DE TRÁMITES
    fig_total.add_trace(go.Scatter(
        x=resumen_graf_total.index,
        y=resumen_graf_total['total_trabajados'],
        mode='lines+markers+text',
        name='Total de Trámites',
        text=[str(v) for v in resumen_graf_total['total_trabajados']],  # Enteros como texto
        textposition="top center"
    ))
    
    # LÍNEA DE TENDENCIA GENERAL
    x_numeric_total = np.arange(len(resumen_graf_total.index))
    y_total = resumen_graf_total['total_trabajados'].values
    if len(x_numeric_total) > 1:
        z_total = np.polyfit(x_numeric_total, y_total, 1)
        tendencia_total = z_total[0] * x_numeric_total + z_total[1]
        fig_total.add_trace(go.Scatter(
            x=resumen_graf_total.index,
            y=tendencia_total,
            mode='lines',
            name='Tendencia',
            line=dict(dash='dash', color='orange')
        ))
    
    fig_total.update_layout(
        title='Total de Trámites Diarios',
        xaxis_title='Fecha',
        yaxis_title='Total de Trámites',
        legend_title='Métrica',
        hovermode='x unified'
    )
    st.plotly_chart(fig_total, use_container_width=True)
```

---

## 📤 SISTEMA DE DESCARGAS

### Tres Tipos de Descarga Excel
```python
def sistema_descargas_excel():
    """
    TRES DESCARGAS INDEPENDIENTES:
    
    1. DESCARGA TABLA PRINCIPAL:
       - Archivo: produccion_diaria_{proceso}.xlsx
       - Contenido: Tabla operador x fecha (últimos 20 días)
       - Función: to_excel_with_format_prod()
    
    2. DESCARGA FINES DE SEMANA:
       - Archivo: fines_semana_{proceso}.xlsx
       - Contenido: Tabla operador x fecha (solo sáb/dom, 5 semanas)
       - Función: to_excel_with_format_weekend()
    
    3. DESCARGA RESUMEN DIARIO:
       - Archivo: resumen_diario_{proceso}.xlsx
       - Contenido: Métricas agregadas por día
       - Función: to_excel_resumen()
    """
    
    # DESCARGA 1: Tabla principal
    excel_data_prod = to_excel_with_format_prod(tabla_filtrada_corr)
    st.download_button(
        label="Descargar tabla de Producción Diaria en Excel",
        data=excel_data_prod,
        file_name=f"produccion_diaria_{proceso}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    
    # DESCARGA 2: Fines de semana (en sección correspondiente)
    excel_data_weekend = to_excel_with_format_weekend(tabla_weekend_filtrada_corr)
    st.download_button(
        label="Descargar tabla de Fines de Semana en Excel",
        data=excel_data_weekend,
        file_name=f"fines_semana_{proceso}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    
    # DESCARGA 3: Resumen diario (en sección correspondiente)
    excel_data_resumen = to_excel_resumen(resumen)
    st.download_button(
        label="Descargar resumen diario en Excel",
        data=excel_data_resumen,
        file_name=f"resumen_diario_{proceso}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
```

---

## 📋 RESUMEN DE FUNCIONAMIENTO

### Características Principales
1. **PERÍODO ANÁLISIS**: Últimos 20 días de fechas de trabajo (FechaPre)
2. **TABLA PRINCIPAL**: Operador x Fecha con casos trabajados
3. **TABLA FINES SEMANA**: Solo sábados/domingos de últimas 5 semanas
4. **FILTROS APLICADOS**: Excluir 3 operadores específicos + umbral >= 5 casos
5. **COLORES POR SUB-EQUIPO**: Mismo sistema que otras pestañas
6. **RESUMEN DIARIO**: Métricas agregadas por día con promedios
7. **3 GRÁFICOS**: Días hábiles, fines semana y total diario con tendencias
8. **3 DESCARGAS EXCEL**: Una por cada sección principal

### Diferencias con Otras Pestañas
- **FECHA USADA**: FechaPre (fecha de trabajo) NO FechaExpendiente
- **COLUMNA OPERADOR**: Prioriza 'OperadorPre' sobre 'OPERADOR'
- **PERÍODO FIJO**: Siempre últimos 20 días (no configurable)
- **FINES DE SEMANA**: Análisis específico de sáb/dom
- **GRÁFICOS MÚLTIPLES**: 3 gráficos con tendencias automáticas

### Flujo de Ejecución
```
1. Determinar columnas disponibles (OperadorPre vs OPERADOR)
   ↓
2. Filtrar últimos 20 días de FechaPre
   ↓
3. Crear tabla dinámica principal Operador x Fecha
   ↓
4. Aplicar filtros (operadores excluidos + umbral >= 5)
   ↓
5. Recalcular totales y formatear fechas
   ↓
6. Aplicar colores por sub-equipo y mostrar
   ↓
7. Crear tabla fines de semana (5 semanas, solo sáb/dom)
   ↓
8. Crear resumen diario con métricas agregadas
   ↓
9. Generar 3 gráficos con tendencias
   ↓
10. Proporcionar 3 descargas Excel independientes
```

### Operadores Excluidos (Todos los Procesos)
- "Aponte Sanchez, Paola Lita"
- "Lucero Martinez, Carlos Martin"
- "USUARIO DE AGENCIA DIGITAL"

**NOTA**: En Producción Diaria NO se excluye "MAURICIO ROMERO, HUGO" (diferencia con Pendientes) 