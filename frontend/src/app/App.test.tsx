import {render, screen} from "@testing-library/react";

import {Provider} from "react-redux";
import App from "./App";
import {store} from "./store";

test("renders Asuntopalvelut heading", () => {
    render(
        <Provider store={store}>
            <App />
        </Provider>
    );
    const linkElement = screen.getAllByText(/Asuntopalvelut/i)[0];
    expect(linkElement).toBeInTheDocument();
});
