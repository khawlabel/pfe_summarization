import React, { useEffect, useState } from 'react';
import {
  Box,
  useTheme,
  TextField,
  IconButton,
  Paper,
  Tooltip,
} from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import RestartAltIcon from '@mui/icons-material/RestartAlt';
import axios from "axios";
import { useNavigate } from 'react-router-dom';  // si tu utilises react-router
import { useDispatch, useSelector } from 'react-redux';
import { reset } from '../features/files/filesSlice';

const ChatInput = ({ onSend, onReset }) => {
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
          backgroundColor: isDarkMode ? theme.palette.background.paper : '#ffffff',
        }}
      >
        <Tooltip title="Réinitialiser pour résumer de nouveaux fichiers" arrow placement="top">
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
          placeholder="Envoyer un message..."
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
            },
          }}
        />

        <IconButton onClick={handleSend} sx={{ color: isDarkMode ? '#80cbc4' : '#1B998B', }}>
          <SendIcon />
        </IconButton>
      </Paper>
    </Box>
  );
};

export default ChatInput;
