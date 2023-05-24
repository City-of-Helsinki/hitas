import {Tabs} from "hds-react";
import Heading from "../../common/components/Heading";
import {PriceCeilingPerSquare, ThirtyYearComparison} from "./";

const Functions = () => {
    return (
        <div className="view--functions">
            <Heading>Järjestelmän toiminnot</Heading>
            <Tabs>
                <Tabs.TabList>
                    <Tabs.Tab>Vapautumisen tarkistus</Tabs.Tab>
                    <Tabs.Tab>Rajaneliöhinnan laskenta</Tabs.Tab>
                </Tabs.TabList>
                <Tabs.TabPanel>
                    <ThirtyYearComparison />
                </Tabs.TabPanel>
                <Tabs.TabPanel>
                    <PriceCeilingPerSquare />
                </Tabs.TabPanel>
            </Tabs>
        </div>
    );
};

export default Functions;
