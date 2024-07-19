import {useContext} from "react";

import {GenericDocumentsPage} from "../../common/components";
import {
    HousingCompanyViewContext,
    HousingCompanyViewContextProvider,
} from "./components/HousingCompanyViewContextProvider";

const LoadedHousingCompanyDocumentsPage = () => {
    const {housingCompany} = useContext(HousingCompanyViewContext);
    if (!housingCompany) throw new Error("Housing company not found");

    return <GenericDocumentsPage housingCompany={housingCompany} />;
};

const HousingCompanyDocumentsPage = () => {
    return (
        <HousingCompanyViewContextProvider viewClassName="view--create view--create-documents">
            <LoadedHousingCompanyDocumentsPage />
        </HousingCompanyViewContextProvider>
    );
};

export default HousingCompanyDocumentsPage;
