import {Button, Dialog, IconCheck} from "hds-react";
import {useContext, useState} from "react";
import {useFormContext} from "react-hook-form";
import {QueryStateHandler} from "../../../common/components";
import {ApartmentSaleFormSchema, IApartmentMaximumPriceCalculationDetails} from "../../../common/schemas";
import {useSaveApartmentMaximumPriceMutation} from "../../../common/services";
import {hdsToast, setAPIErrorsForFormFields} from "../../../common/utils";
import MaximumPriceModalContent from "./ApartmentMaximumPriceBreakdownModal";
import {ApartmentViewContext} from "./ApartmentViewContextProvider";
import {FetchBaseQueryError} from "@reduxjs/toolkit/query";

const MaximumPriceModalError = ({error, closeModal}) => {
    const nonFieldError = error?.data?.message ?? "";
    const errorCode = error?.data?.error ?? "";
    return (
        <>
            <Dialog.Content>
                <p>Virhe: {(error as FetchBaseQueryError)?.status}</p>
                <p>
                    {nonFieldError} {errorCode ? `(${errorCode})` : ""}
                </p>
            </Dialog.Content>
            <Dialog.ActionButtons>
                <Button
                    onClick={closeModal}
                    variant="secondary"
                    theme="black"
                >
                    Sulje
                </Button>
            </Dialog.ActionButtons>
        </>
    );
};

const CreateMaximumPriceCalculationButton = ({
    buttonVariant,
    getParsedFormData,
}: {
    buttonVariant: "primary" | "secondary";
    getParsedFormData: () => {
        calculation_date: string;
        apartment_share_of_housing_company_loans_date: string;
        apartment_share_of_housing_company_loans: number;
        additional_info: string;
    };
}) => {
    const {apartment, housingCompany} = useContext(ApartmentViewContext);
    if (!apartment) throw new Error("Apartment not found");

    const formObject = useFormContext();

    const [isModalOpen, setIsModalOpen] = useState(false);

    const [
        saveMaximumPriceCalculation,
        {data: maximumPriceCreateData, error: maximumPriceCreateError, isLoading: isMaximumPriceCreateLoading},
    ] = useSaveApartmentMaximumPriceMutation();

    const isCalculationFormValid = ApartmentSaleFormSchema.partial().safeParse({
        purchase_date: formObject.getValues("purchase_date"),
        apartment_share_of_housing_company_loans: formObject.getValues("apartment_share_of_housing_company_loans"),
    }).success;

    const handleCreateNewCalculationButton = () => {
        if (isCalculationFormValid) {
            saveMaximumPriceCalculation({
                id: undefined,
                apartmentId: apartment.id,
                housingCompanyId: housingCompany.id,
                data: getParsedFormData(),
            })
                .catch((error) => {
                    // eslint-disable-next-line no-console
                    hdsToast.error("Enimmäishintalaskelman luominen epäonnistui!");
                    setAPIErrorsForFormFields(formObject, error);
                })
                .finally(() => {
                    setIsModalOpen(true);
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
                variant={buttonVariant}
                onClick={handleCreateNewCalculationButton}
                disabled={!isCalculationFormValid}
                iconLeft={<IconCheck />}
            >
                Luo uusi enimmäishintalaskelma
            </Button>

            <Dialog
                id="maximum-price-confirmation-modal"
                aria-labelledby="maximum-price-confirmation-modal__title"
                isOpen={isModalOpen}
                close={() => setIsModalOpen(false)}
                closeButtonLabelText="Sulje"
                variant={maximumPriceCreateError ? "danger" : "primary"}
                boxShadow
            >
                <Dialog.Header
                    id="maximum-price-confirmation-modal__title"
                    title="Vahvistetaanko enimmäishintalaskelma?"
                    iconLeft={<IconCheck />}
                />
                <QueryStateHandler
                    data={maximumPriceCreateData}
                    error={maximumPriceCreateError}
                    isLoading={isMaximumPriceCreateLoading}
                    errorComponent={
                        <MaximumPriceModalError
                            error={maximumPriceCreateError}
                            closeModal={() => setIsModalOpen(false)}
                        />
                    }
                >
                    <MaximumPriceModalContent
                        calculation={maximumPriceCreateData as IApartmentMaximumPriceCalculationDetails}
                        apartment={apartment}
                        setIsModalVisible={setIsModalOpen}
                    />
                </QueryStateHandler>
            </Dialog>
        </>
    );
};

export default CreateMaximumPriceCalculationButton;
