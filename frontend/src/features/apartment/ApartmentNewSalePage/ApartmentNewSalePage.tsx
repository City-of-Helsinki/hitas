import {useParams} from "react-router-dom";
import {useGetApartmentDetailQuery} from "../../../app/services";
import {Heading, QueryStateHandler} from "../../../common/components";
import {IApartmentDetails} from "../../../common/schemas";
import ApartmentHeader from "../components/ApartmentHeader";
import LoadedApartmentSalesPage from "./LoadedApartmentSalesPage";

const ApartmentNewSalePage = () => {
    // Main Apartment New Sale container.
    // Loads the Apartment data before rendering anything.

    const params = useParams();
    const {data, error, isLoading} = useGetApartmentDetailQuery({
        housingCompanyId: params.housingCompanyId as string,
        apartmentId: params.apartmentId as string,
    });

    return (
        <div className="view--apartment-sales">
            <QueryStateHandler
                data={data}
                error={error}
                isLoading={isLoading}
            >
                <ApartmentHeader />
                <Heading type="main">
                    {data && data.prices.first_purchase_date ? "Kauppatapahtuma" : "Uudiskohteen kauppa"}
                </Heading>
                <LoadedApartmentSalesPage apartment={data as IApartmentDetails} />
            </QueryStateHandler>
        </div>
    );
};

export default ApartmentNewSalePage;
