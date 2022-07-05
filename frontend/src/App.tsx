import { Container, Footer, Navigation } from "hds-react";
import { Outlet } from "react-router-dom";

import "./styles/index.sass";

function App() {
    // Function for formatting the NavItem titles into label texts
    const formatStr = (str: string): string => {
        if (str === null) return "";
        const strArray =
            str && str === "companies" // make yhtiot (for url) into yhtiöt, for the label string
                ? "yhtiöt".split("")
                : str.split("");
        // eslint-disable-next-line @typescript-eslint/ban-ts-comment
        // @ts-ignore
        const firstLetter = strArray.shift().toUpperCase();
        return firstLetter + strArray.join("");
    };
    const NavItem = (item) => {
        return (
            <Navigation.Item
                href={"/" + item.title}
                label={formatStr(item.title)}
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
            >
                <Navigation.Row ariaLabel="Main navigation">
                    <NavItem title="companies" />
                    <NavItem title="asunnot" />
                    <NavItem title="raportit" />
                    <NavItem title="dokumentit" />
                    <NavItem title="koodisto" />
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
