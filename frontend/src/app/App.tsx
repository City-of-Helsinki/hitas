import {Container, Footer, Navigation} from "hds-react";
import {Outlet} from "react-router-dom";

import "../styles/index.sass";

function App() {
    const NavItem = (item) => {
        return (
            <Navigation.Item
                href={"/" + item.path}
                label={item.label}
                className={item.className}
            />
        );
    };
    return (
        <div className="App">
            <Navigation
                title="Asuntopalvelut"
                menuToggleAriaLabel=""
                skipTo=""
                skipToContentLabel=""
                titleUrl="/"
            >
                <Navigation.Row ariaLabel="Main navigation">
                    <NavItem
                        label="Yhtiöt"
                        path="housing-companies"
                    />
                    <NavItem
                        label="Asunnot"
                        path="apartments"
                    />
                    <NavItem
                        label="Raportit"
                        path="reports"
                    />
                    <NavItem
                        label="Dokumentit"
                        path="documents"
                    />
                    <NavItem
                        label="Koodisto"
                        path="codes"
                    />
                </Navigation.Row>
            </Navigation>

            <Container className="main-content">
                <Outlet />
            </Container>

            <Footer />
        </div>
    );
}

export default App;
