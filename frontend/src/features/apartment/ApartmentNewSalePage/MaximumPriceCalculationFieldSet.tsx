import {Button, Dialog, Fieldset} from "hds-react";
import {useContext, useState} from "react";
import {useFormContext} from "react-hook-form";
import {useSaveApartmentMaximumPriceMutation} from "../../../app/services";
import {QueryStateHandler} from "../../../common/components";
import SimpleErrorMessage from "../../../common/components/SimpleErrorMessage";
import {ApartmentSaleFormSchema, IApartmentMaximumPriceCalculationDetails} from "../../../common/schemas";
import {hdsToast} from "../../../common/utils";
import MaximumPriceModalContent from "../components/ApartmentMaximumPriceBreakdownModal";
import {ApartmentSaleContext} from "./index";
import {ISalesPageMaximumPrices} from "./LoadedApartmentSalesPage";
import MaximumPriceCalculationExists from "./MaximumPriceCalculationExists";
import MaximumPriceCalculationMissing from "./MaximumPriceCalculationMissing";
import MaximumPriceModalError from "./MaximumPriceModalError";
import {isApartmentMaxPriceCalculationValid} from "./utils";

const MaximumPriceCalculationFieldSet = ({
    setMaximumPrices,
}: {
    setMaximumPrices: (maximumPrices: ISalesPageMaximumPrices) => void;
}) => {
    const [isCreateModalVisible, setIsCreateModalVisible] = useState(false);
    const {apartment, formExtraFieldErrorMessages} = useContext(ApartmentSaleContext);
    const saleForm = useFormContext();

    const [
        saveMaximumPriceCalculation,
        {
            data: maximumPriceCalculationCreateData,
            error: maximumPriceCreateError,
            isLoading: isMaximumPriceCreateLoading,
        },
    ] = useSaveApartmentMaximumPriceMutation();

    if (!apartment) return null; // In reality this will never happen, but TS doesn't know that :)

    const isCalculationValid = isApartmentMaxPriceCalculationValid(apartment, saleForm.watch("purchase_date"));

    const apartmentShareOfLoans = saleForm.getValues("apartment_share_of_housing_company_loans");
    const hasLoanValueChanged =
        formExtraFieldErrorMessages?.apartment_share_of_housing_company_loans && apartmentShareOfLoans !== null;

    const maximumPriceCalculationErrorMessage =
        formExtraFieldErrorMessages?.maximum_price_calculation &&
        formExtraFieldErrorMessages.maximum_price_calculation[0];

    const isCalculationFormValid = ApartmentSaleFormSchema.partial().safeParse({
        purchase_date: saleForm.getValues("purchase_date"),
        apartment_share_of_housing_company_loans: saleForm.getValues("apartment_share_of_housing_company_loans"),
    }).success;

    const handleCreateNewCalculationButton = () => {
        if (isCalculationFormValid) {
            const date = saleForm.getValues("purchase_date") ?? null;

            saveMaximumPriceCalculation({
                data: {
                    calculation_date: date,
                    apartment_share_of_housing_company_loans: apartmentShareOfLoans ?? 0,
                    apartment_share_of_housing_company_loans_date: date,
                    additional_info: "",
                },
                apartmentId: apartment.id,
                housingCompanyId: apartment.links.housing_company.id,
            })
                .then(() => setIsCreateModalVisible(true))
                .catch(() => {
                    // eslint-disable-next-line no-console
                    hdsToast.error("Enimmäishintalaskelman luominen epäonnistui!");
                });
        } else {
            hdsToast.error(
                <>
                    Enimmäishinnan laskemiseen tarvitaan
                    <span>kauppakirjan päivämäärä</span> sekä <span>yhtiön lainaosuus</span>!
                </>
            );
        }
    };

    return (
        <Fieldset heading="Enimmäishintalaskelma *">
            {isCalculationValid ? (
                <MaximumPriceCalculationExists setMaximumPrices={setMaximumPrices} />
            ) : (
                <MaximumPriceCalculationMissing />
            )}

            <SimpleErrorMessage errorMessage={maximumPriceCalculationErrorMessage} />
            <SimpleErrorMessage
                errorMessage={
                    hasLoanValueChanged && (
                        <>
                            <span>Yhtiön lainaosuus</span> on muuttunut, ole hyvä ja
                            <span> tee uusi enimmäishintalaskelma</span>.
                        </>
                    )
                }
            />

            <Button
                theme="black"
                variant={hasLoanValueChanged ? "primary" : "secondary"}
                onClick={handleCreateNewCalculationButton}
                disabled={!isCalculationFormValid || !apartment.surface_area}
            >
                Luo uusi enimmäishintalaskelma
            </Button>

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
                        calculation={maximumPriceCalculationCreateData as IApartmentMaximumPriceCalculationDetails}
                        apartment={apartment}
                        setIsModalVisible={setIsCreateModalVisible}
                    />
                </QueryStateHandler>
            </Dialog>
        </Fieldset>
    );
};

export default MaximumPriceCalculationFieldSet;
