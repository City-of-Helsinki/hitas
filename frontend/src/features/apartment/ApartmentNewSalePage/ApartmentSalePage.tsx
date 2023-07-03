import {useParams} from "react-router-dom";
import {useGetApartmentDetailQuery} from "../../../app/services";
import {Heading, QueryStateHandler} from "../../../common/components";
import {IApartmentDetails} from "../../../common/schemas";
import ApartmentHeader from "../components/ApartmentHeader";
import LoadedApartmentSalePage from "./LoadedApartmentSalePage";

const ApartmentSalePage = () => {
    // Main Apartment New Sale container.
    // Loads the Apartment data before rendering anything.

    const params = useParams();
    const {data, error, isLoading} = useGetApartmentDetailQuery({
        housingCompanyId: params.housingCompanyId as string,
        apartmentId: params.apartmentId as string,
    });

    return (
        <div className="view--apartment-sales">
            <ApartmentHeader />
            <QueryStateHandler
                data={data}
                error={error}
                isLoading={isLoading}
            >
                <Heading type="main">
                    {data && data.prices.first_purchase_date ? "Kauppatapahtuma" : "Uudiskohteen kauppa"}
                </Heading>
                <LoadedApartmentSalePage apartment={data as IApartmentDetails} />
            </QueryStateHandler>
        </div>
    );
};

export default ApartmentSalePage;
