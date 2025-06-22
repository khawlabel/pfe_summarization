import React, { useEffect, useState } from 'react';
import {
  TextField,
  Button,
  Box,
  Typography,
  Paper,
  Alert,
  Menu,
  MenuItem,
  IconButton
} from '@mui/material';
import { useFormik } from 'formik';
import { useDispatch, useSelector } from 'react-redux';
import { login, resetLogin } from '../features/Auth/authSlice';
import { Link, useNavigate } from 'react-router-dom';
import * as yup from 'yup';
import { useLocation } from 'react-router-dom';

import dz from '../images/flags/algeria.webp';
import en from '../images/flags/uk.webp'; 
import fr from '../images/flags/france.png'; 

import { useTranslation } from 'react-i18next';
import { ThemeContext } from '../ThemeContext'; // ajuste le chemin
import { useContext } from 'react';


const COLORS = {
  primary: '#1B998B',
  secondry: '#cccccc',
  background: '#1c1c1c',
  paperBackground: '#2a2a2a',
  buttonBackground: '#1B998B',
  buttonHover: '#166b79',
  textFieldBorder: '#444',
  textFieldFocusBorder: '#1B998B',
  linkHover: '#E94E1B',
};

const Login = () => {
  const { i18n } = useTranslation();
  const { t } = useTranslation();
      
  const changeLang = (langCode) => {
          i18n.changeLanguage(langCode);
        };
  const [anchorEl, setAnchorEl] = useState(null);
  const open = Boolean(anchorEl);
  const { mode } = useContext(ThemeContext);
  const isDarkMode = mode === 'dark';
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const auth = useSelector((state) => state.auth);

  // Local state pour afficher l'alerte
  const [showError, setShowError] = useState(false);
  useEffect(() => {
    if (auth.isErrorlogin == true) {
      setShowError(true);
    }
  }, [auth.isErrorlogin]);


  const location = useLocation();

  
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

    // Si utilisateur connecté dans Redux, redirige vers page protégée
    if (auth.user?.access_token) {
      setShowError(false); // <-- cache l'erreur quand c'est un succès
      window.location.reload()
    }
  }, [auth.user, navigate]);

  const textFieldStyle = {
    backgroundColor: '#2C2C2C',
    borderRadius: 1,
    '& .MuiOutlinedInput-root': {
      '& input': {
        color: '#ffffff',
      },
      '& fieldset': {
        borderColor: COLORS.textFieldBorder,
      },
      '&:hover fieldset': {
        borderColor: COLORS.buttonHover,
      },
      '&.Mui-focused fieldset': {
        borderColor: COLORS.textFieldFocusBorder,
        borderWidth: '2px',
      },
    },
    '& .MuiInputLabel-root': {
      color: '#aaa',
      fontSize: '0.9rem',
      '&.Mui-focused': {
        color: COLORS.primary,
      },
    },
    '& .MuiFormHelperText-root': {
      color: '#ff6b6b',
    },
    '& input:-webkit-autofill': {
      WebkitBoxShadow: '0 0 0 1000px #2C2C2C inset !important',
      WebkitTextFillColor: '#ffffff !important',
    },
  };

  const schema = yup.object().shape({
    email: yup.string().email(t("invalid_email")).required(t("required_field")),
    password: yup.string().required(t("required_field")),
  });

  const formik = useFormik({
    initialValues: {
      email: '',
      password: '',
    },
    validationSchema: schema,
    onSubmit: (values) => {
      dispatch(login(values));

    },
  });

  return (
    <Box
      sx={{
        height: '100vh',
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        backgroundColor: COLORS.background,
        padding: 5,
      }}
    >
      <Paper
        elevation={3}
        sx={{
          display: 'flex',
          flexDirection: 'row',
          borderRadius: 4,
          backgroundColor: COLORS.paperBackground,
          boxShadow: '0 8px 20px rgba(0, 0, 0, 0.3)',
          overflow: 'hidden',
          width: {
            xs: '80%',
            sm: '60%',
            md: '50%',
            lg: '40%',
          },
          maxWidth: '500px',
        }}
      >
        <Box sx={{ flex: 1, padding: 4 }}>
          <Box display="flex" flexDirection="column" alignItems="center">
            <Typography
              component="h1"
              variant="h5"
              sx={{ color: COLORS.primary, fontWeight: 'bold', marginBottom: 2 }}
            >
              {t("login_title")}
            </Typography>

            {showError && (
              <Alert severity="error" sx={{ mb: 2, width: '93%' }}>
                {auth.messagelogin}
              </Alert>
            )}

            <Box component="form" onSubmit={formik.handleSubmit} sx={{ mt: 1 }}>
              <TextField
                margin="dense"
                required
                fullWidth
                id="email"
                label={t("login_email")}
                name="email"
                type="email"
                autoComplete="off"
                autoFocus
                value={formik.values.email}
                onChange={formik.handleChange}
                onBlur={formik.handleBlur}
                error={formik.touched.email && Boolean(formik.errors.email)}
                helperText={formik.touched.email && formik.errors.email}
                sx={textFieldStyle}
              />
              <TextField
                margin="dense"
                required
                fullWidth
                name="password"
                label={t("login_password")}
                type="password"
                id="password"
                autoComplete="new-password"
                value={formik.values.password}
                onChange={formik.handleChange}
                onBlur={formik.handleBlur}
                error={formik.touched.password && Boolean(formik.errors.password)}
                helperText={formik.touched.password && formik.errors.password}
                sx={textFieldStyle}
              />
              <Button
                type="submit"
                fullWidth
                variant="contained"
                disabled={auth.isLoadinglogin}
                sx={{
                  mt: 2,
                  mb: 2,
                  backgroundColor: COLORS.buttonBackground,
                  fontSize: '0.875rem',
                  fontWeight: 'bold',
                  borderRadius: 3,
                  '&:hover': { backgroundColor: COLORS.buttonHover, transform: 'scale(1.03)' },
                  padding: '10px 0',
                }}
              >
                {auth.isLoadinglogin ?  t("login_loading") : t("login_submit")}

              </Button>
            </Box>
          </Box>
          <Typography variant="body2" align="center" sx={{ color: COLORS.secondry, fontWeight: 'normal', fontFamily: 'lato' }}>
            {t("login_no_account")}{" "}
            <Link
              to="/register"
              style={{ color: COLORS.primary, fontWeight: 'bold', textDecoration: 'none', fontFamily: 'lato' }}
              onMouseOver={(e) => (e.target.style.textDecoration = 'underline')}
              onMouseOut={(e) => (e.target.style.textDecoration = 'none')}
            >
               {t("login_register_here")}
            </Link>
          </Typography>
        </Box>
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
            {t("copyright")} © {new Date().getFullYear()} {t("all_rights_reserved")}
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

export default Login;
