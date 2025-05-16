import React from 'react';
import { Link as RouterLink } from 'react-router-dom';
import { Box, Typography, Paper, Button } from '@mui/material';
import CheckCircleOutlineIcon from '@mui/icons-material/CheckCircleOutline';
import checkedIcon from '../images/checked.png';

const COLORS = {
  primary: '#1B998B',
  secondry: '#625f63',
  background: '#f0f4f8',
  paperBackground: '#ffffff',
  buttonBackground: '#1B998B',
  buttonHover: '#166b79',
};

const Verification = () => {
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
          variant="contained"
          to="/"
          sx={{
            mt: 2,
            backgroundColor: COLORS.buttonBackground,
            fontWeight: 'bold',
            textTransform: 'none',
            borderRadius: 2,
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
