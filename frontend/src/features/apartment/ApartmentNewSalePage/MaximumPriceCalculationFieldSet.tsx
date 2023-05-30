import {Dialog, Fieldset} from "hds-react";
import {useState} from "react";
import {useSaveApartmentMaximumPriceMutation} from "../../../app/services";
import {QueryStateHandler} from "../../../common/components";
import {
    ApartmentSaleFormSchema,
    IApartmentConfirmedMaximumPrice,
    IApartmentDetails,
    IApartmentMaximumPrice,
} from "../../../common/schemas";
import {formatDate, hdsToast} from "../../../common/utils";
import MaximumPriceModalContent from "../components/ApartmentMaximumPriceBreakdownModal";
import {ISalesPageMaximumPrices} from "./LoadedApartmentSalesPage";
import MaximumPriceCalculationExists from "./MaximumPriceCalculationExists";
import MaximumPriceCalculationMissing from "./MaximumPriceCalculationMissing";
import MaximumPriceModalError from "./MaximumPriceModalError";

const MaximumPriceCalculationFieldSet = ({
    apartment,
    setMaximumPrices,
    saleForm,
}: {
    apartment: IApartmentDetails;
    setMaximumPrices: (maximumPrices: ISalesPageMaximumPrices) => void;
    saleForm;
}) => {
    const [isCreateModalVisible, setIsCreateModalVisible] = useState(false);

    const hasApartmentConfirmedCalculation =
        apartment.prices.maximum_prices.confirmed && apartment.prices.maximum_prices.confirmed.valid.is_valid;

    const [
        saveMaximumPriceCalculation,
        {
            data: maximumPriceCalculationCreateData,
            error: maximumPriceCreateError,
            isLoading: isMaximumPriceCreateLoading,
        },
    ] = useSaveApartmentMaximumPriceMutation();

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

    const isCalculationFormValid = ApartmentSaleFormSchema.partial().safeParse({
        purchase_date: saleForm.getValues("purchase_date"),
        apartment_share_of_housing_company_loans: saleForm.getValues("apartment_share_of_housing_company_loans"),
    }).success;

    return (
        <Fieldset
            heading={`Enimmäishintalaskelma${
                hasApartmentConfirmedCalculation
                    ? ` (vahvistettu ${formatDate(
                          (apartment.prices.maximum_prices.confirmed as IApartmentConfirmedMaximumPrice).confirmed_at
                      )})`
                    : ""
            } *`}
        >
            {hasApartmentConfirmedCalculation ? (
                <MaximumPriceCalculationExists
                    apartment={apartment}
                    saleForm={saleForm}
                    setMaximumPrices={setMaximumPrices}
                    handleCalculateButton={handleCreateNewCalculationButton}
                    isCalculationFormValid={isCalculationFormValid}
                />
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
