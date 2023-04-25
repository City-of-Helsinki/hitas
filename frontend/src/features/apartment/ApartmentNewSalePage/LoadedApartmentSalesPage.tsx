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
import {ApartmentSaleSchema, errorMessages, IApartmentDetails, IApartmentSaleForm} from "../../../common/schemas";
import {hdsToast, today} from "../../../common/utils";
import ApartmentCatalogPrices from "./ApartmentCatalogPrices";
import MaximumPriceCalculationFieldSet from "./MaximumPriceCalculationFieldSet";
import OwnershipsListFieldSet from "./OwnershipsListFieldSet";

const LoadedApartmentSalesPage = ({apartment}: {apartment: IApartmentDetails}) => {
    const navigate = useNavigate();

    const isApartmentFirstSale = !apartment.prices.first_purchase_date;
    const hasValidCatalogPrices =
        apartment.prices.catalog_purchase_price !== null &&
        apartment.prices.catalog_share_of_housing_company_loans !== null &&
        apartment.prices.catalog_acquisition_price !== null;

    const [maximumPrices, setMaximumPrices] = useState<
        | undefined
        | {
              maximumPrice: number;
              debtFreePurchasePrice: number;
              apartmentShareOfHousingCompanyLoans: number;
              index: string;
          }
    >(
        isApartmentFirstSale && hasValidCatalogPrices
            ? {
                  maximumPrice: apartment.prices.catalog_purchase_price ?? 0,
                  debtFreePurchasePrice: apartment.prices.catalog_acquisition_price ?? 0,
                  apartmentShareOfHousingCompanyLoans: apartment.prices.catalog_share_of_housing_company_loans ?? 0,
                  index: "",
              }
            : undefined
    );

    // ************************
    // * Form data and schema *
    // ************************

    const initialFormData: IApartmentSaleForm = {
        notification_date: today(),
        purchase_date: "",
        purchase_price: isApartmentFirstSale && hasValidCatalogPrices ? apartment.prices.catalog_purchase_price : null,
        apartment_share_of_housing_company_loans:
            isApartmentFirstSale && hasValidCatalogPrices
                ? apartment.prices.catalog_share_of_housing_company_loans
                : null,
        exclude_from_statistics: false,
    };
    const initialFormOwnershipsList = apartment.ownerships.map((o) => ({...o, key: uuidv4()}));

    // Hard Errors
    // ApartmentSaleSchema with additional validation related to maximum price calculation
    const RefinedApartmentSaleSchema: ZodSchema = ApartmentSaleSchema.superRefine((data, ctx) => {
        if (!isApartmentFirstSale) {
            // Sale can't be made without a confirmed maximum price calculation.
            if (maximumPrices === undefined) {
                ctx.addIssue({
                    code: z.ZodIssueCode.custom,
                    path: ["maximum_price_calculation"],
                    message: "Enimmäishintalaskelma puuttuu.",
                });
                return;
            }
            // The apartment share of housing company loans must match the maximum price calculations.
            if (data.apartment_share_of_housing_company_loans !== maximumPrices.apartmentShareOfHousingCompanyLoans) {
                ctx.addIssue({
                    code: z.ZodIssueCode.custom,
                    path: ["apartment_share_of_company_loans"],
                    message: errorMessages.loanShareChanged,
                });
            }
        }
    });

    // Soft Errors
    const resolver = (data, context, options) => {
        return zodResolver(
            RefinedApartmentSaleSchema.superRefine((data, ctx) => {
                if (!isApartmentFirstSale) {
                    // Price can not be bigger than the maximum price calculations maximum price.
                    if (
                        !warningsGiven.purchase_price &&
                        (!maximumPrices || data.purchase_price > maximumPrices.maximumPrice)
                    ) {
                        ctx.addIssue({
                            code: z.ZodIssueCode.custom,
                            path: ["purchase_price"],
                            message: errorMessages.overMaxPrice,
                        });
                    }
                } else {
                    // We should show a warning and ask for confirmation if catalog prices are missing
                    if (
                        !warningsGiven.catalog_acquisition_price &&
                        (!hasValidCatalogPrices ||
                            (apartment.prices.catalog_acquisition_price !== null &&
                                (data.purchase_price + data.apartment_share_of_housing_company_loans >
                                    apartment.prices.catalog_acquisition_price ||
                                    data.purchase_price + data.apartment_share_of_housing_company_loans <
                                        apartment.prices.catalog_acquisition_price)))
                    ) {
                        ctx.addIssue({
                            code: z.ZodIssueCode.custom,
                            path: ["catalog_acquisition_price"],
                        });
                    }
                }
            })
        )(data, context, {...options, mode: "sync"});
    };

    const saleForm = useForm({
        defaultValues: {...initialFormData, ownerships: initialFormOwnershipsList},
        mode: "all",
        resolver: resolver,
    });

    // ***********************
    // * Creating a new sale *
    // ***********************

    const [createSale, {isLoading: isCreateSaleLoading}] = useCreateSaleMutation();

    // Certain form errors should be able to be ignored.
    const [isWarningModalVisible, setIsWarningModalVisible] = useState(false);
    const noWarningsGiven = {purchase_price: false, catalog_acquisition_price: false};
    const [warningsGiven, setWarningsGiven] = useState(noWarningsGiven);
    const [warningMessage, setWarningMessage] = useState("");

    const closeWarningsModal = () => {
        setWarningsGiven(noWarningsGiven);
        setWarningMessage("");
        setIsWarningModalVisible(false);
    };

    // We need a reference to the form-element to be able to dispatch a submit event dynamically
    const formRef = useRef<HTMLFormElement | null>(null);
    const handleSaveButtonClick = () => {
        // Dispatch submit event, as the "Tallenna"-button isn't inside the sale form element
        formRef.current && formRef.current.dispatchEvent(new Event("submit", {cancelable: true, bubbles: true}));
    };

    // Sale form was submitted without any errors
    const onSaleFormSubmitValid = () => {
        // Proceed to creating the sale.
        createApartmentSale(saleForm.getValues(), apartment);
    };

    // Sale form was submitted with errors
    const onSaleFormSubmitInvalid = (errors) => {
        // If errors only include ones that can be ignored, show a warning modal and continue creation process
        if (errors.purchase_price && errors.purchase_price.type === z.ZodIssueCode.custom) {
            setIsWarningModalVisible(true);
            setWarningsGiven((prev) => ({...prev, purchase_price: true}));
            setWarningMessage("Kauppahinta ylittää laskelman enimmäishinnan.");
        } else if (
            errors.catalog_acquisition_price &&
            errors.catalog_acquisition_price.type === z.ZodIssueCode.custom
        ) {
            setIsWarningModalVisible(true);
            setWarningsGiven((prev) => ({...prev, catalog_acquisition_price: true}));
            setWarningMessage(getCatalogPriceError());
        } else {
            hdsToast.error(`Virhe luodessa asunnon kauppaa!`);
            // eslint-disable-next-line no-console
            console.error(errors);
        }
    };

    const getCatalogPriceError = () => {
        const acquisitionPrice =
            saleForm.getValues("purchase_price") + saleForm.getValues("apartment_share_of_housing_company_loans");

        if (!hasValidCatalogPrices) {
            return errorMessages.catalogPricesMissing;
        } else if (apartment.prices.catalog_acquisition_price !== null) {
            if (acquisitionPrice > apartment.prices.catalog_acquisition_price) {
                return errorMessages.catalogOverMaxPrice;
            } else if (acquisitionPrice < apartment.prices.catalog_acquisition_price) {
                return errorMessages.catalogUnderMaxPrice;
            }
        }
        return "";
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

    // **************
    // * Validation *
    // **************

    // Check if the parts of the sale form needed for a max price calculation are currently valid
    const hasLoanValueChanged =
        !isApartmentFirstSale &&
        maximumPrices !== undefined &&
        saleForm.getValues("apartment_share_of_housing_company_loans") !==
            maximumPrices.apartmentShareOfHousingCompanyLoans;

    // Disable the saving button when the form has errors or when there is no valid calculation
    const isSavingDisabled = isApartmentFirstSale
        ? !RefinedApartmentSaleSchema.safeParse(saleForm.getValues()).success
        : maximumPrices === undefined || !RefinedApartmentSaleSchema.safeParse(saleForm.getValues()).success;

    // Disable all fields not related to creating a calculation when it's missing (Does not apply for first sales)
    const isMaximumPriceCalculationMissing = !isApartmentFirstSale && maximumPrices === undefined;

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
                                disabled={isMaximumPriceCalculationMissing}
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
                            <div>
                                <NumberInput
                                    name="purchase_price"
                                    label="Kauppahinta"
                                    formObject={saleForm}
                                    unit="€"
                                    fractionDigits={2}
                                    disabled={isMaximumPriceCalculationMissing}
                                    required
                                />
                            </div>
                            <div className={hasLoanValueChanged ? "input-field--invalid" : ""}>
                                <NumberInput
                                    name="apartment_share_of_housing_company_loans"
                                    label="Osuus yhtiön lainoista"
                                    formObject={saleForm}
                                    unit="€"
                                    required
                                />
                            </div>
                        </div>
                        <Checkbox
                            name="exclude_from_statistics"
                            label="Ei tilastoihin (esim. sukulaiskauppa)"
                            formObject={saleForm}
                            triggerField="purchase_price"
                            disabled={isMaximumPriceCalculationMissing}
                        />
                    </form>
                </Fieldset>

                {isApartmentFirstSale ? (
                    <ApartmentCatalogPrices
                        apartment={apartment}
                        errorMessage={getCatalogPriceError()}
                    />
                ) : (
                    <MaximumPriceCalculationFieldSet
                        apartment={apartment}
                        setMaximumPrices={setMaximumPrices}
                        saleForm={saleForm}
                    />
                )}
                <OwnershipsListFieldSet
                    formObject={saleForm}
                    disabled={isMaximumPriceCalculationMissing}
                />
            </div>

            <div className="row row--buttons">
                <NavigateBackButton />
                <SaveButton
                    onClick={handleSaveButtonClick}
                    isLoading={isCreateSaleLoading}
                    disabled={isSavingDisabled}
                />
            </div>

            <ConfirmDialogModal
                successText="Kauppa tallennettu varoituksesta huolimatta"
                isLoading={isCreateSaleLoading}
                isVisible={isWarningModalVisible}
                setIsVisible={setIsWarningModalVisible}
                modalText={`${warningMessage} Haluatko varmasti tallentaa kaupan?`}
                modalHeader="Vahvista kaupan tallennus"
                cancelAction={closeWarningsModal}
                confirmAction={handleSaveButtonClick}
                buttonText="Vahvista tallennus"
            />
        </div>
    );
};

export default LoadedApartmentSalesPage;
