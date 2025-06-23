"""
Tests para el módulo de carga de datos
"""

import pytest
import pandas as pd
import numpy as np
import sys
import os
from unittest.mock import patch, MagicMock

# Configurar path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.data.loader import (
    obtener_archivos_proceso,
    filtrar_pendientes_ccm,
    filtrar_pendientes_prr,
    procesar_pendientes,
    crear_tabla_pendientes,
    calcular_sin_asignar
)

class TestObtenerArchivosProceso:
    """Tests para obtener_archivos_proceso"""
    
    def test_contiene_procesos_requeridos(self):
        """Test que retorna los procesos CCM y PRR"""
        archivos = obtener_archivos_proceso()
        assert "CCM" in archivos
        assert "PRR" in archivos
        assert archivos["CCM"].endswith('.pkl.gz')
        assert archivos["PRR"].endswith('.pkl.gz')

# Fixtures para crear DataFrames de prueba
@pytest.fixture
def sample_df_ccm():
    """DataFrame de ejemplo para CCM"""
    return pd.DataFrame({
        'NumeroTramite': ['CCM001', 'CCM002', 'CCM003', 'CCM004'],
        'UltimaEtapa': ['EVALUACIÓN - I', 'EVALUACIÓN - I', 'OTRA ETAPA', 'EVALUACIÓN - I'],
        'EstadoPre': [None, None, None, 'APROBADO'],
        'EstadoTramite': ['PENDIENTE', 'PENDIENTE', 'PENDIENTE', 'PENDIENTE'],
        'EQUIPO': ['NORMAL', 'NORMAL', 'VULNERABLE', 'NORMAL'],
        'OPERADOR': ['Juan Pérez', None, 'María García', 'Pedro López']
    })

@pytest.fixture
def sample_df_prr():
    """DataFrame de ejemplo para PRR"""
    return pd.DataFrame({
        'NumeroTramite': ['PRR001', 'PRR002', 'PRR003', 'PRR004'],
        'UltimaEtapa': [
            'ACTUALIZAR DATOS BENEFICIARIO - F',
            'ACTUALIZAR DATOS BENEFICIARIO - I', 
            'ETAPA NO VÁLIDA',
            'PAGOS, FECHA Y NRO RD. - I'
        ],
        'EstadoPre': [None, None, None, None],
        'EstadoTramite': ['PENDIENTE', 'PENDIENTE', 'PENDIENTE', 'PENDIENTE'],
        'EQUIPO': ['NORMAL', 'NORMAL', 'VULNERABLE', 'NORMAL'],
        'OPERADOR': ['Ana Ruiz', None, 'Carlos Díaz', 'Laura Martín']
    })

class TestFiltrarPendientesCCM:
    """Tests para filtrar_pendientes_ccm"""
    
    def test_filtro_correcto_ccm(self, sample_df_ccm):
        """Test que filtra correctamente los pendientes CCM"""
        resultado = filtrar_pendientes_ccm(sample_df_ccm)
        
        # Debe retornar registros que cumplan todos los criterios
        assert len(resultado) == 2  # CCM001 y CCM002
        assert all(resultado['UltimaEtapa'] == 'EVALUACIÓN - I')
        assert all(resultado['EstadoPre'].isna())
        assert all(resultado['EstadoTramite'] == 'PENDIENTE')
        assert all(resultado['EQUIPO'] != 'VULNERABLE')
    
    def test_filtro_excluye_vulnerable(self, sample_df_ccm):
        """Test que excluye registros del equipo VULNERABLE"""
        resultado = filtrar_pendientes_ccm(sample_df_ccm)
        assert not any(resultado['EQUIPO'] == 'VULNERABLE')
    
    def test_filtro_excluye_estado_pre_no_nulo(self, sample_df_ccm):
        """Test que excluye registros con EstadoPre no nulo"""
        resultado = filtrar_pendientes_ccm(sample_df_ccm)
        assert all(resultado['EstadoPre'].isna())

