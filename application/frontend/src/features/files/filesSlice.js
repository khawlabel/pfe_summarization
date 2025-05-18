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
  isError: false,
  isLoading: false,
  isSuccess: false,
  message: "",
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

export const generate_summary = createAsyncThunk(
  "files/generate_summary",
  async (files, thunkAPI) => {
    try {
      return await filesService.generate_summary(files);
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
        state.isLoading = true;
      })
      .addCase(uploadfiles.fulfilled, (state, action) => {
        state.isError = false;
        state.isLoading = false;
        state.isSuccess = true;
        state.uploadefiles = action.payload;
        state.message = "success";
      })
      .addCase(uploadfiles.rejected, (state, action) => {
        state.isError = true;
        state.isLoading = false;
        state.isSuccess = false;
        state.message = action.payload || action.error.message;
      })
      .addCase(generate_summary.pending, (state) => {
        state.isLoading = true;
      })
      .addCase(generate_summary.fulfilled, (state, action) => {
        state.isError = false;
        state.isLoading = false;
        state.isSuccess = true;
        state.generate_summary = action.payload;
        state.message = "success";
      })
      .addCase(generate_summary.rejected, (state, action) => {
        state.isError = true;
        state.isLoading = false;
        state.isSuccess = false;
        state.message = action.payload || action.error.message;
      })
      .addCase(reset.pending, (state) => {
        state.isLoading = true;
      })
      .addCase(reset.fulfilled, (state, action) => {
        state.isError = false;
        state.isLoading = false;
        state.isSuccess = true;
        state.reset = action.payload;
        state.message = "success";
      })
      .addCase(reset.rejected, (state, action) => {
        state.isError = true;
        state.isLoading = false;
        state.isSuccess = false;
        state.message = action.payload || action.error.message;
      })
      .addCase(resetState, (state) => {
        return {
          ...state,
          uploadefiles:"",
          generate_summary:null,
        };
      });
  },
});


export const { setFiles, clearFiles } = filesSlice.actions;

export default filesSlice.reducer;
