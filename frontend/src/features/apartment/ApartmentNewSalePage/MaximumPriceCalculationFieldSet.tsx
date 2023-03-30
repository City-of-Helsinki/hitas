import {Dialog, Fieldset} from "hds-react";
import {useEffect, useState} from "react";
import {useGetApartmentMaximumPriceQuery, useSaveApartmentMaximumPriceMutation} from "../../../app/services";
import {QueryStateHandler} from "../../../common/components";
import {ApartmentSaleFormSchema, IApartmentMaximumPrice} from "../../../common/schemas";
import {formatDate, hdsToast} from "../../../common/utils";
import MaximumPriceModalContent from "../components/ApartmentMaximumPriceBreakdownModal";
import MaximumPriceCalculationExists from "./MaximumPriceCalculationExists";
import MaximumPriceCalculationMissing from "./MaximumPriceCalculationMissing";
import MaximumPriceModalError from "./MaximumPriceModalError";

const MaximumPriceCalculationFieldSet = ({apartment, setMaximumPrices, saleForm}) => {
    const [isCreateModalVisible, setIsCreateModalVisible] = useState(false);

    const apartmentHasValidCalculation = apartment.prices.maximum_prices.confirmed?.valid.is_valid;

    const {
        data: maximumPriceCalculationData,
        error: maximumPriceError,
        isLoading: isMaximumPriceLoading,
    } = useGetApartmentMaximumPriceQuery(
        {
            housingCompanyId: apartment.links.housing_company.id,
            apartmentId: apartment.id,
            priceId: apartment.prices.maximum_prices.confirmed?.id as string,
        },
        {skip: !apartmentHasValidCalculation}
    );

    const [
        saveMaximumPriceCalculation,
        {
            data: maximumPriceCalculationCreateData,
            error: maximumPriceCreateError,
            isLoading: isMaximumPriceCreateLoading,
        },
    ] = useSaveApartmentMaximumPriceMutation();

    const handleSetMaxPrices = (calculation: IApartmentMaximumPrice) => {
        const indexVariables = calculation.calculations[calculation.index].calculation_variables;
        setMaximumPrices({
            maximumPrice: calculation.maximum_price,
            maxPricePerSquare: calculation.maximum_price_per_square,
            debtFreePurchasePrice: indexVariables.debt_free_price,
            apartmentShareOfHousingCompanyLoans: indexVariables.apartment_share_of_housing_company_loans,
            index: calculation.index,
        });

        saleForm.setValue("purchase_date", calculation.calculation_date);
        saleForm.setValue(
            "apartment_share_of_housing_company_loans",
            indexVariables.apartment_share_of_housing_company_loans
        );
    };

    const handleCreateNewCalculationButton = () => {
        if (isCalculationFormValid) {
            const date = saleForm.getValues("purchase_date") ?? null;
            const loanShare = saleForm.getValues("apartment_share_of_housing_company_loans") ?? 0;
            saveMaximumPriceCalculation({
                data: {
                    calculation_date: date,
                    apartment_share_of_housing_company_loans: loanShare,
                    apartment_share_of_housing_company_loans_date: date,
                    additional_info: "",
                },
                apartmentId: apartment.id,
                housingCompanyId: apartment.links.housing_company.id,
            })
                .then(() => setIsCreateModalVisible(true))
                .catch(() => hdsToast.error("Enimmäishintalaskelman luominen epäonnistui!"));
        } else {
            hdsToast.error(
                <>
                    Enimmäishinnan laskemiseen tarvitaan
                    <span>kauppakirjan päivämäärä</span> sekä <span>yhtiön lainaosuus</span>!
                </>
            );
        }
    };

    useEffect(() => {
        if (isMaximumPriceLoading || !maximumPriceCalculationData) return;
        if (maximumPriceCalculationData && !maximumPriceError) {
            handleSetMaxPrices(maximumPriceCalculationData);
        } else {
            hdsToast.error("Enimmäishintalaskentan hakeminen epäonnistui.");
        }
        // eslint-disable-next-line
    }, [maximumPriceCalculationData, maximumPriceError, isMaximumPriceLoading]);

    const isCalculationFormValid = ApartmentSaleFormSchema.partial().safeParse({
        purchase_date: saleForm.getValues("purchase_date"),
        apartment_share_of_housing_company_loans: saleForm.getValues("apartment_share_of_housing_company_loans"),
    }).success;

    return (
        <Fieldset
            heading={`Enimmäishintalaskelma${
                apartmentHasValidCalculation
                    ? ` (vahvistettu ${formatDate(apartment.prices.maximum_prices.confirmed.confirmed_at)})`
                    : ""
            } *`}
        >
            {apartmentHasValidCalculation ? (
                <QueryStateHandler
                    data={maximumPriceCalculationData}
                    error={maximumPriceError}
                    isLoading={isMaximumPriceLoading}
                >
                    <MaximumPriceCalculationExists
                        saleForm={saleForm}
                        maximumPriceCalculation={maximumPriceCalculationData}
                        handleCalculateButton={handleCreateNewCalculationButton}
                        isCalculationFormValid={isCalculationFormValid}
                    />
                </QueryStateHandler>
            ) : (
                <MaximumPriceCalculationMissing
                    handleCalculateButton={handleCreateNewCalculationButton}
                    isCalculationFormValid={isCalculationFormValid}
                />
            )}

            <Dialog
                id="maximum-price-confirmation-modal"
                closeButtonLabelText=""
                aria-labelledby=""
                isOpen={isCreateModalVisible}
                close={() => setIsCreateModalVisible(false)}
                boxShadow
            >
                <Dialog.Header
                    id="maximum-price-confirmation-modal-header"
                    title="Vahvistetaanko enimmäishintalaskelma?"
                />
                <QueryStateHandler
                    data={maximumPriceCalculationCreateData}
                    error={maximumPriceCreateError}
                    isLoading={isMaximumPriceCreateLoading}
                    errorComponent={
                        <MaximumPriceModalError
                            error={maximumPriceCreateError}
                            setIsModalVisible={setIsCreateModalVisible}
                        />
                    }
                >
                    <MaximumPriceModalContent
                        calculation={maximumPriceCalculationCreateData as IApartmentMaximumPrice}
                        apartment={apartment}
                        setIsModalVisible={setIsCreateModalVisible}
                    />
                </QueryStateHandler>
            </Dialog>
        </Fieldset>
    );
};

export default MaximumPriceCalculationFieldSet;
