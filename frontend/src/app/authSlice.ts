import {createSlice, PayloadAction} from "@reduxjs/toolkit";
import {RootState} from "./store";

export interface IAuthState {
    isAuthenticated: boolean;
    isAuthenticating: boolean;
}
export const initialState: IAuthState = {
    isAuthenticated: false,
    isAuthenticating: false,
};

export const authSlice = createSlice({
    name: "auth",
    initialState,
    reducers: {
        setIsAuthenticated: (state, action: PayloadAction<boolean>) => {
            // set the new isAuthenticated value
            state.isAuthenticated = action.payload;
        },
        setIsAuthenticating: (state, action: PayloadAction<boolean>) => {
            // set the new isAuthenticating value
            state.isAuthenticating = action.payload;
        },
    },
});

export const {setIsAuthenticated, setIsAuthenticating} = authSlice.actions;
export const selectIsAuthenticated = (state: RootState) => state.auth.isAuthenticated;
export const selectIsAuthenticating = (state: RootState) => state.auth.isAuthenticating;
export default authSlice.reducer;
