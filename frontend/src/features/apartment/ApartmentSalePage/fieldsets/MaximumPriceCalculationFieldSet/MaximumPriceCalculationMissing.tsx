import {useContext, useEffect} from "react";
import {useFormContext} from "react-hook-form";
import {QueryStateHandler} from "../../../../../common/components";
import {ApartmentSaleFormSchema} from "../../../../../common/schemas";
import {useGetApartmentUnconfirmedMaximumPriceForDateQuery} from "../../../../../common/services";
import {formatMoney, hdsToast, today} from "../../../../../common/utils";
import {ApartmentSaleContext} from "../../utils";

const UnconfirmedMaximumPriceError = ({error}) => {
    return (
        <>
            <p>
                <span className="error-text">Enimmäishinta-arvion hakeminen epäonnistui.</span>
            </p>
            <p className="error-text">
                Virhe: {error?.status}
                <br />
                {error?.data?.message ?? "Tuntematon virhe"} ({error?.data?.error ?? "?"})
            </p>
        </>
    );
};

const MaximumPriceCalculationMissing = () => {
    const {apartment, setMaximumPrices} = useContext(ApartmentSaleContext);
    const {watch} = useFormContext();

    const purchaseDate = watch("purchase_date") ?? today();
    const isPurchaseDateValid = ApartmentSaleFormSchema.partial().safeParse({purchase_date: purchaseDate}).success;

    const {
        data: maximumPriceData,
        error: maximumPriceError,
        isFetching: isMaximumPriceLoading,
    } = useGetApartmentUnconfirmedMaximumPriceForDateQuery(
        {
            housingCompanyId: apartment.links.housing_company.id,
            apartmentId: apartment.id,
            date: isPurchaseDateValid ? `${purchaseDate.substring(0, 7)}-01` : "", // Set date day to 01 for better caching
        },
        {skip: !purchaseDate || !isPurchaseDateValid}
    );

    useEffect(() => {
        if (isMaximumPriceLoading || !maximumPriceData) return;
        if (maximumPriceData && !maximumPriceError) {
            setMaximumPrices({
                maximumPrice: maximumPriceData.surface_area_price_ceiling.value,
                debtFreePurchasePrice: maximumPriceData.surface_area_price_ceiling.value,
                apartmentShareOfHousingCompanyLoans: 0,
                index: "surface_area_price_ceiling",
            });
        } else {
            hdsToast.error("Enimmäishinta-arvion hakeminen epäonnistui.");
        }
        // eslint-disable-next-line
    }, [maximumPriceData, maximumPriceError, isMaximumPriceLoading]);

    return (
        <div className="row row--max-prices--unconfirmed">
            <QueryStateHandler
                data={maximumPriceData}
                error={maximumPriceError}
                isLoading={isMaximumPriceLoading}
                errorComponent={<UnconfirmedMaximumPriceError error={maximumPriceError} />}
            >
                <p>Asunnosta ei ole vahvistettua enimmäishintalaskelmaa valitulle kauppakirjan päivämäärälle.</p>
                {maximumPriceData?.surface_area_price_ceiling.value ? (
                    <>
                        <p>
                            Enimmäishintana käytetään asunnon rajaneliöhinta-arviota
                            <span> {formatMoney(maximumPriceData?.surface_area_price_ceiling.value)}.</span>
                        </p>
                        <p>
                            Mikäli asunnon velaton kauppahinta ylittää rajaneliöhinta-arvion, tulee asunnolle luoda
                            vahvistettu enimmäishintalaskelma.
                        </p>
                    </>
                ) : (
                    <b> Asunnon rajaneliöhinta-arviota ei voitu laskea.</b>
                )}
            </QueryStateHandler>
        </div>
    );
};

export default MaximumPriceCalculationMissing;
