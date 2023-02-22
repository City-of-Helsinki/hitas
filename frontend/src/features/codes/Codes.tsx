import {Tabs} from "hds-react";

import IndicesList from "./IndicesList";

const Codes = (): JSX.Element => {
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
                    <IndicesList />
                </Tabs.TabPanel>
                <Tabs.TabPanel className="view--codes__tab--postalcodes">
                    <h1>Postinumerot</h1>
                </Tabs.TabPanel>
                <Tabs.TabPanel className="view--codes__tab--rules">
                    <h1>Laskentasäännöt</h1>
                </Tabs.TabPanel>
                <Tabs.TabPanel className="view--codes__tab--financing-methods">
                    <h1>Rahoitusmuodot</h1>
                </Tabs.TabPanel>
            </Tabs>
        </div>
    );
};

export default Codes;
