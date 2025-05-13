import React, { useState } from 'react'; 
import { Link, TextField, Button, Box, Typography, Paper } from '@mui/material';

const COLORS = {
  primary: '#1B998B',
  secondry: '#625f63',
  background: '#f4f6f9',
  paperBackground: '#ffffff',
  buttonBackground: '#1B998B',
  buttonHover: '#166b79',
  textFieldBorder: '#1B998B',
  textFieldFocusBorder: '#166b79',
  linkHover: '#E94E1B',
};

const Register = () => {
  const [nom, setNom] = useState('');
  const [prenom, setPrenom] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = (event) => {
    event.preventDefault();
    // Suppression de la logique d'appel API
    console.log('Form submitted:', { nom, prenom, email, password });
  };

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
          boxShadow: '0 2px 10px rgba(0, 0, 0, 0.1)',
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
            <Box component="form" onSubmit={handleSubmit} sx={{ mt: 1 }}>
              <TextField
                margin="dense"
                required
                fullWidth
                label="Nom"
                value={nom}
                onChange={(e) => setNom(e.target.value)}
                sx={textFieldStyle}
              />
              <TextField
                margin="dense"
                required
                fullWidth
                label="Prénom"
                value={prenom}
                onChange={(e) => setPrenom(e.target.value)}
                sx={textFieldStyle}
              />
              <TextField
                margin="dense"
                required
                fullWidth
                type="email"
                label="Email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                sx={textFieldStyle}
              />
              <TextField
                margin="dense"
                required
                fullWidth
                type="password"
                label="Mot de passe"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                sx={textFieldStyle}
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
