import {zodResolver} from "@hookform/resolvers/zod/dist/zod";
import {Fieldset} from "hds-react";
import {useRef, useState} from "react";
import {useForm} from "react-hook-form";
import {useNavigate} from "react-router-dom";
import {v4 as uuidv4} from "uuid";
import {z, ZodSchema} from "zod";
import {useCreateSaleMutation} from "../../../app/services";
import {NavigateBackButton, SaveButton} from "../../../common/components";
import ConfirmDialogModal from "../../../common/components/ConfirmDialogModal";
import {Checkbox, DateInput, NumberInput} from "../../../common/components/form";
import {
    ApartmentSaleFormSchema,
    ApartmentSaleSchema,
    errorMessages,
    IApartmentDetails,
    IApartmentSaleForm,
    indexNames,
} from "../../../common/schemas";
import {getApartmentUnconfirmedPrices, hdsToast, today} from "../../../common/utils";
import ApartmentCatalogPrices from "./ApartmentCatalogPrices";
import MaximumPriceCalculationFieldSet from "./MaximumPriceCalculationFieldSet";
import OwnershipsListFieldSet from "./OwnershipsListFieldSet";

export interface ISalesPageMaximumPrices {
    maximumPrice: number;
    debtFreePurchasePrice: number;
    apartmentShareOfHousingCompanyLoans: number;
    index: (typeof indexNames)[number] | "";
}

