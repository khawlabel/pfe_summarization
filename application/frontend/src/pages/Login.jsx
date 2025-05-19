import React, { useEffect, useState } from 'react';
import {
  TextField,
  Button,
  Box,
  Typography,
  Paper,
  Alert
} from '@mui/material';
import { useFormik } from 'formik';
import { useDispatch, useSelector } from 'react-redux';
import { login, resetLogin } from '../features/Auth/authSlice';
import { Link, useNavigate } from 'react-router-dom';
import * as yup from 'yup';
import { useLocation } from 'react-router-dom';

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
    email: yup.string().email("L’adresse e-mail doit être valide").required("Ce champ est obligatoire"),
    password: yup.string().required("Ce champ est obligatoire"),
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
              Connexion
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
                label="Email"
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
                label="Mot de passe"
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
                {auth.isLoadinglogin ? "Connexion..." : "Se connecter"}
              </Button>
            </Box>
          </Box>
          <Typography variant="body2" align="center" sx={{ color: COLORS.secondry, fontWeight: 'normal', fontFamily: 'lato' }}>
            Vous n'avez pas de compte ?{' '}
            <Link
              to="/register"
              style={{ color: COLORS.primary, fontWeight: 'bold', textDecoration: 'none', fontFamily: 'lato' }}
              onMouseOver={(e) => (e.target.style.textDecoration = 'underline')}
              onMouseOut={(e) => (e.target.style.textDecoration = 'none')}
            >
              inscrivez-vous ici
            </Link>
          </Typography>
        </Box>
      </Paper>
    </Box>
  );
};

export default Login;
