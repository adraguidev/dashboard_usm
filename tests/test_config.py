"""
Tests para el módulo de configuración
"""

import pytest
import os
import sys
from unittest.mock import patch, MagicMock

# Configurar path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.config.settings import (
    DATABASE_CONFIG,
    OPERADORES_EXCLUIR_CCM,
    OPERADORES_EXCLUIR_PRR,
    ETAPAS_PRR,
    UMBRALES_EFICIENCIA,
    validar_configuracion,
    inicializar_configuracion
)

class TestConfiguracion:
    """Tests para la configuración del proyecto"""
    
    def test_database_config_contiene_procesos_requeridos(self):
        """Test que DATABASE_CONFIG contiene los procesos CCM y PRR"""
        assert "CCM" in DATABASE_CONFIG
        assert "PRR" in DATABASE_CONFIG
        assert isinstance(DATABASE_CONFIG["CCM"], str)
        assert isinstance(DATABASE_CONFIG["PRR"], str)
    
    def test_operadores_excluir_ccm_no_vacio(self):
        """Test que la lista de operadores a excluir para CCM no está vacía"""
        assert len(OPERADORES_EXCLUIR_CCM) > 0
        assert "Sin asignar" in OPERADORES_EXCLUIR_CCM
        assert "MAURICIO ROMERO, HUGO" in OPERADORES_EXCLUIR_CCM
    
    def test_operadores_excluir_prr_no_vacio(self):
        """Test que la lista de operadores a excluir para PRR no está vacía"""
        assert len(OPERADORES_EXCLUIR_PRR) > 0
        assert "Sin asignar" in OPERADORES_EXCLUIR_PRR
    
    def test_etapas_prr_contiene_etapas_validas(self):
        """Test que ETAPAS_PRR contiene las etapas esperadas"""
        assert len(ETAPAS_PRR) > 0
        assert "ACTUALIZAR DATOS BENEFICIARIO - F" in ETAPAS_PRR
        assert "RECEPCIÓN DINM - F" in ETAPAS_PRR
    
    def test_umbrales_eficiencia_contiene_valores_numericos(self):
        """Test que los umbrales de eficiencia son valores numéricos válidos"""
        assert "produccion_promedio_minima_alta" in UMBRALES_EFICIENCIA
        assert "produccion_promedio_minima_media" in UMBRALES_EFICIENCIA
        assert "aumento_peligroso_pendientes" in UMBRALES_EFICIENCIA
        
        # Verificar que son números
        assert isinstance(UMBRALES_EFICIENCIA["produccion_promedio_minima_alta"], (int, float))
        assert isinstance(UMBRALES_EFICIENCIA["produccion_promedio_minima_media"], (int, float))
        assert isinstance(UMBRALES_EFICIENCIA["aumento_peligroso_pendientes"], (int, float))
        
        # Verificar lógica de umbrales
        assert UMBRALES_EFICIENCIA["produccion_promedio_minima_alta"] > UMBRALES_EFICIENCIA["produccion_promedio_minima_media"]
    
    @patch('os.path.exists')
    def test_validar_configuracion_archivos_existentes(self, mock_exists):
        """Test validación de configuración con archivos existentes"""
        mock_exists.return_value = True
        resultado = validar_configuracion()
        assert resultado is True
    
    @patch('os.path.exists')
    def test_validar_configuracion_archivos_faltantes(self, mock_exists):
        """Test validación de configuración con archivos faltantes"""
        mock_exists.return_value = False
        resultado = validar_configuracion()
        assert resultado is False
    
    @patch('modules.config.settings.validar_configuracion')
    def test_inicializar_configuracion(self, mock_validar):
        """Test inicialización de configuración"""
        mock_validar.return_value = True
        resultado = inicializar_configuracion()
        assert resultado is True
        mock_validar.assert_called_once()

class TestConsistenciaConfiguracion:
    """Tests para verificar consistencia en la configuración"""
    
    def test_archivos_tienen_extension_correcta(self):
        """Test que los archivos de base de datos tienen extensión .pkl.gz"""
        for archivo in DATABASE_CONFIG.values():
            assert archivo.endswith('.pkl.gz'), f"Archivo {archivo} no tiene extensión .pkl.gz"
    
    def test_operadores_comunes_en_ambos_procesos(self):
        """Test que operadores comunes están en ambas listas"""
        operadores_comunes = ["Sin asignar", "Aponte Sanchez, Paola Lita", "Lucero Martinez, Carlos Martin"]
        
        for operador in operadores_comunes:
            assert operador in OPERADORES_EXCLUIR_CCM, f"Operador {operador} falta en CCM"
            assert operador in OPERADORES_EXCLUIR_PRR, f"Operador {operador} falta en PRR"
    
    def test_etapas_prr_no_duplicadas(self):
        """Test que no hay etapas duplicadas en PRR"""
        assert len(ETAPAS_PRR) == len(set(ETAPAS_PRR)), "Hay etapas duplicadas en ETAPAS_PRR"
    
    def test_umbrales_eficiencia_valores_positivos(self):
        """Test que todos los umbrales de eficiencia son positivos"""
        for clave, valor in UMBRALES_EFICIENCIA.items():
            assert valor >= 0, f"Umbral {clave} debe ser positivo, valor actual: {valor}"

if __name__ == "__main__":
    pytest.main([__file__]) 