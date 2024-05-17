import {render, screen} from "@testing-library/react";

import {Provider} from "react-redux";
import App from "./App";
import {store} from "./store";

test("renders Asumisen palvelut heading", () => {
    render(
        <Provider store={store}>
            <App />
        </Provider>
    );
    const linkElement = screen.getAllByText(/Asumisen palvelut/i)[0];
    expect(linkElement).toBeInTheDocument();
});
