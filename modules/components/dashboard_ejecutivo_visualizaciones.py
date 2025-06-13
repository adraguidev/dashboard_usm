"""
Funciones de visualización para el Dashboard Ejecutivo
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from modules.data.loader import cargar_historico_pendientes
from modules.data.historico_sin_asignar import cargar_historico_sin_asignar

def mostrar_evolucion_pendientes_historica() -> None:
    """
    Muestra gráfico de evolución de pendientes con diseño moderno y UX mejorado
    """
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                padding: 20px; border-radius: 15px; margin: 20px 0;">
        <h3 style="color: white; text-align: center; margin: 0;">
            📈 Evolución de Pendientes
        </h3>
        <p style="color: white; text-align: center; opacity: 0.9; margin: 5px 0;">
            Tendencia histórica de carga de trabajo
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Usar histórico de pendientes existente
    historico = cargar_historico_pendientes()
    
    if not historico.empty:
        # Preparar datos del histórico para gráfico
        historico['Fecha'] = pd.to_datetime(historico['Fecha'])
        
        # FILTRAR CASOS ANTIGUOS Y OPERADORES INACTIVOS
        historico_filtrado = historico[historico['Año'] != 'ANTIGUOS'].copy()
        
        # Últimos 60 días para ver tendencia
        historico_reciente = historico_filtrado[historico_filtrado['Fecha'] >= (historico_filtrado['Fecha'].max() - pd.Timedelta(days=60))]
        
        if not historico_reciente.empty:
            # Agrupar por fecha y proceso para mostrar totales
            totales_por_fecha = historico_reciente.groupby(['Fecha', 'Proceso'])['Pendientes'].sum().reset_index()
            
            # Solo mostrar si hay al menos 5 pendientes por proceso por día
            totales_por_fecha = totales_por_fecha[totales_por_fecha['Pendientes'] >= 5].copy()
            
            # Crear gráfico con diseño moderno
            fig = go.Figure()
            
            # Colores modernos para cada proceso
            colores = {
                'CCM': '#FF6B6B',  # Rojo coral moderno
                'PRR': '#4ECDC4'   # Turquesa moderno
            }
            
            # Líneas por proceso con etiquetas mejoradas
            for proceso in ['CCM', 'PRR']:
                datos_proceso = totales_por_fecha[totales_por_fecha['Proceso'] == proceso].copy()
                
                if not datos_proceso.empty:
                    datos_proceso = datos_proceso.sort_values('Fecha')
                    
                    # Estrategia inteligente: mostrar más etiquetas pero con mejor posicionamiento
                    n_puntos = len(datos_proceso)
                    
                    # Estrategia con MÁS ETIQUETAS - más generosa
                    if n_puntos <= 8:
                        # Pocos puntos: mostrar todos
                        mostrar_etiqueta = [True for i in range(n_puntos)]
                    elif n_puntos <= 15:
                        # Puntos medios: mostrar cada 2 (más etiquetas)
                        mostrar_etiqueta = [i % 2 == 0 for i in range(n_puntos)]
                    elif n_puntos <= 25:
                        # Bastantes puntos: mostrar cada 2 + asegurar extremos
                        mostrar_etiqueta = [i % 2 == 0 or i == n_puntos-1 for i in range(n_puntos)]
                    else:
                        # Muchos puntos: mostrar cada 3 + extremos + punto medio
                        mostrar_etiqueta = [i % 3 == 0 or i == n_puntos-1 or i == n_puntos//2 for i in range(n_puntos)]
                    
                    # Sistema de posicionamiento dinámico para evitar choques
                    posiciones_texto = []
                    for i, mostrar in enumerate(mostrar_etiqueta):
                        if mostrar:
                            # Estrategia por proceso con rotación de posiciones
                            if proceso == 'CCM':
                                # CCM: rotar entre 3 posiciones arriba
                                pos_idx = i % 3
                                if pos_idx == 0:
                                    posiciones_texto.append("top center")
                                elif pos_idx == 1:
                                    posiciones_texto.append("top right")
                                else:
                                    posiciones_texto.append("top left")
                            else:  # PRR
                                # PRR: rotar entre 3 posiciones abajo
                                pos_idx = i % 3
                                if pos_idx == 0:
                                    posiciones_texto.append("bottom center")
                                elif pos_idx == 1:
                                    posiciones_texto.append("bottom left")
                                else:
                                    posiciones_texto.append("bottom right")
                        else:
                            # Para puntos sin etiqueta, usar posición válida pero texto vacío
                            posiciones_texto.append("middle center")
                    
                    # Agregar línea SIN etiquetas de texto (solo línea y marcadores)
                    fig.add_trace(go.Scatter(
                        x=datos_proceso['Fecha'],
                        y=datos_proceso['Pendientes'],
                        mode='lines+markers',  # Sin texto aquí
                        name=f'{proceso}',
                        line=dict(width=4, color=colores[proceso]),
                        marker=dict(size=8, color=colores[proceso], 
                                  line=dict(width=2, color='white')),
                        connectgaps=False,
                        hovertemplate=f'<b style="color:{colores[proceso]}">{proceso}</b><br>' +
                                    'Fecha: %{x}<br>' +
                                    'Pendientes: %{y:,}<br>' +
                                    '<extra></extra>'
                    ))
                    
                    # FUNCIÓN ULTRA-INTELIGENTE para encontrar mejor posición
                    def encontrar_mejor_posicion_pendientes(valor_actual, valores_otros_procesos, diferencia_anterior, diferencia_siguiente, proceso, es_ultimo=False):
                        """
                        Algoritmo inteligente para posicionar etiquetas en gráfico de pendientes
                        """
                        # 8 posiciones candidatas con scoring
                        if proceso == 'CCM':
                            candidatos = [
                                (0, -35, "arriba_centro"),      # Posición preferida CCM
                                (30, -15, "arriba_der"),        # Derecha arriba
                                (-30, -15, "arriba_izq"),       # Izquierda arriba
                                (40, 0, "der_centro"),          # Derecha centro
                                (-40, 0, "izq_centro"),         # Izquierda centro
                                (25, -25, "der_arriba_cerca"),  # Derecha arriba cerca
                                (-25, -25, "izq_arriba_cerca"), # Izquierda arriba cerca
                                (0, -45, "arriba_alto")         # Muy arriba
                            ]
                        else:  # PRR
                            candidatos = [
                                (0, 35, "abajo_centro"),        # Posición preferida PRR
                                (-30, 15, "abajo_izq"),         # Izquierda abajo
                                (30, 15, "abajo_der"),          # Derecha abajo
                                (-40, 0, "izq_centro"),         # Izquierda centro
                                (40, 0, "der_centro"),          # Derecha centro
                                (-25, 25, "izq_abajo_cerca"),   # Izquierda abajo cerca
                                (25, 25, "der_abajo_cerca"),    # Derecha abajo cerca
                                (0, 45, "abajo_bajo")           # Muy abajo
                            ]
                        
                        mejor_score = -1000
                        mejor_pos = (0, -35 if proceso == 'CCM' else 35)
                        
                        for ax, ay, nombre in candidatos:
                            score = 0
                            
                            # Bonus base por proceso
                            score += 30
                            
                            # ANÁLISIS DE SEPARACIÓN con otros procesos
                            if valores_otros_procesos:
                                min_distancia = min([abs(valor_actual - v) for v in valores_otros_procesos])
                                if min_distancia > 1500:  # Muy separado
                                    score += 50
                                elif min_distancia > 800:  # Bien separado
                                    score += 30
                                elif min_distancia > 300:  # Moderadamente separado
                                    score += 15
                                else:  # Muy cerca - penalizar posiciones centrales
                                    if "centro" in nombre:
                                        score -= 20
                            
                            # ANÁLISIS DE ESPACIO LATERAL
                            if diferencia_anterior and diferencia_siguiente:
                                # Preferir lado con más espacio
                                if ax > 0 and diferencia_siguiente > diferencia_anterior:
                                    score += 25
                                elif ax < 0 and diferencia_anterior > diferencia_siguiente:
                                    score += 25
                                elif ax == 0:  # Centro siempre bueno si hay espacio
                                    score += 20
                            
                            # BONUS ESPECIAL para último punto
                            if es_ultimo:
                                if "der" in nombre:
                                    score += 35
                                if "centro" in nombre:
                                    score += 20
                            
                            # Preferir posiciones apropiadas por proceso
                            if proceso == 'CCM' and "arriba" in nombre:
                                score += 25
                            elif proceso == 'PRR' and "abajo" in nombre:
                                score += 25
                            
                            # Penalizar posiciones extremas si no hay necesidad
                            if "alto" in nombre or "bajo" in nombre:
                                score -= 10
                            
                            if score > mejor_score:
                                mejor_score = score
                                mejor_pos = (ax, ay)
                        
                        return mejor_pos
                    
                    # ANOTACIONES ULTRA-INTELIGENTES para pendientes
                    etiquetas_colocadas = []  # Para detectar colisiones
                    
                    for i, (fecha, valor, mostrar) in enumerate(zip(datos_proceso['Fecha'], datos_proceso['Pendientes'], mostrar_etiqueta)):
                        if mostrar or i == len(datos_proceso) - 1:  # Siempre mostrar último punto
                            # Obtener valores de otros procesos en la misma fecha
                            otros_valores = []
                            for otro_proc in ['CCM', 'PRR']:
                                if otro_proc != proceso:
                                    otros_datos = totales_por_fecha[totales_por_fecha['Proceso'] == otro_proc]
                                    otros_en_fecha = otros_datos[otros_datos['Fecha'] == fecha]
                                    if not otros_en_fecha.empty:
                                        otros_valores.append(otros_en_fecha['Pendientes'].iloc[0])
                            
                            # Calcular diferencias con puntos adyacentes
                            diff_anterior = abs(valor - datos_proceso['Pendientes'].iloc[i-1]) if i > 0 else 0
                            diff_siguiente = abs(valor - datos_proceso['Pendientes'].iloc[i+1]) if i < len(datos_proceso)-1 else 0
                            
                            # Encontrar mejor posición
                            ax_offset, ay_offset = encontrar_mejor_posicion_pendientes(
                                valor, otros_valores, diff_anterior, diff_siguiente, proceso, i == len(datos_proceso)-1
                            )
                            
                            # ANTI-COLISIÓN: verificar si hay etiquetas muy cercanas
                            posicion_actual = (fecha, valor + ay_offset)
                            colision_detectada = False
                            
                            for fecha_ant, y_ant in etiquetas_colocadas:
                                if abs((fecha - fecha_ant).days) <= 3 and abs(y_ant - (valor + ay_offset)) < 200:
                                    colision_detectada = True
                                    break
                            
                            # Si hay colisión, ajustar posición
                            if colision_detectada:
                                if proceso == 'CCM':
                                    ay_offset = -45 if ay_offset > -40 else -25
                                    ax_offset = 35 if ax_offset >= 0 else -35
                                else:  # PRR
                                    ay_offset = 45 if ay_offset < 40 else 25
                                    ax_offset = -35 if ax_offset <= 0 else 35
                            
                            etiquetas_colocadas.append((fecha, valor + ay_offset))
                            
                            fig.add_annotation(
                                x=fecha,
                                y=valor,
                                text=f'{valor:,}',
                                showarrow=True,
                                arrowhead=1,
                                arrowsize=0.8,
                                arrowwidth=1,
                                arrowcolor=colores[proceso],
                                ax=ax_offset,
                                ay=ay_offset,
                                font=dict(size=9, color=colores[proceso], family="Arial", weight="bold"),
                                bgcolor="rgba(255,255,255,0.9)",
                                bordercolor=colores[proceso],
                                borderwidth=1
                            )
            
            # Total combinado con área sombreada
            if not totales_por_fecha.empty:
                totales_fecha = totales_por_fecha.groupby('Fecha')['Pendientes'].sum().reset_index()
                totales_fecha = totales_fecha[totales_fecha['Pendientes'] >= 10].copy()
                totales_fecha = totales_fecha.sort_values('Fecha')
                
                if len(totales_fecha) > 0:
                    # Estrategia con MÁS ETIQUETAS para el total también
                    n_total = len(totales_fecha)
                    if n_total <= 8:
                        # Pocos puntos: mostrar todos
                        mostrar_total = [True for i in range(n_total)]
                    elif n_total <= 15:
                        # Puntos medios: mostrar cada 2 (más etiquetas)
                        mostrar_total = [i % 2 == 0 for i in range(n_total)]
                    elif n_total <= 22:
                        # Bastantes puntos: mostrar cada 2 + asegurar extremos
                        mostrar_total = [i % 2 == 0 or i == n_total-1 for i in range(n_total)]
                    else:
                        # Muchos puntos: mostrar cada 3 + extremos + punto medio
                        mostrar_total = [i % 3 == 0 or i == n_total-1 or i == n_total//2 for i in range(n_total)]
                    
                    # Posiciones del total rotando en el medio para evitar choques
                    posiciones_total = []
                    for i, mostrar in enumerate(mostrar_total):
                        if mostrar:
                            # Rotar entre middle center y middle right para variedad
                            pos_idx = i % 2
                            if pos_idx == 0:
                                posiciones_total.append("middle center")
                            else:
                                posiciones_total.append("middle right")
                        else:
                            # Para puntos sin etiqueta, usar posición válida pero texto vacío
                            posiciones_total.append("top center")
                    
                    fig.add_trace(go.Scatter(
                        x=totales_fecha['Fecha'],
                        y=totales_fecha['Pendientes'],
                        mode='lines+markers',  # Sin texto aquí
                        name='Total',
                        line=dict(width=5, color='#9B59B6', dash='dash'),
                        marker=dict(size=10, color='#9B59B6', 
                                  line=dict(width=2, color='white'),
                                  symbol='diamond'),
                        connectgaps=False,
                        hovertemplate='<b style="color:#9B59B6">TOTAL COMBINADO</b><br>' +
                                    'Fecha: %{x}<br>' +
                                    'Pendientes: %{y:,}<br>' +
                                    '<extra></extra>'
                    ))
                    
                    # FUNCIÓN INTELIGENTE para el total
                    def encontrar_mejor_posicion_total(valor_actual, diferencia_anterior, diferencia_siguiente, es_ultimo=False):
                        """
                        Algoritmo inteligente para posicionar etiquetas del total
                        """
                        candidatos = [
                            (0, -30, "arriba_centro"),
                            (25, -20, "arriba_der"),
                            (-25, -20, "arriba_izq"),
                            (35, -10, "der_arriba"),
                            (-35, -10, "izq_arriba"),
                            (0, -40, "arriba_alto"),
                            (40, 0, "der_centro"),
                            (-40, 0, "izq_centro")
                        ]
                        
                        mejor_score = -1000
                        mejor_pos = (0, -30)
                        
                        for ax, ay, nombre in candidatos:
                            score = 40  # Bonus base para total
                            
                            # ANÁLISIS DE ESPACIO LATERAL
                            if diferencia_anterior and diferencia_siguiente:
                                if ax > 0 and diferencia_siguiente > diferencia_anterior:
                                    score += 30
                                elif ax < 0 and diferencia_anterior > diferencia_siguiente:
                                    score += 30
                                elif ax == 0:
                                    score += 25
                            
                            # BONUS para último punto
                            if es_ultimo:
                                if "der" in nombre:
                                    score += 40
                                if "centro" in nombre:
                                    score += 25
                            
                            # Preferir posiciones arriba para el total
                            if "arriba" in nombre:
                                score += 20
                            
                            # Penalizar posiciones extremas
                            if "alto" in nombre:
                                score -= 5
                            
                            if score > mejor_score:
                                mejor_score = score
                                mejor_pos = (ax, ay)
                        
                        return mejor_pos
                    
                    # ANOTACIONES INTELIGENTES para el total
                    etiquetas_total_colocadas = []
                    
                    for i, (fecha, valor, mostrar) in enumerate(zip(totales_fecha['Fecha'], totales_fecha['Pendientes'], mostrar_total)):
                        if mostrar or i == len(totales_fecha) - 1:  # Siempre mostrar último punto
                            # Calcular diferencias con puntos adyacentes
                            diff_anterior = abs(valor - totales_fecha['Pendientes'].iloc[i-1]) if i > 0 else 0
                            diff_siguiente = abs(valor - totales_fecha['Pendientes'].iloc[i+1]) if i < len(totales_fecha)-1 else 0
                            
                            # Encontrar mejor posición
                            ax_offset, ay_offset = encontrar_mejor_posicion_total(
                                valor, diff_anterior, diff_siguiente, i == len(totales_fecha)-1
                            )
                            
                            # ANTI-COLISIÓN para el total
                            posicion_actual = (fecha, valor + ay_offset)
                            colision_detectada = False
                            
                            for fecha_ant, y_ant in etiquetas_total_colocadas:
                                if abs((fecha - fecha_ant).days) <= 3 and abs(y_ant - (valor + ay_offset)) < 250:
                                    colision_detectada = True
                                    break
                            
                            # Si hay colisión, ajustar
                            if colision_detectada:
                                ay_offset = -45 if ay_offset > -35 else -25
                                ax_offset = 40 if ax_offset >= 0 else -40
                            
                            etiquetas_total_colocadas.append((fecha, valor + ay_offset))
                            
                            fig.add_annotation(
                                x=fecha,
                                y=valor,
                                text=f'{valor:,}',
                                showarrow=True,
                                arrowhead=1,
                                arrowsize=0.8,
                                arrowwidth=1,
                                arrowcolor='#9B59B6',
                                ax=ax_offset,
                                ay=ay_offset,
                                font=dict(size=10, color='#9B59B6', family="Arial", weight="bold"),
                                bgcolor="rgba(255,255,255,0.9)",
                                bordercolor='#9B59B6',
                                borderwidth=1
                            )
                    
                    # Área sombreada para el total
                    fig.add_trace(go.Scatter(
                        x=totales_fecha['Fecha'],
                        y=totales_fecha['Pendientes'],
                        fill='tonexty',
                        fillcolor='rgba(155, 89, 182, 0.1)',
                        line=dict(color='rgba(255,255,255,0)'),
                        showlegend=False,
                        hoverinfo='skip'
                    ))
            
            # Configuración moderna del layout con mejor espaciado para etiquetas
            fig.update_layout(
                title={
                    'text': "📊 Tendencia de Pendientes (Últimos 60 días)",
                    'x': 0.5,
                    'xanchor': 'center',
                    'font': {'size': 18, 'color': '#2C3E50', 'family': 'Arial Black'}
                },
                xaxis_title="📅 Fecha",
                yaxis_title="📋 Total Pendientes",
                xaxis=dict(
                    showgrid=True,
                    gridwidth=1,
                    gridcolor='rgba(128,128,128,0.2)',
                    tickfont=dict(size=11, color='#34495E'),
                    title_font=dict(size=14, color='#2C3E50', family='Arial Black'),
                    tickangle=45  # Rotar fechas para mejor legibilidad
                ),
                yaxis=dict(
                    rangemode='tozero',  # Empezar desde cero, no negativos
                    showgrid=True,
                    gridwidth=1,
                    gridcolor='rgba(128,128,128,0.2)',
                    tickfont=dict(size=11, color='#34495E'),
                    title_font=dict(size=14, color='#2C3E50', family='Arial Black'),
                    # Mantener rango natural de los datos
                    autorange=True
                ),
                hovermode='x unified',
                height=550,  # Aumentar altura para dar más espacio a etiquetas
                plot_bgcolor='rgba(248,249,250,0.8)',
                paper_bgcolor='white',
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="center",
                    x=0.5,
                    bgcolor='rgba(255,255,255,0.9)',
                    bordercolor='rgba(128,128,128,0.3)',
                    borderwidth=1,
                    font=dict(size=12, color='#2C3E50', family='Arial Black')
                ),
                showlegend=True,
                margin=dict(l=80, r=80, t=120, b=100),  # Más margen arriba y abajo
                # Configuración para evitar recorte de etiquetas
                autosize=True,
                uniformtext_minsize=8,
                uniformtext_mode='hide'
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Resumen estadístico moderno
            col1, col2, col3 = st.columns(3)
            
            with col1:
                ultimo_total = totales_fecha['Pendientes'].iloc[-1] if not totales_fecha.empty else 0
                st.metric("📊 Pendientes Actuales", f"{ultimo_total:,}", 
                         help="Total de pendientes en la última fecha registrada")
            
            with col2:
                promedio = totales_fecha['Pendientes'].mean() if not totales_fecha.empty else 0
                st.metric("📈 Promedio Período", f"{promedio:.0f}", 
                         help="Promedio de pendientes en los últimos 60 días")
            
            with col3:
                tendencia = "📈 Creciente" if len(totales_fecha) > 1 and totales_fecha['Pendientes'].iloc[-1] > totales_fecha['Pendientes'].iloc[0] else "📉 Decreciente"
                variacion = totales_fecha['Pendientes'].iloc[-1] - totales_fecha['Pendientes'].iloc[0] if len(totales_fecha) > 1 else 0
                st.metric("📊 Tendencia", tendencia, delta=int(variacion),
                         help="Comparación entre el primer y último valor del período")
            
            # Información mejorada
            st.info("💡 **Información del gráfico:** Se excluyen casos ANTIGUOS y operadores con menos de 5 pendientes para mostrar solo carga significativa")
            
        else:
            st.warning("📊 Datos históricos insuficientes para mostrar tendencias")
    else:
        st.error("❌ No hay datos históricos disponibles")

def mostrar_evolucion_sin_asignar() -> None:
    """
    Muestra gráfico mejorado de evolución de casos sin asignar
    """
    st.markdown("""
    <div style="background: linear-gradient(135deg, #FF6B6B 0%, #FF8E53 100%); 
                padding: 20px; border-radius: 15px; margin: 20px 0;">
        <h3 style="color: white; text-align: center; margin: 0;">
            ⚠️ Evolución de Sin Asignar
        </h3>
        <p style="color: white; text-align: center; opacity: 0.9; margin: 5px 0;">
            Casos pendientes de asignación por proceso
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Cargar histórico de sin asignar
    historico_sin_asignar = cargar_historico_sin_asignar()
    
    if not historico_sin_asignar.empty:
        # Preparar datos
        historico_sin_asignar['fecha'] = pd.to_datetime(historico_sin_asignar['fecha'])
        
        # Últimos 30 días para ver tendencia
        historico_reciente = historico_sin_asignar[
            historico_sin_asignar['fecha'] >= (historico_sin_asignar['fecha'].max() - pd.Timedelta(days=30))
        ]
        
        # FILTRAR SOLO FECHAS CON VALORES SIGNIFICATIVOS
        fechas_con_valores = historico_reciente.groupby('fecha')['sin_asignar'].sum()
        fechas_validas = fechas_con_valores[fechas_con_valores > 0].index
        historico_reciente = historico_reciente[historico_reciente['fecha'].isin(fechas_validas)]
        
        if not historico_reciente.empty:
            fig = go.Figure()
            
            # Colores modernos
            colores_sin_asignar = {
                'CCM': '#E74C3C',  # Rojo intenso
                'PRR': '#F39C12'   # Naranja
            }
            
            # Líneas por proceso CON ANOTACIONES INTELIGENTES
            for proceso in ['CCM', 'PRR']:
                datos_proceso = historico_reciente[historico_reciente['proceso'] == proceso].copy()
                
                if not datos_proceso.empty:
                    datos_proceso = datos_proceso.sort_values('fecha')
                    n_puntos = len(datos_proceso)
                    
                    # Estrategia con MÁS ETIQUETAS - más generosa
                    if n_puntos <= 8:
                        mostrar_etiqueta = [True for i in range(n_puntos)]
                    elif n_puntos <= 15:
                        mostrar_etiqueta = [i % 2 == 0 for i in range(n_puntos)]
                    elif n_puntos <= 25:
                        mostrar_etiqueta = [i % 2 == 0 or i == n_puntos-1 for i in range(n_puntos)]
                    else:
                        mostrar_etiqueta = [i % 3 == 0 or i == n_puntos-1 or i == n_puntos//2 for i in range(n_puntos)]
                    
                    # Agregar línea SIN etiquetas de texto
                    fig.add_trace(go.Scatter(
                        x=datos_proceso['fecha'],
                        y=datos_proceso['sin_asignar'],
                        mode='lines+markers',
                        name=f'{proceso}',
                        line=dict(width=4, color=colores_sin_asignar[proceso]),
                        marker=dict(size=10, color=colores_sin_asignar[proceso],
                                  line=dict(width=2, color='white')),
                        hovertemplate=f'<b style="color:{colores_sin_asignar[proceso]}">{proceso}</b><br>' +
                                    'Fecha: %{x}<br>' +
                                    'Sin Asignar: %{y:,}<br>' +
                                    '<extra></extra>'
                    ))
                    
                    # FUNCIÓN ULTRA-INTELIGENTE para Sin Asignar
                    def encontrar_mejor_posicion_sin_asignar(valor_actual, valores_otros_procesos, diferencia_anterior, diferencia_siguiente, proceso, es_ultimo=False):
                        """
                        Algoritmo inteligente para posicionar etiquetas en gráfico de sin asignar
                        """
                        if proceso == 'CCM':
                            candidatos = [
                                (0, -35, "arriba_centro"),
                                (30, -15, "arriba_der"),
                                (-30, -15, "arriba_izq"),
                                (40, 0, "der_centro"),
                                (-40, 0, "izq_centro"),
                                (25, -25, "der_arriba_cerca"),
                                (-25, -25, "izq_arriba_cerca"),
                                (0, -45, "arriba_alto")
                            ]
                        else:  # PRR
                            candidatos = [
                                (0, 35, "abajo_centro"),
                                (-30, 15, "abajo_izq"),
                                (30, 15, "abajo_der"),
                                (-40, 0, "izq_centro"),
                                (40, 0, "der_centro"),
                                (-25, 25, "izq_abajo_cerca"),
                                (25, 25, "der_abajo_cerca"),
                                (0, 45, "abajo_bajo")
                            ]
                        
                        mejor_score = -1000
                        mejor_pos = (0, -35 if proceso == 'CCM' else 35)
                        
                        for ax, ay, nombre in candidatos:
                            score = 30
                            
                            # ANÁLISIS DE SEPARACIÓN con otros procesos
                            if valores_otros_procesos:
                                min_distancia = min([abs(valor_actual - v) for v in valores_otros_procesos])
                                if min_distancia > 50:  # Bien separado para sin asignar
                                    score += 40
                                elif min_distancia > 20:  # Moderadamente separado
                                    score += 20
                                elif min_distancia > 5:  # Poco separado
                                    score += 10
                                else:  # Muy cerca - penalizar posiciones centrales
                                    if "centro" in nombre:
                                        score -= 15
                            
                            # ANÁLISIS DE ESPACIO LATERAL
                            if diferencia_anterior and diferencia_siguiente:
                                if ax > 0 and diferencia_siguiente > diferencia_anterior:
                                    score += 25
                                elif ax < 0 and diferencia_anterior > diferencia_siguiente:
                                    score += 25
                                elif ax == 0:
                                    score += 20
                            
                            # BONUS ESPECIAL para último punto
                            if es_ultimo:
                                if "der" in nombre:
                                    score += 35
                                if "centro" in nombre:
                                    score += 20
                            
                            # Preferir posiciones apropiadas por proceso
                            if proceso == 'CCM' and "arriba" in nombre:
                                score += 25
                            elif proceso == 'PRR' and "abajo" in nombre:
                                score += 25
                            
                            # Penalizar posiciones extremas
                            if "alto" in nombre or "bajo" in nombre:
                                score -= 10
                            
                            if score > mejor_score:
                                mejor_score = score
                                mejor_pos = (ax, ay)
                        
                        return mejor_pos
                    
                    # ANOTACIONES ULTRA-INTELIGENTES para sin asignar
                    etiquetas_sin_asignar_colocadas = []
                    
                    for i, (fecha, valor, mostrar) in enumerate(zip(datos_proceso['fecha'], datos_proceso['sin_asignar'], mostrar_etiqueta)):
                        if mostrar or i == len(datos_proceso) - 1:  # SIEMPRE mostrar el último punto
                            # Obtener valores de otros procesos en la misma fecha
                            otros_valores = []
                            for otro_proc in ['CCM', 'PRR']:
                                if otro_proc != proceso:
                                    otros_datos = historico_reciente[historico_reciente['proceso'] == otro_proc]
                                    otros_en_fecha = otros_datos[otros_datos['fecha'] == fecha]
                                    if not otros_en_fecha.empty:
                                        otros_valores.append(otros_en_fecha['sin_asignar'].iloc[0])
                            
                            # Calcular diferencias con puntos adyacentes
                            diff_anterior = abs(valor - datos_proceso['sin_asignar'].iloc[i-1]) if i > 0 else 0
                            diff_siguiente = abs(valor - datos_proceso['sin_asignar'].iloc[i+1]) if i < len(datos_proceso)-1 else 0
                            
                            # Encontrar mejor posición
                            ax_offset, ay_offset = encontrar_mejor_posicion_sin_asignar(
                                valor, otros_valores, diff_anterior, diff_siguiente, proceso, i == len(datos_proceso)-1
                            )
                            
                            # ANTI-COLISIÓN
                            posicion_actual = (fecha, valor + ay_offset)
                            colision_detectada = False
                            
                            for fecha_ant, y_ant in etiquetas_sin_asignar_colocadas:
                                if abs((fecha - fecha_ant).days) <= 2 and abs(y_ant - (valor + ay_offset)) < 15:
                                    colision_detectada = True
                                    break
                            
                            # Si hay colisión, ajustar posición
                            if colision_detectada:
                                if proceso == 'CCM':
                                    ay_offset = -45 if ay_offset > -40 else -25
                                    ax_offset = 35 if ax_offset >= 0 else -35
                                else:  # PRR
                                    ay_offset = 45 if ay_offset < 40 else 25
                                    ax_offset = -35 if ax_offset <= 0 else 35
                            
                            etiquetas_sin_asignar_colocadas.append((fecha, valor + ay_offset))
                            
                            fig.add_annotation(
                                x=fecha,
                                y=valor,
                                text=f'{valor:,}',
                                showarrow=True,
                                arrowhead=1,
                                arrowsize=0.8,
                                arrowwidth=1,
                                arrowcolor=colores_sin_asignar[proceso],
                                ax=ax_offset,
                                ay=ay_offset,
                                font=dict(size=10, color=colores_sin_asignar[proceso], family="Arial"),
                                bgcolor="rgba(255,255,255,0.9)",
                                bordercolor=colores_sin_asignar[proceso],
                                borderwidth=1
                            )
            
            # Total combinado CON ANOTACIONES
            if len(historico_reciente['proceso'].unique()) > 1:
                totales_fecha = historico_reciente.groupby('fecha')['sin_asignar'].sum().reset_index()
                totales_fecha = totales_fecha.sort_values('fecha')
                n_total = len(totales_fecha)
                
                # Estrategia con MÁS ETIQUETAS para el total
                if n_total <= 8:
                    mostrar_total = [True for i in range(n_total)]
                elif n_total <= 15:
                    mostrar_total = [i % 2 == 0 for i in range(n_total)]
                elif n_total <= 22:
                    mostrar_total = [i % 2 == 0 or i == n_total-1 for i in range(n_total)]
                else:
                    mostrar_total = [i % 3 == 0 or i == n_total-1 or i == n_total//2 for i in range(n_total)]
                
                fig.add_trace(go.Scatter(
                    x=totales_fecha['fecha'],
                    y=totales_fecha['sin_asignar'],
                    mode='lines+markers',
                    name='Total',
                    line=dict(width=5, color='#8E44AD', dash='dot'),
                    marker=dict(size=12, color='#8E44AD',
                              line=dict(width=2, color='white'),
                              symbol='diamond'),
                    connectgaps=False,
                    hovertemplate='<b style="color:#8E44AD">TOTAL</b><br>' +
                                'Fecha: %{x}<br>' +
                                'Sin Asignar: %{y:,}<br>' +
                                '<extra></extra>'
                ))
                
                # FUNCIÓN INTELIGENTE para el total de sin asignar
                def encontrar_mejor_posicion_total_sin_asignar(valor_actual, diferencia_anterior, diferencia_siguiente, es_ultimo=False):
                    """
                    Algoritmo inteligente para posicionar etiquetas del total sin asignar
                    """
                    candidatos = [
                        (0, -30, "arriba_centro"),
                        (25, -20, "arriba_der"),
                        (-25, -20, "arriba_izq"),
                        (35, -10, "der_arriba"),
                        (-35, -10, "izq_arriba"),
                        (0, -40, "arriba_alto"),
                        (40, 0, "der_centro"),
                        (-40, 0, "izq_centro")
                    ]
                    
                    mejor_score = -1000
                    mejor_pos = (0, -30)
                    
                    for ax, ay, nombre in candidatos:
                        score = 40  # Bonus base para total
                        
                        # ANÁLISIS DE ESPACIO LATERAL
                        if diferencia_anterior and diferencia_siguiente:
                            if ax > 0 and diferencia_siguiente > diferencia_anterior:
                                score += 30
                            elif ax < 0 and diferencia_anterior > diferencia_siguiente:
                                score += 30
                            elif ax == 0:
                                score += 25
                        
                        # BONUS para último punto
                        if es_ultimo:
                            if "der" in nombre:
                                score += 40
                            if "centro" in nombre:
                                score += 25
                        
                        # Preferir posiciones arriba para el total
                        if "arriba" in nombre:
                            score += 20
                        
                        # Penalizar posiciones extremas
                        if "alto" in nombre:
                            score -= 5
                        
                        if score > mejor_score:
                            mejor_score = score
                            mejor_pos = (ax, ay)
                    
                    return mejor_pos
                
                # ANOTACIONES INTELIGENTES para el total de sin asignar
                etiquetas_total_sin_asignar_colocadas = []
                
                for i, (fecha, valor, mostrar) in enumerate(zip(totales_fecha['fecha'], totales_fecha['sin_asignar'], mostrar_total)):
                    if mostrar or i == len(totales_fecha) - 1:  # SIEMPRE mostrar el último punto
                        # Calcular diferencias con puntos adyacentes
                        diff_anterior = abs(valor - totales_fecha['sin_asignar'].iloc[i-1]) if i > 0 else 0
                        diff_siguiente = abs(valor - totales_fecha['sin_asignar'].iloc[i+1]) if i < len(totales_fecha)-1 else 0
                        
                        # Encontrar mejor posición
                        ax_offset, ay_offset = encontrar_mejor_posicion_total_sin_asignar(
                            valor, diff_anterior, diff_siguiente, i == len(totales_fecha)-1
                        )
                        
                        # ANTI-COLISIÓN para el total
                        posicion_actual = (fecha, valor + ay_offset)
                        colision_detectada = False
                        
                        for fecha_ant, y_ant in etiquetas_total_sin_asignar_colocadas:
                            if abs((fecha - fecha_ant).days) <= 2 and abs(y_ant - (valor + ay_offset)) < 20:
                                colision_detectada = True
                                break
                        
                        # Si hay colisión, ajustar
                        if colision_detectada:
                            ay_offset = -45 if ay_offset > -35 else -25
                            ax_offset = 40 if ax_offset >= 0 else -40
                        
                        etiquetas_total_sin_asignar_colocadas.append((fecha, valor + ay_offset))
                        
                        fig.add_annotation(
                            x=fecha,
                            y=valor,
                            text=f'{valor:,}',
                            showarrow=True,
                            arrowhead=1,
                            arrowsize=0.8,
                            arrowwidth=1,
                            arrowcolor='#8E44AD',
                            ax=ax_offset,
                            ay=ay_offset,
                            font=dict(size=11, color='#8E44AD', family="Arial", weight="bold"),
                            bgcolor="rgba(255,255,255,0.9)",
                            bordercolor='#8E44AD',
                            borderwidth=1
                        )
            
            # Layout moderno y compacto
            fig.update_layout(
                title={
                    'text': "📊 Casos Sin Asignar - Últimos 30 días",
                    'x': 0.5,
                    'xanchor': 'center',
                    'font': {'size': 18, 'color': '#2C3E50', 'family': 'Arial Black'}
                },
                xaxis_title="📅 Fecha",
                yaxis_title="⚠️ Sin Asignar",
                xaxis=dict(
                    showgrid=True,
                    gridwidth=1,
                    gridcolor='rgba(128,128,128,0.2)',
                    tickformat="%d/%m",
                    tickangle=0,
                    dtick="D2",  # Cada 2 días para mejor legibilidad
                    tickfont=dict(size=11, color='#34495E'),
                    title_font=dict(size=14, color='#2C3E50', family='Arial Black')
                ),
                yaxis=dict(
                    rangemode='tozero',
                    showgrid=True,
                    gridwidth=1,
                    gridcolor='rgba(128,128,128,0.2)',
                    tickfont=dict(size=11, color='#34495E'),
                    title_font=dict(size=14, color='#2C3E50', family='Arial Black')
                ),
                hovermode='x unified',
                height=500,  # Aumentado de 350 a 500 para más espacio
                plot_bgcolor='rgba(248,249,250,0.8)',
                paper_bgcolor='white',
                margin=dict(l=80, r=80, t=100, b=80),  # Márgenes aumentados
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="center",
                    x=0.5,
                    bgcolor='rgba(255,255,255,0.9)',
                    bordercolor='rgba(128,128,128,0.3)',
                    borderwidth=1,
                    font=dict(size=12, color='#2C3E50', family='Arial Black')
                ),
                showlegend=True
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Resumen actual mejorado
            ultimo_registro = historico_reciente.groupby('proceso')['sin_asignar'].last()
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if 'CCM' in ultimo_registro:
                    st.metric("🔴 CCM Actual", f"{ultimo_registro['CCM']:,}", 
                             help="Casos CCM sin asignar actualmente")
            
            with col2:
                if 'PRR' in ultimo_registro:
                    st.metric("🟠 PRR Actual", f"{ultimo_registro['PRR']:,}", 
                             help="Casos PRR sin asignar actualmente")
            
            with col3:
                total_actual = ultimo_registro.sum()
                st.metric("⚠️ Total Actual", f"{total_actual:,}", 
                         help="Total de casos sin asignar")
                
        else:
            st.warning("📊 No hay datos recientes de casos sin asignar")
    else:
        st.error("❌ No hay histórico de sin asignar disponible")

def mostrar_panel_control_estado(consolidadas: dict, ccm: dict, prr: dict) -> None:
    """
    Panel de control eliminado - se movió arriba en KPIs
    """
    pass  # Función eliminada según solicitud

def mostrar_ingresos_vs_trabajados_lineal(df_ccm: pd.DataFrame, df_prr: pd.DataFrame) -> None:
    """
    Muestra gráficos separados de ingresos vs trabajados para CCM y PRR
    """
    st.markdown("""
    <div style="background: linear-gradient(135deg, #4ECDC4 0%, #44A08D 100%); 
                padding: 20px; border-radius: 15px; margin: 20px 0;">
        <h3 style="color: white; text-align: center; margin: 0;">
            📊 Ingresos vs Trabajados por Proceso
        </h3>
        <p style="color: white; text-align: center; opacity: 0.9; margin: 5px 0;">
            Análisis de flujo de trabajo por proceso
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Calcular datos para ambos procesos
    ccm_data = calcular_datos_ingresos_trabajados(df_ccm, "CCM")
    prr_data = calcular_datos_ingresos_trabajados(df_prr, "PRR")
    
    # Gráfico CCM (arriba)
    if not ccm_data.empty:
        fig_ccm = go.Figure()
        n_puntos_ccm = len(ccm_data)
        
        # Estrategia de etiquetas para CCM
        if n_puntos_ccm <= 8:
            mostrar_etiqueta_ccm = [True for i in range(n_puntos_ccm)]
        elif n_puntos_ccm <= 15:
            mostrar_etiqueta_ccm = [i % 2 == 0 for i in range(n_puntos_ccm)]
        elif n_puntos_ccm <= 25:
            mostrar_etiqueta_ccm = [i % 2 == 0 or i == n_puntos_ccm-1 for i in range(n_puntos_ccm)]
        else:
            mostrar_etiqueta_ccm = [i % 3 == 0 or i == n_puntos_ccm-1 or i == n_puntos_ccm//2 for i in range(n_puntos_ccm)]
        
        # Línea de ingresos CCM SIN texto
        fig_ccm.add_trace(go.Scatter(
            x=ccm_data['fecha'],
            y=ccm_data['ingresos'],
            mode='lines+markers',
            name='Ingresos',
            line=dict(color='#3498DB', width=4),
            marker=dict(size=8, color='#3498DB', line=dict(width=2, color='white')),
            hovertemplate='<b>CCM - Ingresos</b><br>Fecha: %{x}<br>Cantidad: %{y}<extra></extra>'
        ))
        
        # Línea de trabajados CCM SIN texto
        fig_ccm.add_trace(go.Scatter(
            x=ccm_data['fecha'],
            y=ccm_data['trabajados'],
            mode='lines+markers',
            name='Trabajados',
            line=dict(color='#E74C3C', width=4, dash='dash'),
            marker=dict(size=8, color='#E74C3C', line=dict(width=2, color='white')),
            hovertemplate='<b>CCM - Trabajados</b><br>Fecha: %{x}<br>Cantidad: %{y}<extra></extra>'
        ))
        
        # FUNCIÓN para encontrar la mejor posición de etiqueta
        def encontrar_mejor_posicion(valor_actual, valor_otra_linea, diferencia_con_anterior, diferencia_con_siguiente, es_ultimo=False):
            """
            Calcula la mejor posición para una etiqueta basada en:
            - Posición relativa a la otra línea
            - Espacio disponible hacia los lados
            - Si es el último punto (prioridad especial)
            """
            posiciones_candidatas = []
            
            # Posiciones básicas: arriba, abajo, izquierda, derecha
            candidatos = [
                (0, -35, "arriba_centro"),
                (0, 35, "abajo_centro"), 
                (-30, -15, "arriba_izq"),
                (30, -15, "arriba_der"),
                (-30, 15, "abajo_izq"),
                (30, 15, "abajo_der"),
                (-40, 0, "izq_centro"),
                (40, 0, "der_centro")
            ]
            
            for ax, ay, nombre in candidatos:
                score = 0
                
                # Bonus si está lejos de la otra línea
                if valor_actual > valor_otra_linea and ay < 0:  # Línea arriba, etiqueta arriba
                    score += 50
                elif valor_actual < valor_otra_linea and ay > 0:  # Línea abajo, etiqueta abajo
                    score += 50
                elif abs(valor_actual - valor_otra_linea) > 100:  # Líneas muy separadas
                    score += 30
                
                # Bonus por espacio lateral disponible
                if diferencia_con_anterior and diferencia_con_siguiente:
                    if ax > 0 and diferencia_con_siguiente > diferencia_con_anterior:  # Más espacio a la derecha
                        score += 20
                    elif ax < 0 and diferencia_con_anterior > diferencia_con_siguiente:  # Más espacio a la izquierda
                        score += 20
                
                # Bonus especial para último punto
                if es_ultimo:
                    if "der" in nombre:  # Preferir derecha para último punto
                        score += 30
                
                # Penalizar posiciones muy extremas si las líneas están cerca
                if abs(valor_actual - valor_otra_linea) < 50 and abs(ax) > 35:
                    score -= 20
                
                posiciones_candidatas.append((score, ax, ay, nombre))
            
            # Retornar la mejor posición
            mejor = max(posiciones_candidatas, key=lambda x: x[0])
            return mejor[1], mejor[2]  # ax, ay
        
        # ANOTACIONES ULTRA-INTELIGENTES para CCM
        for i, (fecha, valor_ing, valor_trab, mostrar) in enumerate(zip(ccm_data['fecha'], ccm_data['ingresos'], ccm_data['trabajados'], mostrar_etiqueta_ccm)):
            if mostrar or i == len(ccm_data) - 1:
                # Calcular diferencias con puntos adyacentes para análisis de espacio
                diff_anterior = abs(valor_ing - ccm_data['ingresos'].iloc[i-1]) if i > 0 else 0
                diff_siguiente = abs(valor_ing - ccm_data['ingresos'].iloc[i+1]) if i < len(ccm_data)-1 else 0
                
                # Encontrar mejor posición para ingresos
                ax_ing, ay_ing = encontrar_mejor_posicion(
                    valor_ing, valor_trab, diff_anterior, diff_siguiente, i == len(ccm_data)-1
                )
                
                fig_ccm.add_annotation(
                    x=fecha, y=valor_ing, text=f'{valor_ing}',
                    showarrow=True, arrowhead=1, arrowsize=0.8, arrowwidth=1,
                    arrowcolor='#3498DB', ax=ax_ing, ay=ay_ing,
                    font=dict(size=9, color='#3498DB', family="Arial"),
                    bgcolor="rgba(255,255,255,0.9)", bordercolor='#3498DB', borderwidth=1
                )
                
                # Calcular diferencias para trabajados
                diff_anterior_trab = abs(valor_trab - ccm_data['trabajados'].iloc[i-1]) if i > 0 else 0
                diff_siguiente_trab = abs(valor_trab - ccm_data['trabajados'].iloc[i+1]) if i < len(ccm_data)-1 else 0
                
                # Encontrar mejor posición para trabajados (evitando la posición de ingresos)
                ax_trab, ay_trab = encontrar_mejor_posicion(
                    valor_trab, valor_ing, diff_anterior_trab, diff_siguiente_trab, i == len(ccm_data)-1
                )
                
                # Ajustar si está muy cerca de la etiqueta de ingresos
                if abs(ax_trab - ax_ing) < 20 and abs(ay_trab - ay_ing) < 20:
                    if valor_trab > valor_ing:
                        ay_trab = -40  # Forzar arriba si trabajados > ingresos
                    else:
                        ay_trab = 40   # Forzar abajo si trabajados < ingresos
                    ax_trab = -ax_ing  # Lado opuesto
                
                fig_ccm.add_annotation(
                    x=fecha, y=valor_trab, text=f'{valor_trab}',
                    showarrow=True, arrowhead=1, arrowsize=0.8, arrowwidth=1,
                    arrowcolor='#E74C3C', ax=ax_trab, ay=ay_trab,
                    font=dict(size=9, color='#E74C3C', family="Arial"),
                    bgcolor="rgba(255,255,255,0.9)", bordercolor='#E74C3C', borderwidth=1
                )
        
        # Configuración CCM
        fig_ccm.update_layout(
            title={
                'text': "🔵 CCM - Flujo de Trabajo",
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 16, 'color': '#2C3E50', 'family': 'Arial Black'}
            },
            xaxis_title="Fecha",
            yaxis_title="Cantidad",
            height=500,  # Aumentado de 400 a 500
            plot_bgcolor='rgba(248,249,250,0.8)',
            paper_bgcolor='white',
            hovermode='x unified',
            margin=dict(l=80, r=80, t=100, b=80),  # Márgenes aumentados
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="center",
                x=0.5
            )
        )
        
        st.plotly_chart(fig_ccm, use_container_width=True)
        
        # Análisis CCM
        balance_ccm = ccm_data['trabajados'].mean() - ccm_data['ingresos'].mean()
        if balance_ccm > 0:
            st.success(f"✅ CCM: Superávit de {balance_ccm:.1f} casos/día")
        elif balance_ccm < 0:
            st.error(f"⚠️ CCM: Déficit de {abs(balance_ccm):.1f} casos/día")
        else:
            st.info("🎯 CCM: Equilibrio perfecto")
    else:
        st.warning("No hay datos suficientes para CCM")
    
    # Separador visual
    st.markdown("---")
    
    # Gráfico PRR (abajo)
    if not prr_data.empty:
        fig_prr = go.Figure()
        n_puntos_prr = len(prr_data)
        
        # Estrategia de etiquetas para PRR
        if n_puntos_prr <= 8:
            mostrar_etiqueta_prr = [True for i in range(n_puntos_prr)]
        elif n_puntos_prr <= 15:
            mostrar_etiqueta_prr = [i % 2 == 0 for i in range(n_puntos_prr)]
        elif n_puntos_prr <= 25:
            mostrar_etiqueta_prr = [i % 2 == 0 or i == n_puntos_prr-1 for i in range(n_puntos_prr)]
        else:
            mostrar_etiqueta_prr = [i % 3 == 0 or i == n_puntos_prr-1 or i == n_puntos_prr//2 for i in range(n_puntos_prr)]
        
        # Línea de ingresos PRR SIN texto
        fig_prr.add_trace(go.Scatter(
            x=prr_data['fecha'],
            y=prr_data['ingresos'],
            mode='lines+markers',
            name='Ingresos',
            line=dict(color='#9B59B6', width=4),
            marker=dict(size=8, color='#9B59B6', line=dict(width=2, color='white')),
            hovertemplate='<b>PRR - Ingresos</b><br>Fecha: %{x}<br>Cantidad: %{y}<extra></extra>'
        ))
        
        # Línea de trabajados PRR SIN texto
        fig_prr.add_trace(go.Scatter(
            x=prr_data['fecha'],
            y=prr_data['trabajados'],
            mode='lines+markers',
            name='Trabajados',
            line=dict(color='#F39C12', width=4, dash='dash'),
            marker=dict(size=8, color='#F39C12', line=dict(width=2, color='white')),
            hovertemplate='<b>PRR - Trabajados</b><br>Fecha: %{x}<br>Cantidad: %{y}<extra></extra>'
        ))
        
        # ANOTACIONES ULTRA-INTELIGENTES para PRR (usando la misma función)
        for i, (fecha, valor_ing, valor_trab, mostrar) in enumerate(zip(prr_data['fecha'], prr_data['ingresos'], prr_data['trabajados'], mostrar_etiqueta_prr)):
            if mostrar or i == len(prr_data) - 1:
                # Calcular diferencias con puntos adyacentes para análisis de espacio
                diff_anterior = abs(valor_ing - prr_data['ingresos'].iloc[i-1]) if i > 0 else 0
                diff_siguiente = abs(valor_ing - prr_data['ingresos'].iloc[i+1]) if i < len(prr_data)-1 else 0
                
                # Encontrar mejor posición para ingresos
                ax_ing, ay_ing = encontrar_mejor_posicion(
                    valor_ing, valor_trab, diff_anterior, diff_siguiente, i == len(prr_data)-1
                )
                
                fig_prr.add_annotation(
                    x=fecha, y=valor_ing, text=f'{valor_ing}',
                    showarrow=True, arrowhead=1, arrowsize=0.8, arrowwidth=1,
                    arrowcolor='#9B59B6', ax=ax_ing, ay=ay_ing,
                    font=dict(size=9, color='#9B59B6', family="Arial"),
                    bgcolor="rgba(255,255,255,0.9)", bordercolor='#9B59B6', borderwidth=1
                )
                
                # Calcular diferencias para trabajados
                diff_anterior_trab = abs(valor_trab - prr_data['trabajados'].iloc[i-1]) if i > 0 else 0
                diff_siguiente_trab = abs(valor_trab - prr_data['trabajados'].iloc[i+1]) if i < len(prr_data)-1 else 0
                
                # Encontrar mejor posición para trabajados (evitando la posición de ingresos)
                ax_trab, ay_trab = encontrar_mejor_posicion(
                    valor_trab, valor_ing, diff_anterior_trab, diff_siguiente_trab, i == len(prr_data)-1
                )
                
                # Ajustar si está muy cerca de la etiqueta de ingresos
                if abs(ax_trab - ax_ing) < 20 and abs(ay_trab - ay_ing) < 20:
                    if valor_trab > valor_ing:
                        ay_trab = -40  # Forzar arriba si trabajados > ingresos
                    else:
                        ay_trab = 40   # Forzar abajo si trabajados < ingresos
                    ax_trab = -ax_ing  # Lado opuesto
                
                fig_prr.add_annotation(
                    x=fecha, y=valor_trab, text=f'{valor_trab}',
                    showarrow=True, arrowhead=1, arrowsize=0.8, arrowwidth=1,
                    arrowcolor='#F39C12', ax=ax_trab, ay=ay_trab,
                    font=dict(size=9, color='#F39C12', family="Arial"),
                    bgcolor="rgba(255,255,255,0.9)", bordercolor='#F39C12', borderwidth=1
                )
        
        # Configuración PRR
        fig_prr.update_layout(
            title={
                'text': "🟠 PRR - Flujo de Trabajo",
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 16, 'color': '#2C3E50', 'family': 'Arial Black'}
            },
            xaxis_title="Fecha",
            yaxis_title="Cantidad",
            height=500,  # Aumentado de 400 a 500
            plot_bgcolor='rgba(248,249,250,0.8)',
            paper_bgcolor='white',
            hovermode='x unified',
            margin=dict(l=80, r=80, t=100, b=80),  # Márgenes aumentados
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="center",
                x=0.5
            )
        )
        
        st.plotly_chart(fig_prr, use_container_width=True)
        
        # Análisis PRR
        balance_prr = prr_data['trabajados'].mean() - prr_data['ingresos'].mean()
        if balance_prr > 0:
            st.success(f"✅ PRR: Superávit de {balance_prr:.1f} casos/día")
        elif balance_prr < 0:
            st.error(f"⚠️ PRR: Déficit de {abs(balance_prr):.1f} casos/día")
        else:
            st.info("🎯 PRR: Equilibrio perfecto")
    else:
        st.warning("No hay datos suficientes para PRR")

def calcular_datos_ingresos_trabajados(df: pd.DataFrame, proceso: str) -> pd.DataFrame:
    """
    Calcula datos de ingresos vs trabajados para un proceso (últimos 30 días)
    """
    try:
        # Preparar fechas
        df['FechaExpendiente'] = pd.to_datetime(df['FechaExpendiente'], errors='coerce')
        df['FechaPre'] = pd.to_datetime(df['FechaPre'], errors='coerce')
        
        # Últimos 30 días
        fecha_max = max(df['FechaExpendiente'].max(), df['FechaPre'].max())
        fecha_min = fecha_max - pd.Timedelta(days=30)
        
        # Calcular ingresos por día
        ingresos_df = df[df['FechaExpendiente'] >= fecha_min]
        ingresos_por_dia = ingresos_df.groupby('FechaExpendiente')['NumeroTramite'].count().reset_index()
        ingresos_por_dia.columns = ['fecha', 'ingresos']
        
        # Calcular trabajados por día
        trabajados_df = df[df['FechaPre'] >= fecha_min]
        trabajados_por_dia = trabajados_df.groupby('FechaPre')['NumeroTramite'].count().reset_index()
        trabajados_por_dia.columns = ['fecha', 'trabajados']
        
        # Combinar datos
        datos_combinados = pd.merge(ingresos_por_dia, trabajados_por_dia, on='fecha', how='outer')
        datos_combinados = datos_combinados.fillna(0)
        datos_combinados = datos_combinados.sort_values('fecha')
        
        return datos_combinados
    except Exception:
        return pd.DataFrame()

def mostrar_tabla_comparativa(ccm: dict, prr: dict) -> None:
    """
    Muestra tabla comparativa simple entre procesos
    """
    st.markdown("#### ⚖️ Comparación por Proceso")
    
    # Crear tabla comparativa simple sin emojis en columnas
    data_comparativa = {
        'Métrica': [
            'Pendientes Totales', 
            'Sin Asignar', 
            'Operadores Activos', 
            'Producción Diaria',
            'Ingresos Diarios',
            'Promedio/Operador'
        ],
        'CCM': [
            f"{ccm['total_pendientes']:,}", 
            f"{ccm['sin_asignar']:,}", 
            ccm['operadores_activos'], 
            f"{ccm['produccion_diaria']:.1f}",
            f"{ccm['ingresos_diarios']:.1f}",
            f"{ccm['promedio_por_operador']:.1f}"
        ],
        'PRR': [
            f"{prr['total_pendientes']:,}", 
            f"{prr['sin_asignar']:,}", 
            prr['operadores_activos'], 
            f"{prr['produccion_diaria']:.1f}",
            f"{prr['ingresos_diarios']:.1f}",
            f"{prr['promedio_por_operador']:.1f}"
        ]
    }
    
    df_comparativo = pd.DataFrame(data_comparativa)
    
    # Mostrar tabla con estilo simple
    st.dataframe(df_comparativo, use_container_width=True, hide_index=True)
    
    # Análisis comparativo
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total_pendientes = ccm['total_pendientes'] + prr['total_pendientes']
        porcentaje_ccm = (ccm['total_pendientes'] / total_pendientes * 100) if total_pendientes > 0 else 0
        st.metric("📈 Distribución CCM", f"{porcentaje_ccm:.1f}%", 
                 help="Porcentaje de pendientes que corresponden a CCM")
    
    with col2:
        porcentaje_prr = (prr['total_pendientes'] / total_pendientes * 100) if total_pendientes > 0 else 0
        st.metric("📈 Distribución PRR", f"{porcentaje_prr:.1f}%", 
                 help="Porcentaje de pendientes que corresponden a PRR")
    
    with col3:
        eficiencia_ccm = (ccm['produccion_diaria'] / ccm['ingresos_diarios'] * 100) if ccm['ingresos_diarios'] > 0 else 0
        eficiencia_prr = (prr['produccion_diaria'] / prr['ingresos_diarios'] * 100) if prr['ingresos_diarios'] > 0 else 0
        mejor_eficiencia = "CCM" if eficiencia_ccm > eficiencia_prr else "PRR"
        st.metric("🏆 Mayor Eficiencia", mejor_eficiencia, 
                 help=f"CCM: {eficiencia_ccm:.1f}% | PRR: {eficiencia_prr:.1f}%")
    
    # Información explicativa
    st.info("💡 **Promedio/Operador:** Casos pendientes asignados por operador activo (instantánea actual).") 