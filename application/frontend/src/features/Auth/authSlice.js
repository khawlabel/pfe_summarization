import { createSlice, createAsyncThunk,createAction } from "@reduxjs/toolkit";
import authService from "./authService";
import { toast } from "react-toastify";
const getUserfromLocalStorage = localStorage.getItem("user")
  ? JSON.parse(localStorage.getItem("user"))
  : null;

const initialState = {
  user: getUserfromLocalStorage,
  createUserToken:null,
  createuser:"",
  isError: false,
  isLoading: false,
  isSuccess: false,
  message: "",
};

export const login = createAsyncThunk(
  "auth/login",
  async (userData, thunkAPI) => {
    try {
      return await authService.login(userData);
    } catch (error) {

      // on extrait le message du backend FastAPI
    const message =
        (error.response && error.response.data && error.response.data.detail) ||
        error.message ||
        "Erreur inconnue";
      return thunkAPI.rejectWithValue(message);
    }
  }
);


export const register = createAsyncThunk(
  "auth/register",
  async (user, thunkAPI) => {
    try {
      console.log(user)
      return await authService.register(user);
    } catch (error) {
      return thunkAPI.rejectWithValue(error);
    }
  }
);

export const verifyCompte = createAsyncThunk(
  "auth/verifyCompte",
  async (token, thunkAPI) => {
    try {
      return await authService.verifyCompte(token);
    } catch (error) {
      return thunkAPI.rejectWithValue(error);
    }
  }
);

export const resetState= createAction("resetState_auth");
export const authSlice = createSlice({
    name: "auth",
  initialState,
  reducers: {
    reset: (state) => {
      state.isLoading = false;
      state.isError = false;
      state.isSuccess = false;
      state.message = "";
      state.createuser = null;
      // et si tu as d'autres états à remettre à zéro, fais-le ici
    },
  },
  extraReducers: (builder) => {
      builder
        .addCase(login.pending, (state) => {
          state.isLoading = true;
        })
        .addCase(login.fulfilled, (state, action) => {
          state.isError = false;
          state.isLoading = false;
          state.isSuccess = true;
          state.user = action.payload; // normalement ici response.data
          state.message = "success";
        })
      .addCase(login.rejected, (state, action) => {
        state.isError = true;
        state.isLoading = false;
        state.isSuccess = false;
        state.message = action.payload || action.error.message;
        console.log(state.message)
        toast.error(state.message);
      })
        .addCase(register.pending, (state) => {
          state.isLoading = true;
        })
        .addCase(register.fulfilled, (state, action) => {
          state.isError = false;
          state.isLoading = false;
          state.isSuccess = true;
          state.createuser = action.payload;
          state.message = action.payload.message || "Inscription réussie. Vérifiez votre e-mail.";
        })
        .addCase(register.rejected, (state, action) => {
          state.isError = true;
          state.isSuccess = false;
          state.message = action.payload?.response?.data?.detail || action.error.message || "Une erreur est survenue.";
          state.isLoading = false;
        })
        .addCase(verifyCompte.pending, (state) => {
          state.isLoading = true;
        })
        .addCase(verifyCompte.fulfilled, (state, action) => {
          state.isError = false;
          state.isLoading = false;
          state.isSuccess = true;
          state.verify = action.payload;
          state.message = "success";
        })
        .addCase(verifyCompte.rejected, (state, action) => {
          state.isError = true;
          state.isSuccess = false;
          state.message = action.payload || action.error.message;
          state.isLoading = false;
        })
        .addCase(resetState, (state) => {
          return {
            ...state,
            user: null, 
          };
        })
       
    },
  });

export const { reset } = authSlice.actions;
export default authSlice.reducer;