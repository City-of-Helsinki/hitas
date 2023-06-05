import {Tabs} from "hds-react";
import {Heading} from "../../common/components";
import HousingCompanyReports from "./HousingCompanyReports";
import SalesReports from "./SalesReports";

const Reports = () => {
    return (
        <div className="view--reports">
            <Heading>Raportit</Heading>
            <Tabs>
                <Tabs.TabList>
                    <Tabs.Tab>Taloyhtiön raportit</Tabs.Tab>
                    <Tabs.Tab>Toteutuneet kauppahinnat</Tabs.Tab>
                    <Tabs.Tab>Rajahintalaskelmat</Tabs.Tab>
                    <Tabs.Tab>Enimmäishintojen vertailu</Tabs.Tab>
                </Tabs.TabList>
                <Tabs.TabPanel>
                    <HousingCompanyReports />
                </Tabs.TabPanel>
                <Tabs.TabPanel>
                    <SalesReports />
                </Tabs.TabPanel>
                <Tabs.TabPanel>
                    <h2>Raportit 3</h2>
                </Tabs.TabPanel>
                <Tabs.TabPanel>
                    <h2>Raportit 4</h2>
                </Tabs.TabPanel>
            </Tabs>
        </div>
    );
};

export default Reports;
