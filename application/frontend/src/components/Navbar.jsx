import React, { useState } from 'react';
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

const COLORS = {
  primary: '#1B998B',
  secondry: '#f67e7d',
  background: '#ebf1f8',
  paperBackground: '#ffffff',
  buttonBackground: '#1B998B',
  buttonHover: '#14766d',
  textFieldBorder: '#d0eae7',
  textFieldFocusBorder: '#1B998B',
  fileItemBackground: '#f4f6f9',
};

const CustomMenuIcon = (props) => (
  <SvgIcon {...props} viewBox="0 0 100 80" width="24" height="24">
    <rect width="100" height="10" rx="8" fill="currentColor"></rect>
    <rect y="30" width="100" height="10" rx="8" fill="currentColor"></rect>
    <rect y="60" width="100" height="10" rx="8" fill="currentColor"></rect>
  </SvgIcon>
);

const Navbar = ({ onMenuClick, sidebarOpen }) => {
  const theme = useTheme();
  const isSmallScreen = useMediaQuery(theme.breakpoints.down('sm'));

  const [anchorEl, setAnchorEl] = useState(null);
  const open = Boolean(anchorEl);

  const [themeAnchorEl, setThemeAnchorEl] = useState(null);
  const themeMenuOpen = Boolean(themeAnchorEl);

  const [currentTheme, setCurrentTheme] = useState('light'); // ou 'dark'

  const handleSelectTheme = (mode) => {
      setCurrentTheme(mode);
      setThemeAnchorEl(null);
      // appelle ton système de changement de thème ici
      // ex : toggleTheme(mode)
    };

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
    alert('Déconnexion');
    handleMenuClose();
  };

  return (
    <AppBar
      position="fixed"
      elevation={0}
      sx={{
        backgroundColor: '#f9f9f9',
        color: COLORS.primary,
        borderBottom: '1px solid #e0e0e0',
        zIndex: 1201,
        boxShadow: '0 2px 8px rgba(27, 153, 139, 0.15)', // box-shadow léger sur la barre
      }}
    >
      <Toolbar sx={{ height: '68px' }}>
        {!sidebarOpen && (
          <IconButton
            edge="start"
            color="inherit"
            onClick={onMenuClick}
            sx={{
              backgroundColor: COLORS.primary,
              color: '#fff',
              borderRadius: '12px',
              boxShadow: '0 6px 14px rgba(27, 153, 139, 0.35)', // ombre plus marquée pour bouton
              mr: 2,
              mt: 1.5,
              ml: 1,
              mb: 1,
              transition: 'background-color 0.3s ease',
              '&:hover': {
                backgroundColor: COLORS.buttonHover,
                boxShadow: '0 8px 20px rgba(20, 118, 109, 0.5)',
              },
            }}
          >
            <CustomMenuIcon />
          </IconButton>
        )}

        <Typography
            variant="h6"
            sx={{
              flexGrow: 1,
              fontWeight: 'bold',
              mt: 0.5,
              fontFamily: 'Arial, sans-serif',
              fontSize: '1.6rem',
              userSelect: 'none',
              textShadow: '0 2px 6px rgba(27, 153, 139, 0.4)', // légère ombre portée au texte
              // ou si tu préfères un boxShadow "bloc" autour du texte (un glow) :
              // boxShadow: '0 4px 10px rgba(27, 153, 139, 0.3)',
            }}
          >
            <span style={{ color: COLORS.primary }}>Sum</span>
            <span style={{ color: COLORS.secondry }}>AI</span>
          </Typography>

        {/* Bouton profil à droite */}
        <Box>
          <IconButton
            size="large"
            edge="end"
            color="inherit"
            onClick={handleProfileMenuOpen}
            sx={{
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
            anchorOrigin={{
              vertical: 'bottom',
              horizontal: 'right',
            }}
            transformOrigin={{
              vertical: 'top',
              horizontal: 'right',
            }}
            PaperProps={{
              sx: {
                backgroundColor: COLORS.paperBackground,
                borderRadius: '12px',
                boxShadow: '0 8px 24px rgba(0,0,0,0.12)', // ombre plus douce et étendue pour menu
                minWidth: 180,
                p: 1,
              },
            }}
          >
            <MenuItem
                onClick={handleThemeClick}
                sx={{
                  borderRadius: 2,
                  color: COLORS.primary,
                  '&:hover': {
                    backgroundColor: COLORS.background,
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
                color: COLORS.primary,
                '&:hover': {
                  backgroundColor: COLORS.background,
                },
              }}
            >
              <SettingsIcon sx={{ fontSize: 20, mr: 1 }} />
              Paramètres
            </MenuItem>

            <Divider
              sx={{
                my: 0.75,
                width: '90%',
                mx: 'auto',
                borderColor: '#d3d3d3',
                opacity: 0.6,
                borderBottomWidth: '1.2px',
                borderRadius: '2px',
              }}
            />

            <MenuItem
              onClick={handleLogout}
              sx={{
                borderRadius: 2,
                fontWeight: 'bold',
                color: COLORS.secondry,
                '&:hover': {
                  backgroundColor: '#ffe6e6',
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
                anchorOrigin={{
                  vertical: 'bottom',
                  horizontal: 'right',
                }}
                transformOrigin={{
                  vertical: 'top',
                  horizontal: 'right',
                }}
                PaperProps={{
                  sx: {
                    backgroundColor: COLORS.paperBackground,
                    borderRadius: '12px',
                    boxShadow: '0 8px 24px rgba(0,0,0,0.12)',
                    minWidth: 180,
                    p: 1,
                  },
                }}
              >
                <MenuItem
                  onClick={() => handleSelectTheme('light')}
                  selected={currentTheme === 'light'}
                  sx={{ borderRadius: 2 }}
                >
                  🌞 Mode clair
                </MenuItem>
                <MenuItem
                  onClick={() => handleSelectTheme('dark')}
                  selected={currentTheme === 'dark'}
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

export default Navbar;
