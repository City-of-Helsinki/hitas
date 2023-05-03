import {Container, Footer, IconSignout, Navigation} from "hds-react";
import {ReactNode, useEffect, useState} from "react";
import {Outlet} from "react-router-dom";
import Notifications from "../common/components/Notifications";
import Spinner from "../common/components/Spinner";
import Unauthorized from "../common/components/Unauthorized";
import "../styles/index.sass";
import {selectIsAuthenticated, selectIsAuthenticating, setIsAuthenticated} from "./authSlice";
import {useAppDispatch, useAppSelector} from "./hooks";
import {useGetUserInfoQuery} from "./services";
import useAuthentication from "./useAuthentication";

interface AppProps {
    isContentProtected?: boolean;
    children?: ReactNode;
}

const App = ({isContentProtected = true, children}: AppProps): JSX.Element => {
    // Authentication
    const {data: userInfoData, isLoading: isUserInfoLoading} = useGetUserInfoQuery();
    const isAuthenticated = useAppSelector(selectIsAuthenticated);
    const isAuthenticating = useAppSelector(selectIsAuthenticating);
    const {signIn, logOut} = useAuthentication();
    const dispatch = useAppDispatch();
    const [userTitle, setUserTitle] = useState<string | number>(0);
    const token = process.env.REACT_APP_AUTH_TOKEN;

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
            }
        }
    }, [userInfoData, isUserInfoLoading, dispatch, token]);

    // Layout
    const NavItem = (item) => {
        return (
            <Navigation.Item
                href={"/" + item.path}
                label={item.label}
                className={item.className}
            />
        );
    };

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
                    <NavItem
                        label="Yhtiöt"
                        path="housing-companies"
                    />
                    <NavItem
                        label="Asunnot"
                        path="apartments"
                    />
                    <NavItem
                        label="Raportit"
                        path="reports"
                    />
                    <NavItem
                        label="Dokumentit"
                        path="documents"
                    />
                    <NavItem
                        label="Koodisto"
                        path="codes"
                    />
                    <NavItem
                        label="Toiminnot"
                        path="functions"
                    />
                </Navigation.Row>
            </Navigation>

            <Container className="main-content">
                {isContentProtected ? (
                    isAuthenticating ? (
                        <Spinner />
                    ) : isUserInfoLoading ? (
                        <></>
                    ) : isAuthenticated ? (
                        <Outlet />
                    ) : (
                        <Unauthorized />
                    )
                ) : (
                    children
                )}
            </Container>

            <Notifications />

            <Footer />
        </div>
    );
};

export default App;
