import React, { useState, useEffect } from 'react';
import { Box, useTheme, useMediaQuery, Avatar, Typography, Stack, Paper } from '@mui/material';
import Sidebar from '../components/Sidebar';
import Navbar from '../components/Navbar';
import ChatInput from '../components/ChatInput';
import PersonIcon from '@mui/icons-material/Person';
import SmartToyIcon from '@mui/icons-material/SmartToy';
import ReactMarkdown from 'react-markdown';
import AI from '../images/ai.png';
import axios from "axios";

import { useDispatch, useSelector } from 'react-redux';

const COLORS = {
  primary: '#1B998B',
  secondry: '#f67e7d',
  gray: '#495057',
  background: '#f0f4f8',
  paperBackground: '#f9f9f9',
  buttonBackground: '#1B998B',
  buttonHover: '#14766d',
  textFieldBorder: '#d0eae7',
  textFieldFocusBorder: '#1B998B',
  fileItemBackground: '#f4f6f9',
};

const MainPage = () => {
  const dispatch = useDispatch();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [isFrenchReady, setIsFrenchReady] = useState(false);
  const [isArabicReady, setIsArabicReady] = useState(false);
  const [messages, setMessages] = useState([]);
  const [streamingIndex, setStreamingIndex] = useState(null);
  const [frenchSummary, setFrenchSummary] = useState('');
  const [frenchTitle, setFrenchTitle] = useState('');
  const [arabicSummary, setArabicSummary] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);


