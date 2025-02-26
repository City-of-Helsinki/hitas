import {FetchBaseQueryError} from "@reduxjs/toolkit/query";
import {Container, Footer, Logo, logoFi, Header, IconUser, IconSignin, LogoSize} from "hds-react";
import React, {useEffect, useState} from "react";
import {NavLink, Outlet, useMatch} from "react-router-dom";
import {Notifications} from "../common/components";
import {useGetUserInfoQuery} from "../common/services";
import {hdsToast} from "../common/utils";
import "../styles/index.sass";
import {selectIsAuthenticated, selectIsAuthenticating, setIsAuthenticated} from "./authSlice";
import {Spinner} from "./components/Spinner";
import {useAppDispatch, useAppSelector} from "./hooks";
import useAuthentication from "./useAuthentication";

const App = (): React.JSX.Element => {
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

    // Get the current environment from the url
    const getEnvironment = () => {
        const url = window.location.href;
        const domain = url.split("/")[2];
        let environmentName = domain.split(":")[0] === "localhost" ? "local" : domain.split(".")[1];
        switch (environmentName) {
            case "stage":
                environmentName = "staging";
                break;
            case "dev":
                environmentName = "development";
                break;
        }
        const hasDevelopmentBanner =
            environmentName === "local" ||
            environmentName === "development" ||
            environmentName === "test" ||
            environmentName === "staging";
        return {name: environmentName, hasDevelopmentBanner: hasDevelopmentBanner};
    };
    const environment = getEnvironment();

    // Check the authentication and get the username
    useEffect(() => {
        // UserInfo endpoint should not be called when using token authentication in development
        if (token) {
            dispatch(setIsAuthenticated(true));
            return;
        }

        if (userInfoData) {
            // Set the user title if name or email is available
            const userName = [userInfoData.first_name, userInfoData.last_name].join(" ").trim();
            setUserTitle(userName || userInfoData.email || "tuntematon");
            dispatch(setIsAuthenticated(true));
        } else {
            dispatch(setIsAuthenticated(false));

            // Error 401 is returned when the user is not authenticated
            // Error 403 is returned when the user is authenticated but does not have access
            if ((userInfoError as FetchBaseQueryError | undefined)?.status === 403) {
                hdsToast.error("Kirjautuminen onnistui, mutta sinulla on puutteelliset oikeudet!");
            }
        }
    }, [userInfoData, userInfoError, dispatch, token]);

    // Layout
    return (
        <div className="app-container">
            {environment.hasDevelopmentBanner && <div className="development-banner">{environment.name}</div>}
            <div className="App">
                <Header>
                    <Header.ActionBar
                        title="Asumisen palvelut"
                        frontPageLabel=""
                        titleAriaLabel=""
                        titleHref="/"
                        logo={
                            <Logo
                                src={logoFi}
                                alt="Helsingin kaupunki"
                            />
                        }
                        logoAriaLabel="Helsingin kaupunki"
                        logoHref="/"
                        openFrontPageLinksAriaLabel="Avaa Etusivun linkkivalikko"
                    >
                        {!isUserInfoLoading && !token && (
                            <Header.ActionBarItem
                                fixedRightPosition
                                label={isAuthenticated && userTitle ? `${userTitle}` : "Kirjaudu sisään"}
                                icon={isAuthenticated ? <IconUser /> : <IconSignin />}
                                onClick={isAuthenticated ? () => {} : signIn}
                                id="action-bar-login"
                            >
                                {isAuthenticated ? (
                                    <Header.ActionBarItem
                                        label="Kirjaudu ulos"
                                        closeLabel=""
                                        onClick={logOut}
                                        id="action-bar-logout"
                                    />
                                ) : null}
                            </Header.ActionBarItem>
                        )}
                    </Header.ActionBar>

                    <Header.NavigationMenu>
                        <Header.Link
                            as={NavLink}
                            to="housing-companies"
                            label="Yhtiöt"
                            active={!!useMatch("/housing-companies/*")}
                        />
                        <Header.Link
                            as={NavLink}
                            to="apartments"
                            label="Asunnot"
                            active={!!useMatch("/apartments/*")}
                        />
                        <Header.Link
                            as={NavLink}
                            to="codes"
                            label="Koodisto"
                            active={!!useMatch("/codes/*")}
                        />
                        <Header.Link
                            as={NavLink}
                            to="documents"
                            label="Dokumenttipohjat"
                            active={!!useMatch("/documents/*")}
                        />
                        <Header.Link
                            as={NavLink}
                            to="reports"
                            label="Raportit"
                            active={!!useMatch("/reports/*")}
                        />
                        <Header.Link
                            as={NavLink}
                            to="functions"
                            label="Toiminnot"
                            active={!!useMatch("/functions/*")}
                        />
                    </Header.NavigationMenu>
                </Header>

                <Container className="main-content">
                    {isAuthenticating || isUserInfoLoading ? <Spinner /> : <Outlet />}
                </Container>

                <Notifications />

                <Footer title="Asumisen palvelut">
                    <Footer.Base
                        backToTopLabel="Takaisin ylös"
                        logo={
                            <Logo
                                src={logoFi}
                                size={LogoSize.Medium}
                                alt="Helsingin kaupunki"
                            />
                        }
                    />
                </Footer>
            </div>
        </div>
    );
};

export default App;
