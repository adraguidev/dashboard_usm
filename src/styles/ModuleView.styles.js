import { styled, alpha } from '@mui/material';
import { Tab } from '@mui/material';

export const StyledTab = styled(Tab)(({ theme, color }) => ({
  minHeight: 48,
  textTransform: 'none',
  fontSize: '0.9rem',
  fontWeight: 500,
  marginRight: 2,
  color: alpha(color, 0.7),
  '&.Mui-selected': {
    color: color,
    fontWeight: 600,
    backgroundColor: alpha(color, 0.05),
  },
  '&:hover': {
    backgroundColor: alpha(color, 0.05),
    color: color,
  },
  '&.MuiTab-root': {
    borderRadius: '4px 4px 0 0',
  },
  '&:focus': {
    outline: 'none',
  },
  '&.Mui-focusVisible': {
    backgroundColor: alpha(color, 0.05),
  },
  transition: 'all 0.2s ease-in-out',
}));

export const moduleViewStyles = {
  container: {
    display: 'flex',
    flexDirection: 'column',
    height: '100vh',
    width: '100%',
    overflow: 'hidden',
    bgcolor: 'background.default'
  },
  header: {
    py: 2,
    px: 3,
    display: 'flex',
    alignItems: 'center',
    borderBottom: 1,
    borderColor: 'divider',
    bgcolor: 'background.paper'
  },
  headerTitle: {
    fontWeight: 600
  },
  content: {
    flex: 1,
    display: 'flex',
    flexDirection: 'column',
    overflow: 'hidden'
  },
  tabsContainer: {
    borderBottom: 1,
    borderColor: 'divider',
    bgcolor: 'background.paper'
  },
  tabs: {
    px: 2,
    '& .MuiTabs-indicator': {
      height: 3,
      borderRadius: '3px 3px 0 0',
    },
    '& .MuiTabs-scrollButtons': {
      '&.Mui-disabled': {
        opacity: 0.3,
      },
    },
  },
  tabIcon: {
    color: 'inherit',
    fontSize: '1.3rem',
    mr: 1
  },
  tabContent: {
    flex: 1,
    overflow: 'auto',
  },
  tabPanel: {
    p: 2,
    height: '100%',
  },
  paper: {
    p: 3,
    height: '100%',
    borderRadius: 2,
    border: 1,
    borderColor: 'divider',
    bgcolor: 'background.paper'
  },
  tabTitle: {
    mb: 3,
    fontWeight: 600
  }
}; 