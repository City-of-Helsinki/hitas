import {getLogOutUrl, getSignInUrl} from "../common/utils";
import {setIsAuthenticating} from "./authSlice";
import {useAppDispatch} from "./hooks";

export default function useAuthentication() {
    const dispatch = useAppDispatch();

    // Redirect the user to the sign in dialog and return to the current url after sign in
    const signIn = () => {
        dispatch(setIsAuthenticating(true));
        const currentUrl = window.location.href;
        window.location.href = getSignInUrl(currentUrl);
    };

    // Log the user out and redirect to route /logout
    const logOut = () => {
        dispatch(setIsAuthenticating(true));
        window.location.href = getLogOutUrl();
    };

    return {logOut, signIn};
}
