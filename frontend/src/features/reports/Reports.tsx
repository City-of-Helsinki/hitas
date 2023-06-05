import {Tabs} from "hds-react";
import {Heading} from "../../common/components";
import SalesReports from "./SalesReports";

const Reports = () => {
    return (
        <div className="view--reports">
            <Heading>Raportit</Heading>
            <Tabs>
                <Tabs.TabList>
                    <Tabs.Tab>Kaupat</Tabs.Tab>
                    <Tabs.Tab>Raportit 2</Tabs.Tab>
                    <Tabs.Tab>Raportit 3</Tabs.Tab>
                    <Tabs.Tab>Raportit 4</Tabs.Tab>
                </Tabs.TabList>
                <Tabs.TabPanel>
                    <SalesReports />
                </Tabs.TabPanel>
                <Tabs.TabPanel>
                    <h2>Raportit 3</h2>
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
