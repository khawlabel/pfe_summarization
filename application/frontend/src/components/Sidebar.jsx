import React from 'react';
import { Box, Typography, IconButton, useMediaQuery, useTheme } from '@mui/material';
import ChevronLeftIcon from '@mui/icons-material/ChevronLeft';
import DescriptionOutlinedIcon from '@mui/icons-material/DescriptionOutlined';
import { useTranslation } from 'react-i18next';

const Sidebar = ({ open, onClose }) => {

  const { t } = useTranslation();
  const theme = useTheme();
  const isDarkMode = theme.palette.mode === 'dark';
  const isSmallScreen = useMediaQuery(theme.breakpoints.down('sm'));

  const primaryColor = '#1B998B';
  const secondaryColor = '#f67e7d';

  return (
    <>
      {open && (
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
          backgroundColor: theme.palette.mode === 'dark' ? '#1a1a1a': '#f9f9f9',
          boxShadow: '4px 0 20px rgba(0,0,0,0.1)',
          zIndex: 1300,
          p: 2,
          display: 'flex',
          flexDirection: 'column',
          transition: 'transform 0.3s ease-in-out',
          transform: open ? 'translateX(0)' : 'translateX(-100%)',
          borderRight: `1px solid ${theme.palette.divider}`,
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
            borderBottom: `1px solid ${theme.palette.divider}`,
          }}
        >
          <Typography
            variant="h6"
            sx={{
              flexGrow: 1,
              fontWeight: 'bold',
              ml: 0.5,
              fontFamily: 'Arial, sans-serif',
              fontSize: '1.6rem',
              userSelect: 'none',
              textShadow: '0 2px 6px rgba(27, 153, 139, 0.4)',
            }}
          >
            <span style={{ color: primaryColor }}>Sum</span>
            <span style={{ color: secondaryColor }}>AI</span>
          </Typography>

          <IconButton onClick={onClose}>
            <ChevronLeftIcon sx={{ color: primaryColor, fontSize: 28 }} />
          </IconButton>
        </Box>

        {/* Historique */}
        <Box sx={{ flexGrow: 1, overflowY: 'auto', mt: 2 }}>
          <Typography variant="body1" sx={{ fontWeight: 600, color: theme.palette.text.primary, mb: 2 }}>
             {t('sidebar_history')}
          </Typography>

          {[t('sidebar_doc_summary'), t('sidebar_audio_summary'), t('sidebar_video_chat')].map(
            (item, index) => (
              <Box
                key={index}
                sx={{
                  display: 'flex',
                  alignItems: 'center',
                  backgroundColor: theme.palette.mode === 'light' ? '#f0f4f8' : '#1e1e1e',
                  borderRadius: 2,
                  p: 1.1,
                  mb: 1.5,
                  fontSize: '0.9rem',
                  cursor: 'pointer',
                  transition: 'all 0.3s ease',
                  border: '1px solid transparent',
                  boxShadow: theme.palette.mode === 'light'
                    ? '0 1px 2px rgba(0,0,0,0.05)'
                    : '0 1px 2px rgba(255,255,255,0.05)',
                  '&:hover': {
                    backgroundColor: theme.palette.mode === 'light' ? '#e6f4f1' : '#2a2a2a',
                    boxShadow: '0 4px 12px rgba(0,0,0,0.08)',
                    borderColor: primaryColor,
                  },
                }}
              >
                <DescriptionOutlinedIcon sx={{ color: primaryColor, mr: 1 }} />
                <Typography sx={{ color: theme.palette.text.primary, fontWeight: 500 }}>{item}</Typography>
              </Box>
            )
          )}
        </Box>
      </Box>
    </>
  );
};

export default Sidebar;
