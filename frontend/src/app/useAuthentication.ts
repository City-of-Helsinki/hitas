import {useEffect, useState} from "react";
import {getLogOutUrl, getSignInUrl} from "../common/utils";
import {setIsAuthenticating} from "./authSlice";
import {useAppDispatch} from "./hooks";

export default function useAuthentication() {
    const dispatch = useAppDispatch();
    const [currentUrl, setCurrentUrl] = useState<string>("");

    // Redirect the user to the sign in dialog and return to the current url after sign in
    const signIn = () => {
        dispatch(setIsAuthenticating(true));
        window.location.href = getSignInUrl(currentUrl);
    };

    // Log the user out and redirect to route /logout
    const logOut = () => {
        dispatch(setIsAuthenticating(true));
        window.location.href = getLogOutUrl();
    };

    useEffect(() => {
        setCurrentUrl(window.location.href);
    }, []);

    return {logOut, signIn};
}
