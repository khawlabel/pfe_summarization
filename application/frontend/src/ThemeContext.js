import React, { createContext, useState, useMemo } from 'react';
import { createTheme, ThemeProvider } from '@mui/material/styles';

export const ThemeContext = createContext();

export const CustomThemeProvider = ({ children }) => {
  const [mode, setMode] = useState(localStorage.getItem('theme') || 'dark');

  const toggleTheme = () => {
    const newMode = mode === 'light' ? 'dark' : 'light';
    setMode(newMode);
    localStorage.setItem('theme', newMode); // Persiste le choix
  };

  const theme = useMemo(() => 
    createTheme({
      palette: {
        mode: mode,
        primary: { main: '#1B998B' },
        secondary: { main: '#f67e7d' },
      },
    }), [mode]);

  return (
    <ThemeContext.Provider value={{ mode, toggleTheme }}>
      <ThemeProvider theme={theme}>
        {children}
      </ThemeProvider>
    </ThemeContext.Provider>
  );
};
