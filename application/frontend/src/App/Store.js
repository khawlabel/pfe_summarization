import { configureStore } from "@reduxjs/toolkit";
import authSlice from "../features/Auth/authSlice";
import filesSlice from "../features/files/filesSlice";

export const store = configureStore({
    reducer: {
      auth:authSlice,
      files:filesSlice
    },
    middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: false,
    }),
  });

  export default store;