import React, { useState ,useEffect} from 'react';
import { Box, Typography, Paper, Button, IconButton } from '@mui/material';
import { useDropzone } from 'react-dropzone';
import UploadFileIcon from '@mui/icons-material/UploadFile';
import CloseIcon from '@mui/icons-material/Close';  // Icone pour retirer un fichier
import ChatBotGif from '../images/Chat_bot.gif';
import Arrow from '../images/arrow (3).png'; // Import de l'image de la flèche
import BackgroundDescription from '../images/shape9.png';
import { uploadfiles,setFiles } from '../features/files/filesSlice';
import { Alert } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { useSelector, useDispatch } from 'react-redux';
import CircularProgress from '@mui/material/CircularProgress';

const COLORS = {
  primary: '#1B998B',
  secondry: '#444',
  background: '#ebf1f8',
  paperBackground: '#ffffff',
  buttonBackground: '#1B998B',
  buttonHover: '#14766d',
  textFieldBorder: '#d0eae7',
  textFieldFocusBorder: '#1B998B',
  fileItemBackground: '#f4f6f9',
};


const UploadFiles = () => {

  const dispatch = useDispatch();
  const navigate = useNavigate();
  const upload = useSelector((state) => state.files);
  const { isLoading, isError, isSuccess, message } = upload;


  

  const [files, setFiles] = useState([]);
  const [rejectedFiles, setRejectedFiles] = useState([]);

      useEffect(() => {
      if (isSuccess) {
        // Redirection après 3 secondes
        setTimeout(() => {
          navigate('/mainpage');
        }, 3000);
      }
    }, [isSuccess, navigate, files]);

  
  const { getRootProps, getInputProps } = useDropzone({
    multiple: true,
    accept: {
      'application/pdf': ['.pdf'],
      'audio/*': ['.mp3', '.wav', '.ogg', '.flac', '.m4a'],
      'video/*': ['.mp4', '.avi', '.mov', '.mkv'],
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
      justifyContent: 'center',
      alignItems: 'center',
      px: 4,
      py: 10,
    }}
  >
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        width: '100%',
        maxWidth: '1200px',
      }}
    >
      {/* ➤ Ligne 1 : description + gif */}
      <Box
        sx={{
          display: 'flex',
          flexDirection: { xs: 'column', md: 'row' },
          gap: 6,
          justifyContent: 'space-between',
          alignItems: 'flex-start',
        }}
      >
        {/* Colonne gauche : Description */}
        <Box
          sx={{
            width: { xs: '100%', md: '70%' },
            textAlign: 'justify',
              marginLeft: { xs: 0 , md: 3 },
               backgroundImage: `url(${BackgroundDescription})`,
                backgroundSize: '95%',
                backgroundRepeat: 'no-repeat',
                backgroundPosition: 'center',
                padding: 3,
                
          }}
        >
        <Typography
              variant="h3"
              sx={{
                fontWeight: 'bold',
                fontSize: { xs: '2.2rem', md: '3rem' },
                color: COLORS.secondry,
                mb: 2,
                lineHeight: 1.2,
              }}
            >
              <span style={{
                color: '#f67e7d',
                textTransform: 'uppercase',
                fontStyle: 'italic',
                letterSpacing: '0.5px',
                
              }}>
                Résumez
              </span>{' '}
              vos contenus en un clin d’œil
            </Typography>


          <Typography
            variant="body1"
            sx={{
              fontSize: '1.2rem',
              color: COLORS.secondry,
              lineHeight: 2,
              fontWeight: 500,
            }}
          >
            Transformez vos <strong>PDF</strong>, <strong>audios</strong> ou <strong>vidéos</strong> en résumés instantanés, 
            <strong> en français ou en arabe</strong>, prêts à l’emploi.<br />
            <span style={{ fontStyle: 'italic' }}>
              Gagnez du temps, boostez votre productivité .
            </span><br />
            Et si vous avez des questions, <strong>discutez directement avec votre contenu</strong> grâce à notre IA intelligente !<br />
        
            <strong>Déposez simplement votre fichier ci-dessous </strong> – notre IA fait le reste !
          </Typography>

        </Box>

        {/* Colonne droite : GIF */}
        <Box
          sx={{
            width: { xs: '100%', md: '35%' },
            marginRight: { xs: 0 , md: 5 },
            marginTop: { xs: 0 , md: 4 },
            display: 'flex',
            justifyContent: 'center',
          }}
        >
         <img
            src={ChatBotGif}
            alt="Illustration IA"
            style={{ width: '100%', maxWidth: '320px' }}
          />
        </Box>
      </Box>
       <Box
        >
         <img
            src={Arrow}
            alt="Fleche"
            style={{ width: '100%', maxWidth: '150px', marginLeft: 'auto', marginRight: 'auto', display: 'block' }}
          />
        </Box>

      {/* ➤ Ligne 2 : Dropzone centrée */}
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'center',
          marginTop: 4,
        }}
      >
        <Paper
          elevation={4}
          sx={{
            borderRadius: '24px',
            padding: 6,
            background: COLORS.paperBackground,
            textAlign: 'center',
            boxShadow: '0px 15px 45px rgba(0, 0, 0, 0.15)',
            width: '100%',
            maxWidth: 600,
            overflowY: 'auto',
          }}
        >
          {/* Zone de drop */}
          <Box
            {...getRootProps()}
          sx={{
                border: `2px dashed ${COLORS.primary}`,
                borderRadius: '20px',
                p: 4,
                cursor: 'pointer',
                backgroundColor: '#fff',
                transition: 'all 0.3s ease',
                '&:hover': {
                  backgroundColor: '#f1fdfb',
                  borderColor: COLORS.buttonHover,
                },
              }}

          >
            <input {...getInputProps()} />
            <UploadFileIcon sx={{ fontSize: 40, color: COLORS.primary, mb: 1 }} />
            <Typography variant="body1" fontWeight="bold" sx={{ mb: 1 }}>
              Cliquez ou glissez vos fichiers ici
            </Typography>
            <Typography variant="body2" sx={{ color: COLORS.secondry }}>
              Formats supportés : <strong>.pdf, .mp3, .wav, .ogg, .flac, .m4a,.mp4, .avi, .mov, .mkv</strong>
            </Typography>
          </Box>

          {/* Fichiers sélectionnés */}
          {files.length > 0 && (
            <Box sx={{ mt: 4, display: 'flex', flexDirection: 'column', gap: 1.5 }}>
              <Typography variant="body2" sx={{ color: COLORS.primary, fontWeight: 'bold' }}>
                Fichiers sélectionnés :
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
                    transition: 'all 0.2s',
                    '&:hover': {
                      boxShadow: '0 2px 6px rgba(0,0,0,0.06)',
                    },
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



              {isLoading ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', mt: 3 }}>
               <CircularProgress size={32} sx={{ color: '#0d5b53' }} />

                </Box>
              ) : isSuccess ? (
                <Alert severity="success" sx={{ mt: 3 }}>
                  Fichiers uploadés avec succès !
                </Alert>
              ) : isError ? (
                <Alert severity="error" sx={{ mt: 3 }}>
                  Erreur lors de l’upload : {message}
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
                  Soumettre
                </Button>
              )}

            </Box>
          )}
        </Paper>
           {/* 🔻 ALERTE fichiers rejetés ici */}
        {rejectedFiles.length > 0 && (
          <Box sx={{ mt: 2, width: '100%', maxWidth: 600 }}>
            <Alert severity="error">
              Les fichiers suivants ne sont pas acceptés :
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
  </Box>
);

};

export default UploadFiles;
