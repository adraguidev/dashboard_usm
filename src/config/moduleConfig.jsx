import React from 'react';
import { Description as ReportIcon } from '@mui/icons-material';
import PendingReport from '../components/PendingReport';

// Configuración de pestañas comunes para módulos regulares
const commonTabs = (moduleId) => [
  {
    id: 'reporte-pendientes',
    label: 'Reporte de pendientes',
    icon: ReportIcon,
    component: () => <PendingReport moduleName={moduleId} />
  }
];

// Configuración completa de módulos con gradientes
const moduleConfig = {
  CCM: {
    name: 'CCM',
    tabs: (id) => commonTabs(id),
    color: '#4A90E2',
    gradient: 'linear-gradient(135deg, #4A90E2 0%, #357ABD 100%)',
    lightColor: '#ECF3FC'
  },
  PRR: {
    name: 'PRR',
    tabs: (id) => commonTabs(id),
    color: '#FF6B6B',
    gradient: 'linear-gradient(135deg, #FF6B6B 0%, #FF8585 100%)',
    lightColor: '#FFF0F0'
  },
  'CCM-ESP': {
    name: 'CCM-ESP',
    tabs: (id) => commonTabs(id),
    color: '#3498DB',
    gradient: 'linear-gradient(135deg, #3498DB 0%, #2980B9 100%)',
    lightColor: '#EAF4FB'
  },
  'CCM-LEY': {
    name: 'CCM-LEY',
    tabs: (id) => commonTabs(id),
    color: '#9B59B6',
    gradient: 'linear-gradient(135deg, #9B59B6 0%, #8E44AD 100%)',
    lightColor: '#F5EEF8'
  },
  SOL: {
    name: 'SOL',
    tabs: (id) => commonTabs(id),
    color: '#F1C40F',
    gradient: 'linear-gradient(135deg, #F1C40F 0%, #F39C12 100%)',
    lightColor: '#FEF9E7'
  },
  SPE: {
    name: 'SPE',
    tabs: (id) => commonTabs(id),
    color: '#2ECC71',
    gradient: 'linear-gradient(135deg, #2ECC71 0%, #27AE60 100%)',
    lightColor: '#E9F7EF'
  }
};

// Función auxiliar para obtener la configuración de un módulo
export const getModuleConfig = (moduleId) => {
  const config = moduleConfig[moduleId];
  if (!config) return null;

  return {
    ...config,
    id: moduleId,
    tabs: config.tabs(moduleId)
  };
};

export const modules = Object.keys(moduleConfig).map(id => ({
  id,
  label: moduleConfig[id].name
})); 