import {Tabs} from "hds-react";
import Heading from "../../common/components/Heading";
import {PriceCeilingPerSquare, ThirtyYearRegulation} from "./";

const Functions = () => {
    return (
        <div className="view--functions">
            <Heading>Järjestelmän toiminnot</Heading>
            <Tabs>
                <Tabs.TabList>
                    <Tabs.Tab>Rajaneliöhinnan laskenta</Tabs.Tab>
                    <Tabs.Tab>Vapautumisen tarkistus</Tabs.Tab>
                </Tabs.TabList>
                <Tabs.TabPanel>
                    <PriceCeilingPerSquare />
                </Tabs.TabPanel>
                <Tabs.TabPanel>
                    <ThirtyYearRegulation />
                </Tabs.TabPanel>
            </Tabs>
        </div>
    );
};

export default Functions;
