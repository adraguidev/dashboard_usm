import { createTheme } from '@mui/material';

export const theme = createTheme({
  palette: {
    primary: {
      main: '#4A90E2',
      light: '#5C9CE5',
      dark: '#357ABD',
      contrastText: '#fff',
    },
    secondary: {
      main: '#FF6B6B',
      light: '#FF8585',
      dark: '#E65151',
      contrastText: '#fff',
    },
    background: {
      default: '#F8FAFC',
      paper: '#FFFFFF',
    },
    success: {
      main: '#2ECC71',
    },
    warning: {
      main: '#F1C40F',
    },
    error: {
      main: '#E74C3C',
    },
    info: {
      main: '#3498DB',
    },
    text: {
      primary: '#2C3E50',
      secondary: '#34495E',
    },
    divider: 'rgba(0, 0, 0, 0.08)',
  },
  typography: {
    fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
    h4: {
      fontWeight: 600,
      fontSize: '1.75rem',
    },
    h5: {
      fontWeight: 600,
      fontSize: '1.25rem',
    },
    h6: {
      fontWeight: 600,
      fontSize: '1rem',
    },
    subtitle1: {
      fontWeight: 500,
      fontSize: '1rem',
    },
  },
  shape: {
    borderRadius: 8,
  },
  components: {
    MuiCssBaseline: {
      styleOverrides: {
        body: {
          backgroundColor: '#F8FAFC',
          height: '100vh',
          overflow: 'hidden'
        }
      }
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          border: '1px solid rgba(0, 0, 0, 0.08)',
          boxShadow: 'none',
          transition: 'transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out',
          '&:hover': {
            transform: 'translateY(-2px)',
            boxShadow: '0px 4px 8px rgba(0, 0, 0, 0.05)',
          },
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          boxShadow: 'none',
        },
      },
    },
    MuiListItemIcon: {
      styleOverrides: {
        root: {
          minWidth: 40,
        },
      },
    },
    MuiDrawer: {
      styleOverrides: {
        paper: {
          backgroundColor: '#FFFFFF',
          borderRight: '1px solid rgba(0, 0, 0, 0.08)',
        },
      },
    },
    MuiTab: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          fontSize: '0.9rem',
          fontWeight: 500,
          minHeight: 48,
          transition: 'all 0.2s ease-in-out',
          '&.Mui-selected': {
            fontWeight: 600,
          },
          '&:focus': {
            outline: 'none',
          },
          '&.Mui-focusVisible': {
            backgroundColor: 'rgba(0, 0, 0, 0.05)',
          },
        },
      },
    },
    MuiTabs: {
      styleOverrides: {
        root: {
          '& .MuiTabs-indicator': {
            transition: 'all 0.2s ease-in-out',
          },
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          borderRadius: 6,
          fontWeight: 500,
          boxShadow: 'none',
          '&:hover': {
            boxShadow: '0px 2px 4px rgba(0, 0, 0, 0.05)',
          },
          '&:focus': {
            outline: 'none',
          },
        },
      },
    },
  },
}); 