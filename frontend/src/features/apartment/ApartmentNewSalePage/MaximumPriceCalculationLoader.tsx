import {useGetApartmentMaximumPriceQuery} from "../../../app/services";
import {Heading, QueryStateHandler} from "../../../common/components";
import {IApartmentMaximumPrice} from "../../../common/schemas";
import ApartmentHeader from "../components/ApartmentHeader";
import LoadedApartmentSalesPage from "./LoadedApartmentSalesPage";

export const MaximumPriceCalculationLoader = ({apartment}) => {
    const {data, error, isLoading} = useGetApartmentMaximumPriceQuery({
        housingCompanyId: apartment.links.housing_company.id,
        apartmentId: apartment.id,
        priceId: apartment.prices.maximum_prices.confirmed?.id as string,
    });

    const ApartmentSalesPageContent = () => (
        <>
            <ApartmentHeader apartment={apartment} />
            <Heading type="main">Kauppatapahtuma</Heading>
            <LoadedApartmentSalesPage
                maxPriceCalculation={data ? (data as IApartmentMaximumPrice) : null}
                apartment={apartment}
            />
        </>
    );

    const hasValidCalculation = apartment.prices.maximum_prices.confirmed?.valid.is_valid;
    return hasValidCalculation ? (
        <QueryStateHandler
            data={data}
            error={error}
            isLoading={isLoading}
        >
            <ApartmentSalesPageContent />
        </QueryStateHandler>
    ) : (
        <ApartmentSalesPageContent />
    );
};