const LoadedApartmentSalesPage = ({apartment}: {apartment: IApartmentDetails}) => {
    const navigate = useNavigate();

    const isApartmentFirstSale = !apartment.prices.first_purchase_date;
    const isApartmentMaxPriceCalculationValid = !!apartment.prices.maximum_prices.confirmed?.valid.is_valid;
    const unconfirmedPrices = getApartmentUnconfirmedPrices(apartment);

    const [maximumPrices, setMaximumPrices] = useState<ISalesPageMaximumPrices>(
        isApartmentFirstSale
            ? {
                  maximumPrice: apartment.prices.catalog_purchase_price ?? 0,
                  debtFreePurchasePrice: apartment.prices.catalog_acquisition_price ?? 0,
                  apartmentShareOfHousingCompanyLoans: apartment.prices.catalog_share_of_housing_company_loans ?? 0,
                  index: "",
              }
            : {
                  maximumPrice: unconfirmedPrices.surface_area_price_ceiling.value,
                  debtFreePurchasePrice: unconfirmedPrices.surface_area_price_ceiling.value,
                  apartmentShareOfHousingCompanyLoans: 0,
                  index: "surface_area_price_ceiling",
              }
    );

    // ************************
    // * Form data and schema *
    // ************************

    // Certain form errors should be able to be ignored.
    const [isWarningModalVisible, setIsWarningModalVisible] = useState(false);
    const noWarningsGiven = {maximum_price_calculation: false, catalog_acquisition_price: false};
    const [warningsGiven, setWarningsGiven] = useState(noWarningsGiven);
    const [warningMessage, setWarningMessage] = useState("");

    const initialFormData: IApartmentSaleForm = {
        notification_date: today(),
        purchase_date: "",
        purchase_price: isApartmentFirstSale ? apartment.prices.catalog_purchase_price : null,
        apartment_share_of_housing_company_loans: isApartmentFirstSale
            ? apartment.prices.catalog_share_of_housing_company_loans
            : null,
        exclude_from_statistics: false,
    };
    const initialFormOwnershipsList = apartment.ownerships.map((o) => ({...o, key: uuidv4()}));

    // superRefine does not run if the schema validation fails early.
    // Use as simple as possible schema for the form to allow superRefine to always run.
    const RefinedApartmentSaleFormSchema: ZodSchema = ApartmentSaleFormSchema.pick({
        purchase_price: true,
        apartment_share_of_housing_company_loans: true,
        exclude_from_statistics: true,
    }).superRefine((data, ctx) => {
        const debtFreePurchasePrice = (data.purchase_price ?? 0) + (data.apartment_share_of_housing_company_loans ?? 0);

        // First sale
        if (isApartmentFirstSale) {
            // We should show a warning and ask for confirmation if catalog prices are missing
            if (!warningsGiven.catalog_acquisition_price) {
                if (apartment.prices.catalog_acquisition_price === null) {
                    ctx.addIssue({
                        code: z.ZodIssueCode.custom,
                        path: ["catalog_acquisition_price"],
                        message: errorMessages.catalogPricesMissing,
                    });
                } else if (debtFreePurchasePrice < apartment.prices.catalog_acquisition_price) {
                    ctx.addIssue({
                        code: z.ZodIssueCode.custom,
                        path: ["catalog_acquisition_price"],
                        message: errorMessages.catalogUnderMaxPrice,
                    });
                } else if (debtFreePurchasePrice > apartment.prices.catalog_acquisition_price) {
                    ctx.addIssue({
                        code: z.ZodIssueCode.custom,
                        path: ["catalog_acquisition_price"],
                        message: errorMessages.catalogOverMaxPrice,
                    });
                }
            }
        } else if (!warningsGiven.maximum_price_calculation) {
            // Normal apartment sale without confirmed maximum price calculation
            if (!isApartmentMaxPriceCalculationValid) {
                if (debtFreePurchasePrice > maximumPrices.debtFreePurchasePrice) {
                    ctx.addIssue({
                        code: z.ZodIssueCode.custom,
                        path: ["maximum_price_calculation"],
                        message: errorMessages.priceHigherThanUnconfirmedMaxPrice,
                    });
                    ctx.addIssue({
                        code: z.ZodIssueCode.custom,
                        path: ["purchase_price"],
                        message: errorMessages.overMaxPrice,
                    });
                }
            }
            // Normal apartment sale with confirmed maximum price calculation
            else {
                // Price can not be bigger than the maximum price calculations maximum price.
                if (data.purchase_price && data.purchase_price > maximumPrices.maximumPrice) {
                    ctx.addIssue({
                        code: z.ZodIssueCode.custom,
                        path: ["purchase_price"],
                        message: errorMessages.overMaxPrice,
                    });
                    ctx.addIssue({
                        code: z.ZodIssueCode.custom,
                        path: ["maximum_price_calculation"],
                        message: errorMessages.overMaxPrice,
                    });
                }
            }

            // Price can be zero only if sale is excluded from statistics.
            if (!data.exclude_from_statistics && data.purchase_price === 0) {
                ctx.addIssue({
                    code: z.ZodIssueCode.custom,
                    path: ["purchase_price"],
                    message: "Pakollinen jos kauppa tilastoidaan.",
                });
            }

            // The apartment share of housing company loans must match the maximum price calculations or catalog loan value.
            if (
                isApartmentMaxPriceCalculationValid &&
                data.apartment_share_of_housing_company_loans !== null &&
                data.apartment_share_of_housing_company_loans !== maximumPrices.apartmentShareOfHousingCompanyLoans
            ) {
                ctx.addIssue({
                    code: z.ZodIssueCode.custom,
                    path: ["apartment_share_of_housing_company_loans"],
                    message: errorMessages.loanShareChanged,
                });
            }
        }
    });
    // Merge the schemas to get access to all the errors at the same time.
    const RefinedApartmentSaleSchema: ZodSchema = z.intersection(ApartmentSaleSchema, RefinedApartmentSaleFormSchema);

    const resolver = (data, context, options) => {
        return zodResolver(RefinedApartmentSaleSchema)(data, context, {
            ...options,
            mode: "sync",
        });
    };

    const saleForm = useForm({
        resolver: resolver,
        defaultValues: {...initialFormData, ownerships: initialFormOwnershipsList},
        mode: "all",
    });

    // We need a reference to the form-element to be able to dispatch a submit event dynamically
    const formRef = useRef<HTMLFormElement | null>(null);

    // TODO: Find a way to do this with the only saleForm
    // saleForm can not be trusted to always validate everything and have the errors, so force a parse on every render
    const extraValidationResult = RefinedApartmentSaleSchema.safeParse(saleForm.getValues());
    let formExtraFieldErrorMessages;
    if (!extraValidationResult.success) {
        formExtraFieldErrorMessages = extraValidationResult.error.flatten().fieldErrors;
    }

    // ***********************
    // * Creating a new sale *
    // ***********************

    const [createSale, {isLoading: isCreateSaleLoading}] = useCreateSaleMutation();

    const closeWarningsModal = () => {
        setWarningsGiven(noWarningsGiven);
        setWarningMessage("");
        setIsWarningModalVisible(false);
    };

    const handleSaveButtonClick = () => {
        // Dispatch submit event, as the "Tallenna"-button isn't inside the sale form element
        formRef.current && formRef.current.dispatchEvent(new Event("submit", {cancelable: true, bubbles: true}));
    };

    // Sale form was submitted without any errors
    const onSaleFormSubmitValid = () => {
        // Proceed to creating the sale.
        createApartmentSale(saleForm.getValues(), apartment);
    };

    // ******************
    // * Error Handling *
    // ******************

    // Sale form was submitted with errors
    const onSaleFormSubmitInvalid = (errors) => {
        // Handle Hard errors
        if (errors.ownerships) {
            hdsToast.error(errors.ownerships.message);
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
            // eslint-disable-next-line no-console
            console.error(errors);
        }
    };

    // Send a request to the API to create a sale
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

    return (
        <div className="view--apartment-conditions-of-sale">
            <div className="fieldsets">
                <Fieldset heading="Kaupan tiedot *">
                    <form
                        ref={formRef}
                        onSubmit={saleForm.handleSubmit(onSaleFormSubmitValid, onSaleFormSubmitInvalid)}
                    >
                        <div className="row">
                            <DateInput
                                name="notification_date"
                                label="Ilmoituspäivämäärä"
                                formObject={saleForm}
                                maxDate={new Date()}
                                required
                            />
                            <DateInput
                                name="purchase_date"
                                label="Kauppakirjan päivämäärä"
                                formObject={saleForm}
                                maxDate={new Date()}
                                required
                            />
                        </div>
                        <div className="row">
                            <NumberInput
                                name="purchase_price"
                                label="Kauppahinta"
                                formObject={saleForm}
                                unit="€"
                                fractionDigits={2}
                                required
                            />
                            <NumberInput
                                name="apartment_share_of_housing_company_loans"
                                label="Osuus yhtiön lainoista"
                                formObject={saleForm}
                                unit="€"
                                required
                            />
                        </div>
                        {!isApartmentFirstSale ? (
                            <Checkbox
                                name="exclude_from_statistics"
                                label="Ei tilastoihin (esim. sukulaiskauppa)"
                                formObject={saleForm}
                                triggerField="purchase_price"
                            />
                        ) : null}
                    </form>
                </Fieldset>

                {isApartmentFirstSale ? (
                    <ApartmentCatalogPrices
                        apartment={apartment}
                        formExtraFieldErrorMessages={formExtraFieldErrorMessages}
                    />
                ) : (
                    <MaximumPriceCalculationFieldSet
                        apartment={apartment}
                        setMaximumPrices={setMaximumPrices}
                        saleForm={saleForm}
                        formExtraFieldErrorMessages={formExtraFieldErrorMessages}
                    />
                )}
                <OwnershipsListFieldSet formObject={saleForm} />
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

export default LoadedApartmentSalesPage;
