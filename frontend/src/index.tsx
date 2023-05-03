import ReactDOM from "react-dom/client";
import {BrowserRouter} from "react-router-dom";

import {Provider} from "react-redux";
import {store} from "./app/store";
import ScrollToTop from "./common/components/ScrollToTop";
import Router from "./Router";

const root = ReactDOM.createRoot(document.getElementById("root") as HTMLElement);

root.render(
    <Provider store={store}>
        <BrowserRouter>
            <ScrollToTop />
            <Router />
        </BrowserRouter>
    </Provider>
);
