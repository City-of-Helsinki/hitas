import {useGetApartmentMaximumPriceQuery} from "../../../app/services";
import {QueryStateHandler} from "../../../common/components";
import {IApartmentMaximumPrice} from "../../../common/schemas";
import LoadedApartmentSalesPage from "./LoadedApartmentSalesPage";

export const MaximumPriceCalculationLoader = ({apartment}) => {
    const {data, error, isLoading} = useGetApartmentMaximumPriceQuery(
        {
            housingCompanyId: apartment.links.housing_company.id,
            apartmentId: apartment.id,
            priceId: apartment.prices.maximum_prices.confirmed?.id as string,
        },
        {skip: !apartment.prices.maximum_prices.confirmed?.valid.is_valid}
    );

    const hasValidCalculation = apartment.prices.maximum_prices.confirmed?.valid.is_valid;
    return hasValidCalculation ? (
        <QueryStateHandler
            data={data}
            error={error}
            isLoading={isLoading}
        >
            <LoadedApartmentSalesPage
                maxPriceCalculation={data ? (data as IApartmentMaximumPrice) : null}
                apartment={apartment}
            />
        </QueryStateHandler>
    ) : (
        <LoadedApartmentSalesPage
            maxPriceCalculation={null}
            apartment={apartment}
        />
    );
};
