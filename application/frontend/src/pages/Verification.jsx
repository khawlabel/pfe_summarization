import React, { useEffect } from 'react';

import { Link as RouterLink } from 'react-router-dom';
import { Box, Typography, Paper, Button } from '@mui/material';
import CheckCircleOutlineIcon from '@mui/icons-material/CheckCircleOutline';
import checkedIcon from '../images/checked.png';
import { useLocation } from 'react-router-dom';
import { useDispatch } from 'react-redux';
import { verifyCompte }  from '../features/Auth/authSlice';
import { useNavigate } from 'react-router-dom';

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

    const location = useLocation();
    const navigate = useNavigate();
    const dispatch = useDispatch();

    const token = location.pathname.split('/')[2];
  
    useEffect(() => {
      // Dispatch l'action de vérification du compte avec le token
      dispatch(verifyCompte(token));
     
    }, [dispatch, token]);

  return (
    <Box
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
           Compte vérifié !
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
          Votre compte a été vérifié avec succès.<br />
          Vous pouvez maintenant accéder à toutes les fonctionnalités.
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
          Se connecter maintenant
        </Button>
      </Paper>
    </Box>
  );
};

export default Verification;
