import {zodResolver} from "@hookform/resolvers/zod/dist/zod";
import {Dialog, Fieldset} from "hds-react";
import {useRef, useState} from "react";
import {useForm} from "react-hook-form";
import {useNavigate} from "react-router-dom";
import {v4 as uuidv4} from "uuid";
import {z, ZodSchema} from "zod";
import {useCreateSaleMutation, useSaveApartmentMaximumPriceMutation} from "../../../app/services";
import {NavigateBackButton, QueryStateHandler, SaveButton} from "../../../common/components";
import ConfirmDialogModal from "../../../common/components/ConfirmDialogModal";
import {Checkbox, DateInput, NumberInput} from "../../../common/components/form";
import {
    ApartmentSaleFormSchema,
    ApartmentSaleSchema,
    errorMessages,
    IApartmentDetails,
    IApartmentMaximumPrice,
    IApartmentSaleForm,
    OwnershipsListSchema,
} from "../../../common/schemas";
import {formatDate, hdsToast, today} from "../../../common/utils";
import MaximumPriceModalContent from "../components/ApartmentMaximumPriceBreakdownModal";
import MaximumPriceCalculationExists from "./MaximumPriceCalculationExists";
import MaximumPriceCalculationMissing from "./MaximumPriceCalculationMissing";
import MaximumPriceModalError from "./MaximumPriceModalError";
import OwnershipsList from "./OwnershipsList";

