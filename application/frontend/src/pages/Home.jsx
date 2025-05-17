import React, { useEffect } from 'react';
import {
  TextField,
  Button,
  Box,
  Typography,
  Paper
} from '@mui/material';
import { useFormik } from 'formik';
import { useDispatch, useSelector } from 'react-redux';
import { login } from '../features/Auth/authSlice';
import { Link, useNavigate } from 'react-router-dom';
import * as yup from 'yup';



const Home = () => {
    const dispatch = useDispatch();
    const navigate = useNavigate();
    const auth = useSelector((state) => state.auth);
  
  const schema = yup.object().shape({
    email: yup.string().email("L’adresse e-mail doit être valide").required("Ce champ est obligatoire"),
    password: yup.string().required("Ce champ est obligatoire"),
  });

  const formik = useFormik({
    initialValues: {
      email:'',
      password: '',
    },
    validationSchema: schema,
    onSubmit: (values) => {
      dispatch(login(values));
      formik.resetForm();
      setTimeout(() => {
        navigate('/uploadfiles');
      }, 300);
    },
  });
  return (
    "hi"
   
  );
};

export default Home;
