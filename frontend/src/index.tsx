import ReactDOM from "react-dom/client";
import {BrowserRouter} from "react-router-dom";

import ScrollToTop from "./common/components/ScrollToTop";
import Router from "./Router";

const root = ReactDOM.createRoot(document.getElementById("root") as HTMLElement);

root.render(
    <BrowserRouter>
        <ScrollToTop />
        <Router />
    </BrowserRouter>
);
