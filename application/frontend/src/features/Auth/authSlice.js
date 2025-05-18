import { createSlice, createAsyncThunk, createAction } from "@reduxjs/toolkit";
import authService from "./authService";

const getUserFromLocalStorage = localStorage.getItem("user")
  ? JSON.parse(localStorage.getItem("user"))
  : null;

const initialState = {
  user: getUserFromLocalStorage,
  createUserToken: null,
  createuser: null,
  isErrorlogin: false,
  isLoadinglogin: false,
  isSuccesslogin: false,
  messagelogin: "",
  isErrorregister: false,
  isLoadingregister: false,
  isSuccessregister: false,
  messageregister: "",
  verify: null,
  isErrorverifyCompte: false,
  isLoadingverifyCompte: false,
  isSuccessverifyCompte: false,
  messageverifyCompte: "",
  
};

export const login = createAsyncThunk(
  "auth/login",
  async (userData, thunkAPI) => {
    try {
      const response = await authService.login(userData);
      return response;
    } catch (error) {
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

export const resetState = createAction("resetState_auth");

const authSlice = createSlice({
  name: "auth",
  initialState,
  reducers: {
    resetLogin: (state) => {
    state.isLoadinglogin = false;
    state.isErrorlogin = false;
    state.isSuccesslogin = false;
    state.messagelogin = "";
  },

  resetRegister: (state) => {
    state.isLoadingregister = false;
    state.isErrorregister = false;
    state.isSuccessregister = false;
    state.messageregister = "";
    state.createuser = null;
  },

  resetVerifyCompte: (state) => {
    state.isLoadingverifyCompte = false;
    state.isErrorverifyCompte = false;
    state.isSuccessverifyCompte = false;
    state.messageverifyCompte = "";
    state.verify = null;
  }

  },
  extraReducers: (builder) => {
    builder
      // login
      .addCase(login.pending, (state) => {
        state.isLoadinglogin = true;
      })
      .addCase(login.fulfilled, (state, action) => {
        state.isErrorlogin = false;
        state.isLoadinglogin = false;
        state.isSuccesslogin = true;
        state.user = action.payload;
        localStorage.setItem("user", JSON.stringify(action.payload));
        state.messagelogin = "Connexion réussie";
      })
      .addCase(login.rejected, (state, action) => {
        state.isErrorlogin = true;
        state.isLoadinglogin = false;
        state.isSuccesslogin = false;
        state.messagelogin = action.payload || action.error.message;
        state.user = null;
      })
      // register
      .addCase(register.pending, (state) => {
        state.isLoadingregister = true;
      })
      .addCase(register.fulfilled, (state, action) => {
        state.isErrorregister  = false;
        state.isLoadingregister  = false;
        state.isSuccessregister  = true;
        state.createuser = action.payload;
        state.messageregister  = action.payload.message || "Inscription réussie. Vérifiez votre e-mail.";
      })
      .addCase(register.rejected, (state, action) => {
        state.isErrorregister  = true;
        state.isLoadingregister  = false;
        state.isSuccessregister  = false;
        state.messageregister  =
          action.payload?.response?.data?.detail || action.error.message || "Une erreur est survenue.";
      })
      // verifyCompte
      .addCase(verifyCompte.pending, (state) => {
        state.isLoadingverifyCompte = true;
      })
      .addCase(verifyCompte.fulfilled, (state, action) => {
        state.isErrorverifyCompte = false;
        state.isLoadingverifyCompte = false;
        state.isSuccessverifyCompte = true;
        state.verify = action.payload;
        state.messageverifyCompte = "Compte vérifié avec succès";
      })
      .addCase(verifyCompte.rejected, (state, action) => {
        state.isErrorverifyCompte = true;
        state.isLoadingverifyCompte = false;
        state.isSuccessverifyCompte = false;
        state.messageverifyCompte = action.payload || action.error.message;
      })
      // resetState action
      .addCase(resetState, (state) => {
        return {
          ...state,
        };
      });
  },
});

export const { resetLogin, resetRegister, resetVerifyCompte } = authSlice.actions;
export default authSlice.reducer;
