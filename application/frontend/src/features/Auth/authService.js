import axios from "axios";
import { base_url } from "../../utils/baseUrl";
import {getAuthConfig} from "../../utils/axiosconfig";
import {LOGIN_URL,REGISTER_URL,VERIFY_EMAIL_URL} from "../../routes/constants"

const login = async (user) => {
  
  console.log("login",LOGIN_URL)
  const response = await axios.post(LOGIN_URL,user,{
  headers: {
    'Content-Type': 'application/json'
  }});

  return response.data;
  };

const register = async (user) => {
  const response = await axios.post(REGISTER_URL, user,{
  headers: {
    'Content-Type': 'application/json'
  }});
  return response.data;
};


const verifyCompte = async (token) => {
  
  const response = await axios.get(`${VERIFY_EMAIL_URL}/${token}`);
  return response.data;
};


const authService = {
    login,
    register,
    verifyCompte
    
  };
  
export default authService;
  