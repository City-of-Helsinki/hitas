import {useContext} from "react";

import {GenericImprovementsPage} from "../../common/components/improvements";
import ApartmentViewContextProvider, {ApartmentViewContext} from "./components/ApartmentViewContextProvider";

const LoadedApartmentImprovementsPage = () => {
    const {housingCompany, apartment} = useContext(ApartmentViewContext);
    if (!apartment) throw new Error("Apartment not found");

    return (
        <GenericImprovementsPage
            housingCompany={housingCompany}
            apartment={apartment}
        />
    );
};

const ApartmentImprovementsPage = () => {
    return (
        <ApartmentViewContextProvider viewClassName="view--create view--create-improvements">
            <LoadedApartmentImprovementsPage />
        </ApartmentViewContextProvider>
    );
};
export default ApartmentImprovementsPage;
