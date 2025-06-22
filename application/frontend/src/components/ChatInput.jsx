import React, { useEffect, useState } from 'react';
import {
  Box,
  useTheme,
  TextField,
  IconButton,
  Paper,
  Tooltip,
  CircularProgress,
} from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import RestartAltIcon from '@mui/icons-material/RestartAlt';
import axios from "axios";
import { useNavigate } from 'react-router-dom';  // si tu utilises react-router
import { useDispatch, useSelector } from 'react-redux';
import { reset } from '../features/files/filesSlice';
import { useTranslation } from 'react-i18next';

const ChatInput = ({ onSend, onReset ,isResponding}) => {
  const { t,i18n } = useTranslation();

  const [message, setMessage] = React.useState('');
  const dispatch = useDispatch();
  const navigate = useNavigate();  // Hook pour redirection
  const [shouldRedirect, setShouldRedirect] = useState(false);
  const { isLoadingreset, isErrorreset, isSuccessreset } = useSelector(state => state.files);


  const theme = useTheme();
  const isDarkMode = theme.palette.mode === 'dark';

    const handleReset = async () => {
        try {
          await dispatch(reset()); // Appel API
          setShouldRedirect(true); // Marquer pour redirection après succès
        } catch (error) {
          console.error("Erreur lors de la réinitialisation :", error);
        }
      };

      useEffect(() => {
        if (isSuccessreset && shouldRedirect) {
          localStorage.setItem("uploadDone", "false");

          setTimeout(() => {
           window.location.reload()
          }, 500);
        }
      }, [isSuccessreset, shouldRedirect, navigate]);



  

  const handleSend = () => {
    if (message.trim()) {
      onSend(message);
      setMessage('');
    }
  };



  return (
    <Box
      sx={{
        position: 'fixed',
        bottom: 0,
        left: 0,
        width: '100%',
        pb:'20px',
        zIndex: 1000,
        display: 'flex',
        justifyContent: 'center',
        backgroundColor: isDarkMode ? theme.palette.background.default : '#f0f4f8',
      }}
    >
      <Paper
        elevation={3}
        sx={{
          display: 'flex',
          alignItems: 'center',
          width: '100%',
          maxWidth:  { xs: '330px',sm:'530px',md: '670px' ,lg: '780px' },
          padding: '8px 12px',
          borderRadius: '24px',
          backgroundColor: isDarkMode ? theme.palette.background.paper : '#f9f9f9',
          '--autofill-bg': isDarkMode ? theme.palette.background.paper : '#f9f9f9', // 💡 variable CSS
  
        }}
      >
    <Tooltip 
      title={
        <Box
          sx={{
            fontSize: i18n.language === 'ar' ? '0.9rem' : '0.75rem',
            wordSpacing: i18n.language === 'ar' ? '0.1em' : 'normal',
            direction: i18n.language === 'ar' ? 'rtl' : 'ltr',
            textAlign: i18n.language === 'ar' ? 'right' : 'left',
            padding: '3px 7px',
          }}
        >
          {t('reset_tooltip')}
        </Box>
      }
      arrow
      placement="top"
    >
          <IconButton
            onClick={handleReset}
            sx={{
              color: isDarkMode ? '#f28b82' : '#f67e7d',
              marginRight: 1,
              backgroundColor: isDarkMode ? '#3a2a2a' : '#fceeee',
              '&:hover': {
                backgroundColor: isDarkMode ? '#593636' : '#fbd2d2',
              },
            }}
          >
            <RestartAltIcon />
          </IconButton>
        </Tooltip>

        <TextField
          fullWidth
          variant="standard"
          placeholder={t('input_placeholder')}
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyPress={(e) => {
            if (e.key === 'Enter') {
              e.preventDefault();
              handleSend();
            }
          }}
          InputProps={{
            disableUnderline: true,
            sx: {
              paddingLeft: 1,
              fontSize: '1rem',
                '& input:-webkit-autofill': {
                   WebkitTextFillColor: isDarkMode ? '#f9f9f9' : '#000000',
                  transition: 'background-color 5000s ease-in-out 0s',
                },
            },
          }}
        />

        <IconButton
            onClick={!isResponding ? handleSend : null}
            disabled={isResponding}
            sx={{ color: isDarkMode ? '#1B998B' : '#1B998B' }}
          >
            {isResponding ? (
              <CircularProgress size={25} sx={{  color: isDarkMode ? '#1B998B' : '#1B998B' }}/>
            ) : (
              <SendIcon />
            )}
          </IconButton>

      </Paper>
    </Box>
  );
};

export default ChatInput;
