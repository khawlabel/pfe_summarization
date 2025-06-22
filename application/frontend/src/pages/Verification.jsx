import React, { useEffect, useState } from 'react';

import { Link as RouterLink } from 'react-router-dom';
import { Box, Typography, Paper, Button , Menu, MenuItem,IconButton} from '@mui/material';
import CheckCircleOutlineIcon from '@mui/icons-material/CheckCircleOutline';
import checkedIcon from '../images/checked.png';
import { useLocation } from 'react-router-dom';
import { useDispatch } from 'react-redux';
import { verifyCompte }  from '../features/Auth/authSlice';
import { useNavigate } from 'react-router-dom';

import dz from '../images/flags/algeria.webp';
import en from '../images/flags/uk.webp'; 
import fr from '../images/flags/france.png'; 

import { useTranslation } from 'react-i18next';
import { ThemeContext } from '../ThemeContext'; // ajuste le chemin
import { useContext } from 'react';


const COLORS = {
  primary: '#1B998B',                // On garde la couleur principale
  secondry: '#cccccc',              // Texte secondaire clair
  background: '#1c1c1c',            // Fond général sombre
  paperBackground: '#2a2a2a',       // Fond des papiers sombre
  buttonBackground: '#1B998B',      // Bouton couleur principale
  buttonHover: '#166b79',           // Hover du bouton
  textFieldBorder: '#444',          // Bord sombre
  textFieldFocusBorder: '#1B998B',  // Focus avec couleur principale
  linkHover: '#E94E1B',
};


