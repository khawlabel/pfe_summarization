import React, { useEffect, useState } from 'react';
import { Box, Typography, IconButton } from '@mui/material';
import ChevronLeftIcon from '@mui/icons-material/ChevronLeft';
import DescriptionOutlinedIcon from '@mui/icons-material/DescriptionOutlined';
import { useMediaQuery, useTheme } from '@mui/material';

const COLORS = {
  primary: '#1B998B',
  secondry: '#f67e7d',
  background: '#f0f4f8',
  paperBackground: '#f9f9f9',
  textColor: '#333',
  borderColor: '#e0e0e0',
};

const Sidebar = ({ open, onClose }) => {
  const theme = useTheme();
  const isSmallScreen = useMediaQuery(theme.breakpoints.down('sm'));

  return (
  <>
    { open && (
      <Box
        sx={{
          position: 'fixed',
          top: 0,
          left: 0,
          width: '100vw',
          height: '100vh',
          backgroundColor: 'rgba(0,0,0,0.3)',
          zIndex: 1299,
          transition: 'background-color 0.3s ease',
        }}
        onClick={onClose}
      />
    )}

    <Box
      sx={{
        position: 'fixed',
        top: 0,
        left: 0,
        height: '100vh',
        width: '255px',
        backgroundColor: COLORS.paperBackground,
        boxShadow: '4px 0 20px rgba(0,0,0,0.1)',
        zIndex: 1300,
        p: 2,
        display: 'flex',
        flexDirection: 'column',
        transition: 'transform 0.3s ease-in-out',
        transform: open ? 'translateX(0)' : 'translateX(-100%)',
        borderRight: `1px solid ${COLORS.borderColor}`,
        overflow: 'hidden',
      }}
    >
      {/* En-tête */}
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          mb: 2.5,
          pb: 1,
          borderBottom: `1px solid ${COLORS.borderColor}`,
        }}
      >
          <Typography
            variant="h6"
            sx={{
              flexGrow: 1,
              fontWeight: 'bold',
              ml:0.5,
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

        <IconButton onClick={onClose}>
          <ChevronLeftIcon sx={{ color: COLORS.primary, fontSize: 28 }} />
        </IconButton>
      </Box>

      {/* Historique */}
      <Box sx={{ flexGrow: 1, overflowY: 'auto', mt: 2 }}>
        <Typography variant="body1" sx={{ fontWeight: 600, color: COLORS.textColor, mb: 2 }}>
          Historique
        </Typography>

        {['Résumé du document X.pdf', 'Résumé audio réunion.m4a', 'Discussion vidéo.mp4'].map(
          (item, index) => (
            <Box
              key={index}
              sx={{
                display: 'flex',
                alignItems: 'center',
                backgroundColor: COLORS.background,
                borderRadius: 2,
                p: 1.1,
                mb: 1.5,
                fontSize: '0.9rem',
                cursor: 'pointer',
                transition: 'all 0.3s ease',
                border: `1px solid transparent`,
                boxShadow: '0 1px 2px rgba(0,0,0,0.05)',
                '&:hover': {
                  backgroundColor: '#e6f4f1',
                  boxShadow: '0 4px 12px rgba(0,0,0,0.08)',
                  borderColor: COLORS.primary,
                },
              }}
            >
              <DescriptionOutlinedIcon sx={{ color: COLORS.primary, mr: 1 }} />
              <Typography sx={{ color: COLORS.textColor, fontWeight: 500 }}>{item}</Typography>
            </Box>
          )
        )}
      </Box>


    </Box>
  </>
);

};


export default Sidebar;
