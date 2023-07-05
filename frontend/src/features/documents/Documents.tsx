import {Tab, TabList, TabPanel, Tabs} from "hds-react";
import {Heading} from "../../common/components";
import ManageEmailTemplates from "./ManageEmailTemplates";
import ManagePDFTemplates from "./ManagePDFTemplates";

const Documents = () => {
    return (
        <div className="view--documents">
            <Heading type="main">Dokumenttipohjat</Heading>
            <Tabs>
                <TabList>
                    <Tab>PDF-pohjat</Tab>
                    <Tab>Sähköpostipohjat</Tab>
                </TabList>
                <TabPanel>
                    <h2>Ladattavien PDF-tiedostojen leipätekstit</h2>
                    <ManagePDFTemplates />
                </TabPanel>
                <TabPanel>
                    <h2>Sähköpostipohjat</h2>
                    <ManageEmailTemplates />
                </TabPanel>
            </Tabs>
        </div>
    );
};

export default Documents;