const Verification = () => {

    const { i18n } = useTranslation();
    const { t } = useTranslation();
      
    const changeLang = (langCode) => {
          i18n.changeLanguage(langCode);
        };
    const [anchorEl, setAnchorEl] = useState(null);
    const open = Boolean(anchorEl);
    const { mode } = useContext(ThemeContext);
    const isDarkMode = mode === 'dark';
    const location = useLocation();
    const navigate = useNavigate();
    const dispatch = useDispatch();

    const token = location.pathname.split('/')[2];

    
  const handleClick = (event) => {
    setAnchorEl(event.currentTarget);
  };

    const handleClose = () => {
      setAnchorEl(null);
    };

    const handleLangChange = (lang) => {
      i18n.changeLanguage(lang);
      localStorage.setItem('language', lang); // ✅ persist the choice
      handleClose();
    };

    const getFlagImage = (lang) => {
      switch (lang) {
        case 'en':
          return en;
        case 'fr':
          return fr;
        case 'ar':
          return dz;
        default:
          return en; // par défaut anglais
      }
    };
    
    
      const getLangLabel = (lang) => {
        return t(`lang_${lang}`);
      };
    
    
    const isArabic = i18n.language === 'ar';

  
    useEffect(() => {
      // Dispatch l'action de vérification du compte avec le token
      dispatch(verifyCompte(token));
     
    }, [dispatch, token]);

  return (
    <Box
    dir={isArabic ? 'rtl' : 'ltr'}
      sx={{
        height: '100vh',
        backgroundColor: COLORS.background,
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        padding: 3,
      }}
    >
      <Paper
        elevation={3}
        sx={{
          padding: 5,
          borderRadius: 4,
          backgroundColor: COLORS.paperBackground,
          boxShadow: '0 8px 20px rgba(0, 0, 0, 0.3)', // plus prononcé
          maxWidth: 500,
          width: '100%',
          textAlign: 'center',
        }}
      >
        {/* Affiche l'image */}
        <Box
          component="img"
          src={checkedIcon}
          alt="Icone de vérification"
          sx={{ width: 80, height: 80, marginBottom: 2 }}
        />
        
        <Typography
          variant="h5"
          sx={{
            fontWeight: 'bold',
            color: COLORS.primary,
            marginBottom: 2,
          }}
        >
          {t('verification_title')}
        </Typography>

        <Typography
          variant="body1"
          sx={{
            marginBottom: 2,
            color: COLORS.secondry,
            fontSize: '1rem',
            fontFamily: 'Lato, sans-serif',
          }}
        >
            {t('verification_success1')}<br />
            {t('verification_success2')}
        </Typography>


        <Button
          component={RouterLink}  // <-- ici
          variant="contained"
          to="/login"
          sx={{
            mt: 2,
            backgroundColor: COLORS.buttonBackground,
            fontSize: '0.875rem',
            fontWeight: 'bold',
            borderRadius: 3,
            padding: '10px 20px',
            '&:hover': {
              backgroundColor: COLORS.buttonHover,
              transform: 'scale(1.03)',
            },
          }}
        >
          {t('verification_login_button')}
        </Button>
       </Paper>
              <Box
                sx={{
                  position: 'fixed',
                  bottom: 10,
                  left: 0,
                  right: 0,
                  zIndex: 9999,
                }}
              >
                <Typography
                  align="center"
                  sx={{
                    color: '#cccccc',
                    fontSize: '0.95rem',
                    fontFamily: `'Cormorant Garamond', serif`, // écriture élégante
                    letterSpacing: '0.5px',
                    fontStyle: 'italic',
                    fontWeight: 500,
                    fontSize: isArabic ? '0.8rem' : '0.rem', 
                  }}
                >
                   {t('copyright')} © {new Date().getFullYear()} {t('all_rights_reserved')}
                </Typography>
              </Box>
                    {/* === Bouton flottant pour switch de langue === */}
        <Box
        sx={{
          position: 'fixed',
          bottom: 20,
          left: 20,
          zIndex: 9999,
        }}
      >
        <IconButton
          onClick={handleClick}
          sx={{
            width: 50,
            height: 50,
            backgroundColor: COLORS.buttonBackground,
            borderRadius: '50%',
            boxShadow: isDarkMode
            ? '0 4px 10px rgba(0, 255, 255, 0.15)'
            : '0 4px 10px rgba(0, 0, 0, 0.15)',
          transition: 'all 0.3s ease',
          opacity: 0.5, // ✅ légère transparence
          transform: 'scale(1)', // ✅ état initial
          '&:hover': {
            backgroundColor: COLORS.buttonHover,
           
            opacity: 1, // ✅ plein visible au hover
            },
          }}
        >
          <Box
        component="img"
        src={getFlagImage(i18n.language)}
        alt="flag"
        sx={{
          width: 28,
          height: 28,
          borderRadius: '50%',
          objectFit: 'cover',
        }}
      />
      
        </IconButton>
      
        <Menu
          anchorEl={anchorEl}
          open={open}
          onClose={handleClose}
          anchorOrigin={{ vertical: 'top', horizontal: 'right' }}
          transformOrigin={{ vertical: 'bottom', horizontal: 'left' }}
          sx={{
            '& .MuiMenu-paper': {
              backgroundColor: COLORS.paperBackground,
              borderRadius: '12px',
              boxShadow: isDarkMode
                ? '0px 8px 20px rgba(0, 255, 255, 0.08)'
                : '0px 10px 30px rgba(0, 0, 0, 0.1)',
              border: `1px solid ${COLORS.textFieldBorder}`,
              padding: '8px 0',
            },
          }}
        >
          {[
        { code: 'en', label: 'English', image: en },
        { code: 'fr', label: 'Français', image: fr },
        { code: 'ar', label: 'العربية', image: dz },
      ].map(({ code, label, image }) => (
      
            <MenuItem
        key={code}
        onClick={() => handleLangChange(code)}
        sx={{
          color: COLORS.secondry,
          fontWeight: i18n.language === code ? 'bold' : 'normal',
          fontSize: '1rem',
          display: 'flex',
          alignItems: 'center',
          paddingY: '8px',
          paddingX: '16px',
          gap: 1,
          transition: 'transform 0.2s ease, background-color 0.2s ease',
          '&:hover': {
            transform: 'scale(1.05)',
            backgroundColor: isDarkMode ? '#2a2a2a' : '#f5f5f5',
          },
        }}
      >
        <Box
          component="img"
          src={image}
          alt={label}
          sx={{
            width: 24,
            height: 24,
            borderRadius: '4px',
            mr: 1,
            transition: 'transform 0.3s ease',
          }}
        />
         <Typography>{getLangLabel(code)}</Typography>
      </MenuItem>
      
          ))}
        </Menu>
      </Box>
    </Box>
  );
};

export default Verification;
