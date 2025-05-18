import React, { useState, useMemo } from 'react';
import Login from './pages/Login';
import Register from './pages/Register';
import UploadFiles from './pages/UploadFiles';
import Home from  './pages/Home';
import MainPage from './pages/MainPage';
import Verification from './pages/Verification';
import {BrowserRouter,Routes,Route,Navigate } from "react-router-dom";
import { Provider } from 'react-redux';
import store from './App/Store';
import { ThemeProvider, createTheme, CssBaseline } from '@mui/material';
import './App.css';

//private route 
import {checkUserRole} from './routes/Route';

function App() {
   const [mode, setMode] = useState('light');
  
    const theme = useMemo(() => createTheme({
      palette: {
        mode,
        primary: { main: '#1B998B' },
        secondary: { main: '#f67e7d' },
      },
    }), [mode]);
  
    const toggleTheme = (newMode) => {
      setMode(newMode);
    };

  return (
    <>
    <ThemeProvider theme={theme}>
          <CssBaseline />
     <Provider store={store}>
    <BrowserRouter>
    <Routes>

              <Route path="/" element={<Home />} />
              
              <Route path="/login" element= {localStorage.getItem("user")  ? (
               <Navigate to="/" />
               ) : (
                 <Login/>
               )
             }/>

              <Route path="/register" element={localStorage.getItem("user")  ? (
               <Navigate to="/" />
               ) : (
                 <Register/>
               )
             }/>
              <Route path="/uploadfiles" element={localStorage.getItem("user")  ? (<UploadFiles/>)  : (<Navigate to="/login" />)}/>
              <Route path="/mainpage" element={localStorage.getItem("user")  ? (<MainPage onThemeChange={toggleTheme}/>) : (<Navigate to="/login" />)}/>
              <Route path="/verify-email/:token" element={<Verification/>} />
    </Routes>
    </BrowserRouter>
    </Provider>
    </ThemeProvider>
    </>
  );
}

export default App;
