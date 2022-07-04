import React from "react";
import { Route, Routes } from "react-router-dom";

import { Container, Footer, Navigation } from "hds-react";

import CompanyListing from "./pages/CompanyListing";
import Apartmentslisting from "./pages/ApartmentsListing";
import Reports from "./pages/Reports";
import Documents from "./pages/Documents";
import Codes from "./pages/Codes";

import "./styles/index.sass";

function App(children) {
    return (
        <div className="App">
            <Navigation
                title="Asuntopalvelut"
                menuToggleAriaLabel=""
                skipTo=""
                skipToContentLabel=""
            >
                <Navigation.Row ariaLabel="Main navigation">
                    <Navigation.Item
                        href="/yhtiot/"
                        label="Yhtiöt"
                    />
                    <Navigation.Item
                        href="/asunnot/"
                        label="Asunnot"
                    />
                    <Navigation.Item
                        href="/raportit/"
                        label="Raportit"
                    />
                    <Navigation.Item
                        href="/dokumentit/"
                        label="Dokumentit"
                    />
                    <Navigation.Item
                        href="/koodisto/"
                        label="Koodisto"
                    />
                </Navigation.Row>
            </Navigation>

            <Container className="main-content">
                <Routes>
                    <Route
                        path="yhtiot/"
                        element={<CompanyListing />}
                    />
                    <Route
                        path="asunnot/"
                        element={<Apartmentslisting />}
                    />
                    <Route
                        path="raportit/"
                        element={<Reports />}
                    />
                    <Route
                        path="dokumentit/"
                        element={<Documents />}
                    />
                    <Route
                        path="koodisto/"
                        element={<Codes />}
                    />
                </Routes>
            </Container>

            <Footer />
        </div>
    );
}

export default App;
