import React from 'react';
import {
  Box,
  TextField,
  IconButton,
  Paper,
  Tooltip,
} from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import RestartAltIcon from '@mui/icons-material/RestartAlt';

const ChatInput = ({ onSend, onReset }) => {
  const [message, setMessage] = React.useState('');

  const handleSend = () => {
    if (message.trim()) {
      onSend(message);
      setMessage('');
    }
  };

  const handleReset = () => {
    setMessage('');
    if (onReset) {
      onReset();
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
          backgroundColor: '#f0f4f8',

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
          backgroundColor: '#ffffff',
        }}
      >
        <Tooltip title="Réinitialiser pour résumer de nouveaux fichiers" arrow placement="top">
          <IconButton
            onClick={handleReset}
            sx={{
              color: '#f67e7d',
              marginRight: 1,
              backgroundColor: '#fceeee',
              '&:hover': {
                backgroundColor: '#fbd2d2',
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

        <IconButton onClick={handleSend} sx={{ color: '#1B998B' }}>
          <SendIcon />
        </IconButton>
      </Paper>
    </Box>
  );
};

export default ChatInput;
