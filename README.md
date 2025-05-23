# 📊 Dashboard de Análisis de Procesos

Un dashboard interactivo desarrollado en Streamlit para el análisis y seguimiento de procesos CCM (Carnet de Extranjería) y PRR (Permiso de Residencia y Refugio), diseñado para optimizar la gestión operativa y el análisis de productividad.

## 🚀 Características Principales- **🎯 Dashboard Ejecutivo**: Vista consolidada con KPIs, semáforos y alertas críticas para toma de decisiones- **Análisis de Pendientes**: Seguimiento detallado de expedientes pendientes por operador y año- **Producción Diaria**: Monitoreo de la productividad diaria y por fines de semana- **Ingresos Diarios**: Análisis de tendencias de ingreso de nuevos expedientes- **Proyección de Cierre**: Simulaciones y proyecciones para planificación operativa- **Evolución de Pendientes**: Ranking y evolución histórica por operador- **Exportación a Excel**: Descarga de reportes con formato profesional- **Actualizaciones Automáticas**: Guardado automático del histórico de pendientes

## 🏗️ Arquitectura del Proyecto

### Estructura Modular

```
dashboard/
├── app.py                          # Aplicación principal
├── modules/
│   ├── __init__.py
│   ├── data/
│   │   ├── __init__.py
│   │   └── loader.py               # Carga y procesamiento de datos
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── excel_export.py         # Exportación a Excel
│   │   └── analytics.py            # Análisis y cálculos
│   ├── charts/
│   │   ├── __init__.py
│   │   └── plotting.py             # Gráficos y visualizaciones
│   └── components/
│       ├── __init__.py
│       ├── pendientes.py           # Componente de pendientes
│       ├── produccion_diaria.py    # Componente de producción
│       ├── ingresos_diarios.py     # Componente de ingresos
│       ├── proyeccion_cierre.py    # Componente de proyecciones
│       └── evolucion_pendientes.py # Componente de evolución
├── ARCHIVOS/                       # Directorio de datos
│   ├── consolidado_final_CCM_personal.xlsx
│   ├── consolidado_final_PRR_personal.xlsx
│   └── historico_pendientes_operador.csv
└── README.md
```

## 📋 Requisitos

### Dependencias Python

```python
streamlit>=1.28.0
pandas>=2.0.0
plotly>=5.15.0
openpyxl>=3.1.0
numpy>=1.24.0
pytz>=2023.3
```

## 🔧 Instalación

1. **Clonar o descargar el proyecto**
   ```bash
   git clone <url-del-repositorio>
   cd dashboard
   ```

2. **Instalar dependencias**
   ```bash
   pip install streamlit pandas plotly openpyxl numpy pytz
   ```

3. **Preparar datos**
   - Crear directorio `ARCHIVOS/` en la raíz del proyecto
   - Colocar los archivos Excel de datos:
     - `consolidado_final_CCM_personal.xlsx`
     - `consolidado_final_PRR_personal.xlsx`

4. **Ejecutar la aplicación**
   ```bash
   streamlit run app.py
   ```

## 💻 Uso de la Aplicación

### Inicio de la Aplicación

Una vez ejecutado el comando, la aplicación estará disponible en:
- **URL Local**: http://localhost:8502
- **URL de Red**: http://[tu-ip]:8502

### Navegación

1. **Selección de Proceso**: Utiliza el selector en la barra lateral para elegir entre CCM o PRR
2. **Pestañas Disponibles**:   - 🎯 **Dashboard Ejecutivo**: Vista consolidada para ejecutivos   - 📋 **Pendientes**: Análisis de expedientes pendientes   - 📈 **Producción Diaria**: Métricas de productividad   - 📥 **Ingresos Diarios**: Tendencias de nuevos expedientes   - 🎯 **Proyección de Cierre**: Simulaciones y proyecciones   - 📊 **Evolución Pendientes**: Histórico y ranking por operador

## 📊 Funcionalidades por Pestaña### 🎯 Dashboard Ejecutivo- **KPIs Consolidados**: Métricas principales de ambos procesos (CCM + PRR)- **Semáforos de Estado**: Indicadores visuales de salud del sistema- **Alertas Críticas**: Notificaciones automáticas de situaciones que requieren atención- **Tendencias Ejecutivas**: Gráficos de alto nivel con evolución de métricas clave- **Análisis Comparativo**: Comparación directa entre procesos CCM y PRR- **Métricas de Productividad**: Indicadores de rendimiento y cumplimiento de objetivos### 📋 Pendientes
- **Tabla Dinámica**: Pendientes por operador y año
- **Métricas**: Total de casos sin asignar
- **Exportación**: Descarga en Excel con formato
- **Guardado Automático**: Actualización del histórico

