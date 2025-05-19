import axios from "axios";
import { base_url } from "../../utils/baseUrl";
import {getAuthConfig} from "../../utils/axiosconfig";

const uploadfiles = async (files) => {

  const response = await axios.post(`${base_url}upload_and_store_file`,files,getAuthConfig());

  return response.data;
  };

  
const reset = async () => {

  const response = await axios.get(`${base_url}reset`);

  return response.data;
  };


const filesService = {
    uploadfiles,
    reset
    
  };
  
export default filesService;
  