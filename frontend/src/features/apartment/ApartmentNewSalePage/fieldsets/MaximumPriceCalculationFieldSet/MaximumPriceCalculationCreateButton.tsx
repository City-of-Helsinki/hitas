import {Button, Dialog} from "hds-react";
import {useContext, useState} from "react";
import {useFormContext} from "react-hook-form";
import {useSaveApartmentMaximumPriceMutation} from "../../../../../app/services";
import {QueryStateHandler} from "../../../../../common/components";
import {ApartmentSaleFormSchema, IApartmentMaximumPriceCalculationDetails} from "../../../../../common/schemas";
import {hdsToast} from "../../../../../common/utils";
import MaximumPriceModalContent from "../../../components/ApartmentMaximumPriceBreakdownModal";
import {ApartmentSaleContext} from "../../utils";
import MaximumPriceModalError from "./MaximumPriceModalError";

const MaximumPriceCalculationFieldSet = ({hasLoanValueChanged}) => {
    const [isCreateModalVisible, setIsCreateModalVisible] = useState(false);
    const {apartment} = useContext(ApartmentSaleContext);
    const saleForm = useFormContext();

    const [
        saveMaximumPriceCalculation,
        {data: maximumPriceCreateData, error: maximumPriceCreateError, isLoading: isMaximumPriceCreateLoading},
    ] = useSaveApartmentMaximumPriceMutation();

    const isCalculationFormValid = ApartmentSaleFormSchema.partial().safeParse({
        purchase_date: saleForm.getValues("purchase_date"),
        apartment_share_of_housing_company_loans: saleForm.getValues("apartment_share_of_housing_company_loans"),
    }).success;

    const handleCreateNewCalculationButton = () => {
        if (isCalculationFormValid) {
            const date = saleForm.watch("purchase_date") ?? null;

            saveMaximumPriceCalculation({
                housingCompanyId: apartment.links.housing_company.id,
                apartmentId: apartment.id,
                data: {
                    calculation_date: date,
                    apartment_share_of_housing_company_loans_date: date,
                    apartment_share_of_housing_company_loans:
                        saleForm.watch("apartment_share_of_housing_company_loans") ?? 0,
                    additional_info: "",
                },
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
        <>
            <Button
                theme="black"
                variant={hasLoanValueChanged ? "primary" : "secondary"}
                onClick={handleCreateNewCalculationButton}
                disabled={!isCalculationFormValid}
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
                    data={maximumPriceCreateData}
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
                        calculation={maximumPriceCreateData as IApartmentMaximumPriceCalculationDetails}
                        apartment={apartment}
                        setIsModalVisible={setIsCreateModalVisible}
                    />
                </QueryStateHandler>
            </Dialog>
        </>
    );
};

export default MaximumPriceCalculationFieldSet;
