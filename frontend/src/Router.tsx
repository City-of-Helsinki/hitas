import React from "react";

import {Navigate, Route, Routes} from "react-router-dom";

import App from "./App";
import Codes from "./pages/Codes";
import Documents from "./pages/Documents";
import Reports from "./pages/Reports";
import {ApartmentDetailsPage, ApartmentListPage} from "./pages/apartments";
import {HousingCompanyDetailsPage, HousingCompanyListPage} from "./pages/housingCompanies";

export default function Router() {
    return (
        <Routes>
            <Route
                path="/"
                element={<App />}
            >
                <Route path="housing-companies">
                    <Route
                        index
                        element={<HousingCompanyListPage />}
                    />
                    <Route
                        path=":housingCompanyId"
                        element={<HousingCompanyDetailsPage />}
                    />
                </Route>
                <Route path="apartments">
                    <Route
                        index
                        element={<ApartmentListPage />}
                    />
                    <Route
                        path=":apartmentId"
                        element={<ApartmentDetailsPage />}
                    />
                </Route>
                <Route
                    path="reports"
                    element={<Reports />}
                />
                <Route
                    path="documents"
                    element={<Documents />}
                />
                <Route
                    path="codes"
                    element={<Codes />}
                />
                <Route
                    index
                    element={<Navigate to="/housing-companies" />}
                />
                <Route
                    path="*"
                    element={
                        <main style={{padding: "1rem"}}>
                            <h1>Päädyit tyhjälle sivulle. Ole hyvä ja tarkista osoite!</h1>
                        </main>
                    }
                />
            </Route>
        </Routes>
    );
}
