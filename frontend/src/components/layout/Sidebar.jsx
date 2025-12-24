import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Divider,
  Box,
  Typography,
} from '@mui/material';
import {
  Dashboard as DashboardIcon,
  DevicesOther as DevicesIcon,
  Warning as AlertsIcon,
  BugReport as VulnIcon,
  AccountTree as TopologyIcon,
  Science as ResearchIcon,
  Settings as SettingsIcon,
} from '@mui/icons-material';

const DRAWER_WIDTH = 240;
const DRAWER_WIDTH_COLLAPSED = 60;

const menuItems = [
  { text: 'Dashboard', icon: <DashboardIcon />, path: '/dashboard' },
  { text: 'Devices', icon: <DevicesIcon />, path: '/devices' },
  { text: 'Alerts', icon: <AlertsIcon />, path: '/alerts' },
  { text: 'Vulnerabilities', icon: <VulnIcon />, path: '/vulnerabilities' },
  { text: 'Network Topology', icon: <TopologyIcon />, path: '/topology' },
  { text: 'Research', icon: <ResearchIcon />, path: '/research' },
  { text: 'Settings', icon: <SettingsIcon />, path: '/settings' },
];

const Sidebar = ({ open, onToggle }) => {
  const navigate = useNavigate();
  const location = useLocation();

  const handleNavigation = (path) => {
    navigate(path);
  };

  return (
    <Drawer
      variant="permanent"
      sx={{
        width: open ? DRAWER_WIDTH : DRAWER_WIDTH_COLLAPSED,
        flexShrink: 0,
        '& .MuiDrawer-paper': {
          width: open ? DRAWER_WIDTH : DRAWER_WIDTH_COLLAPSED,
          boxSizing: 'border-box',
          transition: 'width 0.3s ease',
          overflowX: 'hidden',
          mt: 8, // Account for header height
          height: 'calc(100vh - 64px)',
        },
      }}
    >
      <Box sx={{ overflow: 'auto' }}>
        {open && (
          <Box sx={{ p: 2, textAlign: 'center' }}>
            <Typography variant="h6" color="primary">
              IoT Security
            </Typography>
            <Typography variant="caption" color="text.secondary">
              Research Platform
            </Typography>
          </Box>
        )}

        <Divider />

        <List>
          {menuItems.map((item) => (
            <ListItem key={item.text} disablePadding>
              <ListItemButton
                onClick={() => handleNavigation(item.path)}
                selected={location.pathname === item.path}
                sx={{
                  minHeight: 48,
                  justifyContent: open ? 'initial' : 'center',
                  px: 2.5,
                }}
              >
                <ListItemIcon
                  sx={{
                    minWidth: 0,
                    mr: open ? 3 : 'auto',
                    justifyContent: 'center',
                  }}
                >
                  {item.icon}
                </ListItemIcon>
                <ListItemText
                  primary={item.text}
                  sx={{ opacity: open ? 1 : 0 }}
                />
              </ListItemButton>
            </ListItem>
          ))}
        </List>

        <Divider />

        {open && (
          <Box sx={{ p: 2, mt: 'auto' }}>
            <Typography variant="caption" color="text.secondary">
              Version 2.0.0
            </Typography>
            <br />
            <Typography variant="caption" color="text.secondary">
              Research Grade Platform
            </Typography>
          </Box>
        )}
      </Box>
    </Drawer>
  );
};

export default Sidebar;