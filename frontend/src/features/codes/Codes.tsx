import React, {useState} from "react";

import {Tabs} from "hds-react";

import IndicesList from "./IndicesList";

const Codes = (): JSX.Element => {
    const [filterParams, setFilterParams] = useState({name: ""});
    return (
        <div className="view--codes">
            <h1 className="main-heading">Koodisto</h1>
            <Tabs>
                <Tabs.TabList>
                    <Tabs.Tab>Indeksit</Tabs.Tab>
                    <Tabs.Tab>Postinumerot</Tabs.Tab>
                    <Tabs.Tab>Laskentasäännöt</Tabs.Tab>
                    <Tabs.Tab>Rahoitusmuodot</Tabs.Tab>
                </Tabs.TabList>
                <Tabs.TabPanel className="view--codes__tab--indices">
                    <IndicesList
                        filterParams={filterParams}
                        setFilterParams={setFilterParams}
                    />
                </Tabs.TabPanel>
                <Tabs.TabPanel>
                    <h2>Postinumerot</h2>
                </Tabs.TabPanel>
                <Tabs.TabPanel>
                    <h2>Laskentasäännöt</h2>
                </Tabs.TabPanel>
                <Tabs.TabPanel>
                    <h2>Rahoitusmuodot</h2>
                </Tabs.TabPanel>
            </Tabs>
        </div>
    );
};

export default Codes;
