import {zodResolver} from "@hookform/resolvers/zod/dist/zod";
import {Fieldset} from "hds-react";
import {useEffect, useRef, useState} from "react";
import {FormProvider, useForm} from "react-hook-form";
import {useNavigate} from "react-router-dom";
import {v4 as uuidv4} from "uuid";
import {z, ZodSchema} from "zod";
import {useCreateSaleMutation} from "../../../app/services";
import {ConfirmDialogModal, NavigateBackButton, OwnershipList, SaveButton} from "../../../common/components";
import {IApartmentDetails, IApartmentSaleForm, OwnershipsListSchema} from "../../../common/schemas";
import {hdsToast, today} from "../../../common/utils";
import {ApartmentCatalogPricesFieldSet, ApartmentSaleFormFieldSet, MaximumPriceCalculationFieldSet} from "./fieldsets";
import {ApartmentSaleContext, getRefinedApartmentSaleFormSchema, ISalesPageMaximumPrices} from "./utils";

const LoadedApartmentSalePage = ({apartment}: {apartment: IApartmentDetails}) => {
    const navigate = useNavigate();

    // **********
    // * States *
    // **********

    const [maximumPrices, setMaximumPrices] = useState<ISalesPageMaximumPrices>({
        maximumPrice: null,
        debtFreePurchasePrice: null,
        apartmentShareOfHousingCompanyLoans: null,
        index: "",
    });

    // ************
    // * Warnings *
    // ************

    // Certain form errors should be able to be ignored.
    const noWarningsGiven = {maximum_price_calculation: false, catalog_acquisition_price: false};
    const [isWarningModalVisible, setIsWarningModalVisible] = useState(false);
    const [warningMessage, setWarningMessage] = useState("");
    const [warningsGiven, setWarningsGiven] = useState(noWarningsGiven);
    const closeWarningsModal = () => {
        setWarningsGiven(noWarningsGiven);
        setWarningMessage("");
        setIsWarningModalVisible(false);
    };

    // ***********************
    // * Form initialization *
    // ***********************

    const isApartmentFirstSale = !apartment.prices.first_purchase_date;
    const initialFormData: IApartmentSaleForm = {
        notification_date: today(),
        purchase_date: "",
        purchase_price: isApartmentFirstSale ? apartment.prices.catalog_purchase_price : null,
        apartment_share_of_housing_company_loans: isApartmentFirstSale
            ? apartment.prices.catalog_share_of_housing_company_loans
            : null,
        exclude_from_statistics: false,
        ownerships: apartment.ownerships.map((o) => ({...o, key: uuidv4()})),
    };

    const RefinedApartmentSaleSchema: ZodSchema = getRefinedApartmentSaleFormSchema(
        apartment,
        maximumPrices,
        warningsGiven
    );
    const resolver = (data, context, options) => {
        return zodResolver(RefinedApartmentSaleSchema)(data, context, {...options, mode: "sync"});
    };

    const saleForm = useForm({
        resolver: resolver,
        defaultValues: initialFormData,
        mode: "all",
    });

    // We need a reference to the form-element to be able to dispatch a submit event dynamically
    const formRef = useRef<HTMLFormElement | null>(null);

    const handleSaveButtonClick = () => {
        // Dispatch submit event, as the "Tallenna"-button isn't inside the sale form element
        formRef.current && formRef.current.dispatchEvent(new Event("submit", {cancelable: true, bubbles: true}));
    };

    useEffect(() => {
        // Re-validate form due to maximum prices changing to get rid of errors
        if (maximumPrices.maximumPrice !== null && saleForm.getValues("purchase_price")) {
            saleForm.trigger();
        }
        // If purchase_price didn't have a value, clear only loan share errors in case there are any
        else if (saleForm.getValues("apartment_share_of_housing_company_loans") !== null) {
            saleForm.trigger("apartment_share_of_housing_company_loans");
        }
    }, [maximumPrices]);

    // ************************
    // * Form submit handling *
    // ************************

    // Sale form was submitted with errors
    const onSaleFormSubmitInvalid = (errors) => {
        // Handle Hard errors
        if (errors.notification_date) {
            hdsToast.error(`Ilmoituspäivämäärä: ${errors.notification_date.message}`);
            return;
        } else if (errors.purchase_date) {
            hdsToast.error(`Kauppakirjan päivämäärä: ${errors.purchase_date.message}`);
            return;
        } else if (errors.purchase_price && !errors.maximum_price_calculation) {
            hdsToast.error(`Kauppahinta: ${errors.purchase_price.message}`);
            return;
        } else if (errors.apartment_share_of_housing_company_loans) {
            hdsToast.error(`Osuus yhtiön lainoista: ${errors.apartment_share_of_housing_company_loans.message}`);
            return;
        } else if (errors.ownerships) {
            hdsToast.error(`Omistajuudet: ${errors.ownerships.message}`);
            return;
        }

        // Handle Soft errors
        // If errors only include ones that can be ignored, show a warning modal and continue creation process
        if (errors.maximum_price_calculation && errors.maximum_price_calculation.type === z.ZodIssueCode.custom) {
            setIsWarningModalVisible(true);
            setWarningsGiven((prev) => ({...prev, maximum_price_calculation: true}));
            setWarningMessage("Kauppahinta ylittää laskelman enimmäishinnan.");
        } else if (
            errors.catalog_acquisition_price &&
            errors.catalog_acquisition_price.type === z.ZodIssueCode.custom
        ) {
            setIsWarningModalVisible(true);
            setWarningsGiven((prev) => ({...prev, catalog_acquisition_price: true}));
            setWarningMessage(errors.catalog_acquisition_price.message);
        } else {
            hdsToast.error(`Virhe luodessa asunnon kauppaa!`);
            setIsWarningModalVisible(false);
            // eslint-disable-next-line no-console
            console.error(errors);
        }
    };

    // Sale form was submitted without any errors
    const onSaleFormSubmitValid = () => {
        // Proceed to creating the sale.
        createApartmentSale(saleForm.getValues(), apartment);
    };

    // ***********************
    // * Creating a new sale *
    // ***********************

    // Send a request to the API to create a sale
    const [createSale, {isLoading: isCreateSaleLoading}] = useCreateSaleMutation();
    const createApartmentSale = (data, apartment) => {
        if (isWarningModalVisible) closeWarningsModal();

        createSale({
            data: data,
            apartmentId: apartment.id,
            housingCompanyId: apartment.links.housing_company.id,
        })
            .unwrap()
            .then((payload) => {
                hdsToast.success("Kauppa tallennettu onnistuneesti!");
                if (payload.conditions_of_sale_created) {
                    hdsToast.info("Asunnolle luotiin myyntiehtoja.");
                }
                navigate(`/housing-companies/${apartment.links.housing_company.id}/apartments/${apartment.id}`);
            })
            .catch((error) => {
                hdsToast.error("Kaupan tallentaminen epäonnistui!");
                error.data.fields.forEach((field) =>
                    saleForm.setError(field.field, {type: "custom", message: field.message})
                );
            });
    };

    // *************************
    // * Extra form validation *
    // *************************

    // saleForm can not be trusted to always validate everything and have the errors, so force a parse on every render
    const extraValidationResult = RefinedApartmentSaleSchema.safeParse(saleForm.getValues());
    let formExtraFieldErrorMessages;
    if (!extraValidationResult.success) {
        formExtraFieldErrorMessages = extraValidationResult.error.flatten().fieldErrors;
    }

    return (
        <div className="view--apartment-conditions-of-sale">
            <div className="fieldsets">
                <ApartmentSaleContext.Provider value={{apartment, formExtraFieldErrorMessages, setMaximumPrices}}>
                    <FormProvider {...saleForm}>
                        <ApartmentSaleFormFieldSet
                            formRef={formRef}
                            onSubmit={saleForm.handleSubmit(onSaleFormSubmitValid, onSaleFormSubmitInvalid)}
                        />
                        {isApartmentFirstSale ? (
                            <ApartmentCatalogPricesFieldSet />
                        ) : (
                            <MaximumPriceCalculationFieldSet />
                        )}
                        <Fieldset
                            className={`ownerships-fieldset ${
                                OwnershipsListSchema.safeParse(saleForm.getValues("ownerships")).success ? "" : "error"
                            }`}
                            heading="Omistajuudet"
                        >
                            <OwnershipList />
                        </Fieldset>
                    </FormProvider>
                </ApartmentSaleContext.Provider>
            </div>

            <div className="row row--buttons">
                <NavigateBackButton />
                <SaveButton
                    onClick={handleSaveButtonClick}
                    isLoading={isCreateSaleLoading}
                />
            </div>

            <ConfirmDialogModal
                successText="Kauppa tallennettu varoituksesta huolimatta"
                isLoading={isCreateSaleLoading}
                isVisible={isWarningModalVisible}
                setIsVisible={setIsWarningModalVisible}
                modalText={`${warningMessage}. Haluatko varmasti tallentaa kaupan?`}
                modalHeader="Vahvista kaupan tallennus"
                cancelAction={closeWarningsModal}
                confirmAction={handleSaveButtonClick}
                buttonText="Vahvista tallennus"
            />
        </div>
    );
};

export default LoadedApartmentSalePage;
