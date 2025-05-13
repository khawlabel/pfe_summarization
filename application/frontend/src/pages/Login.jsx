import React, { useState } from 'react'; 
import { Link, TextField, Button, Box, Typography, Paper } from '@mui/material';

const COLORS = {
  primary: '#1B998B  ',
  secondry: '#625f63    ',
  background: '#f4f6f9',
  paperBackground: '#ffffff',
  buttonBackground: '#1B998B  ',
  buttonHover: '#166b79',
  textFieldBorder: '#1B998B ',
  textFieldFocusBorder: '#166b79',
  linkHover: '#E94E1B',
};

const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = (event) => {
    event.preventDefault();
    // Suppression de la logique d'appel API
    console.log('Form submitted:', { email, password });
  };

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
          boxShadow: '0 2px 10px rgba(0, 0, 0, 0.1)',
          overflow: 'hidden',
          width: {
          xs: '80%',   // petits écrans (téléphones)
          sm: '60%',   // tablettes
          md: '50%',   // desktops moyens
          lg: '40%',   // écrans larges
        },
        maxWidth: '500px', // pour éviter qu'il s'étale trop sur très grands écrans
      
        }}
      >
        {/* Left side: Login Form */}
        <Box sx={{ flex: 1, padding: 4 }}>
          <Box display="flex" flexDirection="column" alignItems="center">
            <Typography
              component="h1"
              variant="h5"
              sx={{ color: COLORS.primary, fontWeight: 'bold', marginBottom: 2 }}
            >
              Connexion
            </Typography>
            <Box component="form" onSubmit={handleSubmit} sx={{ mt: 1 }}>
              <TextField
                margin="dense"
                required
                fullWidth
                id="email"
                label="Email"
                name="email"
                type="email"
                autoComplete="email"
                autoFocus
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                sx={{
                  backgroundColor: '#fff',
                  borderRadius: 1,
                  '& .MuiOutlinedInput-root': {
                    '& fieldset': { borderColor: COLORS.textFieldBorder },
                    '&:hover fieldset': { borderColor: COLORS.buttonHover },
                    '&.Mui-focused fieldset': { borderColor: COLORS.buttonHover },
                  },
                  '& .MuiInputLabel-root': { 
                    '&.Mui-focused': { color: '#166b79' },
                    fontSize: '0.875rem' },
                }}
              />
              <TextField
                margin="dense"
                required
                fullWidth
                name="password"
                label="Mot de passe"
                type="password"
                id="password"
                autoComplete="current-password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                sx={{
                  backgroundColor: '#fff',
                  borderRadius: 1,
                  '& .MuiOutlinedInput-root': {
                    '& fieldset': { borderColor: COLORS.textFieldBorder },
                    '&:hover fieldset': { borderColor: COLORS.buttonHover },
                    '&.Mui-focused fieldset': { borderColor: COLORS.buttonHover },
                  },
                  '& .MuiInputLabel-root': { 
                    fontSize: '0.875rem',
                    '&.Mui-focused': { color: '#166b79' }, },
                }}
              />
              {error && (
                <Typography color="error" sx={{ mb: 1, fontSize: '0.875rem' }}>
                  {error}
                </Typography>
              )}
              <Button
                type="submit"
                fullWidth
                variant="contained"
                sx={{
                  mt: 2,
                  mb: 2,
                  backgroundColor: COLORS.buttonBackground,
                  fontSize: '0.875rem',
                  fontWeight: 'bold',
                  borderRadius: 2,
                  '&:hover': { backgroundColor: COLORS.buttonHover, transform: 'scale(1.03)' },
                  padding: '10px 0',
                }}
              >
                Se connecter
              </Button>
            </Box>
          </Box>
          <Typography variant="body2" align="center" sx={{color: COLORS.secondry,  fontWeight: 'normal', fontFamily: 'lato' }}>
            Voulez n'avez pas de compte ?{' '}
            <Link
                          to="/"
                          style={{ color: COLORS.primary, fontWeight: 'bold', textDecoration: 'none', fontFamily: 'lato' }}
                          onMouseOver={(e) => (e.target.style.textDecoration = 'underline')}
                          onMouseOut={(e) => (e.target.style.textDecoration = 'none')}
                        >
              inscrivez-vous ici
            </Link>
          </Typography>
        </Box>

      </Paper>

      {/* Global style for the animation (optionnel) */}
      <style>
        {`
          @keyframes pulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.2); }
          }
        `}
      </style>
    </Box>
  );
};

export default Login;
