import axios from "axios";
import { base_url } from "../../utils/baseUrl";
import {getAuthConfig} from "../../utils/axiosconfig";

const uploadfiles = async (files) => {

  const response = await axios.post(`${base_url}upload_and_store_file`,files,getAuthConfig());

  return response.data;
  };

const stream_summary  = async (files, setTextCallback) => {
  const response = await axios.post(`${base_url}generate_summary`, files, {
    headers: { Accept: "text/event-stream" },
    responseType: "stream",
  });

  const reader = response.data.getReader();
  const decoder = new TextDecoder("utf-8");

  let partialData = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    partialData += decoder.decode(value, { stream: true });
    const parts = partialData.split("\n\n");

    for (let i = 0; i < parts.length - 1; i++) {
      const line = parts[i].replace(/^data:\s*/, "");
      if (line !== "[END]") {
        setTextCallback(prev => prev + line);
      }
    }

    partialData = parts[parts.length - 1]; // garder le reste
  }
};



const filesService = {
    uploadfiles,
    stream_summary 
    
  };
  
export default filesService;
  