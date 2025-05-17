import axios from "axios";
import { base_url } from "../../utils/baseUrl";
import {getAuthConfig} from "../../utils/axiosconfig";

const login = async (user) => {

  const response = await axios.post(`${base_url}login`,user,{
  headers: {
    'Content-Type': 'application/json'
  }});

  if (response.data) {
    localStorage.setItem("user", JSON.stringify(response.data));
  }
  return response.data;
  };

const register = async (user) => {
  const response = await axios.post(`${base_url}register`, user,{
  headers: {
    'Content-Type': 'application/json'
  }});
  return response.data;
};

const verifyCompte = async (token) => {
  
  const response = await axios.get(`${base_url}verify-email/${token}`);
  return response.data;
};


const authService = {
    login,
    register,
    verifyCompte
    
  };
  
export default authService;
  