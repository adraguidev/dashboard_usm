import React, { useState } from 'react';
import {
  Box,
  Tabs,
  Tab,
  Typography,
  Fade,
} from '@mui/material';
import EvaluatorManagement from './EvaluatorManagement';
import PendingReport from '../PendingReport';

const TabPanel = (props) => {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`tabpanel-${index}`}
      aria-labelledby={`tab-${index}`}
      {...other}
      style={{ height: '100%' }}
    >
      {value === index && (
        <Box sx={{ height: '100%' }}>
          {children}
        </Box>
      )}
    </div>
  );
};

const AdminPanel = () => {
  const [selectedTab, setSelectedTab] = useState(0);
  const [selectedModule, setSelectedModule] = useState('CCM');

  const handleTabChange = (event, newValue) => {
    setSelectedTab(newValue);
  };

  return (
    <Box sx={{ 
      display: 'flex', 
      flexDirection: 'column', 
      height: '100%',
      bgcolor: 'background.default'
    }}>
      <Fade in={true} style={{ transitionDelay: '50ms' }}>
        <Box sx={{ 
          borderBottom: 1, 
          borderColor: 'divider',
          bgcolor: 'background.paper',
          px: 2,
        }}>
          <Tabs value={selectedTab} onChange={handleTabChange}>
            <Tab label="Gestión de Evaluadores" />
            <Tab label="Reportes" />
          </Tabs>
        </Box>
      </Fade>

      <Box sx={{ flexGrow: 1, minHeight: 0 }}>
        <TabPanel value={selectedTab} index={0}>
          <Fade in={selectedTab === 0} style={{ transitionDelay: selectedTab === 0 ? '100ms' : '0ms' }}>
            <div style={{ height: '100%' }}>
              <EvaluatorManagement moduleName={selectedModule} onModuleChange={setSelectedModule} />
            </div>
          </Fade>
        </TabPanel>
        <TabPanel value={selectedTab} index={1}>
          <Fade in={selectedTab === 1} style={{ transitionDelay: selectedTab === 1 ? '100ms' : '0ms' }}>
            <div style={{ height: '100%' }}>
              <PendingReport moduleName={selectedModule} />
            </div>
          </Fade>
        </TabPanel>
      </Box>
    </Box>
  );
};

export default AdminPanel; 