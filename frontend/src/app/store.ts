import {configureStore} from "@reduxjs/toolkit";
import {setupListeners} from "@reduxjs/toolkit/query";
import authReducer from "./authSlice";
import {authApi, hitasApi} from "./services";

export const store = configureStore({
    reducer: {
        [hitasApi.reducerPath]: hitasApi.reducer,
        [authApi.reducerPath]: authApi.reducer,
        auth: authReducer,
    },
    middleware: (getDefaultMiddleware) => getDefaultMiddleware().concat([hitasApi.middleware, authApi.middleware]),
});

setupListeners(store.dispatch);

export type AppDispatch = typeof store.dispatch;
export type RootState = ReturnType<typeof store.getState>;
