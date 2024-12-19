import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  FormControl,
  RadioGroup,
  Radio,
  FormControlLabel,
  Button,
  Grid,
  Card,
  CardContent,
  IconButton,
  Tooltip,
} from '@mui/material';
import { DataGrid } from '@mui/x-data-grid';
import {
  AssignmentTurnedIn as AssignedIcon,
  Warning as UnassignedIcon,
  Help as HelpIcon,
  Close as CloseIcon,
  FileDownload as FileDownloadIcon,
} from '@mui/icons-material';
import * as XLSX from 'xlsx';
import { saveAs } from 'file-saver';
import { api } from '../services/api';

const PendingReport = ({ moduleName }) => {
  const [years, setYears] = useState([]);
  const [selectedYears, setSelectedYears] = useState([]);
  const [viewType, setViewType] = useState('Activos');
  const [report, setReport] = useState(null);
  const [summaryData, setSummaryData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    console.log('ModuleName recibido:', moduleName);
    loadAvailableYears();
    loadSummaryData();
  }, [moduleName]);

  useEffect(() => {
    if (selectedYears.length > 0) {
      console.log('Cargando reporte con años:', selectedYears, 'y vista:', viewType);
      loadReport();
    }
  }, [selectedYears, viewType]);

  const loadAvailableYears = async () => {
    try {
      console.log('Solicitando años disponibles para el módulo:', moduleName);
      const response = await api.getAvailableYears(moduleName);
      console.log('Respuesta de años disponibles:', response);
      
      if (response && response.years && Array.isArray(response.years) && response.years.length > 0) {
        setYears(response.years);
        setSelectedYears([response.years[0]]);
      } else {
        setError('No se encontraron años disponibles');
      }
    } catch (error) {
      console.error('Error al cargar años:', error);
      setError('Error al cargar los años disponibles');
    }
  };

  const loadReport = async () => {
    setLoading(true);
    setError(null);
    try {
      console.log('Solicitando reporte con parámetros:', {
        moduleName,
        years: selectedYears,
        viewType
      });
      const data = await api.getPendingReport(moduleName, selectedYears, viewType);
      console.log('Datos del reporte recibidos:', data);
      
      if (data && data.tables) {
        setReport(data);
      } else {
        setError('Los datos recibidos no tienen el formato esperado');
      }
    } catch (error) {
      console.error('Error al cargar reporte:', error);
      setError('Error al cargar el reporte');
    } finally {
      setLoading(false);
    }
  };

  const loadSummaryData = async () => {
    try {
      const data = await api.getPendingSummary(moduleName);
      console.log('Datos del resumen recibidos:', data);
      setSummaryData(data);
    } catch (error) {
      console.error('Error al cargar resumen:', error);
      setError('Error al cargar el resumen general');
    }
  };

  const handleYearSelect = (year) => {
    setSelectedYears(prev => {
      if (prev.includes(year)) {
        // Si el año ya está seleccionado, lo quitamos
        return prev.filter(y => y !== year);
      } else {
        // Si el año no está seleccionado, lo agregamos
        return [...prev, year].sort();
      }
    });
  };

  const renderMetrics = () => {
    if (!report?.metrics) return null;
    const { pendingAssigned, pendingUnassigned } = report.metrics;

    return (
      <Box sx={{ mb: 4 }}>
        <Typography variant="h6" sx={{ mb: 2, display: 'flex', alignItems: 'center' }}>
          <AssignedIcon sx={{ mr: 1 }} /> Panel de Control de Pendientes
        </Typography>
        <Grid container spacing={4}>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  <AssignedIcon sx={{ mr: 1, color: 'primary.main' }} />
                  <Typography variant="subtitle1">
                    Expedientes Pendientes Asignados
                    <Tooltip title="Expedientes asignados a evaluadores">
                      <IconButton size="small" sx={{ ml: 1 }}>
                        <HelpIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                  </Typography>
                </Box>
                <Typography variant="h3">{pendingAssigned}</Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  <UnassignedIcon sx={{ mr: 1, color: 'warning.main' }} />
                  <Typography variant="subtitle1">
                    Expedientes Pendientes No Asignados
                    <Tooltip title="Expedientes sin asignar a evaluadores">
                      <IconButton size="small" sx={{ ml: 1 }}>
                        <HelpIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                  </Typography>
                </Box>
                <Typography variant="h3">{pendingUnassigned}</Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Box>
    );
  };

  const renderMainTable = () => {
    if (!report?.tables?.mainTable) return null;

    const handleExportExcel = () => {
      // Preparar los datos para Excel
      const data = report.tables.mainTable.map(row => {
        const baseData = {
          'Evaluador': row.evaluador,
        };

        // Si es un solo año, mostrar meses
        if (selectedYears.length === 1) {
          return {
            ...baseData,
            'Enero': row.Enero,
            'Febrero': row.Febrero,
            'Marzo': row.Marzo,
            'Abril': row.Abril,
            'Mayo': row.Mayo,
            'Junio': row.Junio,
            'Julio': row.Julio,
            'Agosto': row.Agosto,
            'Septiembre': row.Septiembre,
            'Octubre': row.Octubre,
            'Noviembre': row.Noviembre,
            'Diciembre': row.Diciembre,
            'Total': row.TOTAL
          };
        } else {
          // Si son múltiples años, mostrar totales por año
          const yearData = {};
          selectedYears.forEach(year => {
            yearData[`Total ${year}`] = row[year] || 0;
          });
          return {
            ...baseData,
            ...yearData,
            'Total General': row.TOTAL
          };
        }
      });

      // Crear el libro de trabajo
      const ws = XLSX.utils.json_to_sheet(data);
      const wb = XLSX.utils.book_new();
      XLSX.utils.book_append_sheet(wb, ws, "Reporte de Pendientes");

      // Estilos para el encabezado
      const headerStyle = {
        font: { bold: true, color: { rgb: "FFFFFF" } },
        fill: { patternType: "solid", fgColor: { rgb: "1976D2" } },
        alignment: { horizontal: "center", vertical: "center" },
        border: {
          top: { style: "thin", color: { rgb: "000000" } },
          bottom: { style: "thin", color: { rgb: "000000" } },
          left: { style: "thin", color: { rgb: "000000" } },
          right: { style: "thin", color: { rgb: "000000" } }
        }
      };

      // Estilos para las celdas de datos
      const dataStyle = {
        alignment: { horizontal: "center", vertical: "center" },
        border: {
          top: { style: "thin", color: { rgb: "000000" } },
          bottom: { style: "thin", color: { rgb: "000000" } },
          left: { style: "thin", color: { rgb: "000000" } },
          right: { style: "thin", color: { rgb: "000000" } }
        }
      };

      // Estilos para la columna total
      const totalStyle = {
        font: { bold: true, color: { rgb: "FFFFFF" } },
        fill: { patternType: "solid", fgColor: { rgb: "2196F3" } },
        alignment: { horizontal: "center", vertical: "center" },
        border: {
          top: { style: "thin", color: { rgb: "000000" } },
          bottom: { style: "thin", color: { rgb: "000000" } },
          left: { style: "thin", color: { rgb: "000000" } },
          right: { style: "thin", color: { rgb: "000000" } }
        }
      };

      // Aplicar estilos
      const range = XLSX.utils.decode_range(ws['!ref']);
      for (let R = range.s.r; R <= range.e.r; ++R) {
        for (let C = range.s.c; C <= range.e.c; ++C) {
          const address = XLSX.utils.encode_cell({ r: R, c: C });
          if (!ws[address]) continue;
          
          if (R === 0) {
            // Encabezados
            ws[address].s = headerStyle;
          } else if (C === range.e.c) {
            // Columna total
            ws[address].s = totalStyle;
          } else {
            // Datos normales
            ws[address].s = dataStyle;
          }
        }
      }

      // Ajustar el ancho de las columnas
      const colWidths = [
        { wch: 30 }, // Evaluador
        { wch: 10 }, // Enero
        { wch: 10 }, // Febrero
        { wch: 10 }, // Marzo
        { wch: 10 }, // Abril
        { wch: 10 }, // Mayo
        { wch: 10 }, // Junio
        { wch: 10 }, // Julio
        { wch: 10 }, // Agosto
        { wch: 10 }, // Septiembre
        { wch: 10 }, // Octubre
        { wch: 10 }, // Noviembre
        { wch: 10 }, // Diciembre
        { wch: 10 }, // Total
      ];
      ws['!cols'] = colWidths;

      // Ajustar altura de filas
      const rowHeights = Array(range.e.r + 1).fill({ hpt: 25 }); // 25 puntos de altura
      ws['!rows'] = rowHeights;

      // Generar el archivo
      const excelBuffer = XLSX.write(wb, { bookType: 'xlsx', type: 'array' });
      const dataBlob = new Blob([excelBuffer], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;charset=UTF-8' });
      saveAs(dataBlob, `Reporte_Pendientes_${moduleName}_${viewType}_${selectedYears.join('-')}.xlsx`);
    };

    const handleExportImage = () => {
      const gridElement = document.querySelector('.MuiDataGrid-root');
      if (!gridElement) return;

      // Crear un elemento temporal para la captura
      const tempDiv = document.createElement('div');
      tempDiv.style.position = 'absolute';
      tempDiv.style.left = '-9999px';
      document.body.appendChild(tempDiv);

      // Clonar la tabla y aplicar estilos
      const tableClone = gridElement.cloneNode(true);
      tableClone.style.background = 'white';
      tempDiv.appendChild(tableClone);

      // Usar html2canvas para la captura
      import('html2canvas').then(({ default: html2canvas }) => {
        html2canvas(tableClone, {
          scale: 2,
          backgroundColor: '#ffffff',
          logging: false,
          useCORS: true,
          allowTaint: true,
        }).then(canvas => {
          // Convertir a PNG y descargar
          canvas.toBlob(blob => {
            saveAs(blob, `Reporte_Pendientes_${moduleName}_${viewType}_${selectedYears.join('-')}.png`);
            document.body.removeChild(tempDiv);
          }, 'image/png');
        });
      });
    };

    // Definir las columnas según los años seleccionados
    const getColumns = () => {
      const baseColumns = [
        { 
          field: 'evaluador', 
          headerName: 'Evaluador', 
          flex: 1,
          minWidth: 200,
          headerAlign: 'left',
          align: 'left',
        }
      ];

      if (selectedYears.length === 1) {
        // Columnas mensuales para un solo año
        const monthColumns = [
          { field: 'Enero', headerName: 'Enero', width: 85, type: 'number', align: 'center', headerAlign: 'center' },
          { field: 'Febrero', headerName: 'Febrero', width: 85, type: 'number', align: 'center', headerAlign: 'center' },
          { field: 'Marzo', headerName: 'Marzo', width: 85, type: 'number', align: 'center', headerAlign: 'center' },
          { field: 'Abril', headerName: 'Abril', width: 85, type: 'number', align: 'center', headerAlign: 'center' },
          { field: 'Mayo', headerName: 'Mayo', width: 85, type: 'number', align: 'center', headerAlign: 'center' },
          { field: 'Junio', headerName: 'Junio', width: 85, type: 'number', align: 'center', headerAlign: 'center' },
          { field: 'Julio', headerName: 'Julio', width: 85, type: 'number', align: 'center', headerAlign: 'center' },
          { field: 'Agosto', headerName: 'Agosto', width: 85, type: 'number', align: 'center', headerAlign: 'center' },
          { field: 'Septiembre', headerName: 'Septiembre', width: 85, type: 'number', align: 'center', headerAlign: 'center' },
          { field: 'Octubre', headerName: 'Octubre', width: 85, type: 'number', align: 'center', headerAlign: 'center' },
          { field: 'Noviembre', headerName: 'Noviembre', width: 85, type: 'number', align: 'center', headerAlign: 'center' },
          { field: 'Diciembre', headerName: 'Diciembre', width: 85, type: 'number', align: 'center', headerAlign: 'center' }
        ];
        return [...baseColumns, ...monthColumns, {
          field: 'TOTAL',
          headerName: 'Total',
          width: 85,
          type: 'number',
          align: 'center',
          headerAlign: 'center',
          cellClassName: 'total-column'
        }];
      } else {
        // Columnas de años para múltiples años
        const yearColumns = selectedYears.map(year => ({
          field: year.toString(),
          headerName: `Total ${year}`,
          width: 120,
          type: 'number',
          align: 'center',
          headerAlign: 'center'
        }));
        return [...baseColumns, ...yearColumns, {
          field: 'TOTAL',
          headerName: 'Total General',
          width: 120,
          type: 'number',
          align: 'center',
          headerAlign: 'center',
          cellClassName: 'total-column'
        }];
      }
    };

    // Transformar los datos según los años seleccionados
    const getRows = () => {
      return report.tables.mainTable.map((row, index) => {
        if (selectedYears.length === 1) {
          // Datos mensuales para un solo año
          return {
            id: index,
            ...row
          };
        } else {
          // Datos anuales para múltiples años
          const yearData = {};
          selectedYears.forEach(year => {
            yearData[year] = row[year] || 0;
          });
          return {
            id: index,
            evaluador: row.evaluador,
            ...yearData,
            TOTAL: row.TOTAL
          };
        }
      });
    };

    return (
      <Box>
        <Box sx={{ 
          mb: 2, 
          px: 2, 
          display: 'flex', 
          justifyContent: 'space-between',
          alignItems: 'center'
        }}>
          <Typography variant="h6">
            Detalle de Pendientes por Evaluador
            {selectedYears.length > 1 && (
              <Typography variant="subtitle2" color="text.secondary">
                Vista por años: {selectedYears.join(', ')}
              </Typography>
            )}
          </Typography>
          <Box sx={{ display: 'flex', gap: 2 }}>
            <Button
              variant="contained"
              startIcon={<FileDownloadIcon />}
              onClick={handleExportExcel}
              sx={{ 
                backgroundColor: '#217346', // Color verde de Excel
                '&:hover': {
                  backgroundColor: '#1a5c38'
                }
              }}
            >
              Exportar a Excel
            </Button>
            <Button
              variant="contained"
              startIcon={<FileDownloadIcon />}
              onClick={handleExportImage}
              sx={{ 
                backgroundColor: '#5c2d91', // Color morado para imagen
                '&:hover': {
                  backgroundColor: '#4a2475'
                }
              }}
            >
              Exportar como Imagen
            </Button>
          </Box>
        </Box>
        <Paper 
          elevation={1}
          sx={{ 
            p: 2,
            width: '100%',
            overflow: 'visible'
          }}
        >
          <DataGrid
            rows={getRows()}
            columns={getColumns()}
            pageSize={10}
            rowsPerPageOptions={[10, 25, 50]}
            disableSelectionOnClick
            autoHeight
            density="compact"
            showCellRightBorder
            showColumnRightBorder
            disableExtendRowFullWidth
            sx={{
              width: '100%',
              border: 'none',
              '& .MuiDataGrid-cell': {
                borderRight: '1px solid rgba(224, 224, 224, 1)',
              },
              '& .MuiDataGrid-columnHeader': {
                borderRight: '1px solid rgba(224, 224, 224, 1)',
                backgroundColor: 'primary.main',
                color: 'white',
              },
              '& .MuiDataGrid-row:nth-of-type(even)': {
                backgroundColor: 'action.hover',
              },
              '& .total-column': {
                backgroundColor: 'primary.light',
                color: 'white',
                fontWeight: 'bold',
              },
              '& .MuiDataGrid-columnHeaders': {
                borderBottom: '2px solid rgba(224, 224, 224, 1)',
              },
              '& .MuiDataGrid-virtualScroller': {
                overflow: 'visible'
              }
            }}
          />
        </Paper>
      </Box>
    );
  };

  const renderSummaryTable = () => {
    if (!summaryData) return null;

    const estados = ['Activos', 'Inactivos', 'No Asignado', 'Suspendida', 'Vulnerabilidad'];
    
    // Preparar columnas para DataGrid
    const summaryColumns = [
      { 
        field: 'estado', 
        headerName: 'Estado', 
        flex: 1,
        minWidth: 150,
        headerAlign: 'left',
        align: 'left',
      },
      ...years.map(year => ({
        field: year.toString(),
        headerName: year.toString(),
        width: 120,
        type: 'number',
        align: 'center',
        headerAlign: 'center'
      })),
      {
        field: 'TOTAL',
        headerName: 'TOTAL',
        width: 120,
        type: 'number',
        align: 'center',
        headerAlign: 'center',
        cellClassName: 'total-column'
      }
    ];

    // Preparar filas para DataGrid usando los datos del backend
    const summaryRows = estados.map((estado, index) => ({
      id: index,
      estado,
      ...summaryData[estado]
    }));

    const handleExportSummaryExcel = () => {
      // Definir el orden de las columnas
      const columnOrder = ['Estado', ...years.map(year => year.toString()), 'TOTAL'];
      
      // Preparar datos para Excel manteniendo el orden
      const data = estados.map(estado => {
        const rowData = {
          'Estado': estado
        };
        
        // Agregar años en orden
        years.forEach(year => {
          rowData[year.toString()] = summaryData[estado][year] || 0;
        });
        
        // Agregar total al final
        rowData['TOTAL'] = summaryData[estado]['TOTAL'] || 0;
        
        return rowData;
      });

      // Crear el libro de trabajo
      const ws = XLSX.utils.json_to_sheet(data);
      const wb = XLSX.utils.book_new();
      XLSX.utils.book_append_sheet(wb, ws, "Resumen General");

      // Aplicar estilos
      const headerStyle = {
        font: { bold: true, color: { rgb: "FFFFFF" } },
        fill: { patternType: "solid", fgColor: { rgb: "1976D2" } },
        alignment: { horizontal: "center", vertical: "center" },
        border: {
          top: { style: "thin", color: { rgb: "000000" } },
          bottom: { style: "thin", color: { rgb: "000000" } },
          left: { style: "thin", color: { rgb: "000000" } },
          right: { style: "thin", color: { rgb: "000000" } }
        }
      };

      // Establecer el orden de las columnas
      ws['!cols'] = columnOrder.map(col => ({
        wch: col === 'Estado' ? 20 : 12
      }));

      // Aplicar estilos a los encabezados
      const range = XLSX.utils.decode_range(ws['!ref']);
      for (let C = range.s.c; C <= range.e.c; ++C) {
        const address = XLSX.utils.encode_cell({ r: 0, c: C });
        if (!ws[address]) continue;
        ws[address].s = headerStyle;
      }

      // Generar el archivo
      const excelBuffer = XLSX.write(wb, { bookType: 'xlsx', type: 'array' });
      const dataBlob = new Blob([excelBuffer], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;charset=UTF-8' });
      saveAs(dataBlob, `Resumen_General_${moduleName}.xlsx`);
    };

    const handleExportSummaryImage = () => {
      const gridElement = document.querySelector('.summary-grid');
      if (!gridElement) return;

      // Crear un elemento temporal para la captura
      const tempDiv = document.createElement('div');
      tempDiv.style.position = 'absolute';
      tempDiv.style.left = '-9999px';
      document.body.appendChild(tempDiv);

      // Clonar la tabla y aplicar estilos
      const tableClone = gridElement.cloneNode(true);
      tableClone.style.background = 'white';
      tempDiv.appendChild(tableClone);

      // Usar html2canvas para la captura
      import('html2canvas').then(({ default: html2canvas }) => {
        html2canvas(tableClone, {
          scale: 2,
          backgroundColor: '#ffffff',
          logging: false,
          useCORS: true,
          allowTaint: true,
        }).then(canvas => {
          canvas.toBlob(blob => {
            saveAs(blob, `Resumen_General_${moduleName}.png`);
            document.body.removeChild(tempDiv);
          }, 'image/png');
        });
      });
    };

    return (
      <Box sx={{ mt: 4 }}>
        <Box sx={{ 
          mb: 2, 
          px: 2, 
          display: 'flex', 
          justifyContent: 'space-between',
          alignItems: 'center'
        }}>
          <Typography variant="h6">
            Resumen General por Año
          </Typography>
          <Box sx={{ display: 'flex', gap: 2 }}>
            <Button
              variant="contained"
              startIcon={<FileDownloadIcon />}
              onClick={handleExportSummaryExcel}
              sx={{ 
                backgroundColor: '#217346',
                '&:hover': {
                  backgroundColor: '#1a5c38'
                }
              }}
            >
              Exportar Resumen a Excel
            </Button>
            <Button
              variant="contained"
              startIcon={<FileDownloadIcon />}
              onClick={handleExportSummaryImage}
              sx={{ 
                backgroundColor: '#5c2d91',
                '&:hover': {
                  backgroundColor: '#4a2475'
                }
              }}
            >
              Exportar Resumen como Imagen
            </Button>
          </Box>
        </Box>
        <Paper 
          elevation={1}
          sx={{ 
            p: 2,
            width: '100%',
            overflow: 'visible'
          }}
        >
          <DataGrid
            className="summary-grid"
            rows={summaryRows}
            columns={summaryColumns}
            hideFooter
            autoHeight
            density="compact"
            disableSelectionOnClick
            showCellRightBorder
            showColumnRightBorder
            disableExtendRowFullWidth
            sx={{
              width: '100%',
              border: 'none',
              '& .MuiDataGrid-cell': {
                borderRight: '1px solid rgba(224, 224, 224, 1)',
              },
              '& .MuiDataGrid-columnHeader': {
                borderRight: '1px solid rgba(224, 224, 224, 1)',
                backgroundColor: 'primary.main',
                color: 'white',
              },
              '& .MuiDataGrid-row:nth-of-type(even)': {
                backgroundColor: 'action.hover',
              },
              '& .total-column': {
                backgroundColor: 'primary.light',
                color: 'white',
                fontWeight: 'bold',
              },
              '& .MuiDataGrid-columnHeaders': {
                borderBottom: '2px solid rgba(224, 224, 224, 1)',
              },
              '& .MuiDataGrid-virtualScroller': {
                overflow: 'visible'
              }
            }}
          />
        </Paper>
      </Box>
    );
  };

  return (
    <Box 
      sx={{ 
        p: 3,
        display: 'flex',
        flexDirection: 'column',
        width: '100%',
        minHeight: 'fit-content',
        '& > *': {
          width: '100%'
        }
      }}
    >
      <Typography variant="h5" sx={{ mb: 4 }}>
        Reporte de Pendientes
      </Typography>

      {error && (
        <Box sx={{ mb: 2, p: 2, bgcolor: 'error.light', borderRadius: 1 }}>
          <Typography color="error">{error}</Typography>
        </Box>
      )}

      <Grid container spacing={4} sx={{ mb: 4, width: '100%' }}>
        <Grid item xs={12} md={6}>
          <Typography variant="subtitle1" sx={{ mb: 2 }}>
            Seleccionar Vista
          </Typography>
          <FormControl component="fieldset">
            <RadioGroup
              row
              value={viewType}
              onChange={(e) => setViewType(e.target.value)}
            >
              <FormControlLabel
                value="Activos"
                control={<Radio color="primary" />}
                label="Activos"
              />
              <FormControlLabel
                value="Inactivos"
                control={<Radio />}
                label="Inactivos"
              />
              <FormControlLabel
                value="Vulnerabilidad"
                control={<Radio />}
                label="Vulnerabilidad"
              />
              <FormControlLabel
                value="Total"
                control={<Radio />}
                label="Total"
              />
            </RadioGroup>
          </FormControl>
        </Grid>
        <Grid item xs={12} md={6}>
          <Typography variant="subtitle1" sx={{ mb: 2 }}>
            Seleccionar Año(s)
          </Typography>
          <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
            {years.map((year) => (
              <Button
                key={year}
                variant={selectedYears.includes(year) ? "contained" : "outlined"}
                onClick={() => handleYearSelect(year)}
                sx={{ minWidth: '100px' }}
                endIcon={selectedYears.includes(year) && <CloseIcon />}
              >
                {year}
              </Button>
            ))}
          </Box>
        </Grid>
      </Grid>

      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
          <Typography>Cargando datos del módulo {moduleName}...</Typography>
        </Box>
      ) : (
        <Box sx={{ 
          width: '100%',
          minHeight: 'fit-content',
          '& .MuiPaper-root': {
            height: 'fit-content',
            overflow: 'visible'
          }
        }}>
          {renderMetrics()}
          {renderMainTable()}
          {renderSummaryTable()}
        </Box>
      )}
    </Box>
  );
};

export default PendingReport; 