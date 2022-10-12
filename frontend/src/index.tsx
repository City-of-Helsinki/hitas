import React from "react";

import ReactDOM from "react-dom/client";
import {BrowserRouter} from "react-router-dom";

import Router from "./Router";
import ScrollToTop from "./common/components/ScrollToTop";

const root = ReactDOM.createRoot(document.getElementById("root") as HTMLElement);

root.render(
    <BrowserRouter>
        <ScrollToTop />
        <Router />
    </BrowserRouter>
);
