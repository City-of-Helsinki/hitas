import {useContext} from "react";

import {GenericImprovementsPage} from "../../common/components";
import {
    HousingCompanyViewContext,
    HousingCompanyViewContextProvider,
} from "./components/HousingCompanyViewContextProvider";

const LoadedHousingCompanyImprovementsPage = () => {
    const {housingCompany} = useContext(HousingCompanyViewContext);
    if (!housingCompany) throw new Error("Housing company not found");

    return <GenericImprovementsPage housingCompany={housingCompany} />;
};

const HousingCompanyImprovementsPage = () => {
    return (
        <HousingCompanyViewContextProvider viewClassName="view--create view--create-improvements">
            <LoadedHousingCompanyImprovementsPage />
        </HousingCompanyViewContextProvider>
    );
};

export default HousingCompanyImprovementsPage;
