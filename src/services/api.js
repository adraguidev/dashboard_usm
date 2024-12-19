import axios from 'axios';

const API_URL = 'http://localhost:3001/api';

// Configuración global de axios
axios.interceptors.request.use(request => {
  console.log('Enviando solicitud:', {
    url: request.url,
    method: request.method,
    params: request.params,
    data: request.data
  });
  return request;
});

axios.interceptors.response.use(
  response => {
    console.log('Respuesta recibida:', {
      url: response.config.url,
      status: response.status,
      data: response.data
    });
    return response;
  },
  error => {
    console.error('Error en la solicitud:', {
      url: error.config?.url,
      status: error.response?.status,
      message: error.message,
      response: error.response?.data
    });
    throw error;
  }
);

export const api = {
  // Obtener reporte de pendientes
  getPendingReport: async (moduleName, years, viewType) => {
    try {
      const response = await axios.get(`${API_URL}/reports/pending/${moduleName}`, {
        params: {
          years: years.join(','),
          viewType
        }
      });
      return response.data;
    } catch (error) {
      console.error('Error al obtener reporte:', error);
      throw error;
    }
  },

  // Nueva función para obtener el resumen general
  getPendingSummary: async (moduleName) => {
    try {
      const response = await axios.get(`${API_URL}/reports/pending/${moduleName}/summary`);
      return response.data;
    } catch (error) {
      console.error('Error al obtener resumen:', error);
      throw error;
    }
  },

  // Obtener años disponibles para un módulo
  getAvailableYears: async (moduleName) => {
    if (!moduleName) {
      throw new Error('El nombre del módulo es requerido');
    }

    try {
      const response = await axios.get(`${API_URL}/reports/pending/${moduleName}/years`);
      
      if (!response.data || !response.data.success) {
        throw new Error(response.data?.error || 'Error al obtener años disponibles');
      }

      return response.data;
    } catch (error) {
      console.error('Error al obtener años disponibles:', error);
      throw error;
    }
  },

  // Obtener todos los evaluadores de un módulo
  getModuleEvaluators: async (moduleName) => {
    try {
      const response = await axios.get(`${API_URL}/admin/evaluators/${moduleName}`);
      return response.data;
    } catch (error) {
      console.error('Error al obtener evaluadores:', error);
      throw error;
    }
  },

  // Obtener categorías de evaluadores
  getEvaluatorCategories: async (moduleName) => {
    try {
      const response = await axios.get(`${API_URL}/admin/evaluators/${moduleName}/categories`);
      return response.data;
    } catch (error) {
      console.error('Error al obtener categorías:', error);
      throw error;
    }
  },

  // Agregar nueva categoría
  addEvaluatorCategory: async (moduleName, categoryData) => {
    try {
      const response = await axios.post(
        `${API_URL}/admin/evaluators/${moduleName}/categories`,
        categoryData
      );
      return response.data;
    } catch (error) {
      console.error('Error al agregar categoría:', error);
      throw error;
    }
  },

  // Actualizar categoría existente
  updateEvaluatorCategory: async (moduleName, categoryId, categoryData) => {
    try {
      const response = await axios.put(
        `${API_URL}/admin/evaluators/${moduleName}/categories/${categoryId}`,
        categoryData
      );
      return response.data;
    } catch (error) {
      console.error('Error al actualizar categoría:', error);
      throw error;
    }
  },

  // Eliminar categoría
  deleteEvaluatorCategory: async (moduleName, categoryId) => {
    try {
      const response = await axios.delete(
        `${API_URL}/admin/evaluators/${moduleName}/categories/${categoryId}`
      );
      return response.data;
    } catch (error) {
      console.error('Error al eliminar categoría:', error);
      throw error;
    }
  },

  // Actualizar categoría de un evaluador
  updateEvaluatorCategoryAssignment: async (moduleName, evaluatorId, data) => {
    try {
      const response = await axios.put(
        `${API_URL}/admin/evaluators/${moduleName}/evaluator/${evaluatorId}`,
        data
      );
      return response.data;
    } catch (error) {
      console.error('Error al actualizar evaluador:', error);
      throw error;
    }
  }
}; 