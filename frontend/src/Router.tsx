import React from "react";
import {Navigate, Route, Routes} from "react-router-dom";
import App from "./app/App";
import {selectIsAuthenticated} from "./app/authSlice";
import {useAppSelector} from "./app/hooks";
import {Logout, Unauthorized} from "./common/components/authentication";
import {
    ApartmentConditionsOfSalePage,
    ApartmentCreatePage,
    ApartmentDetailsPage,
    ApartmentDocumentsPage,
    ApartmentImprovementsPage,
    ApartmentListPage,
    ApartmentMaxPricePage,
    ApartmentSalePage,
} from "./features/apartment";
import CodesPage from "./features/codes";
import {Templates} from "./features/documentTemplates";
import {FunctionsPage} from "./features/functions";
import {
    HousingCompanyBuildingsPage,
    HousingCompanyCreatePage,
    HousingCompanyDetailsPage,
    HousingCompanyDocumentsPage,
    HousingCompanyImprovementsPage,
    HousingCompanyListPage,
    HousingCompanyRealEstatesPage,
} from "./features/housingCompany";
import ReportsPage from "./features/reports";

export default function Router() {
    const isAuthenticated = useAppSelector(selectIsAuthenticated);

    // Use this function to protect routes that require authentication
    const protect = (element: React.JSX.Element) => {
        return isAuthenticated ? element : <Unauthorized />;
    };

    return (
        <Routes>
            <Route
                path="/"
                element={<App />}
            >
                <Route path="housing-companies">
                    <Route
                        index
                        element={protect(<HousingCompanyListPage />)}
                    />
                    <Route
                        path="create"
                        element={protect(<HousingCompanyCreatePage />)}
                    />
                    <Route path=":housingCompanyId">
                        <Route
                            index
                            element={protect(<HousingCompanyDetailsPage />)}
                        />
                        <Route
                            path="edit"
                            element={protect(<HousingCompanyCreatePage />)}
                        />
                        <Route
                            path="improvements"
                            element={protect(<HousingCompanyImprovementsPage />)}
                        />
                        <Route
                            path="real-estates"
                            element={protect(<HousingCompanyRealEstatesPage />)}
                        />
                        <Route
                            path="buildings"
                            element={protect(<HousingCompanyBuildingsPage />)}
                        />
                        <Route
                            path="documents"
                            element={protect(<HousingCompanyDocumentsPage />)}
                        />
                        <Route path="apartments">
                            <Route
                                index
                                element={protect(<Navigate to=".." />)}
                            />
                            <Route
                                path="create"
                                element={protect(<ApartmentCreatePage />)}
                            />
                            <Route path=":apartmentId">
                                <Route
                                    index
                                    element={protect(<ApartmentDetailsPage />)}
                                />
                                <Route
                                    path="edit"
                                    element={protect(<ApartmentCreatePage />)}
                                />
                                <Route
                                    path="improvements"
                                    element={protect(<ApartmentImprovementsPage />)}
                                />
                                <Route
                                    path="max-price"
                                    element={protect(<ApartmentMaxPricePage />)}
                                />
                                <Route
                                    path="sales"
                                    element={protect(<ApartmentSalePage />)}
                                />
                                <Route
                                    path="conditions-of-sale"
                                    element={protect(<ApartmentConditionsOfSalePage />)}
                                />
                                <Route
                                    path="documents"
                                    element={protect(<ApartmentDocumentsPage />)}
                                />
                            </Route>
                        </Route>
                    </Route>
                </Route>
                <Route path="apartments">
                    <Route
                        index
                        element={protect(<ApartmentListPage />)}
                    />
                    <Route
                        path=":apartmentId"
                        element={protect(<ApartmentDetailsPage />)}
                    />
                </Route>
                <Route
                    path="codes"
                    element={protect(<CodesPage />)}
                />
                <Route
                    path="documents"
                    element={protect(<Templates />)}
                />
                <Route
                    path="reports"
                    element={protect(<ReportsPage />)}
                />
                <Route
                    path="functions"
                    element={protect(<FunctionsPage />)}
                />
                <Route
                    path="logout"
                    element={isAuthenticated ? <></> : <Logout />}
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
