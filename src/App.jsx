import React, { useState } from 'react'
import { Box, CssBaseline, ThemeProvider } from '@mui/material'
import Dashboard from './components/Dashboard'
import Sidebar from './components/Sidebar'
import AdminPanel from './components/admin/AdminPanel'
import { theme } from './styles/theme'

function App() {
  const [selectedModule, setSelectedModule] = useState(null);
  const [isAdminView, setIsAdminView] = useState(false);

  const handleModuleSelect = (moduleId) => {
    setSelectedModule(moduleId);
    setIsAdminView(false);
  };

  const handleAdminClick = () => {
    setIsAdminView(true);
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={{ 
        display: 'flex',
        height: '100vh',
        width: '100vw',
        overflow: 'hidden',
        bgcolor: 'background.default'
      }}>
        <Sidebar 
          onModuleSelect={handleModuleSelect} 
          onAdminClick={handleAdminClick}
        />
        <Box 
          component="main" 
          sx={{ 
            flex: 1,
            display: 'flex',
            flexDirection: 'column',
            minWidth: 0,
            height: '100vh',
            overflow: 'hidden',
            bgcolor: 'background.default'
          }}
        >
          {isAdminView ? (
            <AdminPanel selectedModule={selectedModule} />
          ) : (
            <Dashboard selectedModule={selectedModule} />
          )}
        </Box>
      </Box>
    </ThemeProvider>
  )
}

export default App
