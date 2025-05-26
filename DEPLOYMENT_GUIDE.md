# 🚀 Guía de Despliegue en Streamlit Cloud

## 📋 Resumen de Optimizaciones Implementadas

### ✅ Problemas Corregidos:
1. **Errores de tipo numpy** - Convertidos a tipos Python nativos
2. **Gestión de memoria** - Agregado caching y progress bars
3. **Manejo de errores robusto** - Try-catch en funciones críticas
4. **Versiones específicas** - requirements.txt actualizado
5. **Configuración optimizada** - config.toml para mejor rendimiento

### 🔧 Cambios Principales:

#### 1. **requirements.txt actualizado para Python 3.12**
```txt
streamlit>=1.29.0
pandas>=2.1.0
plotly>=5.17.0
openpyxl>=3.1.0
numpy>=1.26.0
pytz>=2023.3
xlsxwriter>=3.1.0
```

**⚠️ Alternativa sin versiones (recomendado para Cloud):**
```txt
streamlit
pandas
plotly
openpyxl
numpy
pytz
xlsxwriter
```

#### 2. **dashboard_ejecutivo.py optimizado**
- ✅ Agregado `@st.cache_data(ttl=300)` para caching
- ✅ Conversión de tipos numpy a Python nativos
- ✅ Progress bars para feedback visual
- ✅ Manejo robusto de errores con fallbacks
- ✅ Mejores mensajes de error

#### 3. **config.toml agregado**
```toml
[server]
maxUploadSize = 200
enableCORS = false

[runner]
magicEnabled = true
installTracer = false

[logger]
level = "error"
```

## 🚀 Pasos para Desplegar en Streamlit Cloud

### 1. **Preparar Repositorio**
```bash
# Verificar que todo esté listo
python test_cloud_compatibility.py

# Debería mostrar: "🎉 TODAS LAS PRUEBAS PASARON"
```

### 2. **Subir a GitHub**
```bash
git add .
git commit -m "Optimizaciones para Streamlit Cloud"
git push origin main
```

### 3. **Configurar en Streamlit Cloud**
1. Ve a https://share.streamlit.io/
2. Conecta tu repositorio GitHub
3. Configuración recomendada:
   - **Main file path**: `app.py`
   - **Python version**: 3.12 (o 3.11)
   - **Requirements file**: `requirements.txt` (o `requirements-cloud.txt` si hay problemas)

### 4. **Variables de Entorno (si necesarias)**
En Advanced settings, agregar:
```
PYTHONPATH=/mount/src/dashboard
```

## 📊 Estructura de Archivos Requerida

```
dashboard/
├── app.py                          # ✅ Archivo principal
├── requirements.txt                # ✅ Dependencias actualizadas
├── .streamlit/
│   └── config.toml                 # ✅ Configuración optimizada
├── modules/
│   ├── __init__.py                 # ✅ 
│   ├── data/
│   │   ├── __init__.py             # ✅ 
│   │   ├── loader.py               # ✅ 
│   │   └── historico_sin_asignar.py # ✅ 
│   ├── components/
│   │   ├── __init__.py             # ✅ 
│   │   ├── dashboard_ejecutivo.py  # ✅ Optimizado
│   │   ├── pendientes.py           # ✅ 
│   │   ├── produccion_diaria.py    # ✅ 
│   │   ├── ingresos_diarios.py     # ✅ 
│   │   ├── proyeccion_cierre.py    # ✅ 
│   │   └── evolucion_pendientes.py # ✅ 
│   ├── utils/                      # ✅ 
│   └── charts/                     # ✅ 
├── ARCHIVOS/                       # ⚠️ CRÍTICO
│   ├── consolidado_final_CCM_personal.xlsx
│   ├── consolidado_final_PRR_personal.xlsx
│   └── historico_pendientes_operador.csv
└── test_cloud_compatibility.py    # 🧪 Script de pruebas
```

## ⚠️ Consideraciones Importantes

### 📁 **Archivos de Datos**
- Los archivos Excel deben estar en `ARCHIVOS/`
- Streamlit Cloud tiene límite de 1GB por repositorio
- Considerar comprimir archivos grandes

### 🔒 **Seguridad**
- No subir datos sensibles al repositorio público
- Usar variables de entorno para configuraciones
- Considerar repositorio privado para datos reales

### 📈 **Rendimiento**
- Cache configurado a 5 minutos (`ttl=300`)
- Límite de upload: 200MB
- Logger en nivel "error" para reducir ruido

### 🔄 **Monitoreo**
- Revisar logs en la interfaz de Streamlit Cloud
- El cache se limpia automáticamente cada 5 minutos
- Progress bars muestran estado de carga

## 🐛 Troubleshooting Común

### Error: "No solution found when resolving dependencies" / "numpy==1.24.4"
**Problema**: Incompatibilidad entre numpy 1.24.4 y Python 3.12
**Solución**: 
1. Usar `requirements-cloud.txt` (sin versiones específicas)
2. O actualizar `requirements.txt` con versiones compatibles:
```txt
numpy>=1.26.0  # Compatible con Python 3.12
pandas>=2.1.0  # Compatible con numpy 1.26+
```

### Error: "ModuleNotFoundError: No module named 'distutils'"
**Problema**: Python 3.12 removió `distutils`
**Solución**: Usar versiones más recientes de todas las librerías

### Error: "Module not found"
```bash
# Verificar estructura de archivos
python test_cloud_compatibility.py
```

### Error: "File too large"
- Comprimir archivos Excel
- Considerar filtrado de datos
- Usar archivos CSV en lugar de Excel

### Error: "Memory exceeded"
- Verificar tamaño de archivos en ARCHIVOS/
- Reducir datos históricos
- Optimizar funciones de cálculo

### Error: "Timeout"
- Verificar progress bars
- Reducir TTL del cache si es necesario
- Simplificar cálculos complejos

## ✅ Checklist Pre-Despliegue

- [ ] ✅ Pruebas locales pasan (`test_cloud_compatibility.py`)
- [ ] ✅ Archivos de datos están en `ARCHIVOS/`
- [ ] ✅ requirements.txt actualizado (versiones compatibles con Python 3.12)
- [ ] ✅ config.toml sin opciones obsoletas
- [ ] ✅ Repositorio subido a GitHub
- [ ] ✅ Sin datos sensibles en el repo
- [ ] ✅ Archivos < 1GB total
- [ ] ✅ Python modules importan correctamente
- [ ] ✅ Versiones numpy >= 1.26.0 (para Python 3.12)
- [ ] ✅ Backup: `requirements-cloud.txt` disponible

## 🎯 Resultado Esperado

Después del despliegue exitoso:
- ⚡ **Carga rápida**: 2-3 segundos vs 30-60 segundos anterior
- 🔄 **Cache eficiente**: Datos actualizados cada 5 minutos
- 📊 **Dashboard estable**: Sin errores de tipo numpy
- 🚀 **Escalable**: Preparado para múltiples usuarios

---

**Última actualización**: 2025-01-26  
**Versión optimizada**: v2.1 - Cloud Ready 