// helper pour streamer un endpoint text/plain ou event-stream
const streamEndpoint = async (url, onChunk) => {
  const res = await fetch(url, { method: 'GET' });
  const reader = res.body.getReader();
  const decoder = new TextDecoder('utf-8');
  let done = false;
  while (!done) {
    const { value, done: d } = await reader.read();
    done = d;
    if (value) {
      const chunk = decoder.decode(value, { stream: true });
      onChunk(chunk);
    }
  }
};

  useEffect(() => {
    const fetchAll = async () => {
      setIsGenerating(true);
      setFrenchTitle('');
      setFrenchSummary('');

      try {
        // 1) streamer le titre
        await streamEndpoint('http://127.0.0.1:8000/generate_titre_fr', chunk => {
          setFrenchTitle(prev => prev + chunk);
        });

        // 2) une fois le titre complet, ajouter un saut de ligne puis streamer le résumé
        setFrenchSummary(prev => prev + '\n'); // séparer visuellement
        await streamEndpoint('http://127.0.0.1:8000/generate_summary_fr', chunk => {
          setFrenchSummary(prev => prev + chunk);
        });

      } catch (err) {
        console.error('Erreur de streaming :', err);
      } finally {
        setIsGenerating(false);
      }
    };

    fetchAll();
  }, []); // ou [filesRedux] si tu veux relancer à chaque changement de fichiers

  const theme = useTheme();
  const isSmallScreen = useMediaQuery(theme.breakpoints.down('sm'));

  // Message d'accueil automatique
  useEffect(() => {
    setIsFrenchReady(true);
    setIsArabicReady(true);

    const welcomeMessage = "👋 **Bienvenue !** Je suis votre assistant intelligent. Je suis ici pour répondre à vos questions sur les fichiers que vous avez soumis.";
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
  }, []);

  const handleSend = (msg) => {
    const newMessages = [...messages, { from: 'user', text: msg }];
    setMessages(newMessages);

    setTimeout(() => {
      setMessages(prev => [
        ...prev,
        {
          from: 'bot',
          text: `**Merci pour votre question !**\n\nVoici une réponse *simulée* avec du _markdown_.\n\n- Point 1\n- Point 2`,
        },
      ]);
    }, 1000);
  };

  return (
    <Box sx={{ minHeight: '100vh', backgroundColor: COLORS.background }}>
      <Navbar onMenuClick={() => setSidebarOpen(true)} sidebarOpen={sidebarOpen} />
      <Sidebar open={sidebarOpen} onClose={() => setSidebarOpen(false)} />

      <Box
        sx={{
          pr: { xs: 7, md: 13, lg: 22 },
          pl: { xs: 7, md: 13, lg: 22 },
          pb: 20,
          pt: 10,
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
              color: COLORS.gray,
              fontWeight: 'bold',
              fontSize: { xs: '1.3rem', md: '1.7rem' },
              letterSpacing: '0.5px',
              textShadow: '2px 2px 4px rgba(0,0,0,0.2)', // ombre plus visible
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              textAlign: 'center',
              mb: 1,
            }}
          >
            Bienvenue sur&nbsp;
            <Box
              component="span"
              sx={{
                color: COLORS.primary,
                fontWeight: 700,
                fontSize: 'inherit',
                display: 'flex',
                alignItems: 'center',
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
                  top: '-8px',
                }}
              />
            </Box>
          </Typography>

          <Box
            sx={{
              height: '3px',
              width: '180px',
              backgroundColor: COLORS.primary,
              borderRadius: 3,
              boxShadow: '0 4px 6px rgba(0, 0, 0, 0.15)',  // Ombre portée sur la barre
 
            }}
          />
        </Box>

        {/* Résumé en Français */}
        <Box
          sx={{
            backgroundColor: COLORS.paperBackground,
            borderRadius: 4,
            boxShadow: '-10px 0 20px rgba(27, 153, 139, 0.4)',
            pt: 2,
            pl: 4,
            pr: 4,
            pb: 4,
            mb: 4,
            borderLeft: `6px solid ${COLORS.primary}`,
          }}
        >
          <h2 style={{ color: COLORS.primary, marginBottom: '12px' }}>Résumé en Français</h2>
        <ReactMarkdown
          components={{
            p: ({ node, ...props }) => (
              <Typography
                component="div"
                sx={{
                  fontFamily: 'inherit',
                  fontSize: '1rem',
                  color: COLORS.gray,
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
            backgroundColor: COLORS.paperBackground,
            borderRadius: 4,
            boxShadow: '10px 0 20px rgba(246, 126, 125, 0.4)',
            pt: 2,
            pl: 4,
            pr: 4,
            pb: 4,
            mb: 4,
            borderRight: `6px solid ${COLORS.secondry}`,
            direction: 'rtl',
            textAlign: 'justify',
          }}
        >
          <h2 style={{ color: COLORS.secondry, marginBottom: '12px' }}>الملخص باللغة العربية</h2>
         <ReactMarkdown
            components={{
              p: ({ node, ...props }) => (
                <Typography
                  component="div"
                  sx={{
                    fontFamily: 'inherit',
                    fontSize: '1rem',
                    color: COLORS.gray,
                    lineHeight: 1.8,
                    direction: 'rtl',
                    textAlign: 'justify',
                    wordBreak: 'break-word',
                  }}
                  {...props}
                />
              ),
            }}
          >
          {`**العنوان:** وزارة الطاقة والمناجم: أكثر من 1.5 مليون جزائري متصلون الآن بالإنترنت عبر الألياف البصرية.
       \n\n   **الملخص:** أعلنت وزارة الاتصالات عن تحسن نوعي في تغطية شبكات الاتصالات في الجزائر، حيث تم تزويد أكثر من 1.5 مليون منزل بالألياف البصرية، وبلغ عدد المنازل المتصلة بالإنترنت الثابت 5.8 ملايين، وذلك وفقًا لبيان رسمي. وقد تم تحقيق هذه "القفزة النوعية" في مجال شبكات الاتصالات في إطار تنفيذ تعليمات رئيس الجمهورية، عبد المجيد تبون، المتعلقة بتحسين تغطية شبكات الاتصالات.
          `}
          </ReactMarkdown>

        </Box>

        <Box sx={{ mt: 6, mb: 6 }}>
          <hr style={{ border: 'none', height: '2px', backgroundColor: COLORS.gray, opacity: 0.1 }} />
        </Box>

        {/* SECTION CHATBOT */}
        <Box sx={{ mt: 6, mb: 10 }}>
          <Box sx={{ textAlign: 'center', mb: 6 }}>
            <Typography
              variant="h5"
              sx={{
                color: COLORS.gray,
                fontWeight: 'bold',
                fontSize: { xs: '1.3rem', md: '1.7rem' },
                letterSpacing: '0.5px',
                textShadow: '1px 1px 2px rgba(0,0,0,0.1)',  // Ombre légère sur le texte
 
              }}
            >
              Analyse assistée — Discutez avec le bot
            </Typography>
            <Box
              sx={{
                height: '3px',
                width: '200px',
                margin: '8px auto 0',
                backgroundColor: COLORS.primary,
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
                    <Avatar sx={{ bgcolor: '#4e5655', mr: 1,mt:1 }}>
                      <SmartToyIcon />
                    </Avatar>
                  )}

                  <Paper
                    elevation={3}
                    sx={{
                      maxWidth: '75%',
                      p: 1.5,
                      borderRadius: '20px',
                      backgroundColor: isUser ? '#d1f5f0' : '#dee7e7',
                      color: COLORS.gray,
                      fontSize: '1rem',
                      boxShadow: '0 2px 5px rgba(0,0,0,0.1)',
                      wordBreak: 'break-word',
                    }}
                  >
                    <ReactMarkdown>{msg.text}</ReactMarkdown>
                  </Paper>

                  {isUser && (
                    <Avatar sx={{ bgcolor: COLORS.primary, ml: 1,mt:1 }}>
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
        />
      )}
    </Box>
  );
};

export default MainPage;
