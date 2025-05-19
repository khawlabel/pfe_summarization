
import {
  AppBar,
  Box,
  IconButton,
  Toolbar,
  Typography,
  useTheme,
  useMediaQuery,
  SvgIcon,
  Menu,
  MenuItem,
  Divider,
} from '@mui/material';
import AccountCircle from '@mui/icons-material/AccountCircle';
import SettingsIcon from '@mui/icons-material/Settings';
import LogoutIcon from '@mui/icons-material/Logout';
import PaletteIcon from '@mui/icons-material/Palette';
import React, { useEffect,useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Link, useNavigate } from 'react-router-dom';
import  { useContext } from 'react';
import { ThemeContext } from '../ThemeContext';

const CustomMenuIcon = (props) => (
  <SvgIcon {...props} viewBox="0 0 100 80" width="24" height="24">
    <rect width="100" height="10" rx="8" fill="currentColor"></rect>
    <rect y="30" width="100" height="10" rx="8" fill="currentColor"></rect>
    <rect y="60" width="100" height="10" rx="8" fill="currentColor"></rect>
  </SvgIcon>
);

const NavbarUploadFiles = ({ onMenuClick, sidebarOpen }) => {
  const { mode, toggleTheme } = useContext(ThemeContext);

  const theme = useTheme();
  const isSmallScreen = useMediaQuery(theme.breakpoints.down('sm'));

  const [anchorEl, setAnchorEl] = useState(null);
  const open = Boolean(anchorEl);
  const [themeAnchorEl, setThemeAnchorEl] = useState(null);
  const themeMenuOpen = Boolean(themeAnchorEl);

  
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const auth = useSelector((state) => state.auth);

 

  const handleProfileMenuOpen = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleThemeClick = (event) => {
    setThemeAnchorEl(event.currentTarget);
  };

  const handleThemeMenuClose = () => {
    setThemeAnchorEl(null);
  };

  const handleSettings = () => {
    alert('Paramètres');
    handleMenuClose();
  };
  const handleLogout = () => {
    localStorage.removeItem("user"); // Supprime l'utilisateur du stockage local  
    localStorage.removeItem("uploadDone");
    localStorage.removeItem("theme"); // Supprime le thème enregistré
    window.location.reload()
  };

  return (
    <AppBar
      position="fixed"
      elevation={0}
      sx={{
        backgroundColor: theme.palette.mode === 'dark'
                        ? '#121212' :'#ebf1f8',
        color: theme.palette.primary.main,
        borderBottom: `1px solid ${theme.palette.divider}`,
        zIndex: 1201,
        boxShadow: `0 2px 8px ${theme.palette.mode === 'dark' ? 'rgba(0,0,0,0.5)' : 'rgba(27,153,139,0.15)'}`,
      }}
    >
      <Toolbar sx={{ height: '68px' }}>
      
        <Typography
          variant="h6"
          sx={{
            flexGrow: 1,
            fontWeight: 'bold',
            mt: 0.5,
            fontFamily: 'Arial, sans-serif',
            fontSize: '1.6rem',
            userSelect: 'none',
            textShadow: theme.palette.mode === 'dark'
              ? '0 2px 6px rgba(255, 255, 255, 0.1)'
              : '0 2px 6px rgba(27, 153, 139, 0.4)',
          }}
        >
          <span style={{ color: theme.palette.primary.main }}>Sum</span>
          <span style={{ color: theme.palette.secondary.main }}>AI</span>
        </Typography>

        <Box>
          <IconButton
            size="large"
            edge="end"
            onClick={handleProfileMenuOpen}
            sx={{
              color: theme.palette.primary.main,
              '& svg': {
                fontSize: 38,
                transition: 'transform 0.3s ease',
              },
              '&:hover svg': {
                transform: 'scale(1.1)',
              },
            }}
          >
            <AccountCircle />
          </IconButton>

          <Menu
            anchorEl={anchorEl}
            open={open}
            onClose={handleMenuClose}
            anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
            transformOrigin={{ vertical: 'top', horizontal: 'right' }}
            PaperProps={{
              sx: {
                backgroundColor: theme.palette.background.paper,
                borderRadius: '12px',
                boxShadow: theme.shadows[5],
                minWidth: 180,
                p: 1,
              },
            }}
          >
            <MenuItem
              onClick={handleThemeClick}
              sx={{
                borderRadius: 2,
                color: theme.palette.primary.main,
                '&:hover': {
                  backgroundColor: theme.palette.action.hover,
                },
              }}
            >
              <PaletteIcon sx={{ fontSize: 20, mr: 1 }} />
              Thème
            </MenuItem>

            <MenuItem
              onClick={handleSettings}
              sx={{
                borderRadius: 2,
                color: theme.palette.primary.main,
                '&:hover': {
                  backgroundColor: theme.palette.action.hover,
                },
              }}
            >
              <SettingsIcon sx={{ fontSize: 20, mr: 1 }} />
              Paramètres
            </MenuItem>

            <Divider sx={{ my: 0.75, width: '90%', mx: 'auto' }} />

            <MenuItem
              onClick={handleLogout}
              sx={{
                borderRadius: 2,
                fontWeight: 'bold',
                color: theme.palette.secondary.main,
                '&:hover': {
                  backgroundColor: theme.palette.mode === 'dark' ? '#5a4747': '#ffe6e6',
                },
              }}
            >
              <LogoutIcon sx={{ fontSize: 23, mr: 1 }} />
              Déconnexion
            </MenuItem>
          </Menu>

          <Menu
            anchorEl={themeAnchorEl}
            open={themeMenuOpen}
            onClose={handleThemeMenuClose}
            anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
            transformOrigin={{ vertical: 'top', horizontal: 'right' }}
            PaperProps={{
              sx: {
                backgroundColor: theme.palette.background.paper,
                borderRadius: '12px',
                boxShadow: theme.shadows[5],
                minWidth: 180,
                p: 1,
              },
            }}
          >
           <MenuItem
              onClick={() => {
                if (mode !== 'light') {
                  toggleTheme();
                }
              }}
              selected={mode === 'light'}
              sx={{ borderRadius: 2 }}
            >
              🌞 Mode clair
            </MenuItem>

            <MenuItem
              onClick={() => {
                if (mode !== 'dark') {
                  toggleTheme();
                }
              }}
              selected={mode === 'dark'}
              sx={{ borderRadius: 2 }}
            >
              🌙 Mode sombre
            </MenuItem>

          </Menu>
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default NavbarUploadFiles;
