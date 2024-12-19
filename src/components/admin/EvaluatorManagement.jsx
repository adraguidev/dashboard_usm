import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Button,
  IconButton,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Alert,
  DialogContentText,
  Stack,
  Tabs,
  Tab,
  List,
  ListItem,
  ListItemText,
  ListItemAvatar,
  Avatar,
  InputAdornment,
  Select,
  MenuItem,
  FormControl,
  CircularProgress,
  Fade,
  ListItemIcon,
  Checkbox,
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Search as SearchIcon,
  Person as PersonIcon,
} from '@mui/icons-material';
import { api } from '../../services/api';
import { alpha } from '@mui/material/styles';

const EvaluatorManagement = ({ moduleName, onModuleChange }) => {
  const [evaluators, setEvaluators] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [openCategoryDialog, setOpenCategoryDialog] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState(null);
  const [newCategoryName, setNewCategoryName] = useState('');
  const [editMode, setEditMode] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [openDeleteDialog, setOpenDeleteDialog] = useState(false);
  const [categoryToDelete, setCategoryToDelete] = useState(null);
  const [selectedTab, setSelectedTab] = useState(0);
  const [selectedEvaluators, setSelectedEvaluators] = useState([]);
  const modules = ['CCM', 'PRR', 'CCM-ESP', 'CCM-LEY', 'SOL', 'SPE'];

  useEffect(() => {
    loadData();
  }, [moduleName]);

  const loadData = async () => {
    try {
      setLoading(true);
      const [evaluatorsData, categoriesData] = await Promise.all([
        api.getModuleEvaluators(moduleName),
        api.getEvaluatorCategories(moduleName)
      ]);
      setEvaluators(evaluatorsData);
      setCategories(categoriesData);
      setError(null);
    } catch (err) {
      setError('Error al cargar los datos: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleAddCategory = async () => {
    try {
      if (!newCategoryName.trim()) return;
      await api.addEvaluatorCategory(moduleName, { name: newCategoryName });
      await loadData();
      setNewCategoryName('');
      setOpenCategoryDialog(false);
    } catch (err) {
      setError('Error al agregar categoría: ' + err.message);
    }
  };

  const handleEditCategory = async (category) => {
    try {
      await api.updateEvaluatorCategory(moduleName, category.id, { name: category.name });
      await loadData();
      setOpenCategoryDialog(false);
      setSelectedCategory(null);
      setEditMode(false);
    } catch (err) {
      setError('Error al editar categoría: ' + err.message);
    }
  };

  const handleDeleteCategory = async (categoryId) => {
    setCategoryToDelete(categoryId);
    setOpenDeleteDialog(true);
  };

  const confirmDeleteCategory = async () => {
    try {
      await api.deleteEvaluatorCategory(moduleName, categoryToDelete);
      await loadData();
      setOpenDeleteDialog(false);
      setCategoryToDelete(null);
      setSelectedTab(0); // Volver a "Sin Categoría" después de eliminar
    } catch (err) {
      setError('Error al eliminar categoría: ' + err.message);
    }
  };

  const handleSelectEvaluator = (evaluatorId) => {
    setSelectedEvaluators(prev => 
      prev.includes(evaluatorId)
        ? prev.filter(id => id !== evaluatorId)
        : [...prev, evaluatorId]
    );
  };

  const handleSelectAll = (evaluators) => {
    setSelectedEvaluators(prev => 
      prev.length === evaluators.length ? [] : evaluators.map(e => e.id)
    );
  };

  const handleUpdateEvaluatorCategory = async (evaluatorIds, categoryId) => {
    try {
      setLoading(true);
      const ids = Array.isArray(evaluatorIds) ? evaluatorIds : [evaluatorIds];
      
      await Promise.all(ids.map(evaluatorId =>
        api.updateEvaluatorCategoryAssignment(moduleName, evaluatorId, {
          categoryId: categoryId || null
        })
      ));
      
      await loadData();
      setSelectedEvaluators([]);
      setError(null);
    } catch (err) {
      setError('Error al actualizar evaluadores: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const filteredEvaluators = evaluators.filter(evaluator =>
    evaluator.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const renderHeader = () => (
    <Stack direction="row" spacing={2} alignItems="center" sx={{ mb: 2 }}>
      <Stack direction="row" spacing={2} alignItems="center" sx={{ flexGrow: 1 }}>
        <FormControl size="small" sx={{ minWidth: 120 }}>
          <Select
            value={moduleName}
            onChange={(e) => onModuleChange(e.target.value)}
            sx={{ 
              '& .MuiSelect-select': { 
                py: 1,
                fontWeight: 500,
                fontSize: '1.1rem',
                color: 'primary.main'
              }
            }}
          >
            {modules.map((module) => (
              <MenuItem key={module} value={module}>
                {module}
              </MenuItem>
            ))}
          </Select>
        </FormControl>
        <TextField
          size="small"
          placeholder="Buscar evaluadores..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon />
              </InputAdornment>
            ),
          }}
          sx={{ 
            maxWidth: 300,
            '& .MuiOutlinedInput-root': {
              backgroundColor: 'background.paper',
            }
          }}
        />
      </Stack>
      <Button
        variant="contained"
        startIcon={<AddIcon />}
        onClick={() => setOpenCategoryDialog(true)}
        size="small"
      >
        Nueva Categoría
      </Button>
    </Stack>
  );

  const renderTabs = () => {
    const allTabs = [
      { id: null, name: 'Sin Categoría' },
      ...categories
    ];

    return (
      <Box sx={{ 
        backgroundColor: 'background.paper',
        borderRadius: 2,
        mb: 2,
        boxShadow: 1
      }}>
        <Tabs 
          value={selectedTab} 
          onChange={(e, newValue) => setSelectedTab(newValue)}
          variant="scrollable"
          scrollButtons="auto"
          sx={{
            px: 2,
            '& .MuiTab-root': {
              minHeight: '48px',
              textTransform: 'none',
              fontSize: '0.95rem'
            }
          }}
        >
          {allTabs.map((tab, index) => (
            <Tab
              key={tab.id || 'uncategorized'}
              label={
                <Stack direction="row" spacing={1} alignItems="center">
                  <span>{tab.name}</span>
                  <span style={{ 
                    backgroundColor: alpha('#000', 0.08),
                    padding: '2px 8px',
                    borderRadius: '12px',
                    fontSize: '0.85rem'
                  }}>
                    {filteredEvaluators.filter(e => e.categoryId === tab.id).length}
                  </span>
                  {index > 0 && (
                    <Stack direction="row" spacing={0.5}>
                      <IconButton
                        size="small"
                        onClick={(e) => {
                          e.stopPropagation();
                          setSelectedCategory(tab);
                          setEditMode(true);
                          setOpenCategoryDialog(true);
                        }}
                        sx={{ 
                          color: 'primary.main',
                          '&:hover': { backgroundColor: alpha('#000', 0.04) }
                        }}
                      >
                        <EditIcon fontSize="small" />
                      </IconButton>
                      <IconButton
                        size="small"
                        color="error"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleDeleteCategory(tab.id);
                        }}
                        sx={{ '&:hover': { backgroundColor: alpha('#f44336', 0.04) } }}
                      >
                        <DeleteIcon fontSize="small" />
                      </IconButton>
                    </Stack>
                  )}
                </Stack>
              }
            />
          ))}
        </Tabs>
      </Box>
    );
  };

  const renderEvaluatorsList = () => {
    const currentCategory = selectedTab === 0 ? null : categories[selectedTab - 1];
    const currentEvaluators = filteredEvaluators.filter(e => e.categoryId === (currentCategory?.id ?? null));

    return (
      <Box>
        {currentEvaluators.length > 0 && (
          <ListItem
            sx={{
              py: 1,
              px: 2,
              borderBottom: '1px solid',
              borderColor: 'divider',
              bgcolor: alpha('#000', 0.02),
            }}
          >
            <ListItemIcon sx={{ minWidth: 40 }}>
              <Checkbox
                edge="start"
                checked={selectedEvaluators.length === currentEvaluators.length}
                indeterminate={selectedEvaluators.length > 0 && selectedEvaluators.length < currentEvaluators.length}
                onChange={() => handleSelectAll(currentEvaluators)}
                sx={{ p: 0 }}
              />
            </ListItemIcon>
            <ListItemText 
              primary={
                <Typography variant="body2" color="text.secondary">
                  {selectedEvaluators.length > 0 
                    ? `${selectedEvaluators.length} evaluador${selectedEvaluators.length !== 1 ? 'es' : ''} seleccionado${selectedEvaluators.length !== 1 ? 's' : ''}`
                    : 'Seleccionar todos'}
                </Typography>
              }
            />
            {selectedEvaluators.length > 0 && (
              <Stack direction="row" spacing={1} sx={{ ml: 2 }}>
                {currentCategory ? (
                  <Button
                    size="small"
                    variant="outlined"
                    color="error"
                    onClick={() => handleUpdateEvaluatorCategory(selectedEvaluators, null)}
                    startIcon={<DeleteIcon sx={{ fontSize: 16 }} />}
                    sx={{
                      py: 0.5,
                      minHeight: 0,
                      borderRadius: '12px',
                      textTransform: 'none',
                      fontSize: '0.8rem',
                    }}
                  >
                    Quitar seleccionados
                  </Button>
                ) : (
                  categories.map((cat) => (
                    <Button
                      key={cat.id}
                      size="small"
                      variant="outlined"
                      onClick={() => handleUpdateEvaluatorCategory(selectedEvaluators, cat.id)}
                      startIcon={<PersonIcon sx={{ fontSize: 16 }} />}
                      sx={{
                        py: 0.5,
                        minHeight: 0,
                        borderRadius: '12px',
                        textTransform: 'none',
                        fontSize: '0.8rem',
                      }}
                    >
                      Mover a {cat.name}
                    </Button>
                  ))
                )}
              </Stack>
            )}
          </ListItem>
        )}
        <List sx={{ width: '100%', p: 0 }}>
          {currentEvaluators
            .sort((a, b) => a.name.localeCompare(b.name))
            .map((evaluator) => (
              <ListItem
                key={evaluator.id}
                sx={{
                  py: 1,
                  px: 2,
                  borderBottom: '1px solid',
                  borderColor: 'divider',
                  '&:hover': {
                    backgroundColor: alpha('#000', 0.02)
                  },
                  '&:last-child': {
                    borderBottom: 'none'
                  },
                  ...(selectedEvaluators.includes(evaluator.id) && {
                    bgcolor: alpha('#1976d2', 0.08),
                    '&:hover': {
                      bgcolor: alpha('#1976d2', 0.12)
                    }
                  })
                }}
              >
                <ListItemIcon sx={{ minWidth: 40 }}>
                  <Checkbox
                    edge="start"
                    checked={selectedEvaluators.includes(evaluator.id)}
                    onChange={() => handleSelectEvaluator(evaluator.id)}
                    sx={{ p: 0 }}
                  />
                </ListItemIcon>
                <ListItemAvatar>
                  <Avatar 
                    sx={{ 
                      width: 32,
                      height: 32,
                      bgcolor: 'primary.light',
                      color: 'primary.dark'
                    }}
                  >
                    <PersonIcon sx={{ fontSize: 20 }} />
                  </Avatar>
                </ListItemAvatar>
                <ListItemText 
                  primary={evaluator.name}
                  primaryTypographyProps={{
                    variant: 'body2',
                    fontWeight: 500,
                    color: 'text.primary'
                  }}
                />
                {!selectedEvaluators.includes(evaluator.id) && (
                  <Stack direction="row" spacing={1} sx={{ ml: 2, flexWrap: 'wrap', gap: 1 }}>
                    {currentCategory ? (
                      <Button
                        size="small"
                        variant="outlined"
                        color="error"
                        onClick={() => handleUpdateEvaluatorCategory(evaluator.id, null)}
                        startIcon={<DeleteIcon sx={{ fontSize: 16 }} />}
                        sx={{
                          py: 0.5,
                          minHeight: 0,
                          borderRadius: '12px',
                          textTransform: 'none',
                          fontSize: '0.8rem',
                          '&:hover': {
                            backgroundColor: alpha('#f44336', 0.04)
                          }
                        }}
                      >
                        Quitar
                      </Button>
                    ) : (
                      categories.map((cat) => (
                        <Button
                          key={cat.id}
                          size="small"
                          variant="outlined"
                          onClick={() => handleUpdateEvaluatorCategory(evaluator.id, cat.id)}
                          startIcon={<PersonIcon sx={{ fontSize: 16 }} />}
                          sx={{
                            py: 0.5,
                            minHeight: 0,
                            borderRadius: '12px',
                            textTransform: 'none',
                            fontSize: '0.8rem',
                            '&:hover': {
                              backgroundColor: alpha('#1976d2', 0.04)
                            }
                          }}
                        >
                          {cat.name}
                        </Button>
                      ))
                    )}
                  </Stack>
                )}
              </ListItem>
            ))}
        </List>
      </Box>
    );
  };

  const renderDialogs = () => (
    <>
      <Dialog 
        open={openCategoryDialog} 
        onClose={() => {
          setOpenCategoryDialog(false);
          setEditMode(false);
          setNewCategoryName('');
          setSelectedCategory(null);
        }}
      >
        <DialogTitle>
          {editMode ? 'Editar Categoría' : 'Nueva Categoría'}
        </DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Nombre de la categoría"
            fullWidth
            value={editMode ? selectedCategory?.name : newCategoryName}
            onChange={(e) => {
              if (editMode) {
                setSelectedCategory({
                  ...selectedCategory,
                  name: e.target.value
                });
              } else {
                setNewCategoryName(e.target.value);
              }
            }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => {
            setOpenCategoryDialog(false);
            setEditMode(false);
            setNewCategoryName('');
            setSelectedCategory(null);
          }}>
            Cancelar
          </Button>
          <Button 
            onClick={() => {
              if (editMode) {
                handleEditCategory(selectedCategory);
              } else {
                handleAddCategory();
              }
            }}
            variant="contained"
          >
            {editMode ? 'Guardar' : 'Agregar'}
          </Button>
        </DialogActions>
      </Dialog>

      <Dialog
        open={openDeleteDialog}
        onClose={() => {
          setOpenDeleteDialog(false);
          setCategoryToDelete(null);
        }}
      >
        <DialogTitle>Confirmar eliminación</DialogTitle>
        <DialogContent>
          <DialogContentText>
            ¿Está seguro de que desea eliminar esta categoría? Los evaluadores asignados a esta categoría quedarán sin categoría.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => {
            setOpenDeleteDialog(false);
            setCategoryToDelete(null);
          }}>
            Cancelar
          </Button>
          <Button onClick={confirmDeleteCategory} color="error" variant="contained">
            Eliminar
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );

  if (loading) {
    return (
      <Box sx={{ 
        display: 'flex', 
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        height: '100%',
        gap: 2
      }}>
        <Fade in={true} style={{ transitionDelay: '100ms' }}>
          <CircularProgress size={40} />
        </Fade>
        <Fade in={true} style={{ transitionDelay: '200ms' }}>
          <Typography variant="body1" color="text.secondary">
            Cargando datos...
          </Typography>
        </Fade>
      </Box>
    );
  }

  return (
    <Box sx={{ 
      height: '100%',
      display: 'flex',
      flexDirection: 'column',
      p: 2,
      gap: 2,
      bgcolor: 'background.default',
    }}>
      {error && (
        <Fade in={true}>
          <Alert 
            severity="error" 
            sx={{ 
              py: 0,
              borderRadius: 1
            }}
          >
            {error}
          </Alert>
        </Fade>
      )}

      <Fade in={true} style={{ transitionDelay: '100ms' }}>
        <div>
          {renderHeader()}
        </div>
      </Fade>
      
      <Fade in={true} style={{ transitionDelay: '200ms' }}>
        <Box sx={{ 
          flexGrow: 1,
          display: 'flex',
          flexDirection: 'column',
          bgcolor: 'background.paper',
          borderRadius: 1,
          overflow: 'hidden',
        }}>
          {renderTabs()}
          <Box sx={{ 
            flexGrow: 1,
            overflow: 'auto',
            '&::-webkit-scrollbar': {
              width: '6px',
            },
            '&::-webkit-scrollbar-track': {
              background: '#f1f1f1',
            },
            '&::-webkit-scrollbar-thumb': {
              background: '#bbb',
              '&:hover': {
                background: '#999'
              }
            },
          }}>
            {renderEvaluatorsList()}
          </Box>
        </Box>
      </Fade>
      
      {renderDialogs()}
    </Box>
  );
};

export default EvaluatorManagement; 