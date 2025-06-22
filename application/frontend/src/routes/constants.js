// Variables d'environnement
const apiUrl = process.env.REACT_APP_BACKEND_HOST;
console.log(apiUrl)

// URLs des API
export const LOGIN_URL = `${apiUrl}/login`;
export const REGISTER_URL = `${apiUrl}/register`;
export const VERIFY_EMAIL_URL = `${apiUrl}/verify-email`;
export const UPLOAD_FILES_URL = `${apiUrl}/upload_and_store_file`;
export const RESET_URL = `${apiUrl}/reset`;
export const GENERATE_TITRE_FR_URL = `${apiUrl}/generate_titre_fr`;
export const GENERATE_SUMMARY_FR_URL = `${apiUrl}/generate_summary_fr`;
export const GENERATE_TITRE_AR_URL = `${apiUrl}/generate_titre_ar`;
export const GENERATE_SUMMARY_AR_URL = `${apiUrl}/generate_summary_ar`;
export const CHAT_URL = `${apiUrl}/chat`;
