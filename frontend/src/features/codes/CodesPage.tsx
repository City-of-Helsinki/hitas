import {Tabs} from "hds-react";
import React from "react";
import {Heading} from "../../common/components";
import {
    developerMutateFormProps,
    MutateForm,
    MutateSearchList,
    OwnerMutateForm,
    propertyManagerMutateFormProps,
} from "../../common/components/mutateComponents";
import {useGetDevelopersQuery, useGetOwnersQuery, useGetPropertyManagersQuery} from "../../common/services";
import IndicesTab from "./IndicesTab";

const CodesPage = (): React.JSX.Element => {
    return (
        <div className="view--codes">
            <Heading type="main">Koodisto</Heading>
            <Tabs>
                <Tabs.TabList>
                    <Tabs.Tab>Indeksit</Tabs.Tab>
                    <Tabs.Tab>Postinumerot</Tabs.Tab>
                    <Tabs.Tab>Rahoitusmuodot</Tabs.Tab>
                    <Tabs.Tab>Omistajat</Tabs.Tab>
                    <Tabs.Tab>Isännöitsijät</Tabs.Tab>
                    <Tabs.Tab>Rakennuttajat</Tabs.Tab>
                </Tabs.TabList>
                <Tabs.TabPanel className="view--codes__tab--indices">
                    <IndicesTab />
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
                        useGetQuery={useGetOwnersQuery}
                        emptyFilterParams={{name: "", identifier: ""}}
                        dialogTitles={{modify: "Muokkaa henkilötietoja"}}
                        MutateFormComponent={OwnerMutateForm}
                    />
                </Tabs.TabPanel>
                <Tabs.TabPanel className="view--codes__tab--property-managers">
                    <MutateSearchList
                        listFieldsWithTitles={{name: "Nimi", email: "Sähköpostiosoite"}}
                        useGetQuery={useGetPropertyManagersQuery}
                        emptyFilterParams={{name: "", email: ""}}
                        dialogTitles={{modify: "Muokkaa isännöitsijän tietoja", new: "Lisää isännöitsijä"}}
                        MutateFormComponent={MutateForm}
                        mutateFormProps={propertyManagerMutateFormProps}
                    />
                </Tabs.TabPanel>
                <Tabs.TabPanel className="view--codes__tab--developers">
                    <MutateSearchList
                        listFieldsWithTitles={{value: "Nimi"}}
                        useGetQuery={useGetDevelopersQuery}
                        emptyFilterParams={{value: ""}}
                        dialogTitles={{modify: "Muokkaa rakennuttajan tietoja", new: "Lisää rakennuttaja"}}
                        MutateFormComponent={MutateForm}
                        mutateFormProps={developerMutateFormProps}
                    />
                </Tabs.TabPanel>
            </Tabs>
        </div>
    );
};

export default CodesPage;
