import {FetchBaseQueryError} from "@reduxjs/toolkit/query";
import {Container, Footer, IconSignout, Navigation} from "hds-react";
import {useEffect, useState} from "react";
import {Link, Outlet} from "react-router-dom";
import Notifications from "../common/components/Notifications";
import Spinner from "../common/components/Spinner";
import {hitasToast} from "../common/utils";
import "../styles/index.sass";
import {selectIsAuthenticated, selectIsAuthenticating, setIsAuthenticated} from "./authSlice";
import {useAppDispatch, useAppSelector} from "./hooks";
import {useGetUserInfoQuery} from "./services";
import useAuthentication from "./useAuthentication";

const App = (): JSX.Element => {
    // Authentication
    const token = process.env.REACT_APP_AUTH_TOKEN;
    const {
        currentData: userInfoData,
        isFetching: isUserInfoLoading,
        error: userInfoError,
    } = useGetUserInfoQuery(null, {skip: !!token});
    const isAuthenticated = useAppSelector(selectIsAuthenticated);
    const isAuthenticating = useAppSelector(selectIsAuthenticating);
    const {signIn, logOut} = useAuthentication();
    const [userTitle, setUserTitle] = useState<string | number>(0);
    const dispatch = useAppDispatch();

    // Check the authentication and get the user name
    useEffect(() => {
        // userinfo endpoint is not called when using token authentication in development mode
        if (token) {
            dispatch(setIsAuthenticated(true));
        } else {
            if (userInfoData) {
                // Set the user title if name or email is available
                const userFirstName = userInfoData.first_name ? `${userInfoData.first_name} ` : "";
                const userName =
                    userInfoData.first_name || userInfoData.last_name ? userFirstName + userInfoData.last_name : "";
                const userEmail = userInfoData.email || "";
                setUserTitle(userName || userEmail);
                // Set the user as authenticated if user info data fetch was successful
                dispatch(setIsAuthenticated(true));
            } else {
                // Set the user as unauthenticated if user info data fetch was not successful
                dispatch(setIsAuthenticated(false));

                // Error 401 is returned when the user is not authenticated
                // Error 403 is returned when the user is authenticated but does not have access
                if ((userInfoError as FetchBaseQueryError | undefined)?.status === 403) {
                    hitasToast("Kirjautuminen onnistui, mutta sinulla on puutteelliset oikeudet!", "error");
                }
            }
        }
    }, [userInfoData, userInfoError, dispatch, token]);

    // Layout
    return (
        <div className="App">
            <Navigation
                title="Asuntopalvelut"
                menuToggleAriaLabel=""
                skipTo=""
                skipToContentLabel=""
                titleUrl="/"
            >
                {!isUserInfoLoading && !token && (
                    <Navigation.Actions>
                        <Navigation.User
                            authenticated={isAuthenticated && userTitle !== 0}
                            buttonAriaLabel={`Käyttäjä ${userTitle}`}
                            label="Kirjaudu sisään"
                            onSignIn={signIn}
                            userName={userTitle}
                        >
                            <Navigation.Item
                                onClick={logOut}
                                variant="supplementary"
                                label="Kirjaudu ulos"
                                icon={<IconSignout aria-hidden />}
                            />
                        </Navigation.User>
                    </Navigation.Actions>
                )}
                <Navigation.Row ariaLabel="Main navigation">
                    <Link to="housing-companies">Yhtiöt</Link>
                    <Link to="apartments">Asunnot</Link>
                    <Link to="reports">Raportit</Link>
                    <Link to="documents">Dokumentit</Link>
                    <Link to="codes">Koodisto</Link>
                    <Link to="functions">Toiminnot</Link>
                </Navigation.Row>
            </Navigation>

            <Container className="main-content">
                {isAuthenticating ? <Spinner /> : isUserInfoLoading ? <></> : <Outlet />}
            </Container>

            <Notifications />

            <Footer />
        </div>
    );
};

export default App;
