import {Tab, TabList, TabPanel, Tabs} from "hds-react";
import ManageEmailTemplates from "./ManageEmailTemplates";
import ManagePDFTemplates from "./ManagePDFTemplates";

const Documents = () => {
    return (
        <div className="view--documents">
            <h1 className="main-heading">Dokumentit</h1>
            <Tabs>
                <TabList>
                    <Tab>PDF pohjat</Tab>
                    <Tab>Sähköpostipohjat</Tab>
                </TabList>
                <TabPanel>
                    <ManagePDFTemplates />
                </TabPanel>
                <TabPanel>
                    <ManageEmailTemplates />
                </TabPanel>
            </Tabs>
        </div>
    );
};

export default Documents;
