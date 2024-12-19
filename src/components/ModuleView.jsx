import React, { useState } from 'react';
import {
  Box,
  Tabs,
  Tab,
  Paper,
  Typography,
  useTheme,
  alpha,
} from '@mui/material';
import { getModuleConfig } from '../config/moduleConfig.jsx';
import { StyledTab, moduleViewStyles } from '../styles/ModuleView.styles';

// Panel de contenido para cada pestaña
const TabPanel = ({ children, value, index, ...other }) => (
  <Box
    role="tabpanel"
    hidden={value !== index}
    id={`tabpanel-${index}`}
    aria-labelledby={`tab-${index}`}
    {...other}
    sx={{
      height: '100%',
      display: 'flex',
      flexDirection: 'column',
      flex: 1,
      overflow: 'auto'
    }}
  >
    {value === index && (
      <Box sx={{ 
        display: 'flex',
        flexDirection: 'column',
        flex: 1
      }}>
        {children}
      </Box>
    )}
  </Box>
);

const ModuleView = ({ moduleId }) => {
  const theme = useTheme();
  const [activeTab, setActiveTab] = useState(0);
  const moduleConfig = getModuleConfig(moduleId);

  if (!moduleConfig) {
    return (
      <Box sx={{ p: 2 }}>
        <Typography>Módulo no encontrado</Typography>
      </Box>
    );
  }

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  return (
    <Box sx={{
      ...moduleViewStyles.container,
      height: '100%',
      display: 'flex',
      flexDirection: 'column'
    }}>
      {/* Encabezado del módulo */}
      <Box sx={moduleViewStyles.header}>
        <Typography 
          variant="h5" 
          sx={{ 
            color: moduleConfig.color,
            ...moduleViewStyles.headerTitle
          }}
        >
          {moduleConfig.name}
        </Typography>
      </Box>

      {/* Contenedor de pestañas y contenido */}
      <Box sx={{
        ...moduleViewStyles.content,
        flex: 1,
        display: 'flex',
        flexDirection: 'column',
        overflow: 'hidden'
      }}>
        {/* Barra de pestañas */}
        <Box sx={moduleViewStyles.tabsContainer}>
          <Tabs
            value={activeTab}
            onChange={handleTabChange}
            variant="scrollable"
            scrollButtons="auto"
            sx={{
              ...moduleViewStyles.tabs,
              '& .MuiTabs-indicator': {
                backgroundColor: moduleConfig.color,
                ...moduleViewStyles.tabs['& .MuiTabs-indicator']
              }
            }}
          >
            {moduleConfig.tabs.map((tab, index) => (
              <StyledTab
                key={tab.id}
                icon={<tab.icon sx={moduleViewStyles.tabIcon} />}
                label={tab.label}
                id={`tab-${index}`}
                aria-controls={`tabpanel-${index}`}
                iconPosition="start"
                color={moduleConfig.color}
              />
            ))}
          </Tabs>
        </Box>

        {/* Contenido de las pestañas */}
        <Box sx={{
          ...moduleViewStyles.tabContent,
          bgcolor: alpha(moduleConfig.color, 0.02),
          flex: 1,
          display: 'flex',
          flexDirection: 'column',
          overflow: 'hidden'
        }}>
          {moduleConfig.tabs.map((tab, index) => (
            <TabPanel key={tab.id} value={activeTab} index={index}>
              <Box sx={{
                ...moduleViewStyles.tabPanel,
                flex: 1,
                display: 'flex',
                flexDirection: 'column'
              }}>
                <Paper 
                  elevation={0}
                  sx={{
                    ...moduleViewStyles.paper,
                    flex: 1,
                    display: 'flex',
                    flexDirection: 'column',
                    overflow: 'auto'
                  }}
                >
                  {tab.component()}
                </Paper>
              </Box>
            </TabPanel>
          ))}
        </Box>
      </Box>
    </Box>
  );
};

export default ModuleView; 