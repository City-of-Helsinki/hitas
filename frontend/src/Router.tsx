import {Provider} from "react-redux";
import {Navigate, Route, Routes} from "react-router-dom";

import App from "./app/App";
import {store} from "./app/store";
import {
    ApartmentConditionsOfSalePage,
    ApartmentCreatePage,
    ApartmentDetailsPage,
    ApartmentImprovementsPage,
    ApartmentListPage,
    ApartmentMaxPricePage,
    ApartmentNewSalePage,
} from "./features/apartment";
import {Codes} from "./features/codes";
import Documents from "./features/documents/Documents";
import {Functions} from "./features/functions";
import {
    HousingCompanyBuildingsPage,
    HousingCompanyCreatePage,
    HousingCompanyDetailsPage,
    HousingCompanyImprovementsPage,
    HousingCompanyListPage,
    HousingCompanyRealEstatesPage,
} from "./features/housingCompany";
import Reports from "./features/reports/Reports";

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
                            path="improvements"
                            element={<HousingCompanyImprovementsPage />}
                        />
                        <Route
                            path="real-estates"
                            element={<HousingCompanyRealEstatesPage />}
                        />
                        <Route
                            path="buildings"
                            element={<HousingCompanyBuildingsPage />}
                        />
                        <Route path="apartments">
                            <Route
                                index
                                element={<Navigate to=".." />}
                            />
                            <Route
                                path="create"
                                element={<ApartmentCreatePage />}
                            />
                            <Route path=":apartmentId">
                                <Route
                                    index
                                    element={<ApartmentDetailsPage />}
                                />
                                <Route
                                    path="edit"
                                    element={<ApartmentCreatePage />}
                                />
                                <Route
                                    path="improvements"
                                    element={<ApartmentImprovementsPage />}
                                />
                                <Route
                                    path="max-price"
                                    element={<ApartmentMaxPricePage />}
                                />
                                <Route
                                    path="sales"
                                    element={<ApartmentNewSalePage />}
                                />
                                <Route
                                    path="conditions-of-sale"
                                    element={<ApartmentConditionsOfSalePage />}
                                />
                            </Route>
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
                    path="functions"
                    element={<Functions />}
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
