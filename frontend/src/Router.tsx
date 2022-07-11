import React from "react";
import { Route, Routes } from "react-router-dom";

import App from "./App";
import Companies from "./pages/companies/Companies";
import Apartments from "./pages/apartments/Apartments";
import Reports from "./pages/Reports";
import Documents from "./pages/Documents";
import Codes from "./pages/Codes";
import Company from "./pages/companies/Company";
import Apartment from "./pages/apartments/Apartment";

export default function Router() {
    return (
        <Routes>
            <Route
                path="/"
                element={<App />}
            >
                <Route path="companies">
                    <Route
                        index
                        element={<Companies />}
                    />
                    <Route
                        path=":companyId"
                        element={<Company />}
                    />
                </Route>
                <Route path="asunnot">
                    <Route
                        index
                        element={<Apartments />}
                    />
                    <Route
                        path=":apartmentId"
                        element={<Apartment />}
                    />
                </Route>
                <Route
                    path="raportit"
                    element={<Reports />}
                />
                <Route
                    path="dokumentit"
                    element={<Documents />}
                />
                <Route
                    path="koodisto"
                    element={<Codes />}
                />
                <Route
                    index
                    element={<Companies />}
                />
                <Route
                    path="*"
                    element={
                        <main style={{ padding: "1rem" }}>
                            <h1>
                                Päädyit tyhjälle sivulle. Ole hyvä ja
                                tarkista osoite!
                            </h1>
                        </main>
                    }
                />
            </Route>
        </Routes>
    );
}
