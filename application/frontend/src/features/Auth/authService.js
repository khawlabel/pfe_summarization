import axios from "axios";
import { base_url } from "../../utils/baseUrl";
import { getAuthConfig } from "../../utils/axiosconfig";
import { LOGIN_URL, REGISTER_URL, VERIFY_EMAIL_URL } from "../../routes/constants";

// 🟡 Fonction pour récupérer la langue actuelle depuis le store
const getCurrentLanguage = () => {
  return localStorage.getItem("language") || "fr"; // valeur par défaut : fr
};

// 🔵 Requête login
const login = async (user) => {
  const lang = getCurrentLanguage();

  const response = await axios.post(LOGIN_URL, user, {
    headers: {
      "Content-Type": "application/json",
      "Accept-Language": lang,
    },
  });

  return response.data;
};

// 🔵 Requête register
const register = async (user) => {
  const lang = getCurrentLanguage();

  const response = await axios.post(REGISTER_URL, user, {
    headers: {
      "Content-Type": "application/json",
      "Accept-Language": lang,
    },
  });

  return response.data;
};

// 🔵 Requête verify email
const verifyCompte = async (token) => {
  const lang = getCurrentLanguage();

  const response = await axios.get(`${VERIFY_EMAIL_URL}/${token}`, {
    headers: {
      "Accept-Language": lang,
    },
  });

  return response.data;
};

// Export
const authService = {
  login,
  register,
  verifyCompte,
};

export default authService;
