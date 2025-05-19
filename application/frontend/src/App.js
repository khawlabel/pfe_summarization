import React, { useState, useMemo } from 'react';
import Login from './pages/Login';
import Register from './pages/Register';
import UploadFiles from './pages/UploadFiles';
import MainPage from './pages/MainPage';
import Verification from './pages/Verification';
import {BrowserRouter,Routes,Route,Navigate } from "react-router-dom";
import { Provider } from 'react-redux';
import store from './App/Store';
import { ThemeProvider, createTheme, CssBaseline } from '@mui/material';
import './App.css';
import { CustomThemeProvider } from './ThemeContext'; // ajuste le chemin



//private route 
import {checkUserRole} from './routes/Route';

function App() {
   

  return (
    <>
    <CustomThemeProvider>
     <Provider store={store}>
    <BrowserRouter>
    <Routes>       
              <Route path="/" element={<Navigate to="/login" />} />

              <Route
              path="/login"
              element={
                localStorage.getItem("user") ? (
                  localStorage.getItem("uploadDone") === "true" ? (
                    <Navigate to="/mainpage" />
                  ) : (
                    <Navigate to="/uploadfiles" />
                  )
                ) : (
                  <Login />
                )
              }
            />

            <Route
              path="/register"
              element={
                localStorage.getItem("user") ? (
                  localStorage.getItem("uploadDone") === "true" ? (
                    <Navigate to="/mainpage" />
                  ) : (
                    <Navigate to="/uploadfiles" />
                  )
                ) : (
                  <Register />
                )
              }
            />

            <Route
              path="/uploadfiles"
              element={
                localStorage.getItem("user") ? (
                  localStorage.getItem("uploadDone") === "true" ? (
                    <Navigate to="/mainpage" />
                  ) : (
                    <UploadFiles />
                  )
                ) : (
                  <Navigate to="/login" />
                )
              }
            />

            <Route
              path="/mainpage"
              element={
                localStorage.getItem("user") ? (
                  localStorage.getItem("uploadDone") === "true" ? (
                    <MainPage  />
                  ) : (
                    <Navigate to="/uploadfiles" />
                  )
                ) : (
                  <Navigate to="/login" />
                )
              }
            />

            <Route path="/verify-email/:token" element={<Verification />} />

    </Routes>
    </BrowserRouter>
    </Provider>
     </CustomThemeProvider>
    </>
  );
}

export default App;