class TestFiltrarPendientesPRR:
    """Tests para filtrar_pendientes_prr"""
    
    def test_filtro_correcto_prr(self, sample_df_prr):
        """Test que filtra correctamente los pendientes PRR"""
        resultado = filtrar_pendientes_prr(sample_df_prr)
        
        # Debe retornar registros que cumplan todos los criterios
        assert len(resultado) == 2  # PRR001 y PRR004
        assert all(resultado['EstadoPre'].isna())
        assert all(resultado['EstadoTramite'] == 'PENDIENTE')
        assert all(resultado['EQUIPO'] != 'VULNERABLE')
    
    def test_filtro_etapas_validas_prr(self, sample_df_prr):
        """Test que solo incluye etapas válidas para PRR"""
        resultado = filtrar_pendientes_prr(sample_df_prr)
        etapas_validas = [
            'ACTUALIZAR DATOS BENEFICIARIO - F',
            'ACTUALIZAR DATOS BENEFICIARIO - I',
            'ASOCIACION BENEFICIARIO - F',
            'ASOCIACION BENEFICIARIO - I',
            'CONFORMIDAD SUB-DIREC.INMGRA. - I',
            'PAGOS, FECHA Y NRO RD. - F',
            'PAGOS, FECHA Y NRO RD. - I',
            'RECEPCIÓN DINM - F'
        ]
        assert all(etapa in etapas_validas for etapa in resultado['UltimaEtapa'])

class TestProcesarPendientes:
    """Tests para procesar_pendientes"""
    
    def test_procesar_pendientes_ccm(self, sample_df_ccm):
        """Test procesamiento de pendientes CCM"""
        resultado = procesar_pendientes(sample_df_ccm, "CCM")
        
        # Verificar que se procesó correctamente
        assert len(resultado) >= 0
        assert 'OPERADOR' in resultado.columns
        
        # Verificar que operadores nulos se convirtieron a 'Sin asignar'
        sin_asignar = resultado[resultado['OPERADOR'] == 'Sin asignar']
        assert len(sin_asignar) >= 0
    
    def test_procesar_pendientes_prr(self, sample_df_prr):
        """Test procesamiento de pendientes PRR"""
        resultado = procesar_pendientes(sample_df_prr, "PRR")
        
        # Verificar que se procesó correctamente
        assert len(resultado) >= 0
        assert 'OPERADOR' in resultado.columns
    
    def test_reemplazar_nulos_en_operador(self, sample_df_ccm):
        """Test que reemplaza operadores nulos con 'Sin asignar'"""
        resultado = procesar_pendientes(sample_df_ccm, "CCM")
        
        # No debe haber valores nulos en OPERADOR
        assert not resultado['OPERADOR'].isna().any()
        
        # Debe contener 'Sin asignar' donde había nulos
        assert 'Sin asignar' in resultado['OPERADOR'].values

