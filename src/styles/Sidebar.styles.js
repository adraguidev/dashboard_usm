import { styled } from '@mui/material';
import { ListItem } from '@mui/material';

export const DRAWER_WIDTH = 240;
export const COLLAPSED_DRAWER_WIDTH = 65;

export const DrawerHeader = styled('div')(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
  padding: theme.spacing(0, 1),
  ...theme.mixins.toolbar,
  justifyContent: 'flex-end',
}));

export const StyledListItem = styled(ListItem)(({ theme, active }) => ({
  margin: '8px 8px',
  borderRadius: '12px',
  backgroundColor: active ? theme.palette.primary.main : 'transparent',
  color: active ? theme.palette.primary.contrastText : theme.palette.text.primary,
  '&:hover': {
    backgroundColor: active 
      ? theme.palette.primary.dark 
      : theme.palette.action.hover,
  },
  transition: 'all 0.3s ease',
  minHeight: 48,
  position: 'relative',
}));

export const StyledSubListItem = styled(ListItem)(({ theme, active }) => ({
  margin: '4px 8px 4px 16px',
  borderRadius: '12px',
  backgroundColor: active ? theme.palette.primary.main : 'transparent',
  color: active ? theme.palette.primary.contrastText : theme.palette.text.primary,
  '&:hover': {
    backgroundColor: active 
      ? theme.palette.primary.dark 
      : theme.palette.action.hover,
  },
  transition: 'all 0.3s ease',
  minHeight: 40,
}));

export const sidebarStyles = {
  drawer: (theme, open) => ({
    width: open ? DRAWER_WIDTH : COLLAPSED_DRAWER_WIDTH,
    flexShrink: 0,
    whiteSpace: 'nowrap',
    '& .MuiDrawer-paper': {
      width: open ? DRAWER_WIDTH : COLLAPSED_DRAWER_WIDTH,
      boxSizing: 'border-box',
      borderRight: '1px solid rgba(0, 0, 0, 0.12)',
      backgroundColor: theme.palette.background.default,
      transition: theme.transitions.create(['width', 'margin'], {
        easing: theme.transitions.easing.sharp,
        duration: theme.transitions.duration.enteringScreen,
      }),
      overflowX: 'hidden',
    },
  }),
  title: {
    flexGrow: 1,
    ml: 2
  },
  menuButton: {
    mx: 'auto'
  },
  listItemIcon: (selectedIndex, index) => ({
    color: selectedIndex === index ? 'white' : 'inherit',
    minWidth: 40
  }),
  collapsedListItem: {
    justifyContent: 'center',
    px: 2.5
  },
  collapsedListItemIcon: (selectedIndex, index) => ({
    color: selectedIndex === index ? 'white' : 'inherit',
    minWidth: 0,
    justifyContent: 'center'
  }),
  adminListItem: {
    mb: 1
  },
  collapsedAdminListItem: {
    justifyContent: 'center',
    px: 2.5,
    mb: 1
  }
};