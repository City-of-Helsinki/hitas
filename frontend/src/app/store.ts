import {configureStore} from "@reduxjs/toolkit";
import {setupListeners} from "@reduxjs/toolkit/query";

import {hitasApi} from "./services";

export const store = configureStore({
    reducer: {
        [hitasApi.reducerPath]: hitasApi.reducer,
    },
    middleware: (getDefaultMiddleware) => getDefaultMiddleware().concat(hitasApi.middleware),
});

setupListeners(store.dispatch);

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
