import React from "react";

import {Provider} from "react-redux";
import {Navigate, Route, Routes} from "react-router-dom";

import App from "./app/App";
import {store} from "./app/store";
import Codes from "./features/Codes";
import Documents from "./features/Documents";
import Reports from "./features/Reports";
import {ApartmentCreatePage, ApartmentDetailsPage, ApartmentListPage} from "./features/apartment";
import {
    BuildingsCreatePage,
    HousingCompanyCreatePage,
    HousingCompanyDetailsPage,
    HousingCompanyListPage,
    RealEstatesCreatePage,
} from "./features/housingCompany";

export default function Router() {
    return (
        <Routes>
            <Route
                path="/"
                element={
                    <Provider store={store}>
                        <App />
                    </Provider>
                }
            >
                <Route path="housing-companies">
                    <Route
                        index
                        element={<HousingCompanyListPage />}
                    />
                    <Route
                        path="create"
                        element={<HousingCompanyCreatePage />}
                    />
                    <Route path=":housingCompanyId">
                        <Route
                            index
                            element={<HousingCompanyDetailsPage />}
                        />
                        <Route
                            path="edit"
                            element={<HousingCompanyCreatePage />}
                        />
                        <Route
                            path="real-estates"
                            element={<RealEstatesCreatePage />}
                        />
                        <Route
                            path="buildings"
                            element={<BuildingsCreatePage />}
                        />
                        <Route path={"apartments"}>
                            <Route
                                index
                                element={<HousingCompanyDetailsPage />}
                            />
                            <Route
                                path={"create"}
                                element={<ApartmentCreatePage />}
                            />
                            <Route
                                path=":apartmentId"
                                element={<ApartmentDetailsPage />}
                            />
                        </Route>
                    </Route>
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
