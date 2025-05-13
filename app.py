import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import io
from openpyxl.styles import Font, PatternFill
from openpyxl.utils import get_column_letter
import plotly.figure_factory as ff
from numpy import polyfit, arange
import numpy as np

# Configuración de la página
st.set_page_config(
    page_title="Dashboard de Procesos",
    page_icon="📊",
    layout="wide"
)

# Título principal
st.title("Dashboard de Análisis de Procesos")

# Función para cargar los datos
@st.cache_data
def cargar_datos(archivo):
    return pd.read_excel(f"ARCHIVOS/{archivo}")

# Sidebar para selección de proceso
proceso = st.sidebar.selectbox(
    "Seleccione el Proceso",
    ["CCM", "PRR"]
)

# Mapeo de archivos
archivos = {
    "CCM": "consolidado_final_CCM_personal.xlsx",
    "PRR": "consolidado_final_PRR_personal.xlsx"
}

# Cargar datos según el proceso seleccionado
try:
    df = cargar_datos(archivos[proceso])
    
    # Crear pestañas para diferentes análisis
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Pendientes", 
        "Producción Diaria", 
        "Ingresos Diarios",
        "Tiempos de Asignación y Pretrabajo",
        "Proyección de Cierre"
    ])
    
    with tab1:
        st.header("Pendientes CCM" if proceso == "CCM" else "Pendientes PRR")
        
        # Definir filtros según el proceso
        if proceso == "CCM":
            df_filtrado = df[
                (df['UltimaEtapa'] == 'EVALUACIÓN - I') &
                (df['EstadoPre'].isna()) &
                (df['EstadoTramite'] == 'PENDIENTE') &
                (df['EQUIPO'] != 'VULNERABLE')
            ]
        else:
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
            df_filtrado = df[
                (df['UltimaEtapa'].isin(etapas_prr)) &
                (df['EstadoPre'].isna()) &
                (df['EstadoTramite'] == 'PENDIENTE') &
                (df['EQUIPO'] != 'VULNERABLE')
            ]

        # Reemplazar nulos en OPERADOR por 'Sin asignar'
        df_filtrado['OPERADOR'] = df_filtrado['OPERADOR'].fillna('Sin asignar')

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
        # Excluir operadores específicos en CCM y Sin asignar en PRR
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
        # Mostrar tabla
        st.dataframe(tabla, use_container_width=True, height=500)
        # Mostrar el total de "Sin asignar" solo para los últimos 2 años
        anios = sorted(df_filtrado['Anio'].dropna().unique())
        ultimos_2_anios = anios[-2:] if len(anios) >= 2 else anios
        if proceso == "CCM":
            total_sin_asignar = df_filtrado[
                (df_filtrado['OPERADOR'] == 'Sin asignar') &
                (df_filtrado['Anio'].isin(ultimos_2_anios))
            ]['NumeroTramite'].count()
            st.metric("Sin asignar (últimos 2 años)", total_sin_asignar)
        elif proceso == "PRR":
            total_sin_asignar = df_filtrado[
                (df_filtrado['OPERADOR'] == 'Sin asignar') &
                (df_filtrado['Anio'].isin(ultimos_2_anios))
            ]['NumeroTramite'].count()
            st.metric("Sin asignar (últimos 2 años)", total_sin_asignar)
        
        # Botón para descargar Excel con formato
        def to_excel_with_format(tabla):
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                tabla.to_excel(writer, sheet_name='Pendientes')
                ws = writer.sheets['Pendientes']
                # Resaltar fila Total
                total_row = ws.max_row
                for col in range(1, ws.max_column + 1):
                    ws.cell(row=total_row, column=col).font = Font(bold=True)
                    ws.cell(row=total_row, column=col).fill = PatternFill(start_color='FFFF00', end_color='FFFF00', fill_type='solid')
                # Resaltar columna Total
                total_col = ws.max_column
                for row in range(2, ws.max_row + 1):
                    ws.cell(row=row, column=total_col).font = Font(bold=True)
                    ws.cell(row=row, column=total_col).fill = PatternFill(start_color='FFFF00', end_color='FFFF00', fill_type='solid')
            output.seek(0)
            return output

        excel_data = to_excel_with_format(tabla)
        st.download_button(
            label="Descargar tabla en Excel",
            data=excel_data,
            file_name=f"pendientes_{proceso}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    with tab2:
        st.header("Producción Diaria")
        # Determinar nombres de columnas según proceso
        col_operador = 'OperadorPre'
        col_fecha = 'FechaPre'
        col_tramite = 'NumeroTramite'
        if col_operador not in df.columns:
            col_operador = 'OPERADOR'  # fallback por si acaso
        if col_fecha not in df.columns:
            col_fecha = 'FechaPre'  # fallback
        # Filtrar últimos 20 días
        if pd.api.types.is_datetime64_any_dtype(df[col_fecha]):
            fechas_ordenadas = df[col_fecha].dropna().sort_values().unique()
        else:
            df[col_fecha] = pd.to_datetime(df[col_fecha], errors='coerce')
            fechas_ordenadas = df[col_fecha].dropna().sort_values().unique()
        ultimos_20 = fechas_ordenadas[-20:]
        df_20dias = df[df[col_fecha].isin(ultimos_20)]
        # Crear tabla dinámica
        tabla_prod = pd.pivot_table(
            df_20dias,
            index=col_operador,
            columns=col_fecha,
            values=col_tramite,
            aggfunc='count',
            fill_value=0,
            margins=True,
            margins_name='Total'
        )
        # Excluir operadores específicos y aquellos con total menor a 5
        operadores_excluir = ["Aponte Sanchez, Paola Lita", "Lucero Martinez, Carlos Martin", "USUARIO DE AGENCIA DIGITAL"]
        if 'Total' in tabla_prod.index:
            tabla_filtrada = tabla_prod.drop(operadores_excluir, errors='ignore')
            # Excluir filas con total menor a 5 (excepto la fila Total)
            if tabla_filtrada.shape[0] > 1:
                tabla_filtrada = tabla_filtrada[ (tabla_filtrada['Total'] >= 5) | (tabla_filtrada.index == 'Total') ]
        else:
            tabla_filtrada = tabla_prod.drop(operadores_excluir, errors='ignore')
            tabla_filtrada = tabla_filtrada[tabla_filtrada['Total'] >= 5]

        # Recalcular la fila Total después de filtrar y ordenar (Producción Diaria)
        tabla_sin_total = tabla_filtrada.drop('Total', errors='ignore')
        total_row = tabla_sin_total.sum(numeric_only=True)
        total_row.name = 'Total'
        tabla_filtrada_corr = pd.concat([tabla_sin_total, pd.DataFrame([total_row])])
        # Formatear las fechas de las columnas al formato dd/mm/YYYY
        fechas_formateadas = [f.strftime('%d/%m/%Y') if not isinstance(f, str) and f != 'Total' else f for f in tabla_filtrada_corr.columns]
        tabla_filtrada_corr.columns = fechas_formateadas
        # Ordenar por Total descendente, dejando la fila 'Total' al final (Producción Diaria)
        if 'Total' in tabla_filtrada_corr.index:
            tabla_sin_total = tabla_filtrada_corr.drop('Total')
            tabla_sin_total = tabla_sin_total.sort_values(by='Total', ascending=False)
            tabla_filtrada_corr = pd.concat([tabla_sin_total, tabla_filtrada_corr.loc[['Total']]])
        else:
            tabla_filtrada_corr = tabla_filtrada_corr.sort_values(by='Total', ascending=False)

        st.dataframe(tabla_filtrada_corr, use_container_width=True, height=500)

        # Botón para descargar Excel con formato (Producción Diaria)
        def to_excel_with_format_prod(tabla):
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                tabla.to_excel(writer, sheet_name='ProduccionDiaria')
                ws = writer.sheets['ProduccionDiaria']
                # Resaltar fila Total
                total_row = ws.max_row
                for col in range(1, ws.max_column + 1):
                    ws.cell(row=total_row, column=col).font = Font(bold=True)
                    ws.cell(row=total_row, column=col).fill = PatternFill(start_color='FFFF00', end_color='FFFF00', fill_type='solid')
                # Resaltar columna Total
                total_col = ws.max_column
                for row in range(2, ws.max_row + 1):
                    ws.cell(row=row, column=total_col).font = Font(bold=True)
                    ws.cell(row=row, column=total_col).fill = PatternFill(start_color='FFFF00', end_color='FFFF00', fill_type='solid')
            output.seek(0)
            return output
        excel_data_prod = to_excel_with_format_prod(tabla_filtrada_corr)
        st.download_button(
            label="Descargar tabla de Producción Diaria en Excel",
            data=excel_data_prod,
            file_name=f"produccion_diaria_{proceso}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        # --- Tabla de fines de semana (últimas 5 semanas) ---
        st.subheader("Producción Fines de Semana (Últimas 5 semanas)")
        # Calcular el rango de fechas de las últimas 5 semanas
        fecha_max = df[col_fecha].max()
        fecha_min = fecha_max - pd.Timedelta(weeks=5)
        df_5sem = df[(df[col_fecha] >= fecha_min) & (df[col_fecha] <= fecha_max)]
        # Filtrar solo sábados (5) y domingos (6)
        df_5sem = df_5sem[df_5sem[col_fecha].dt.weekday.isin([5, 6])]
        # Crear tabla dinámica
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
        # Excluir operadores específicos y totales menores a 5
        if 'Total' in tabla_weekend.index:
            tabla_weekend_filtrada = tabla_weekend.drop(operadores_excluir, errors='ignore')
            if tabla_weekend_filtrada.shape[0] > 1:
                tabla_weekend_filtrada = tabla_weekend_filtrada[(tabla_weekend_filtrada['Total'] >= 5) | (tabla_weekend_filtrada.index == 'Total')]
        else:
            tabla_weekend_filtrada = tabla_weekend.drop(operadores_excluir, errors='ignore')
            tabla_weekend_filtrada = tabla_weekend_filtrada[tabla_weekend_filtrada['Total'] >= 5]
        # Recalcular la fila Total después de filtrar y ordenar (Fines de Semana)
        tabla_sin_total_w = tabla_weekend_filtrada.drop('Total', errors='ignore')
        total_row_w = tabla_sin_total_w.sum(numeric_only=True)
        total_row_w.name = 'Total'
        tabla_weekend_filtrada_corr = pd.concat([tabla_sin_total_w, pd.DataFrame([total_row_w])])
        # Formatear las fechas de las columnas al formato dd/mm/YYYY
        fechas_formateadas_w = [f.strftime('%d/%m/%Y') if not isinstance(f, str) and f != 'Total' else f for f in tabla_weekend_filtrada_corr.columns]
        tabla_weekend_filtrada_corr.columns = fechas_formateadas_w
        # Ordenar por Total descendente, dejando la fila 'Total' al final (Fines de Semana)
        if 'Total' in tabla_weekend_filtrada_corr.index:
            tabla_sin_total_w = tabla_weekend_filtrada_corr.drop('Total')
            tabla_sin_total_w = tabla_sin_total_w.sort_values(by='Total', ascending=False)
            tabla_weekend_filtrada_corr = pd.concat([tabla_sin_total_w, tabla_weekend_filtrada_corr.loc[['Total']]])
        else:
            tabla_weekend_filtrada_corr = tabla_weekend_filtrada_corr.sort_values(by='Total', ascending=False)

        st.dataframe(tabla_weekend_filtrada_corr, use_container_width=True, height=400)
        # Botón para descargar Excel con formato (Fines de Semana)
        def to_excel_with_format_weekend(tabla):
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                tabla.to_excel(writer, sheet_name='FinesDeSemana')
                ws = writer.sheets['FinesDeSemana']
                # Resaltar fila Total
                total_row = ws.max_row
                for col in range(1, ws.max_column + 1):
                    ws.cell(row=total_row, column=col).font = Font(bold=True)
                    ws.cell(row=total_row, column=col).fill = PatternFill(start_color='FFFF00', end_color='FFFF00', fill_type='solid')
                # Resaltar columna Total
                total_col = ws.max_column
                for row in range(2, ws.max_row + 1):
                    ws.cell(row=row, column=total_col).font = Font(bold=True)
                    ws.cell(row=row, column=total_col).fill = PatternFill(start_color='FFFF00', end_color='FFFF00', fill_type='solid')
            output.seek(0)
            return output
        excel_data_weekend = to_excel_with_format_weekend(tabla_weekend_filtrada_corr)
        st.download_button(
            label="Descargar tabla de fines de semana en Excel",
            data=excel_data_weekend,
            file_name=f"produccion_fines_semana_{proceso}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        # --- Tabla resumen por FechaPre ---
        st.subheader("Resumen Diario de Producción")
        # Operadores a excluir
        operadores_excluir_resumen = ["Aponte Sanchez, Paola Lita", "Lucero Martinez, Carlos Martin", "USUARIO DE AGENCIA DIGITAL"]
        # Filtrar el dataframe de los últimos 20 días
        df_resumen = df_20dias[~df_20dias[col_operador].isin(operadores_excluir_resumen)].copy()
        # Calcular el total por operador (en los últimos 20 días)
        totales_operador = df_resumen.groupby(col_operador)[col_tramite].count()
        operadores_validos = totales_operador[totales_operador >= 5].index
        df_resumen = df_resumen[df_resumen[col_operador].isin(operadores_validos)]
        # Calcular cantidad de operadores y total de trámites por FechaPre
        resumen = df_resumen.groupby(col_fecha).agg(
            cantidad_operadores=(col_operador, lambda x: x.nunique()),
            total_trabajados=(col_tramite, 'count')
        )
        resumen = resumen.sort_index()
        resumen['promedio_por_operador'] = resumen['total_trabajados'] / resumen['cantidad_operadores']
        # Formatear fechas
        resumen.index = [f.strftime('%d/%m/%Y') if not isinstance(f, str) else f for f in resumen.index]
        st.dataframe(resumen, use_container_width=True, height=400)
        # Botón para descargar Excel
        def to_excel_resumen(tabla):
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                tabla.to_excel(writer, sheet_name='Resumen')
            output.seek(0)
            return output
        excel_data_resumen = to_excel_resumen(resumen)
        st.download_button(
            label="Descargar resumen diario en Excel",
            data=excel_data_resumen,
            file_name=f"resumen_diario_{proceso}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        # --- Gráficos representativos ---
        st.subheader("Gráfica: Promedio Diario por Operador (Lunes a Viernes)")
        resumen_graf_habiles = resumen.copy()
        resumen_graf_habiles.index = pd.to_datetime(resumen_graf_habiles.index, format='%d/%m/%Y')
        dias_habiles = resumen_graf_habiles.index.weekday < 5
        resumen_graf_habiles = resumen_graf_habiles[dias_habiles]
        fig_habiles = go.Figure()
        fig_habiles.add_trace(go.Scatter(
            x=resumen_graf_habiles.index,
            y=resumen_graf_habiles['promedio_por_operador'],
            mode='lines+markers+text',
            name='Promedio por Operador (L-V)',
            text=[f"{v:.1f}" for v in resumen_graf_habiles['promedio_por_operador']],
            textposition="top center"
        ))
        # Línea de tendencia
        x_numeric = arange(len(resumen_graf_habiles.index))
        y = resumen_graf_habiles['promedio_por_operador'].values
        if len(x_numeric) > 1:
            z = polyfit(x_numeric, y, 1)
            tendencia = z[0] * x_numeric + z[1]
            fig_habiles.add_trace(go.Scatter(
                x=resumen_graf_habiles.index,
                y=tendencia,
                mode='lines',
                name='Tendencia',
                line=dict(dash='dash', color='orange')
            ))
        fig_habiles.update_layout(
            title='Promedio Diario de Trámites por Operador (Lunes a Viernes)',
            xaxis_title='Fecha',
            yaxis_title='Promedio por Operador',
            legend_title='Métrica',
            hovermode='x unified'
        )
        st.plotly_chart(fig_habiles, use_container_width=True)

        st.subheader("Gráfica: Promedio Diario por Operador (Fines de Semana)")
        resumen_graf_fds = resumen.copy()
        resumen_graf_fds.index = pd.to_datetime(resumen_graf_fds.index, format='%d/%m/%Y')
        dias_fds = resumen_graf_fds.index.weekday >= 5
        resumen_graf_fds = resumen_graf_fds[dias_fds]
        fig_fds = go.Figure()
        fig_fds.add_trace(go.Scatter(
            x=resumen_graf_fds.index,
            y=resumen_graf_fds['promedio_por_operador'],
            mode='lines+markers+text',
            name='Promedio por Operador (S-D)',
            text=[f"{v:.1f}" for v in resumen_graf_fds['promedio_por_operador']],
            textposition="top center"
        ))
        # Línea de tendencia
        x_numeric_fds = arange(len(resumen_graf_fds.index))
        y_fds = resumen_graf_fds['promedio_por_operador'].values
        if len(x_numeric_fds) > 1:
            z_fds = polyfit(x_numeric_fds, y_fds, 1)
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

        st.subheader("Gráfica: Total de Trámites Diarios")
        resumen_graf_total = resumen.copy()
        resumen_graf_total.index = pd.to_datetime(resumen_graf_total.index, format='%d/%m/%Y')
        fig_total = go.Figure()
        fig_total.add_trace(go.Scatter(
            x=resumen_graf_total.index,
            y=resumen_graf_total['total_trabajados'],
            mode='lines+markers+text',
            name='Total de Trámites',
            text=[str(v) for v in resumen_graf_total['total_trabajados']],
            textposition="top center"
        ))
        # Línea de tendencia
        x_numeric_total = arange(len(resumen_graf_total.index))
        y_total = resumen_graf_total['total_trabajados'].values
        if len(x_numeric_total) > 1:
            z_total = polyfit(x_numeric_total, y_total, 1)
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

    with tab3:
        st.header("Ingreso de Expedientes")
        # Determinar columna de fecha (corregido a FechaExpendiente)
        col_fecha_ing = 'FechaExpendiente'
        col_tramite_ing = 'NumeroTramite'
        if col_fecha_ing not in df.columns:
            st.warning("No se encontró la columna FechaExpendiente en los datos.")
        else:
            # Asegurar tipo datetime
            df[col_fecha_ing] = pd.to_datetime(df[col_fecha_ing], errors='coerce')
            # Filtrar últimos 60 días
            fecha_max = df[col_fecha_ing].max()
            fecha_min = fecha_max - pd.Timedelta(days=60)
            df_60dias = df[(df[col_fecha_ing] >= fecha_min) & (df[col_fecha_ing] <= fecha_max)]
            # Agrupar por fecha y contar NumeroTramite
            ingresos_diarios = df_60dias.groupby(col_fecha_ing)[col_tramite_ing].count().reset_index()
            ingresos_diarios = ingresos_diarios.sort_values(col_fecha_ing)
            # Gráfico
            fig = go.Figure()
            # Línea y puntos
            fig.add_trace(go.Scatter(
                x=ingresos_diarios[col_fecha_ing],
                y=ingresos_diarios[col_tramite_ing],
                mode='lines+markers+text',
                name='NumeroTramite',
                text=[str(v) for v in ingresos_diarios[col_tramite_ing]],
                textposition="top center",
                line=dict(color='royalblue'),
                fill='tozeroy',
                fillcolor='rgba(65,105,225,0.1)'
            ))
            # Línea de tendencia
            x_numeric = arange(len(ingresos_diarios))
            y = ingresos_diarios[col_tramite_ing].values
            if len(x_numeric) > 1:
                z = polyfit(x_numeric, y, 1)
                tendencia = z[0] * x_numeric + z[1]
                fig.add_trace(go.Scatter(
                    x=ingresos_diarios[col_fecha_ing],
                    y=tendencia,
                    mode='lines',
                    name='Tendencia',
                    line=dict(dash='dash', color='red', width=3)
                ))
            # Formato de fechas en eje X
            fig.update_xaxes(
                tickformat="%d %b",
                tickangle=0
            )
            fig.update_layout(
                title='',
                xaxis_title='',
                yaxis_title='',
                legend_title='',
                hovermode='x unified',
                margin=dict(l=20, r=20, t=40, b=20)
            )
            st.plotly_chart(fig, use_container_width=True)

            # Tabla de los últimos 15 días
            st.write("#### Ingresos diarios - últimos 15 días")
            tabla_15 = ingresos_diarios.tail(15).copy()
            tabla_15['FechaExpendiente'] = tabla_15['FechaExpendiente'].dt.strftime('%d/%m/%Y')
            tabla_15 = tabla_15.rename(columns={'FechaExpendiente': 'Fecha', 'NumeroTramite': 'Ingresos'})
            st.dataframe(tabla_15, use_container_width=True)
            # Gráfico de promedio semanal
            st.write("#### Promedio semanal de ingresos diarios")
            # Usar el DataFrame original para el histórico
            col_fecha_ing = 'FechaExpendiente'
            col_tramite_ing = 'NumeroTramite'
            if col_fecha_ing not in df.columns:
                st.warning("No se encontró la columna FechaExpendiente en los datos.")
            else:
                df_sem = df.copy()
                df_sem[col_fecha_ing] = pd.to_datetime(df_sem[col_fecha_ing], errors='coerce')
                # Filtrar el último año completo
                fecha_max = df_sem[col_fecha_ing].max()
                fecha_min = fecha_max - pd.Timedelta(days=365)
                df_sem = df_sem[(df_sem[col_fecha_ing] >= fecha_min) & (df_sem[col_fecha_ing] <= fecha_max)]
                # Agrupar por semana y calcular el promedio
                df_sem['Semana'] = df_sem[col_fecha_ing].dt.to_period('W').dt.start_time
                ingresos_diarios_semanal = df_sem.groupby('Semana')[col_tramite_ing].count().reset_index()
                ingresos_diarios_semanal = ingresos_diarios_semanal.rename(columns={col_tramite_ing: 'Total ingresos'})
                ingresos_diarios_semanal['Promedio semanal'] = ingresos_diarios_semanal['Total ingresos'] / 7
                # Formatear la fecha para el eje X
                ingresos_diarios_semanal['Fecha'] = ingresos_diarios_semanal['Semana'].dt.strftime('%d/%m/%Y')
                # Calcular el rango de fechas para cada semana (lunes a domingo)
                ingresos_diarios_semanal['Rango de fechas'] = ingresos_diarios_semanal['Semana'].dt.strftime('%d/%m/%Y') + ' - ' + (ingresos_diarios_semanal['Semana'] + pd.Timedelta(days=6)).dt.strftime('%d/%m/%Y')
                # Determinar si la semana actual aún no ha terminado
                semana_actual = pd.Timestamp.today().to_period('W').start_time
                ingresos_diarios_semanal['Es semana actual'] = ingresos_diarios_semanal['Semana'] == semana_actual
                fig_sem = px.line(
                    ingresos_diarios_semanal,
                    x='Fecha',
                    y='Promedio semanal',
                    title='Promedio semanal de ingresos diarios (último año)',
                    labels={'Fecha': 'Fecha', 'Promedio semanal': 'Promedio semanal de ingresos'},
                    hover_data={'Rango de fechas': True}
                )
                fig_sem.update_traces(mode='lines+markers', marker=dict(color=ingresos_diarios_semanal['Es semana actual'].map({True: 'red', False: 'blue'})))
                # Línea de tendencia SOLO para el año en curso
                anio_actual = pd.Timestamp.today().year
                mask_anio = ingresos_diarios_semanal['Semana'].dt.year == anio_actual
                sem_actual = ingresos_diarios_semanal[mask_anio].reset_index(drop=True)
                if len(sem_actual) > 1:
                    x_numeric = np.arange(len(sem_actual))
                    y = sem_actual['Promedio semanal'].values
                    z = np.polyfit(x_numeric, y, 1)
                    tendencia = z[0] * x_numeric + z[1]
                    fig_sem.add_scatter(
                        x=sem_actual['Fecha'],
                        y=tendencia,
                        mode='lines',
                        name='Tendencia año en curso',
                        line=dict(dash='dash', color='orange')
                    )
                fig_sem.update_xaxes(tickangle=45)
                st.plotly_chart(fig_sem, use_container_width=True)
            st.write("""
            **¿Qué muestra este gráfico?**
            - Permite ver si el tiempo promedio para pretrabajar un expediente ha mejorado o empeorado a lo largo del año.
            - Una tendencia descendente indica mayor eficiencia; una ascendente, posibles cuellos de botella o sobrecarga.
            """)

    with tab4:
        st.header("Tiempos de Asignación y Pretrabajo")
        st.subheader("Resumen de Tiempos Clave del Proceso")
        operadores_excluir = [
            "Aponte Sanchez, Paola Lita",
            "Lucero Martinez, Carlos Martin",
            "USUARIO DE AGENCIA DIGITAL",
            "MAURICIO ROMERO, HUGO",
            "Sin asignar"
        ]
        df_tiempo = df.copy()
        for col in ["FechaExpendiente", "FECHA_ASIGNACION", "FechaPre"]:
            if col in df_tiempo.columns:
                df_tiempo[col] = pd.to_datetime(df_tiempo[col], errors='coerce')
        df_tiempo = df_tiempo[~df_tiempo['OPERADOR'].isin(operadores_excluir)]
        # Calcular tiempos y filtrar solo los necesarios para cada tramo
        # 1. Ingreso → Asignación
        mask_ia = df_tiempo['FechaExpendiente'].notna() & df_tiempo['FECHA_ASIGNACION'].notna()
        dias_ia = (df_tiempo.loc[mask_ia, 'FECHA_ASIGNACION'] - df_tiempo.loc[mask_ia, 'FechaExpendiente']).dt.days
        dias_ia = dias_ia[dias_ia >= 0]
        # 2. Ingreso → Pretrabajo
        mask_ip = df_tiempo['FechaExpendiente'].notna() & df_tiempo['FechaPre'].notna()
        dias_ip = (df_tiempo.loc[mask_ip, 'FechaPre'] - df_tiempo.loc[mask_ip, 'FechaExpendiente']).dt.days
        dias_ip = dias_ip[dias_ip >= 0]
        # 3. Asignación → Pretrabajo
        mask_ap = df_tiempo['FECHA_ASIGNACION'].notna() & df_tiempo['FechaPre'].notna()
        dias_ap = (df_tiempo.loc[mask_ap, 'FechaPre'] - df_tiempo.loc[mask_ap, 'FECHA_ASIGNACION']).dt.days
        dias_ap = dias_ap[dias_ap >= 0]
        # Cuadro resumen
        resumen = {
            'Promedio (días)': [
                round(dias_ia.mean(), 2),
                round(dias_ip.mean(), 2),
                round(dias_ap.mean(), 2)
            ],
            'Mediana (días)': [
                round(dias_ia.median(), 2),
                round(dias_ip.median(), 2),
                round(dias_ap.median(), 2)
            ],
            'Expedientes': [
                int(dias_ia.count()),
                int(dias_ip.count()),
                int(dias_ap.count())
            ]
        }
        resumen_df = pd.DataFrame(resumen, index=[
            'Ingreso → Asignación',
            'Ingreso → Pretrabajo',
            'Asignación → Pretrabajo'
        ])
        st.dataframe(resumen_df, use_container_width=True)
        st.write("""
        **¿Qué significa este cuadro?**
        - Muestra el tiempo promedio y mediano (en días) que toma cada etapa clave del proceso.
        - Si el tiempo de 'Asignación → Pretrabajo' es alto, puede haber expedientes asignados que demoran en ser trabajados.
        - Si 'Ingreso → Asignación' es alto, puede haber demora en la asignación inicial.
        - El número de expedientes indica cuántos casos válidos se analizaron para cada tramo.
        """)

        # Gráfico de evolución mensual del promedio de días Ingreso → Pretrabajo
        st.write("#### Evolución del promedio de días desde Ingreso hasta Pretrabajo (último año)")
        # Filtrar solo expedientes con ambas fechas válidas
        mask_ip = df_tiempo['FechaExpendiente'].notna() & df_tiempo['FechaPre'].notna()
        df_ip = df_tiempo.loc[mask_ip].copy()
        df_ip = df_ip[df_ip['FechaPre'] >= df_ip['FechaExpendiente']]
        df_ip['mes'] = df_ip['FechaPre'].dt.to_period('M').dt.to_timestamp()
        df_ip_ultimo_anio = df_ip[df_ip['FechaPre'] >= (pd.Timestamp.today() - pd.DateOffset(years=1))]
        promedio_mensual = df_ip_ultimo_anio.groupby('mes').apply(lambda x: (x['FechaPre'] - x['FechaExpendiente']).dt.days.mean())
        promedio_mensual = promedio_mensual.reset_index(name='Promedio días')
        fig = px.line(promedio_mensual, x='mes', y='Promedio días', markers=True, title='Promedio mensual de días desde Ingreso hasta Pretrabajo')
        fig.update_traces(text=promedio_mensual['Promedio días'].round(1), textposition="top center")
        fig.update_layout(xaxis_title='Mes', yaxis_title='Promedio de días', hovermode='x unified')
        st.plotly_chart(fig, use_container_width=True)
        st.write("""
        **¿Qué muestra este gráfico?**
        - Permite ver si el tiempo promedio para pretrabajar un expediente ha mejorado o empeorado a lo largo del año.
        - Una tendencia descendente indica mayor eficiencia; una ascendente, posibles cuellos de botella o sobrecarga.
        """)

    with tab5:
        st.header("Proyección de Cierre y Equilibrio")
        st.write("### Simulador de Personal Activo y Proyección")
        # 1. Pendientes actuales (asignados y sin asignar)
        if proceso == "CCM":
            df_pend = df[
                (df['UltimaEtapa'] == 'EVALUACIÓN - I') &
                (df['EstadoPre'].isna()) &
                (df['EstadoTramite'] == 'PENDIENTE') &
                (df['EQUIPO'] != 'VULNERABLE')
            ]
        else:
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
            df_pend = df[
                (df['UltimaEtapa'].isin(etapas_prr)) &
                (df['EstadoPre'].isna()) &
                (df['EstadoTramite'] == 'PENDIENTE') &
                (df['EQUIPO'] != 'VULNERABLE')
            ]
        pendientes_total = len(df_pend)
        pendientes_sin_asignar = df_pend['OPERADOR'].isna().sum()
        pendientes_asignados = pendientes_total - pendientes_sin_asignar
        # 2. Ingresos diarios promedio (últimos 60 días)
        df['FechaExpendiente'] = pd.to_datetime(df['FechaExpendiente'], errors='coerce')
        fecha_max = df['FechaExpendiente'].max()
        fecha_min = fecha_max - pd.Timedelta(days=60)
        ingresos_ultimos = df[(df['FechaExpendiente'] >= fecha_min) & (df['FechaExpendiente'] <= fecha_max)]
        ingresos_diarios = ingresos_ultimos.groupby('FechaExpendiente')['NumeroTramite'].count()
        ingresos_promedio = ingresos_diarios.mean()
        # Tomar el promedio de 'promedio_por_operador' de Producción Diaria
        col_operador = 'OperadorPre'
        col_fecha = 'FechaPre'
        col_tramite = 'NumeroTramite'
        if col_operador not in df.columns:
            col_operador = 'OPERADOR'
        if col_fecha not in df.columns:
            col_fecha = 'FechaPre'
        if pd.api.types.is_datetime64_any_dtype(df[col_fecha]):
            fechas_ordenadas = df[col_fecha].dropna().sort_values().unique()
        else:
            df[col_fecha] = pd.to_datetime(df[col_fecha], errors='coerce')
            fechas_ordenadas = df[col_fecha].dropna().sort_values().unique()
        ultimos_20 = fechas_ordenadas[-20:]
        df_20dias = df[df[col_fecha].isin(ultimos_20)]
        operadores_excluir = [
            "Aponte Sanchez, Paola Lita",
            "Lucero Martinez, Carlos Martin",
            "USUARIO DE AGENCIA DIGITAL",
            "MAURICIO ROMERO, HUGO",
            "Sin asignar"
        ]
        df_20dias = df_20dias[~df_20dias[col_operador].isin(operadores_excluir)]
        totales_operador = df_20dias.groupby(col_operador)[col_tramite].count()
        operadores_validos = totales_operador[totales_operador >= 5].index
        df_20dias = df_20dias[df_20dias[col_operador].isin(operadores_validos)]
        resumen_prod = df_20dias.groupby(col_fecha).agg(
            cantidad_operadores=(col_operador, lambda x: x.nunique()),
            total_trabajados=(col_tramite, 'count')
        )
        resumen_prod = resumen_prod.sort_index()
        resumen_prod['promedio_por_operador'] = resumen_prod['total_trabajados'] / resumen_prod['cantidad_operadores']
        promedio_por_operador = resumen_prod['promedio_por_operador'].mean() if not resumen_prod.empty else 0
        # Ingreso manual de personal activo actual
        personal_activo_input = st.number_input(
            "Ingrese la cantidad de personal activo para la proyección:",
            min_value=1, max_value=100, value=5, step=1
        )
        cierres_proy_sim = promedio_por_operador * personal_activo_input  # Cierres diarios estimados
        # Proyección de cierre
        if cierres_proy_sim > 0:
            dias_para_cerrar = pendientes_total / cierres_proy_sim
        else:
            dias_para_cerrar = float('inf')
        # Punto de equilibrio
        if ingresos_promedio > 0 and cierres_proy_sim > 0:
            if cierres_proy_sim > ingresos_promedio:
                equilibrio = "Ya se está cerrando más de lo que ingresa."
            else:
                equilibrio = f"Faltan {round((pendientes_total / (cierres_proy_sim - ingresos_promedio)), 1)} días para llegar al equilibrio (si la diferencia se mantiene)."
        else:
            equilibrio = "No hay datos suficientes para calcular el equilibrio."
        # Cuadro resumen
        resumen = {
            'Variable': [
                'Pendientes actuales',
                'Pendientes asignados',
                'Pendientes sin asignar',
                'Ingresos diarios promedio (60 días)',
                'Cierres diarios promedio por persona (20 días)',
                'Personal activo para proyección',
                'Cierres diarios estimados (simulados)',
                'Días estimados para cerrar todo',
                'Proyección de equilibrio'
            ],
            'Valor': [
                pendientes_total,
                pendientes_asignados,
                pendientes_sin_asignar,
                round(ingresos_promedio, 2),
                round(promedio_por_operador, 2),
                personal_activo_input,
                round(cierres_proy_sim, 2),
                round(dias_para_cerrar, 1) if dias_para_cerrar != float('inf') else '∞',
                equilibrio
            ]
        }
        resumen_df = pd.DataFrame(resumen)
        st.dataframe(resumen_df, use_container_width=True)
        st.write("""
        **¿Cómo se calculan estas métricas?**
        - **Pendientes actuales:** cantidad de expedientes pendientes según los filtros de pendientes.
        - **Pendientes asignados/sin asignar:** según si tienen OPERADOR asignado o no.
        - **Ingresos diarios promedio (60 días):** suma de expedientes ingresados en los últimos 60 días dividido entre 60.
        - **Cierres diarios promedio por persona (20 días):** promedio de 'promedio_por_operador' de Producción Diaria.
        - **Personal activo para proyección:** valor que tú ingresas.
        - **Cierres diarios estimados (simulados):** cierres diarios promedio por persona x personal activo ingresado.
        - **Días estimados para cerrar todo:** pendientes actuales / cierres diarios estimados.
        - **Proyección de equilibrio:** días para que (pendientes actuales / (cierres estimados - ingresos promedio)) llegue a cero, si los cierres superan los ingresos.
        """)
        # Tabla y gráfico de proyección
        max_dias = 180 if dias_para_cerrar == float('inf') else int(dias_para_cerrar) + 30
        dias = list(range(0, max_dias + 1))
        pendientes_proyectados = [max(pendientes_total - cierres_proy_sim * d + ingresos_promedio * d, 0) for d in dias]
        ingresos_proy = [ingresos_promedio for _ in dias]
        cierres_proy = [cierres_proy_sim for _ in dias]
        tabla_proy = pd.DataFrame({
            'Día': dias,
            'Pendientes proyectados': pendientes_proyectados,
            'Ingresos diarios estimados': ingresos_proy,
            'Cierres diarios estimados': cierres_proy
        })
        st.write("#### Tabla de proyección diaria (hasta 180 días o cierre)")
        st.dataframe(tabla_proy.head(60), use_container_width=True)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=tabla_proy['Día'], y=tabla_proy['Pendientes proyectados'], mode='lines+markers', name='Pendientes proyectados'))
        fig.add_trace(go.Scatter(x=tabla_proy['Día'], y=tabla_proy['Ingresos diarios estimados'], mode='lines', name='Ingresos diarios estimados', line=dict(dash='dot', color='green')))
        fig.add_trace(go.Scatter(x=tabla_proy['Día'], y=tabla_proy['Cierres diarios estimados'], mode='lines', name='Cierres diarios estimados', line=dict(dash='dot', color='blue')))
        fig.update_layout(title='Proyección de Pendientes, Ingresos y Cierres en el Tiempo', xaxis_title='Días desde hoy', yaxis_title='Cantidad', hovermode='x unified')
        st.plotly_chart(fig, use_container_width=True)
        st.write("""
        **¿Qué muestra la tabla y el gráfico?**
        - Simulan día a día cómo evolucionarían los pendientes, ingresos y cierres si se mantiene el ritmo actual y el personal activo ingresado.
        - La tabla muestra los primeros 60 días, el gráfico hasta 180 días o hasta que los pendientes lleguen a cero.
        - Si la curva de pendientes baja a cero, se estima en cuántos días se cerrarían todos los pendientes.
        - Si la curva se estabiliza, se estaría llegando al punto de equilibrio.
        """)

except Exception as e:
    st.error(f"Error al cargar los datos: {str(e)}") 