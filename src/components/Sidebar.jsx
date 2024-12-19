import React, { useState } from 'react';
import {
  Box,
  Drawer,
  List,
  ListItemIcon,
  ListItemText,
  IconButton,
  Typography,
  useTheme,
  Collapse,
  Tooltip
} from '@mui/material';
import {
  Dashboard as DashboardIcon,
  Assignment as CCMIcon,
  SupervisorAccount as PRRIcon,
  School as CCMESPIcon,
  Gavel as CCMLEYIcon,
  WbSunny as SOLIcon,
  Star as SPEIcon,
  Settings as AdminIcon,
  ChevronLeft as ChevronLeftIcon,
  Menu as MenuIcon,
  ExpandLess,
  ExpandMore
} from '@mui/icons-material';
import {
  DrawerHeader,
  StyledListItem,
  StyledSubListItem,
  sidebarStyles,
  DRAWER_WIDTH,
  COLLAPSED_DRAWER_WIDTH
} from '../styles/Sidebar.styles';
import { modules } from '../config/moduleConfig.jsx';

const menuItems = [
  { 
    text: 'Dashboard', 
    icon: <DashboardIcon />, 
    path: '/',
    subItems: [
      { text: 'CCM', icon: <CCMIcon />, path: '/ccm' },
      { text: 'PRR', icon: <PRRIcon />, path: '/prr' },
      { text: 'CCM-ESP', icon: <CCMESPIcon />, path: '/ccm-esp' },
      { text: 'CCM-LEY', icon: <CCMLEYIcon />, path: '/ccm-ley' },
      { text: 'SOL', icon: <SOLIcon />, path: '/sol' },
      { text: 'SPE', icon: <SPEIcon />, path: '/spe' },
    ]
  }
];

const Sidebar = ({ onModuleSelect, onAdminClick }) => {
  const theme = useTheme();
  const [open, setOpen] = useState(true);
  const [selectedIndex, setSelectedIndex] = useState(0);
  const [selectedSubIndex, setSelectedSubIndex] = useState(-1);
  const [submenuOpen, setSubmenuOpen] = useState(true);

  const handleDrawerToggle = () => {
    setOpen(!open);
    if (!open) {
      setSubmenuOpen(true);
    }
  };

  const handleSubmenuClick = () => {
    if (open) {
      setSubmenuOpen(!submenuOpen);
    }
  };

  const handleModuleSelect = (moduleId) => {
    if (onModuleSelect) {
      onModuleSelect(moduleId);
    }
  };

  const renderMenuItems = () => (
    <List>
      {menuItems.map((item, index) => (
        <React.Fragment key={item.text}>
          {open ? (
            <StyledListItem
              button
              active={index === selectedIndex && selectedSubIndex === -1 ? 1 : 0}
              onClick={handleSubmenuClick}
            >
              <ListItemIcon sx={sidebarStyles.listItemIcon(selectedIndex, index)}>
                {item.icon}
              </ListItemIcon>
              <ListItemText primary={item.text} />
              {submenuOpen ? <ExpandLess /> : <ExpandMore />}
            </StyledListItem>
          ) : (
            <Tooltip title={item.text} placement="right">
              <StyledListItem
                button
                active={index === selectedIndex && selectedSubIndex === -1 ? 1 : 0}
                onClick={handleSubmenuClick}
                sx={sidebarStyles.collapsedListItem}
              >
                <ListItemIcon sx={sidebarStyles.collapsedListItemIcon(selectedIndex, index)}>
                  {item.icon}
                </ListItemIcon>
              </StyledListItem>
            </Tooltip>
          )}
          <Collapse in={submenuOpen && open} timeout="auto" unmountOnExit>
            <List component="div" disablePadding>
              {item.subItems.map((subItem, subIndex) => (
                open ? (
                  <StyledSubListItem
                    button
                    key={subItem.text}
                    active={selectedSubIndex === subIndex ? 1 : 0}
                    onClick={() => {
                      setSelectedIndex(index);
                      setSelectedSubIndex(subIndex);
                      handleModuleSelect(subItem.text);
                    }}
                  >
                    <ListItemIcon sx={sidebarStyles.listItemIcon(selectedSubIndex, subIndex)}>
                      {subItem.icon}
                    </ListItemIcon>
                    <ListItemText primary={subItem.text} />
                  </StyledSubListItem>
                ) : (
                  <Tooltip title={subItem.text} placement="right" key={subItem.text}>
                    <StyledSubListItem
                      button
                      active={selectedSubIndex === subIndex ? 1 : 0}
                      onClick={() => {
                        setSelectedIndex(index);
                        setSelectedSubIndex(subIndex);
                        handleModuleSelect(subItem.text);
                      }}
                      sx={sidebarStyles.collapsedListItem}
                    >
                      <ListItemIcon sx={sidebarStyles.collapsedListItemIcon(selectedSubIndex, subIndex)}>
                        {subItem.icon}
                      </ListItemIcon>
                    </StyledSubListItem>
                  </Tooltip>
                )
              ))}
            </List>
          </Collapse>
        </React.Fragment>
      ))}
    </List>
  );

  return (
    <Drawer
      variant="permanent"
      open={open}
      sx={sidebarStyles.drawer(theme, open)}
    >
      <DrawerHeader>
        {open ? (
          <>
            <Typography variant="h6" sx={sidebarStyles.title}>
              Dashboard USM
            </Typography>
            <IconButton onClick={handleDrawerToggle}>
              <ChevronLeftIcon />
            </IconButton>
          </>
        ) : (
          <IconButton onClick={handleDrawerToggle} sx={sidebarStyles.menuButton}>
            <MenuIcon />
          </IconButton>
        )}
      </DrawerHeader>

      {renderMenuItems()}

      <Box sx={{ flexGrow: 1 }} />

      <List>
        {open ? (
          <StyledListItem
            button
            active={selectedIndex === menuItems.length ? 1 : 0}
            onClick={() => {
              setSelectedIndex(menuItems.length);
              setSelectedSubIndex(-1);
              onAdminClick();
            }}
            sx={sidebarStyles.adminListItem}
          >
            <ListItemIcon sx={sidebarStyles.listItemIcon(selectedIndex, menuItems.length)}>
              <AdminIcon />
            </ListItemIcon>
            <ListItemText primary="Admin" />
          </StyledListItem>
        ) : (
          <Tooltip title="Admin" placement="right">
            <StyledListItem
              button
              active={selectedIndex === menuItems.length ? 1 : 0}
              onClick={() => {
                setSelectedIndex(menuItems.length);
                setSelectedSubIndex(-1);
                onAdminClick();
              }}
              sx={sidebarStyles.collapsedAdminListItem}
            >
              <ListItemIcon sx={sidebarStyles.collapsedListItemIcon(selectedIndex, menuItems.length)}>
                <AdminIcon />
              </ListItemIcon>
            </StyledListItem>
          </Tooltip>
        )}
      </List>
    </Drawer>
  );
};

export default Sidebar; 