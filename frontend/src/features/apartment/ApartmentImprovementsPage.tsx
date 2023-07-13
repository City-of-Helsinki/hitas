import {useContext} from "react";

import {NavigateBackButton} from "../../common/components";
import {GenericImprovementsPage} from "../../common/components/improvements";
import ApartmentViewContextProvider, {ApartmentViewContext} from "./components/ApartmentViewContextProvider";

const LoadedApartmentImprovementsPage = () => {
    const {housingCompany, apartment} = useContext(ApartmentViewContext);
    if (!apartment) throw new Error("Apartment not found");

    // New Hitas apartments don't have any improvements so display an 'error' message if user somehow ended up here
    if (
        housingCompany.new_hitas &&
        !apartment.improvements.market_price_index.length &&
        !apartment.improvements.construction_price_index.length
    ) {
        return (
            <div>
                <p>Uusi-Hitas asunnoilla ei voi olla parannuksia.</p>
                <div className="row row--buttons">
                    <NavigateBackButton />
                    <div />
                </div>
            </div>
        );
    }

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
