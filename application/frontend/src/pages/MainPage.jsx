import React, { useState, useEffect } from 'react';
import { Box, useTheme, useMediaQuery, Avatar, Typography, Stack, Paper, IconButton } from '@mui/material';
import Sidebar from '../components/Sidebar';
import Navbar from '../components/Navbar';
import ChatInput from '../components/ChatInput';
import PersonIcon from '@mui/icons-material/Person';
import SmartToyIcon from '@mui/icons-material/SmartToy';
import ReactMarkdown from 'react-markdown';
import AI from '../images/ai.png';
import { ThemeContext } from '../ThemeContext'; // ajuste le chemin
import { useContext } from 'react';
import {GENERATE_TITRE_FR_URL,GENERATE_SUMMARY_FR_URL,GENERATE_TITRE_AR_URL,GENERATE_SUMMARY_AR_URL,CHAT_URL} from "../routes/constants"

import Menu from '@mui/material/Menu';
import MenuItem from '@mui/material/MenuItem';

import dz from '../images/flags/algeria.webp';
import en from '../images/flags/uk.webp'; 
import fr from '../images/flags/france.png'; 

import { useTranslation } from 'react-i18next';


const MainPage = () => {
   const { i18n } = useTranslation();
    const { t } = useTranslation();
  
    const changeLang = (langCode) => {
      i18n.changeLanguage(langCode);
    };
  const { mode } = useContext(ThemeContext);

  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [isFrenchReady, setIsFrenchReady] = useState(false);
  const [isArabicReady, setIsArabicReady] = useState(false);
  const [messages, setMessages] = useState([]);
  const [streamingIndex, setStreamingIndex] = useState(null);
  const [frenchSummary, setFrenchSummary] = useState('');
  const [frenchTitle, setFrenchTitle] = useState('');
  const [arabicTitle, setArabicTitle] = useState('');
  const [arabicSummary, setArabicSummary] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [isResponding, setIsResponding] = useState(false);
  const [anchorEl, setAnchorEl] = useState(null);
  const open = Boolean(anchorEl);
  
  
  const handleClick = (event) => {
  setAnchorEl(event.currentTarget);
};

  const handleClose = () => {
    setAnchorEl(null);
  };

  const handleLangChange = (lang) => {
    i18n.changeLanguage(lang);
    localStorage.setItem('language', lang); // ✅ persist the choice
    handleClose();
  };

  const getFlagImage = (lang) => {
    switch (lang) {
      case 'en':
        return en;
      case 'fr':
        return fr;
      case 'ar':
        return dz;
      default:
        return en; // par défaut anglais
    }
  };
  
  
    const getLangLabel = (lang) => {
      return t(`lang_${lang}`);
    };
    const isArabic = i18n.language === 'ar';
  

async function streamEndpoint(url, onChunk) {
  const response = await fetch(url);
  const reader = response.body.getReader();
  const decoder = new TextDecoder("utf-8");
  let done = false;

  while (!done) {
    const { value, done: doneReading } = await reader.read();
    done = doneReading;
    if (value) {
      // IMPORTANT : utiliser stream:true pour gérer les morceaux incomplets correctement
      const chunk = decoder.decode(value, { stream: !done });
      onChunk(chunk);
    }
  }
}


useEffect(() => {
  let cancelled = false;

  const fetchAll = async () => {
    if (cancelled) return;
    setIsGenerating(true);
    setFrenchTitle('');
    setFrenchSummary('');
    setArabicTitle('');
    setArabicSummary('');

    try {
      await streamEndpoint(GENERATE_TITRE_FR_URL, chunk => {
        if (!cancelled) setFrenchTitle(prev => prev + chunk);
      });

      if (!cancelled) setFrenchSummary(prev => prev + '\n');

      await streamEndpoint(GENERATE_SUMMARY_FR_URL, chunk => {
        if (!cancelled) setFrenchSummary(prev => prev + chunk);
      });

      await streamEndpoint(GENERATE_TITRE_AR_URL, chunk => {
        if (!cancelled) setArabicTitle(prev => prev + chunk);
      });

      if (!cancelled) setArabicSummary(prev => prev + '\n');

      await streamEndpoint(GENERATE_SUMMARY_AR_URL, chunk => {
        if (!cancelled) setArabicSummary(prev => prev + chunk);
      });

    } catch (err) {
      if (!cancelled) console.error('Erreur de streaming :', err);
    } finally {
      if (!cancelled) setIsGenerating(false);
    }
  };

  fetchAll();

  return () => {
    cancelled = true;
  };
}, []);

  const theme = useTheme();
  const isSmallScreen = useMediaQuery(theme.breakpoints.down('sm'));
  const isDarkMode = mode === 'dark';
  const getColors = (isDarkMode) => ({
        primary: '#1B998B',
        secondry: isDarkMode ? '#ddd' : '#444',
        background: isDarkMode ? '#121212' : '#ebf1f8',
        paperBackground: isDarkMode ? '#3A3A3A' : '#ffffff',
        buttonBackground: '#1B998B',
        buttonHover: '#14766d',
        textFieldBorder: isDarkMode ? '#254B46' : '#d0eae7',
        textFieldFocusBorder: '#1B998B',
        fileItemBackground: isDarkMode ? '#2c2c2c' : '#f4f6f9',
      });
  const COLORS = getColors(isDarkMode);

  

  // Message d'accueil automatique
  useEffect(() => {
    setIsFrenchReady(true);
    setIsArabicReady(true);

    const welcomeMessage = t('welcome_message');
    let index = 0;
    const interval = setInterval(() => {
      setMessages(prev => {
        const current = prev[0]?.from === 'bot' ? prev[0].text : '';
        const newText = welcomeMessage.slice(0, index + 1);
        if (prev.length === 0 || prev[0]?.from !== 'bot') {
          return [{ from: 'bot', text: newText }, ...prev];
        } else {
          const newMessages = [...prev];
          newMessages[0] = { from: 'bot', text: newText };
          return newMessages;
        }
      });
      index++;
      setStreamingIndex(index);
      if (index >= welcomeMessage.length) clearInterval(interval);
    }, 20); // effet de streaming

    return () => clearInterval(interval);
  }, [i18n.language]); // ⬅️ IMPORTANT : dépendance sur la langue


const handleSend = (msg) => {
  const userMessage = { from: 'user', text: msg };
  const botPlaceholder = { from: 'bot', text: '' };

  // Ajouter immédiatement le message utilisateur et un message bot vide
  setMessages((prev) => [...prev, userMessage, botPlaceholder]);

  // L'index du message bot sera le dernier après ajout
  const botMessageIndex = messages.length + 1;
  setIsResponding(true);

  fetch(CHAT_URL, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ user_input: msg }),
  }).then(response => {
    if (!response.body) throw new Error('ReadableStream not supported');

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let botResponse = '';

    function read() {
      reader.read().then(({ done, value }) => {
        if (done) {
          // Fin du stream : forcer la dernière mise à jour
          setMessages((prev) => {
            const updated = [...prev];
            if (updated[botMessageIndex]) {
              updated[botMessageIndex].text = botResponse;
            }
            return updated;
          });
          setIsResponding(false);
          return;
        }

        botResponse += decoder.decode(value, { stream: true });

        // Mise à jour partielle
        setMessages((prev) => {
          const updated = [...prev];
          if (updated[botMessageIndex]) {
            updated[botMessageIndex].text = botResponse;
          }
          return updated;
        });

        read();
      }).catch((error) => {
        console.error('Erreur pendant le streaming :', error);
        setIsResponding(false);
      });
    }

    read();
  }).catch((err) => {
    console.error('Erreur de requête :', err);
    setMessages((prev) => [...prev, { from: 'bot', text: "Erreur de connexion au serveur." }]);
    setIsResponding(false);
  });
};

  return (
    <Box sx={{ minHeight: '100vh', backgroundColor: isDarkMode ? theme.palette.background.default : '#f0f4f8' }}>
      <Navbar onMenuClick={() => setSidebarOpen(true)} sidebarOpen={sidebarOpen} onReset={() => setMessages([])}/>
      <Sidebar open={sidebarOpen} onClose={() => setSidebarOpen(false)} />

      <Box
        sx={{
          pr: { xs: 7, md: 13, lg: 22 },
          pl: { xs: 7, md: 13, lg: 22 },
          pb: 20,
          pt: 13,
          maxWidth: '100%',
          boxSizing: 'border-box',
          transition: 'all 0.3s ease',
        }}
      >

        {/* TITRE */}
      <Box sx={{ mb: 6, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
        <Typography
          variant="h5"
          sx={{
            color: theme.palette.text.primary,
            fontWeight: 'bold',
            fontSize: { xs: '1.3rem', md: '1.7rem' },
            letterSpacing: '0.5px',
            textShadow: '2px 2px 4px rgba(0,0,0,0.2)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            textAlign: 'center',
            mb: 1,
            gap: 1,
            flexDirection: i18n.language === 'ar' ? 'row-reverse' : 'row', // 🧠 clé ici
          }}
        >
          {/* Partie texte traduisible (RTL si arabe) */}
          <Box
            sx={{
              direction: i18n.language === 'ar' ? 'rtl' : 'ltr',
              display: 'inline-block',
            }}
          >
            {t('main_title_prefix')}
          </Box>

          {/* Partie SUM + image, reste à gauche */}
          <Box
            component="span"
            sx={{
              color: theme.palette.primary.main,
              fontWeight: 700,
              fontSize: 'inherit',
              display: 'flex',
              alignItems: 'center',
              flexShrink: 0,
            }}
          >
            Sum
            <Box
              component="img"
              src={AI}
              alt="AI"
              sx={{
                height: '2.2rem',
                width: 'auto',
                ml: 0.5,
                verticalAlign: 'middle',
                position: 'relative',
                top: '-8.3px',
              }}
            />
          </Box>
        </Typography>



          <Box
            sx={{
              height: '3px',
              width: '180px',
              backgroundColor: theme.palette.primary.main,
              borderRadius: 3,
              boxShadow: '0 4px 6px rgba(0, 0, 0, 0.15)',  // Ombre portée sur la barre
 
            }}
          />
        </Box>

        {/* Résumé en Français */}
        <Box
          sx={{
            backgroundColor: theme.palette.mode === 'dark' ? '#1a1a1a': '#f9f9f9',
            borderRadius: 4,
            boxShadow: `-10px 0 20px ${theme.palette.primary.main}66`,
            pt: 2,
            pl: 4,
            pr: 4,
            pb: 4,
            mb: 4,
            borderLeft: `6px solid ${theme.palette.primary.main}`,
          }}
        >
          <h2 dir={isArabic ? 'rtl' : 'ltr'} style={{  color: theme.palette.primary.main, marginBottom: '12px' }}>{t('french_summary')}</h2>
        <ReactMarkdown
          components={{
            p: ({ node, ...props }) => (
              <Typography
                component="div"
                sx={{
                  fontFamily: 'inherit',
                  fontSize: '1rem',
                   color: theme.palette.mode === 'dark'
                        ? '#f9f9f9' :'#495057',
                  lineHeight: 1.7,
                  textAlign: 'justify',
                  wordBreak: 'break-word',
                }}
                {...props}
              />
            ),
          }}
        >
         {`**Titre :**\n${frenchTitle.trim()}\n\n**Résumé :**\n${frenchSummary.trim()}`}
        </ReactMarkdown>

        </Box>

        {/* Résumé en Arabe */}
        <Box
        
          sx={{
            backgroundColor: theme.palette.mode === 'dark' ? '#1a1a1a': '#f9f9f9',
            borderRadius: 4,
            boxShadow: `10px 0 20px ${theme.palette.secondary.main}66`,
            pt: 2,
            pl: 4,
            pr: 4,
            pb: 4,
            mb: 4,
            borderRight: `6px solid ${theme.palette.secondary.main}`,
            textAlign: 'justify',
          }}
        >
          <h2 dir={isArabic ? 'rtl' : 'ltr'} style={{ color: theme.palette.secondary.main, marginBottom: '12px' }}>{t('arabic_summary')}</h2>
         <ReactMarkdown
            components={{
              p: ({ node, ...props }) => (
                <Typography
                  component="div"
                  sx={{
                    fontFamily: 'inherit',
                    fontSize: '1.1rem',        // 👈 Taille de police légèrement augmentée
                    color: theme.palette.mode === 'dark'
                        ? '#f9f9f9' :'#495057',
                    lineHeight: 1.8,
                    direction: 'rtl',
                    textAlign: 'justify',
                    wordBreak: 'break-word',
                    wordSpacing: '0.12em', // 👈 Ajoute de l’espace entre les mots
      
                  }}
                  {...props}
                />
              ),
            }}
          >
           { `**العنوان :**\n${arabicTitle.trim()}\n\n**الملخص :**\n${arabicSummary.trim()}` }


          </ReactMarkdown>

        </Box>

        <Box sx={{ mt: 6, mb: 6 }}>
          <hr style={{ border: 'none', height: '2px', backgroundColor: theme.palette.grey[500], opacity: 0.1 }} />
        </Box>

        {/* SECTION CHATBOT */}
        <Box sx={{ mt: 6, mb: 10 }}>
          <Box sx={{ textAlign: 'center', mb: 6 }}>
            <Typography
              variant="h5"
              sx={{
                color: theme.palette.text.primary,
                fontWeight: 'bold',
                fontSize: { xs: '1.3rem', md: '1.7rem' },
                letterSpacing: '0.5px',
                textShadow: '1px 1px 2px rgba(0,0,0,0.1)',  // Ombre légère sur le texte
 
              }}
            >
              {t('chat_section_title')}
            </Typography>
            <Box
              sx={{
                height: '3px',
                width: '200px',
                margin: '8px auto 0',
                backgroundColor: theme.palette.primary.main,
                borderRadius: '4px',
                boxShadow: '0 4px 6px rgba(0, 0, 0, 0.15)',  // Ombre portée sur la barre
 
              }}
            />
          </Box>

          <Stack spacing={2}>
            {messages.map((msg, index) => {
              const isUser = msg.from === 'user';
              return (
                <Box
                  key={index}
                  sx={{
                    display: 'flex',
                    justifyContent: isUser ? 'flex-end' : 'flex-start',
                  }}
                >
                  {!isUser && (
                    <Avatar sx={{ bgcolor: theme.palette.grey[700], mr: 1,mt:1 }}>
                      <SmartToyIcon />
                    </Avatar>
                  )}

                  <Paper
                    elevation={3}
                    sx={{
                      maxWidth: '75%',
                      p: 1.5,
                      borderRadius: '20px',
                      backgroundColor: isUser
                      ? theme.palette.mode === 'dark'
                        ? '#245953' // plus foncé que #a5ccc8
                        : '#d1f5f0'
                      : theme.palette.mode === 'dark'
                        ? '#353535' // plus foncé que #c3cdcd
                        : '#cfd8d8',
                      color: theme.palette.text.primary,
                      fontSize: '1rem',
                      boxShadow: '0 2px 5px rgba(0,0,0,0.1)',
                      wordBreak: 'break-word',
                      wordSpacing: msg.from === 'bot' && i18n.language === 'ar' ? '0.15em' : 'normal', // ✅ espace pour arabe
                      fontSize: msg.from === 'bot' && i18n.language === 'ar' ? '1.1rem' : '1rem',
                      direction: msg.from === 'bot' && i18n.language === 'ar' ? 'rtl' : 'ltr',         // ✅ sens RTL
                      textAlign: msg.from === 'bot' && i18n.language === 'ar' ? 'right' : 'left',      // ✅ alignement
                      }}
                                    >
                    <ReactMarkdown>{msg.text}</ReactMarkdown>
                  </Paper>

                  {isUser && (
                    <Avatar sx={{ bgcolor: theme.palette.primary.main, ml: 1,mt:1 }}>
                      <PersonIcon />
                    </Avatar>
                  )}
                </Box>
              );
            })}
          </Stack>
        </Box>
      </Box>

      {/* Chat input */}
      {isFrenchReady && isArabicReady && (
        <ChatInput
          onSend={handleSend}
          onReset={() => setMessages([])}
          isResponding={isResponding}

        />
      )}

       {/* === Bouton flottant pour switch de langue === */}
        <Box
        sx={{
          position: 'fixed',
          bottom: 20,
          left: 20,
          zIndex: 9999,
        }}
      >
        <IconButton
          onClick={handleClick}
          sx={{
            width: 50,
            height: 50,
            backgroundColor: COLORS.buttonBackground,
            borderRadius: '50%',
            boxShadow: isDarkMode
            ? '0 4px 10px rgba(0, 255, 255, 0.15)'
            : '0 4px 10px rgba(0, 0, 0, 0.15)',
          transition: 'all 0.3s ease',
          opacity: 0.5, // ✅ légère transparence
          transform: 'scale(1)', // ✅ état initial
          '&:hover': {
            backgroundColor: COLORS.buttonHover,
           
            opacity: 1, // ✅ plein visible au hover
            },
          }}
        >
          <Box
        component="img"
        src={getFlagImage(i18n.language)}
        alt="flag"
        sx={{
          width: 28,
          height: 28,
          borderRadius: '50%',
          objectFit: 'cover',
        }}
      />
      
        </IconButton>
      
        <Menu
          anchorEl={anchorEl}
          open={open}
          onClose={handleClose}
          anchorOrigin={{ vertical: 'top', horizontal: 'right' }}
          transformOrigin={{ vertical: 'bottom', horizontal: 'left' }}
          sx={{
            '& .MuiMenu-paper': {
              backgroundColor: COLORS.paperBackground,
              borderRadius: '12px',
              boxShadow: isDarkMode
                ? '0px 8px 20px rgba(0, 255, 255, 0.08)'
                : '0px 10px 30px rgba(0, 0, 0, 0.1)',
              border: `1px solid ${COLORS.textFieldBorder}`,
              padding: '8px 0',
            },
          }}
        >
          {[
        { code: 'en', label: 'English', image: en },
        { code: 'fr', label: 'Français', image: fr },
        { code: 'ar', label: 'العربية', image: dz },
      ].map(({ code, label, image }) => (
      
            <MenuItem
        key={code}
        onClick={() => handleLangChange(code)}
        sx={{
          color: COLORS.secondry,
          fontWeight: i18n.language === code ? 'bold' : 'normal',
          fontSize: '1rem',
          display: 'flex',
          alignItems: 'center',
          paddingY: '8px',
          paddingX: '16px',
          gap: 1,
          transition: 'transform 0.2s ease, background-color 0.2s ease',
          '&:hover': {
            transform: 'scale(1.05)',
            backgroundColor: isDarkMode ? '#2a2a2a' : '#f5f5f5',
          },
        }}
      >
        <Box
          component="img"
          src={image}
          alt={label}
          sx={{
            width: 24,
            height: 24,
            borderRadius: '4px',
            mr: 1,
            transition: 'transform 0.3s ease',
          }}
        />
         <Typography>{getLangLabel(code)}</Typography>
      </MenuItem>
      
          ))}
        </Menu>
      </Box>
    </Box>
  );
};

export default MainPage;
