import ApartmentViewContextProvider from "../components/ApartmentViewContextProvider";
import LoadedApartmentSalePage from "./LoadedApartmentSalePage";

const ApartmentSalePage = () => {
    return (
        <ApartmentViewContextProvider viewClassName="view--apartment-sales">
            <LoadedApartmentSalePage />
        </ApartmentViewContextProvider>
    );
};

export default ApartmentSalePage;
