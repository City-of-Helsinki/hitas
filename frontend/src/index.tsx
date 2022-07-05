import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter, Route, Routes } from "react-router-dom";

import App from "./App";
import Apartments from "./pages/Apartments";
import Codes from "./pages/Codes";
import Companies from "./pages/Companies";
import Documents from "./pages/Documents";
import Reports from "./pages/Reports";

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
                    element={<Companies />}
                />
                <Route
                    path="asunnot"
                    element={<Apartments />}
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
    </BrowserRouter>
);
