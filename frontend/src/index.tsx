import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter, Route, Routes } from "react-router-dom";

import App from "./App";
import CompanyListing from "./pages/CompanyListing";
import Apartmentslisting from "./pages/ApartmentsListing";
import Reports from "./pages/Reports";
import Documents from "./pages/Documents";
import Codes from "./pages/Codes";

const root = ReactDOM.createRoot(
    document.getElementById("root") as HTMLElement
);

root.render(
    <BrowserRouter>
        <Routes>
            <Route
                path="/"
                element={<App />}
            >
                <Route
                    path="yhtiot"
                    element={<CompanyListing />}
                />
                <Route
                    path="asunnot"
                    element={<Apartmentslisting />}
                />
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
        <App />
    </BrowserRouter>
);
