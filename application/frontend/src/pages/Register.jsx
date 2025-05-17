
import {TextField, Button, Box, Typography, Paper } from '@mui/material';
import { useFormik } from 'formik';
import { useDispatch, useSelector } from 'react-redux';
import { register, reset } from '../features/Auth/authSlice';
import { useNavigate } from 'react-router-dom';
import * as yup from 'yup'
import React, { useEffect,useState } from 'react';
import { Alert } from '@mui/material';
import { Link } from 'react-router-dom';

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


const Register = () => {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const auth = useSelector((state) => state.auth);
  

    // Local state pour afficher l'alerte
    const [showError, setShowError] = useState(false);
    const [showSuccess, setShowSuccess] = useState(false);
    const textFieldStyle = {
        backgroundColor: '#2C2C2C', // fond du champ
        borderRadius: 1,
        '& .MuiOutlinedInput-root': {
          '& input': {
            color: '#ffffff', // texte blanc
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
          color: '#aaa', // label initial
          fontSize: '0.9rem',
          '&.Mui-focused': {
            color: COLORS.primary, // label quand focus
          },
        },
        '& .MuiFormHelperText-root': {
          color: '#ff6b6b', // couleur de l'aide/erreur
        },
        '& input:-webkit-autofill': {
        WebkitBoxShadow: '0 0 0 1000px #2C2C2C inset !important',
        WebkitTextFillColor: '#ffffff !important',
      },
      };




    useEffect(() => {
      if (auth.isError) {
        setShowError(true);
        setShowSuccess(false);
      } else if (auth.isSuccess) {
        setShowSuccess(true);
        setShowError(false);
      } else {
        setShowError(false);
        setShowSuccess(false);
      }
    }, [auth.isError, auth.isSuccess]);



   const schema = yup.object().shape({
      firstname: yup.string().required("Ce champ est obligatoire"),
      lastname: yup.string().required("Ce champ est obligatoire"),
      email: yup.string().email("L’adresse e-mail doit être valide").required("Ce champ est obligatoire"),
      password: yup.string().required("Ce champ est obligatoire"),
    });
  
    const formik = useFormik({
      initialValues: {
        firstname:'',
        lastname:'',
        email:'',
        password: '',
        role:'user'
      },
      validationSchema: schema,
      onSubmit: (values) => {
        dispatch(register(values));
        formik.resetForm();

      },
    });

      useEffect(() => {
      formik.resetForm();
      dispatch(reset());  // reset état auth aussi
      }, [dispatch]);


  return (
    <Box
      sx={{
        height: '90vh',
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
          boxShadow: '0 8px 20px rgba(0, 0, 0, 0.3)', // plus prononcé
          overflow: 'hidden',
          width: {
            xs: '90%',
            sm: '70%',
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
              Inscription

            </Typography>
                                    {/* Affichage de l'alerte d'erreur */}
                        {showError && (
                          <Alert severity="error" sx={{ mb: 2, width: '93%' }}>
                            {auth.message}
                          </Alert>
                        )}

                        {showSuccess && (
                          <Alert severity="success" sx={{ mb: 2, width: '93%' }}>
                            {typeof auth.message === 'string'
                              ? auth.message
                              : "Inscription réussie. Vérifiez votre e-mail pour activer votre compte."}
                          </Alert>
                        )}
                        
            <Box component="form" onSubmit={formik.handleSubmit}  sx={{ mt: 1 }}>
              <TextField
                margin="dense"
                required
                fullWidth
                id="firstname"
                name="firstname"
                label="firstname"
                value={formik.values.firstname}
                onChange={formik.handleChange}
                onBlur={formik.handleBlur}
                error={formik.touched.firstname && Boolean(formik.errors.firstname)}
                helperText={formik.touched.firstname && formik.errors.firstname}
                sx={textFieldStyle}
              />
              <TextField
                margin="dense"
                required
                fullWidth
                id="lastname"
                name="lastname"
                label="lastname"
                value={formik.values.lastname}
                onChange={formik.handleChange}
                onBlur={formik.handleBlur}
                error={formik.touched.lastname && Boolean(formik.errors.lastname)}
                helperText={formik.touched.lastname && formik.errors.lastname}
                sx={textFieldStyle}
              />
              <TextField
                margin="dense"
                required
                fullWidth
                id="email"
                name="email"
                label="Email"
                type="email"
                autoComplete="off"
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
                id="password"
                name="password"
                label="Mot de passe"
                type="password"
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
                sx={{
                  mt: 2,
                  mb: 3,
                  backgroundColor: COLORS.buttonBackground,
                  fontSize: '0.875rem',
                  fontWeight: 'bold',
                  borderRadius: 2,
                  '&:hover': { backgroundColor: COLORS.buttonHover, transform: 'scale(1.03)' },
                  padding: '10px 0',
                }}
              >
                S'inscrire
              </Button>
            </Box>
          </Box>
          <Typography variant="body2" align="center" sx={{ color: COLORS.secondry, fontWeight: 'normal', fontFamily: 'lato' }}>
            Vous avez déjà un compte ?{' '}
           
              <Link
                            to="/login"
                            style={{ color: COLORS.primary, fontWeight: 'bold', textDecoration: 'none', fontFamily: 'lato' }}
                            onMouseOver={(e) => (e.target.style.textDecoration = 'underline')}
                            onMouseOut={(e) => (e.target.style.textDecoration = 'none')}
                          >
                    Connectez-vous ici
              </Link>
          </Typography>
        </Box>
      </Paper>
    </Box>
  );
};

const textFieldStyle = {
  backgroundColor: '#fff',
  borderRadius: 1,
  '& .MuiOutlinedInput-root': {
    '& fieldset': { borderColor: COLORS.textFieldBorder },
    '&:hover fieldset': { borderColor: COLORS.buttonHover },
    '&.Mui-focused fieldset': { borderColor: COLORS.buttonHover },
  },
  '& .MuiInputLabel-root': {
    fontSize: '0.875rem',
    '&.Mui-focused': { color: COLORS.buttonHover },
  },
};

export default Register;
