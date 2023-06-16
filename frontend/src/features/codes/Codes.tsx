import {Tabs} from "hds-react";
import {useGetOwnersQuery, useGetPropertyManagersQuery} from "../../app/services";
import {ManagerMutateForm, MutateSearchList, OwnerMutateForm} from "../../common/components";
import {IndicesList} from "./";

const Codes = (): JSX.Element => {
    return (
        <div className="view--codes">
            <h1 className="main-heading">Koodisto</h1>
            <Tabs>
                <Tabs.TabList>
                    <Tabs.Tab>Indeksit</Tabs.Tab>
                    <Tabs.Tab>Postinumerot</Tabs.Tab>
                    <Tabs.Tab>Rahoitusmuodot</Tabs.Tab>
                    <Tabs.Tab>Omistajat</Tabs.Tab>
                    <Tabs.Tab>Isännöitsijät</Tabs.Tab>
                </Tabs.TabList>
                <Tabs.TabPanel className="view--codes__tab--indices">
                    <IndicesList />
                </Tabs.TabPanel>
                <Tabs.TabPanel className="view--codes__tab--postalcodes">
                    <h1>Postinumerot</h1>
                </Tabs.TabPanel>
                <Tabs.TabPanel className="view--codes__tab--financing-methods">
                    <h1>Rahoitusmuodot</h1>
                </Tabs.TabPanel>
                <Tabs.TabPanel className="view--codes__tab--owners">
                    <MutateSearchList
                        listFieldsWithTitles={{name: "Nimi", identifier: "Henkilö- tai Y-tunnus"}}
                        searchStringMinLength={2}
                        resultListMaxRows={12}
                        useGetQuery={useGetOwnersQuery}
                        MutateFormComponent={OwnerMutateForm}
                        defaultFilterParams={{name: "", identifier: ""}}
                        dialogTitles={{modify: "Muokkaa henkilötietoja"}}
                    />
                </Tabs.TabPanel>
                <Tabs.TabPanel className="view--codes__tab--managers">
                    <MutateSearchList
                        listFieldsWithTitles={{name: "Nimi", email: "Sähköpostiosoite"}}
                        searchStringMinLength={2}
                        resultListMaxRows={12}
                        useGetQuery={useGetPropertyManagersQuery}
                        MutateFormComponent={ManagerMutateForm}
                        defaultFilterParams={{name: "", email: ""}}
                        dialogTitles={{modify: "Muokkaa isännöitsijän tietoja", new: "Lisää isännöitsijä"}}
                    />
                </Tabs.TabPanel>
            </Tabs>
        </div>
    );
};

export default Codes;
