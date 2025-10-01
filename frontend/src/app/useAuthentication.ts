import {getCookie} from "typescript-cookie";
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

        // Django logout must be a POST request with CSRF token
        const form = document.createElement("form");
        form.method = "POST";
        form.action = getLogOutUrl();

        const input = document.createElement("input");
        input.type = "hidden";
        input.name = "csrfmiddlewaretoken";
        input.value = getCookie("csrftoken") || "";
        form.appendChild(input);

        document.body.appendChild(form);
        form.submit();
        form.remove();
    };

    return {logOut, signIn};
}
