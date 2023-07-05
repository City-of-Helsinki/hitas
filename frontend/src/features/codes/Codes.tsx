import {Tabs} from "hds-react";
import {useGetDevelopersQuery, useGetOwnersQuery, useGetPropertyManagersQuery} from "../../app/services";
import {MutateForm, MutateSearchList, OwnerMutateForm} from "../../common/components";
import {
    developerMutateFormProps,
    propertyManagerMutateFormProps,
} from "../../common/components/mutateComponents/mutateFormProps";
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
                    <Tabs.Tab>Rakennuttajat</Tabs.Tab>
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

export default Codes;