const LoadedApartmentSalesPage = ({
    apartment,
    maxPriceCalculation,
}: {
    apartment: IApartmentDetails;
    maxPriceCalculation: IApartmentMaximumPrice | null;
}) => {
    const [isModalVisible, setIsModalVisible] = useState(false);
    const [isWarningModalVisible, setIsWarningModalVisible] = useState(false);
    const navigate = useNavigate();
    // We need a reference to the formik form-element, to be able to dispatch a submit event dynamically
    const formRef = useRef<HTMLFormElement | null>(null);
    // Queries and mutations
    const [saveSale, {error, isLoading}] = useCreateSaleMutation();
    const [saveMaximumPrice, {data: maxPriceData, error: maxPriceError, isLoading: isMaxPriceLoading}] =
        useSaveApartmentMaximumPriceMutation();

    //  Maximum price calculation variables
    const [maxPrices, setMaxPrices] = useState({
        maximumPrice: apartment.prices.maximum_prices.confirmed?.maximum_price,
        maxPricePerSquare: maxPriceCalculation
            ? maxPriceCalculation.maximum_price_per_square
            : maxPriceData?.maximum_price_per_square,
        debtFreePurchasePrice: maxPriceCalculation
            ? maxPriceCalculation.calculations.construction_price_index.calculation_variables.debt_free_price
            : maxPriceData?.calculations.construction_price_index.calculation_variables.debt_free_price,
        index: maxPriceData ? maxPriceData.index : maxPriceCalculation?.index,
    });

    // *********************************
    // * Form data, schema & variables *
    // *********************************
    const initialFormData: IApartmentSaleForm = {
        notification_date: today(),
        purchase_date: apartment.prices.maximum_prices.confirmed?.valid.is_valid
            ? apartment.prices.maximum_prices.confirmed.calculation_date
            : "",
        purchase_price: null,
        apartment_share_of_housing_company_loans: maxPriceCalculation
            ? maxPriceCalculation.calculations.construction_price_index.calculation_variables
                  .apartment_share_of_housing_company_loans
            : null,
        exclude_from_statistics: false,
    };
    const formOwnershipsList = apartment.ownerships.map((o) => ({...o, key: uuidv4()}));

    const [warningsGiven, setWarningsGiven] = useState({purchase_price: false, has_loan_share_changed: false});

    // React hook form
    const resolver = (data, context, options) => {
        const refinedData: ZodSchema = ApartmentSaleSchema.superRefine((data, ctx) => {
            if ((data.purchase_price as number) > (maxPrices.maximumPrice as number) && !warningsGiven.purchase_price) {
                ctx.addIssue({
                    code: z.ZodIssueCode.custom,
                    path: ["purchase_price"],
                    message: errorMessages.overMaxPrice,
                });
            }
            if (hasLoanValueChanged) {
                ctx.addIssue({
                    code: z.ZodIssueCode.custom,
                    path: ["apartment_share_of_company_loans"],
                    message: errorMessages.loanShareChanged,
                });
            }
        });
        return zodResolver(refinedData)(data, context, {...options, mode: "sync"});
    };
    const saleForm = useForm({
        defaultValues: {...initialFormData, ownerships: formOwnershipsList},
        mode: "all",
        resolver: resolver,
    });

    const {
        setFocus,
        watch,
        formState: {isDirty, errors},
    } = saleForm;

    // ********************************
    // * Button / UI-element handlers *
    // ********************************

    // Handle "calculate maximum price"-button press
    const handleCalculateButton = () => {
        if (
            saleForm.getValues("purchase_date") &&
            !isNaN(Number(saleForm.getValues("apartment_share_of_housing_company_loans")))
        ) {
            // Validate relevant fields for the calculation
            if (errors.purchase_date || errors.apartment_share_of_housing_company_loans) {
                if (errors.purchase_date)
                    hdsToast.error(
                        <>
                            Tarkista <span>kauppakirjan päivämäärä</span>!
                        </>
                    );
                else
                    hdsToast.error(
                        <>
                            Tarkista <span>yhtiön lainaosuus</span>!
                        </>
                    );
            } else makeNewCalculation();
        } else
            hdsToast.error(
                <>
                    Enimmäishintojen laskemiseen tarvitaan <span>kauppakirjan päivämäärä</span> sekä{" "}
                    <span>yhtiön lainaosuus</span>!
                </>
            );
    };

    // Dispatch submit event, as the "Tallenna"-button isn't inside the sale form element
    const handleSaveButtonClick = () => {
        formRef.current && formRef.current.dispatchEvent(new Event("submit", {cancelable: true, bubbles: true}));
    };

    // Handle warning dialog confirm action
    const handleWarningDialogAction = () => {
        setWarningsGiven((prev) => {
            return {...prev, purchase_price: true};
        });
        saveConfirmedSale(saleForm.getValues(), apartment);
    };

    // Handle sale form submit button
    const saveConfirmedSale = (data, apartment) => {
        setIsWarningModalVisible(() => false);
        saveSale({
            data: data,
            apartmentId: apartment.id,
            housingCompanyId: apartment.links.housing_company.id,
        }).then(() => {
            if (error) {
                hdsToast.error("Kaupan tallentaminen epäonnistui.");
            } else {
                hdsToast.success("Kauppa tallennettu onnistuneesti!");
                if (data.conditions_of_sale_created) {
                    hdsToast.info("Asunnolle luotiin myyntiehtoja.");
                }
                navigate(`/housing-companies/${apartment.links.housing_company.id}/apartments/${apartment.id}`);
            }
        });
    };
    const onInvalidSubmit = (errors) => {
        if (errors.purchase_price?.type === "custom" && warningsGiven.purchase_price) {
            setWarningsGiven((prevState) => {
                return {...prevState, purchase_price: false};
            });
            saveConfirmedSale(saleForm.getValues(), apartment);
        }
        setIsWarningModalVisible(true);
        console.warn(errors);
    };
    const onValidSubmit = (data) => {
        if (isOwnershipListFormValid) saveConfirmedSale(saleForm.getValues(), apartment);
        else setIsWarningModalVisible(true);
    };

    // **************
    // * Validation *
    // **************

    const purchasePrice = watch("purchase_price");
    watch(["purchase_date", "notification_date"]);
    const loanShare = watch("apartment_share_of_housing_company_loans");

    const hasCalculation = !!maxPriceCalculation || !!maxPriceData;

    // Check if the parts of the sale form needed for a max price calculation are currently valid
    const isCalculationFormValid = () => {
        return ApartmentSaleFormSchema.partial().safeParse({
            purchase_date: saleForm.getValues("purchase_date"),
            apartment_share_of_housing_company_loans: saleForm.getValues("apartment_share_of_housing_company_loans"),
        });
    };

    // Check if the parts of the sale form needed for a max price calculation are currently valid
    const isOwnershipListFormValid = OwnershipsListSchema.safeParse(saleForm.getValues("ownerships")).success;

    // Check if the loan share value is the same as in the calculation
    const hasLoanValueChanged =
        loanShare !==
            maxPriceCalculation?.calculations[maxPriceCalculation.index].calculation_variables
                .apartment_share_of_housing_company_loans && maxPriceCalculation;

    // Disable the saving button when the form has errors or when there is no valid calculation
    const isSavingDisabled =
        isNaN(Number(purchasePrice)) ||
        purchasePrice > 999999 ||
        !!hasLoanValueChanged ||
        !hasCalculation ||
        !isOwnershipListFormValid;

    // *************************
    // * Max price calculation *
    // *************************

    // Function for updating the maxPrices useState object, and displaying the calculation breakdown (or error) modal
    const updateMaxPrices = () => {
        setMaxPrices({
            maximumPrice: apartment.prices.maximum_prices.confirmed?.maximum_price,
            maxPricePerSquare: maxPriceCalculation
                ? maxPriceCalculation.calculations.construction_price_index.calculation_variables.debt_free_price_m2
                : maxPriceData?.calculations.construction_price_index.calculation_variables.debt_free_price_m2,
            debtFreePurchasePrice: maxPriceCalculation
                ? maxPriceCalculation.calculations.construction_price_index.calculation_variables.debt_free_price
                : maxPriceData?.calculations.construction_price_index.calculation_variables.debt_free_price,
            index: maxPriceData ? maxPriceData.index : maxPriceCalculation?.index,
        });
        // Show the breakdown in the display modal
        setIsModalVisible(true);
    };

    // Calculate a new maximum price calculation
    const makeNewCalculation = () => {
        const purchaseDate: string | null = saleForm.getValues("purchase_date") ?? null;
        const loanShare: number | null = saleForm.getValues("apartment_share_of_housing_company_loans") ?? null;
        saveMaximumPrice({
            data: {
                calculation_date: purchaseDate,
                apartment_share_of_housing_company_loans: loanShare ?? 0,
                apartment_share_of_housing_company_loans_date: purchaseDate,
                additional_info: "",
            },
            apartmentId: apartment.id,
            housingCompanyId: apartment.links.housing_company.id,
        }).then(() => updateMaxPrices());
    };

    // *************************
    // * Functional components *
    // *************************

    return (
        <div className="view--apartment-conditions-of-sale">
            <div className="fieldsets">
                <Fieldset heading={warningsGiven.purchase_price ? "Kaupan tiedot *" : "Kaupan tiedot"}>
                    <form
                        ref={formRef}
                        onSubmit={saleForm.handleSubmit(onValidSubmit, onInvalidSubmit)}
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
                            <div>
                                <NumberInput
                                    name="purchase_price"
                                    label="Kauppahinta"
                                    formObject={saleForm}
                                    unit="€"
                                    fractionDigits={2}
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
                        />
                    </form>
                </Fieldset>

                <Fieldset
                    heading={`Enimmäishintalaskelma ${
                        maxPriceCalculation
                            ? `(vahvistettu ${formatDate(
                                  apartment.prices.maximum_prices.confirmed?.confirmed_at as string
                              )})`
                            : ""
                    } *`}
                >
                    {maxPriceCalculation ? (
                        <MaximumPriceCalculationExists
                            maxPriceCalculation={maxPriceCalculation}
                            hasLoanValueChanged={hasLoanValueChanged}
                            purchasePrice={purchasePrice}
                            maxPrices={maxPrices}
                            warningsGiven={warningsGiven}
                            maxPriceData={maxPriceData}
                            handleCalculateButton={handleCalculateButton}
                            isCalculationFormValid={isCalculationFormValid}
                        />
                    ) : (
                        <MaximumPriceCalculationMissing
                            handleCalculateButton={handleCalculateButton}
                            saleForm={saleForm}
                        />
                    )}
                </Fieldset>
                <OwnershipsList formObject={saleForm} />
            </div>

            <div className="row row--buttons">
                <NavigateBackButton />
                <SaveButton
                    onClick={handleSaveButtonClick}
                    isLoading={isLoading}
                    disabled={!isDirty || isSavingDisabled}
                />
            </div>

            <Dialog
                id="maximum-price-confirmation-modal"
                closeButtonLabelText=""
                aria-labelledby=""
                isOpen={isModalVisible}
                close={() => setIsModalVisible(false)}
                boxShadow
            >
                <Dialog.Header
                    id="maximum-price-confirmation-modal-header"
                    title="Vahvistetaanko enimmäishintalaskelma?"
                />
                <QueryStateHandler
                    data={maxPriceData}
                    error={maxPriceError}
                    isLoading={isMaxPriceLoading}
                    errorComponent={
                        <MaximumPriceModalError
                            error={maxPriceError}
                            setIsModalVisible={setIsModalVisible}
                        />
                    }
                >
                    <MaximumPriceModalContent
                        calculation={maxPriceData as IApartmentMaximumPrice}
                        apartment={apartment}
                        setIsModalVisible={setIsModalVisible}
                    />
                </QueryStateHandler>
            </Dialog>

            <ConfirmDialogModal
                successText="Kauppa tallennettu varoituksesta huolimatta"
                isLoading={isLoading}
                isVisible={isWarningModalVisible}
                setIsVisible={setIsWarningModalVisible}
                modalText="Haluatko tallentaa kaupan vaikka kauppahinta ylittää laskelman enimmäishinnan?"
                modalHeader="Vahvista kaupan tallennus"
                cancelAction={() => {
                    setIsWarningModalVisible(false);
                    setFocus("purchase_price");
                }}
                confirmAction={handleWarningDialogAction}
                buttonText="Vahvista tallennus"
            />
        </div>
    );
};

export default LoadedApartmentSalesPage;
