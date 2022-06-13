import React from "react";

import { Navigation, Container } from "hds-react";

import "./App.sass";

function App() {
    return (
        <div className="App">
            <Navigation
                title="Hitas"
                menuToggleAriaLabel=""
                skipTo=""
                skipToContentLabel=""
            >
                <Navigation.Row ariaLabel="Main navigation">
                    <Navigation.Item
                        href="#"
                        label="Link"
                        active
                        onClick={(e) => e.preventDefault()}
                    />
                    <Navigation.Item
                        href="#"
                        label="Link"
                        onClick={(e) => e.preventDefault()}
                    />
                    <Navigation.Item
                        href="#"
                        label="Link"
                        onClick={(e) => e.preventDefault()}
                    />
                    <Navigation.Item
                        href="#"
                        label="Link"
                        onClick={(e) => e.preventDefault()}
                    />
                    <Navigation.Dropdown label="Dropdown">
                        <Navigation.Item
                            href="#"
                            label="Link"
                            onClick={(e) => e.preventDefault()}
                        />
                        <Navigation.Item
                            href="#"
                            label="Link"
                            onClick={(e) => e.preventDefault()}
                        />
                        <Navigation.Item
                            href="#"
                            label="Link"
                            onClick={(e) => e.preventDefault()}
                        />
                        <Navigation.Item
                            href="#"
                            label="Link"
                            onClick={(e) => e.preventDefault()}
                        />
                    </Navigation.Dropdown>
                </Navigation.Row>
            </Navigation>
            <Container className={"App"}>
                <h1>Hitas</h1>
                <p>
                    Lorem ipsum dolor sit amet, consectetur adipisicing elit. Ad
                    deserunt dolorem eaque esse facilis fugiat fugit illo modi
                    molestias neque nobis perspiciatis possimus ratione,
                    recusandae, repudiandae saepe sapiente.
                </p>
            </Container>
        </div>
    );
}

export default App;