### 📈 Producción Diaria
- **Análisis de Últimos 20 Días**: Productividad reciente
- **Fines de Semana**: Análisis específico de sábados y domingos
- **Resumen Diario**: Estadísticas agregadas
- **Gráficos Interactivos**: Tendencias con líneas de regresión

### 📥 Ingresos Diarios
- **Gráfico de 60 Días**: Evolución de ingresos con tendencias
- **Tabla de 15 Días**: Detalle de ingresos recientes
- **Promedio Semanal**: Análisis de patrones semanales
- **Indicadores de Eficiencia**: Métricas de tiempo de procesamiento

### 🎯 Proyección de Cierre
- **Simulador de Personal**: Configuración de escenarios
- **Métricas de Situación Actual**: Estado presente del proceso
- **Proyecciones**: Estimaciones de cierre y equilibrio
- **Gráficos Predictivos**: Visualización de evolución futura

### 📊 Evolución Pendientes
- **Matriz de Evolución**: Histórico completo por operador
- **Filtros por Año**: Análisis comparativo temporal
- **Ranking de Eficiencia**: Clasificación por rendimiento
- **Gráficos de Dispersión**: Relación productividad vs tendencia

## 🛠️ Módulos del Sistema

### `modules/data/loader.py`
- Carga optimizada con cache de Streamlit
- Filtros específicos por proceso (CCM/PRR)
- Procesamiento de datos históricos
- Funciones de validación y limpieza

### `modules/utils/excel_export.py`
- Exportación con formato profesional
- Resaltado de totales y columnas importantes
- Múltiples tipos de reporte
- Compatibilidad con Excel

### `modules/utils/analytics.py`
- Cálculos de eficiencia avanzados
- Análisis de tendencias
- Métricas de productividad
- Algoritmos de clasificación

### `modules/charts/plotting.py`
- Gráficos interactivos con Plotly
- Líneas de tendencia automáticas
- Visualizaciones personalizadas
- Gráficos de dispersión y evolución

### `modules/components/`
- Componentes modulares por funcionalidad
- Interfaz de usuario organizada
- Lógica de negocio separada
- Reutilización de código

## 🔄 Flujo de Datos

1. **Carga**: Los datos se cargan desde archivos Excel
2. **Procesamiento**: Filtros y transformaciones específicas por proceso
3. **Análisis**: Cálculos de métricas y tendencias
4. **Visualización**: Generación de tablas y gráficos
5. **Exportación**: Descarga de reportes en Excel
6. **Persistencia**: Guardado automático del histórico

## 📈 Métricas y KPIs

### Indicadores de Productividad
- Promedio de expedientes por operador/día
- Total de casos cerrados por período
- Eficiencia individual y de equipo

### Indicadores de Gestión
- Pendientes totales y por operador
- Casos sin asignar
- Tiempo de procesamiento promedio

### Proyecciones
- Días estimados para agotamiento de pendientes
- Personal requerido para equilibrio de flujo
- Simulaciones de escenarios

## 🔒 Consideraciones de Seguridad

- Los datos permanecen locales en el servidor
- No se envía información sensible a servicios externos
- Cache local para optimización de rendimiento
- Validación de datos de entrada

## 🐛 Resolución de Problemas

### Error de Archivos No Encontrados
- Verificar que el directorio `ARCHIVOS/` existe
- Confirmar que los archivos Excel están presentes
- Revisar nombres exactos de archivos

### Problemas de Rendimiento
- El cache de Streamlit optimiza la carga de datos
- Para datos muy grandes, considerar filtrado previo
- Reiniciar la aplicación si el cache se corrompe

### Errores de Datos
- Verificar formato de fechas en Excel
- Confirmar estructura de columnas esperadas
- Revisar encoding de archivos CSV (histórico)

## 🤝 Contribuciones

Para contribuir al proyecto:

1. Hacer fork del repositorio
2. Crear una rama para la nueva funcionalidad
3. Implementar cambios siguiendo la estructura modular
4. Agregar documentación apropiada
5. Enviar pull request con descripción detallada

## 📄 Licencia

Este proyecto está bajo licencia [especificar licencia]. Ver archivo LICENSE para más detalles.

## 👥 Autores

- **Desarrollador Principal**: Adrian Aguirre
- **Análisis de Requerimientos**: Adrian Aguirre

---

**Versión**: 2.0.0 (Modularizada)  
**Tecnologías**: Python, Streamlit, Pandas, Plotly 