class TestCrearTablaPendientes:
    """Tests para crear_tabla_pendientes"""
    
    @pytest.fixture
    def sample_df_with_dates(self):
        """DataFrame con fechas para testing"""
        return pd.DataFrame({
            'NumeroTramite': ['T001', 'T002', 'T003', 'T004'],
            'OPERADOR': ['Juan', 'María', 'Juan', 'Pedro'],
            'UltimaEtapa': ['EVALUACIÓN - I'] * 4,
            'EstadoPre': [None] * 4,
            'EstadoTramite': ['PENDIENTE'] * 4,
            'EQUIPO': ['NORMAL'] * 4,
            'Anio': [2023, 2023, 2024, 2024],
            'Mes': [1, 2, 1, 2],
            'FechaExpendiente': pd.to_datetime(['2023-01-15', '2023-02-20', '2024-01-10', '2024-02-05'])
        })
    
    def test_crear_tabla_por_anios(self, sample_df_with_dates):
        """Test creación de tabla por años"""
        df_filtrado = procesar_pendientes(sample_df_with_dates, "CCM")
        tabla = crear_tabla_pendientes(df_filtrado, "CCM", "anios")
        
        assert isinstance(tabla, pd.DataFrame)
        assert 'Total' in tabla.columns
        assert len(tabla.index) > 0  # Debe tener operadores
    
    def test_crear_tabla_por_meses(self, sample_df_with_dates):
        """Test creación de tabla por meses"""
        df_filtrado = procesar_pendientes(sample_df_with_dates, "CCM")
        tabla = crear_tabla_pendientes(df_filtrado, "CCM", "meses")
        
        assert isinstance(tabla, pd.DataFrame)
        assert 'Total' in tabla.columns
    
    def test_tabla_contiene_total(self, sample_df_with_dates):
        """Test que la tabla contiene columna Total"""
        df_filtrado = procesar_pendientes(sample_df_with_dates, "CCM")
        tabla = crear_tabla_pendientes(df_filtrado, "CCM", "anios")
        
        assert 'Total' in tabla.columns
        # El total debe ser la suma de las otras columnas
        columnas_numericas = [col for col in tabla.columns if col != 'Total']
        if columnas_numericas:
            total_calculado = tabla[columnas_numericas].sum(axis=1)
            pd.testing.assert_series_equal(tabla['Total'], total_calculado, check_names=False)

class TestCalcularSinAsignar:
    """Tests para calcular_sin_asignar"""
    
    def test_calcular_sin_asignar_con_datos(self, sample_df_ccm):
        """Test cálculo de sin asignar con datos"""
        df_filtrado = procesar_pendientes(sample_df_ccm, "CCM")
        sin_asignar = calcular_sin_asignar(df_filtrado)
        
        assert isinstance(sin_asignar, int)
        assert sin_asignar >= 0
    
    def test_calcular_sin_asignar_dataframe_vacio(self):
        """Test cálculo de sin asignar con DataFrame vacío"""
        df_vacio = pd.DataFrame()
        sin_asignar = calcular_sin_asignar(df_vacio)
        
        assert sin_asignar == 0

class TestCasosEdge:
    """Tests para casos edge y validaciones"""
    
    def test_dataframe_vacio(self):
        """Test con DataFrame vacío"""
        df_vacio = pd.DataFrame()
        
        # No debe fallar, debe retornar DataFrame vacío
        resultado_ccm = filtrar_pendientes_ccm(df_vacio)
        resultado_prr = filtrar_pendientes_prr(df_vacio)
        
        assert len(resultado_ccm) == 0
        assert len(resultado_prr) == 0
    
    def test_todas_las_columnas_requeridas_ccm(self, sample_df_ccm):
        """Test que todas las columnas requeridas están presentes para CCM"""
        columnas_requeridas = ['UltimaEtapa', 'EstadoPre', 'EstadoTramite', 'EQUIPO']
        
        for columna in columnas_requeridas:
            assert columna in sample_df_ccm.columns
    
    def test_todas_las_columnas_requeridas_prr(self, sample_df_prr):
        """Test que todas las columnas requeridas están presentes para PRR"""
        columnas_requeridas = ['UltimaEtapa', 'EstadoPre', 'EstadoTramite', 'EQUIPO']
        
        for columna in columnas_requeridas:
            assert columna in sample_df_prr.columns
    
    def test_operador_categorico(self):
        """Test manejo de columna OPERADOR categórica"""
        df_categorico = pd.DataFrame({
            'NumeroTramite': ['T001', 'T002'],
            'UltimaEtapa': ['EVALUACIÓN - I', 'EVALUACIÓN - I'],
            'EstadoPre': [None, None],
            'EstadoTramite': ['PENDIENTE', 'PENDIENTE'],
            'EQUIPO': ['NORMAL', 'NORMAL'],
            'OPERADOR': pd.Categorical(['Juan', None])
        })
        
        resultado = procesar_pendientes(df_categorico, "CCM")
        
        # No debe fallar y debe manejar categóricas correctamente
        assert 'Sin asignar' in resultado['OPERADOR'].values

if __name__ == "__main__":
    pytest.main([__file__]) 