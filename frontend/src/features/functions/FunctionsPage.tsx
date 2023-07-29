import {Tabs} from "hds-react";
import {Heading} from "../../common/components";
import {SurfaceAreaPriceCeilingTab, ThirtyYearRegulation} from "./";

// FIXME: DO NOT COMMIT THIS FILE TO GIT

const FunctionsPage = () => {
    return (
        <div className="view--functions">
            <Heading>Järjestelmän toiminnot</Heading>
            <Tabs>
                <Tabs.TabList>
                    <Tabs.Tab>Vapautumisen tarkistus</Tabs.Tab>
                    <Tabs.Tab>Rajaneliöhinnan laskenta</Tabs.Tab>
                </Tabs.TabList>
                <Tabs.TabPanel>
                    <ThirtyYearRegulation />
                </Tabs.TabPanel>
                <Tabs.TabPanel>
                    <SurfaceAreaPriceCeilingTab />
                </Tabs.TabPanel>
            </Tabs>
        </div>
    );
};

export default FunctionsPage;
