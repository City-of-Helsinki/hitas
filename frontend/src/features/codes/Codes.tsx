import {Tabs} from "hds-react";
import {
    useGetDevelopersQuery,
    useGetOwnersQuery,
    useGetPropertyManagersQuery,
    useSaveDeveloperMutation,
    useSavePropertyManagerMutation,
} from "../../app/services";
import {MutateForm, MutateSearchList, OwnerMutateForm} from "../../common/components";
import {DeveloperSchema, PropertyManagerSchema} from "../../common/schemas";
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
                        searchStringMinLength={2}
                        resultListMaxRows={12}
                        useGetQuery={useGetOwnersQuery}
                        MutateFormComponent={OwnerMutateForm}
                        emptyFilterParams={{name: "", identifier: ""}}
                        dialogTitles={{modify: "Muokkaa henkilötietoja"}}
                    />
                </Tabs.TabPanel>
                <Tabs.TabPanel className="view--codes__tab--property-managers">
                    <MutateSearchList
                        listFieldsWithTitles={{name: "Nimi", email: "Sähköpostiosoite"}}
                        searchStringMinLength={2}
                        resultListMaxRows={12}
                        useGetQuery={useGetPropertyManagersQuery}
                        MutateFormComponent={MutateForm}
                        emptyFilterParams={{name: "", email: ""}}
                        dialogTitles={{modify: "Muokkaa isännöitsijän tietoja", new: "Lisää isännöitsijä"}}
                        formObjectSchema={PropertyManagerSchema}
                        useSaveMutation={useSavePropertyManagerMutation}
                        successMessage="Isännöitsijän tiedot tallennettu onnistuneesti!"
                        errorMessage="Virhe isännöitsijän tietojen tallentamisessa!"
                        notModifiedMessage="Ei muutoksia isännöitsijän tiedoissa."
                        defaultFocusFieldName="name"
                        formFieldsWithTitles={{name: "Nimi", email: "Sähköpostiosoite"}}
                        requiredFields={["name"]}
                    />
                </Tabs.TabPanel>
                <Tabs.TabPanel className="view--codes__tab--developers">
                    <MutateSearchList
                        listFieldsWithTitles={{value: "Nimi"}}
                        searchStringMinLength={2}
                        resultListMaxRows={12}
                        useGetQuery={useGetDevelopersQuery}
                        MutateFormComponent={MutateForm}
                        emptyFilterParams={{value: ""}}
                        dialogTitles={{modify: "Muokkaa rakennuttajan tietoja", new: "Lisää rakennuttaja"}}
                        formObjectSchema={DeveloperSchema}
                        useSaveMutation={useSaveDeveloperMutation}
                        successMessage="Rakennuttajan tiedot tallennettu onnistuneesti!"
                        errorMessage="Virhe rakennuttajan tietojen tallentamisessa!"
                        notModifiedMessage="Ei muutoksia rakennuttajan tiedoissa."
                        defaultFocusFieldName="value"
                        formFieldsWithTitles={{value: "Nimi", description: "Kuvaus", code: "Koodi"}}
                        requiredFields={["value", "description", "code"]}
                    />
                </Tabs.TabPanel>
            </Tabs>
        </div>
    );
};

export default Codes;
