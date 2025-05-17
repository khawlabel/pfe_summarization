import React from 'react';
import { Navigate } from 'react-router-dom';


const getTokenFromLocalStorage = localStorage.getItem("user")
? JSON.parse(localStorage.getItem("user"))
: null;


// Fonction de vérification du rôle
export const checkUserRole = (role) => {
  const userRole =getTokenFromLocalStorage?.role;
  return userRole === role;
};


