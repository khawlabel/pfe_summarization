import React, { useState ,useEffect} from 'react';
import { Box, useTheme, Typography, Paper, Button, IconButton } from '@mui/material';
import { useDropzone } from 'react-dropzone';
import UploadFileIcon from '@mui/icons-material/UploadFile';
import CloseIcon from '@mui/icons-material/Close';  // Icone pour retirer un fichier
import BackgroundDescription_clair from '../images/shape_clair.png';
import BackgroundDescription_sombre from '../images/shape_sombre.png';
import { uploadfiles } from '../features/files/filesSlice';
import { Alert } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { useSelector, useDispatch } from 'react-redux';
import CircularProgress from '@mui/material/CircularProgress';
import Navbar from '../components/NavbarUploadFiles';
import { ThemeContext } from '../ThemeContext'; // ajuste le chemin
import { useContext } from 'react';
import Menu from '@mui/material/Menu';
import MenuItem from '@mui/material/MenuItem';

import dz from '../images/flags/algeria.webp';
import en from '../images/flags/uk.webp'; 
import fr from '../images/flags/france.png'; 


import { useTranslation } from 'react-i18next';

const UploadFiles = () => {

  const { i18n } = useTranslation();
  const { t } = useTranslation();

  const changeLang = (langCode) => {
    i18n.changeLanguage(langCode);
  };

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

  const { mode } = useContext(ThemeContext);

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

  const dispatch = useDispatch();
  const navigate = useNavigate();
  const upload = useSelector((state) => state.files);
  const { isLoadinguploadefiles, isErroruploadefiles, isSuccessuploadefiles, messageuploadefiles } = upload;
  
  const [files, setFiles] = useState([]);
  const [rejectedFiles, setRejectedFiles] = useState([]);

      useEffect(() => {
      if (isSuccessuploadefiles) {
        // Après upload réussi
        localStorage.setItem("uploadDone", "true");
        // Redirection après 3 secondes
        setTimeout(() => {
          window.location.reload()
        }, 3000);
      }
    }, [isSuccessuploadefiles, navigate, files]);

  
  const { getRootProps, getInputProps } = useDropzone({
    multiple: true,
    accept: {
      'application/pdf': ['.pdf'],
      'audio/*': ['.mp3', '.wav', '.ogg', '.flac', '.m4a'],
      'video/*': ['.mp4', '.avi', '.mov', '.mkv'],
      'image/*': ['.png', '.jpg', '.jpeg', '.bmp', '.tiff'],
    },
    onDrop: (acceptedFiles) => {
      setFiles((prevFiles) => [...prevFiles, ...acceptedFiles]);
      setRejectedFiles([]); // reset les erreurs précédentes
    },
    onDropRejected: (fileRejections) => {
      setRejectedFiles(fileRejections.map(rej => rej.file.name));
    },
  });


  // Fonction pour retirer un fichier de la liste
  const removeFile = (file) => {
    setFiles((prevFiles) => prevFiles.filter((f) => f.name !== file.name));
  };

  const handleSubmit = () => {

    if (files.length === 0) return;

    const formData = new FormData();
    files.forEach((file) => {
      formData.append('file', file);  // clé 'files' selon ton API backend
    });

    files.forEach((file) => {
      formData.append('uploaded_files', file);  // clé 'files' selon ton API backend
    });

    dispatch(uploadfiles(formData));
  };


return (
  <Box
    sx={{
      minHeight: '100vh',
      backgroundColor: COLORS.background,
      display: 'flex',
      flexDirection: 'column',
    }}
  >
    <Navbar />

    <Box
      sx={{
        display: 'flex',
        flexDirection: { xs: 'column', md: 'row' },
        alignItems: 'center',
        justifyContent: 'center',
        pt: 5,
        px: 4,
        py: 8,
        gap: 6,
        flex: 1,
          mt: '45px', // Ajoute ça ici si Navbar est en fixed
      }}
    >
      {/* === Description Gauche === */}
         {/* === backgroundImage: isDarkMode
            ? `url(${BackgroundDescription_sombre})`
            : `url(${BackgroundDescription_clair})`,=== */}
      <Box
        sx={{
          flex: 1,
          backgroundSize: 'cover',
          backgroundPosition: 'center',
          padding: 4,
          borderRadius: '20px',
          textAlign: 'justify',
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'center',
          height: '100%',
          maxWidth: '700px',
        }}
      >
        <Typography
          variant="h3"
          dir={i18n.language === 'ar' ? 'rtl' : 'ltr'}
          sx={{
            fontWeight: 'bold',
            fontSize: { xs: '2rem', md: '3rem' },
            color: isDarkMode ? COLORS.primary : '#444',
            mb: 2,
            lineHeight: 1.2,
            textAlign: i18n.language === 'ar' ? 'right' : 'left',
          }}
        >
          <span style={{
            color: '#f67e7d',
            textTransform: 'uppercase',
            fontStyle: 'italic',
            letterSpacing: '0.5px',
          }}>
            {t('summarize')}
          </span>{' '}
          {t('yourContentInstantly')}
        </Typography>

        <Typography
          variant="body1"
          dir={i18n.language === 'ar' ? 'rtl' : 'ltr'}
          sx={{
            fontSize: i18n.language === 'ar' ? '1.4rem' : '1.2rem',
            color: COLORS.secondry,
            lineHeight: i18n.language === 'ar' ? 2 : 2,
            fontWeight: 500,
            textAlign: i18n.language === 'ar' ? 'right' : 'left',
            wordSpacing: i18n.language === 'ar' ? '3px' : 'normal',
            letterSpacing: i18n.language === 'ar' ? '0.8px' : 'normal',
          }}
          dangerouslySetInnerHTML={{ __html: t('description') }}
        />

      </Box>

      {/* === Dropzone Droite === */}
      <Box
        sx={{
          flex: 1,
          maxWidth: '450px',
          width: '100%',
          display: 'flex',
          justifyContent: 'center',
        }}
      >
        <Paper
          elevation={4}
          sx={{
            borderRadius: '24px',
            padding: 6,
            background: COLORS.paperBackground,
            textAlign: 'center',
            width: '100%',
            boxShadow: isDarkMode
              ? '0 4px 15px rgba(100, 255, 255, 0.08)'
              : '0px 15px 45px rgba(0, 0, 0, 0.15)',
          }}
        >
          <Box {...getRootProps()}
            sx={{
              border: `2px dashed ${COLORS.primary}`,
              borderRadius: '20px',
              p: 4,
              cursor: 'pointer',
              backgroundColor: isDarkMode ? '#2c2c2c' : '#fff',
              transition: 'all 0.3s ease',
              '&:hover': {
                backgroundColor: isDarkMode ? '#2C3432' : '#f1fdfb',
                borderColor: COLORS.buttonHover,
              },
            }}>
            <input {...getInputProps()} />
            <UploadFileIcon sx={{ fontSize: 40, color: COLORS.primary, mb: 1 }} />
            <Typography variant="body1" fontWeight="bold" sx={{ mb: 1 }}>
             { t('dropzoneTitle')}
            </Typography>
            <Typography
              variant="body2"
              sx={{ color: COLORS.secondry }}
              dangerouslySetInnerHTML={{ __html: t('dropzoneFormats') }}
            />
          </Box>

          {files.length > 0 && (
            <Box sx={{ mt: 4, display: 'flex', flexDirection: 'column', gap: 1.5 }}>
              <Typography variant="body2" dir={isArabic ? 'rtl' : 'ltr'} sx={{ color: COLORS.primary, fontWeight: 'bold' }}>
               {t('selectedFiles')}
              </Typography>
              {files.map((file) => (
                <Box
                  key={file.name}
                  sx={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    backgroundColor: COLORS.fileItemBackground,
                    padding: 1.5,
                    borderRadius: '12px',
                    border: `1px solid ${COLORS.textFieldBorder}`,
                  }}
                >
                  <Typography variant="body2" sx={{ color: COLORS.secondry }}>
                    {file.name}
                  </Typography>
                  <IconButton size="small" onClick={() => removeFile(file)}>
                    <CloseIcon fontSize="small" sx={{ color: COLORS.primary }} />
                  </IconButton>
                </Box>
              ))}

              {isLoadinguploadefiles ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', mt: 3 }}>
                  <CircularProgress size={32} sx={{ color: '#0d5b53' }} />
                </Box>
              ) : isSuccessuploadefiles ? (
                <Alert dir={i18n.language === 'ar' ? 'rtl' : 'ltr'} severity="success" 
                    sx={{
                      mt: 3,
                      '& .MuiAlert-icon': {
                        marginInlineEnd: '0.5em', // ajoute un espace entre l'icône et le texte
                      },
                    }}
                  >
                  {t('uploadSuccess')}
                </Alert>
              ) : isErroruploadefiles ? (
                <Alert dir={i18n.language === 'ar' ? 'rtl' : 'ltr'} severity="error"
                sx={{
                      mt: 3,
                      '& .MuiAlert-icon': {
                        marginInlineEnd: '0.5em', // ajoute un espace entre l'icône et le texte
                      },
                    }} >
                {t('uploadError')} {messageuploadefiles}
                </Alert>
              ) : (
                <Button
                  variant="contained"
                  disabled={files.length === 0}
                  sx={{
                    mt: 3,
                    background: 'linear-gradient(to right, #1B998B, #14766d)',
                    color: '#fff',
                    fontWeight: 'bold',
                    borderRadius: '999px',
                    px: 7,
                    py: 1.5,
                    fontSize: '1rem',
                    textTransform: 'none',
                    alignSelf: 'center',
                    boxShadow: '0 4px 14px rgba(0,0,0,0.1)',
                    '&:hover': {
                      background: 'linear-gradient(to right, #14766d, #0d5b53)',
                    },
                  }}
                  onClick={handleSubmit}
                >
                 {t('submit')}
                </Button>
              )}
            </Box>
          )}
        </Paper>
         {/* 🔻 ALERTE fichiers rejetés ici */}
                {rejectedFiles.length > 0 && (
                  <Box sx={{ mt: 2, width: '100%', maxWidth: 600 }}>
                    <Alert severity="error">
                     {t('rejectedFilesAlert')}
                      <ul style={{ margin: 0, paddingLeft: '1.2em' }}>
                        {rejectedFiles.map((fileName, index) => (
                          <li key={index}>{fileName}</li>
                        ))}
                      </ul>
                    </Alert>
                  </Box>
                )}
      </Box>
    </Box>
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

export default UploadFiles;
