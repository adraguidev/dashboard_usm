import React from 'react';
import { 
  Box, 
  Container, 
  Grid, 
  Paper, 
  Typography,
  Card,
  CardContent
} from '@mui/material';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';
import ModuleView from './ModuleView';
import { dashboardStyles } from '../styles/Dashboard.styles';

// Datos de ejemplo para el gráfico
const data = [
  { name: 'Ene', valor: 400 },
  { name: 'Feb', valor: 300 },
  { name: 'Mar', valor: 600 },
  { name: 'Abr', valor: 800 },
  { name: 'May', valor: 500 },
  { name: 'Jun', valor: 700 },
];

const Dashboard = ({ selectedModule }) => {
  // Si hay un módulo seleccionado, mostrar su vista
  if (selectedModule) {
    return <ModuleView moduleId={selectedModule} />;
  }

  // Si no hay módulo seleccionado, mostrar el dashboard general
  return (
    <Box sx={dashboardStyles.root}>
      <Container maxWidth="lg">
        <Typography variant="h4" sx={dashboardStyles.title}>
          Dashboard General
        </Typography>
        <Grid container spacing={3}>
          {/* Tarjetas de resumen */}
          <Grid item xs={12} md={4}>
            <Card sx={dashboardStyles.card}>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  Total Estudiantes
                </Typography>
                <Typography variant="h4" sx={dashboardStyles.title}>
                  1,234
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={4}>
            <Card sx={dashboardStyles.card}>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  Promedio General
                </Typography>
                <Typography variant="h4" sx={dashboardStyles.title}>
                  5.6
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={4}>
            <Card sx={dashboardStyles.card}>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  Tasa de Aprobación
                </Typography>
                <Typography variant="h4" sx={dashboardStyles.title}>
                  78%
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          {/* Gráfico */}
          <Grid item xs={12}>
            <Paper sx={dashboardStyles.chartPaper}>
              <Typography variant="h6" gutterBottom sx={dashboardStyles.chartTitle}>
                Rendimiento Académico
              </Typography>
              <ResponsiveContainer width="100%" height={400}>
                <LineChart
                  data={data}
                  margin={{
                    top: 20,
                    right: 30,
                    left: 20,
                    bottom: 20,
                  }}
                >
                  <CartesianGrid strokeDasharray="3 3" stroke="#f5f6fa" />
                  <XAxis dataKey="name" stroke="#2f3542" />
                  <YAxis stroke="#2f3542" />
                  <Tooltip contentStyle={dashboardStyles.tooltip} />
                  <Legend />
                  <Line 
                    type={dashboardStyles.lineChart.type}
                    dataKey="valor" 
                    stroke="#ff4757" 
                    strokeWidth={dashboardStyles.lineChart.strokeWidth}
                    dot={dashboardStyles.lineChart.dot}
                    activeDot={dashboardStyles.lineChart.activeDot}
                  />
                </LineChart>
              </ResponsiveContainer>
            </Paper>
          </Grid>
        </Grid>
      </Container>
    </Box>
  );
};

export default Dashboard; 