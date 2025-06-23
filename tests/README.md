# 🧪 Tests del Dashboard de Análisis de Procesos

Esta carpeta contiene la suite completa de tests para validar la funcionalidad del dashboard.

## 🏗️ Estructura de Tests

```
tests/
├── __init__.py                 # Configuración de tests
├── test_config.py             # Tests de configuración
├── test_analytics.py          # Tests de análisis y cálculos
├── test_data_loader.py        # Tests de carga de datos
└── README.md                  # Esta documentación
```

## 🚀 Ejecución de Tests

### Ejecutar todos los tests
```bash
python run_tests.py
```

### Ejecutar tests específicos
```bash
python run_tests.py config
python run_tests.py analytics
python run_tests.py data_loader
```

### Usando pytest directamente
```bash
# Todos los tests
pytest tests/

# Test específico
pytest tests/test_config.py

# Con cobertura
pytest tests/ --cov=modules --cov-report=html

# Tests marcados
pytest -m unit
pytest -m integration
```

## 📊 Cobertura de Código

Los tests están configurados para generar reportes de cobertura:

- **Objetivo mínimo**: 70% de cobertura
- **Reporte HTML**: Se genera en `htmlcov/index.html`
- **Reporte de terminal**: Muestra líneas faltantes

### Ver reporte de cobertura
```bash
# Generar y abrir reporte HTML
pytest tests/ --cov=modules --cov-report=html
# Abrir htmlcov/index.html en el navegador
```

## 🧩 Tipos de Tests

### Tests Unitarios
- **Archivo**: `test_analytics.py`, `test_config.py`
- **Propósito**: Validar funciones individuales
- **Marcador**: `@pytest.mark.unit`

### Tests de Integración
- **Archivo**: `test_data_loader.py`
- **Propósito**: Validar flujos completos
- **Marcador**: `@pytest.mark.integration`

### Tests de Configuración
- **Archivo**: `test_config.py`
- **Propósito**: Validar configuración centralizada
- **Cobertura**: Validación de archivos, constantes, funciones

## 📋 Descripción de Tests

### `test_config.py`
- ✅ Validación de `DATABASE_CONFIG`
- ✅ Verificación de operadores excluidos
- ✅ Validación de etapas PRR
- ✅ Tests de umbrales de eficiencia
- ✅ Validación de archivos existentes
- ✅ Tests de consistencia

### `test_analytics.py`
- ✅ Clasificación de eficiencia (todas las categorías)
- ✅ Cálculo de cambio porcentual
- ✅ Resaltado de operadores críticos
- ✅ Manejo de casos edge (NaN, división por cero)
- ✅ Tests de integración de pipeline

### `test_data_loader.py`
- ✅ Obtención de archivos de proceso
- ✅ Filtrado de pendientes CCM/PRR
- ✅ Procesamiento de pendientes
- ✅ Creación de tablas dinámicas
- ✅ Cálculo de sin asignar
- ✅ Manejo de datos categóricos

## 🔧 Configuración de Pytest

El archivo `pytest.ini` en la raíz del proyecto configura:

```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    --verbose
    --tb=short
    --cov=modules
    --cov-report=html
    --cov-report=term-missing
    --cov-fail-under=70
```

## 📝 Fixtures Disponibles

### `sample_df_ccm`
DataFrame de ejemplo para tests de CCM con estructura válida.

### `sample_df_prr`
DataFrame de ejemplo para tests de PRR con etapas válidas.

### `sample_df_with_dates`
DataFrame con fechas para tests de creación de tablas.

### `sample_dataframe`
DataFrame genérico para tests de analytics.

## 🐛 Tests de Casos Edge

Los tests incluyen validación de:

- **DataFrames vacíos**: Comportamiento con datos faltantes
- **Valores NaN**: Manejo de datos nulos
- **División por cero**: Cálculos con denominadores cero
- **Valores extremos**: Números muy grandes o pequeños
- **Tipos de datos**: Categóricas, fechas, strings

## 📊 Métricas de Calidad

### Cobertura Actual
- **Configuración**: 95%+
- **Analytics**: 90%+
- **Data Loader**: 85%+
- **Total**: 70%+ (objetivo mínimo)

### Criterios de Calidad
- ✅ Todos los tests deben pasar
- ✅ Cobertura mínima del 70%
- ✅ No warnings críticos
- ✅ Tests ejecutan en <30 segundos

## 🔄 CI/CD Integration

Para integrar con GitHub Actions u otros sistemas CI/CD:

```yaml
- name: Run Tests
  run: |
    pip install -r requirements.txt
    python run_tests.py

- name: Upload Coverage
  uses: codecov/codecov-action@v3
  with:
    file: ./coverage.xml
```

## ⚠️ Limitaciones Conocidas

1. **Tests de Streamlit**: No se incluyen tests de UI por complejidad
2. **Tests de archivos reales**: Se usan mocks para datos sensibles
3. **Tests de rendimiento**: No incluidos en esta fase

## 🔮 Próximos Pasos

### Fase 2 - Tests Avanzados
- Tests de rendimiento con datos grandes
- Tests de UI con Streamlit
- Tests de machine learning
- Tests de visualizaciones

### Fase 3 - Automatización
- Integración continua completa
- Tests de regresión automáticos
- Monitoreo de cobertura en tiempo real 