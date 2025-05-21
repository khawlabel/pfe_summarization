import axios from "axios";
import { base_url } from "../../utils/baseUrl";
import {getAuthConfig} from "../../utils/axiosconfig";
import {UPLOAD_FILES_URL,RESET_URL} from  "../../routes/constants"

const uploadfiles = async (files) => {

  console.log("upload",UPLOAD_FILES_URL)
  const response = await axios.post(UPLOAD_FILES_URL,files);

  return response.data;
  };

  
const reset = async () => {

  const response = await axios.get(RESET_URL);

  return response.data;
  };


const filesService = {
    uploadfiles,
    reset
    
  };
  
export default filesService;
  