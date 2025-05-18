import { createSlice, createAsyncThunk, createAction } from "@reduxjs/toolkit";
import filesService from "./filesService";
import { toast } from "react-toastify";
import CircularProgress from '@mui/material/CircularProgress';
import { base_url } from "../../utils/baseUrl";
import {getAuthConfig} from "../../utils/axiosconfig";
import axios from "axios";

const getUserfromLocalStorage = localStorage.getItem("user")
  ? JSON.parse(localStorage.getItem("user"))
  : null;

const initialState = {
  user: getUserfromLocalStorage,
  generate_summary:null,
  reset:null,
  files:null,
  uploadefiles: "",
  isErroruploadefiles: false,
  isLoadinguploadefiles: false,
  isSuccessuploadefiles: false,
  messageuploadefiles: "",
  isErroruploadereset: false,
  isLoadinguploadereset: false,
  isSuccessuploadereset: false,
  messageuploadereset: "",
};


export const uploadfiles = createAsyncThunk(
  "files/uploadfiles",
  async (files, thunkAPI) => {
    try {
      return await filesService.uploadfiles(files);
    } catch (error) {
      const message =
        error.response?.data?.error || // <-- pour FastAPI
        error.response?.data?.detail ||
        error.message;
      return thunkAPI.rejectWithValue(message);
    }
  }
);

export const reset = createAsyncThunk(
  "files/reset",
  async (thunkAPI) => {
    try {
      return await filesService.reset();
    } catch (error) {
      const message =
        error.response?.data?.error || // <-- pour FastAPI
        error.response?.data?.detail ||
        error.message;
      return thunkAPI.rejectWithValue(message);
    }
  }
);


export const resetState = createAction("resetState_files");

export const filesSlice = createSlice({
  name: "files",
  initialState,
  reducers: {
    setFiles(state, action) {
      state.files = action.payload; // remplace la liste
    },
    clearFiles(state) {
      state.files = [];
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(uploadfiles.pending, (state) => {
        state.isLoadinguploadefiles = true;
      })
      .addCase(uploadfiles.fulfilled, (state, action) => {
        state.isErroruploadefiles = false;
        state.isLoadinguploadefiles = false;
        state.isSuccessuploadefiles = true;
        state.uploadefiles = action.payload;
        state.messageuploadefiles = "success";
      })
      .addCase(uploadfiles.rejected, (state, action) => {
        state.isErroruploadefiles = true;
        state.isLoadinguploadefiles = false;
        state.isSuccessuploadefiles = false;
        state.messageuploadefiles = action.payload || action.error.message;
      })
      .addCase(reset.pending, (state) => {
        state.isLoadingreset = true;
      })
      .addCase(reset.fulfilled, (state, action) => {
        state.isErrorreset = false;
        state.isLoadingreset = false;
        state.isSuccessreset = true;
        state.resetreset = action.payload;
        state.messagereset = "success";
      })
      .addCase(reset.rejected, (state, action) => {
        state.isErrorreset = true;
        state.isLoadingreset = false;
        state.isSuccessreset = false;
        state.messagereset = action.payload || action.error.message;
      })
      .addCase(resetState, (state) => {
        return {
          ...state,
        };
      });
  },
});


export const { setFiles, clearFiles } = filesSlice.actions;

export default filesSlice.reducer;
