import {useContext} from "react";

import {GenericDocumentsPage} from "../../common/components";
import {ApartmentViewContext, ApartmentViewContextProvider} from "./components/ApartmentViewContextProvider";

const LoadedApartmentDocumentsPage = () => {
    const {housingCompany, apartment} = useContext(ApartmentViewContext);
    if (!apartment) throw new Error("Apartment not found");

    return (
        <GenericDocumentsPage
            housingCompany={housingCompany}
            apartment={apartment}
        />
    );
};

const ApartmentDocumentsPage = () => {
    return (
        <ApartmentViewContextProvider viewClassName="view--create view--create-documents">
            <LoadedApartmentDocumentsPage />
        </ApartmentViewContextProvider>
    );
};
export default ApartmentDocumentsPage;
