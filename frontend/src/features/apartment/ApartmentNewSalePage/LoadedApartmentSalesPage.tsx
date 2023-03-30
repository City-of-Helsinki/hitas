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
    ApartmentSaleSchema,
    errorMessages,
    IApartmentDetails,
    IApartmentSaleForm,
    OwnershipsListSchema,
} from "../../../common/schemas";
import {hdsToast, today} from "../../../common/utils";
import MaximumPriceCalculationFieldSet from "./MaximumPriceCalculationFieldSet";
import OwnershipsListFieldSet from "./OwnershipsListFieldSet";

const LoadedApartmentSalesPage = ({apartment}: {apartment: IApartmentDetails}) => {
    const [isWarningModalVisible, setIsWarningModalVisible] = useState(false);
    const navigate = useNavigate();
    // We need a reference to the formik form-element, to be able to dispatch a submit event dynamically
    const formRef = useRef<HTMLFormElement | null>(null);
    // Queries and mutations
    const [createSale, {isLoading: isCreateSaleLoading}] = useCreateSaleMutation();

    //  Maximum price calculation variables
    const [maximumPrices, setMaximumPrices] = useState<
        | undefined
        | {
              maximumPrice: number;
              maxPricePerSquare: number;
              debtFreePurchasePrice: number;
              apartmentShareOfHousingCompanyLoans: number;
              index: string;
          }
    >();

    // *********************************
    // * Form data, schema & variables *
    // *********************************
    const initialFormData: IApartmentSaleForm = {
        notification_date: today(),
        purchase_date: "",
        purchase_price: maximumPrices?.maximumPrice ?? null,
        apartment_share_of_housing_company_loans: maximumPrices?.apartmentShareOfHousingCompanyLoans ?? null,
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

    watch(["purchase_price", "purchase_date", "notification_date", "apartment_share_of_housing_company_loans"]);

    // Check if the parts of the sale form needed for a max price calculation are currently valid
    const hasLoanValueChanged =
        maximumPrices !== undefined &&
        saleForm.getValues("apartment_share_of_housing_company_loans") !==
            maximumPrices.apartmentShareOfHousingCompanyLoans;
    const isOwnershipListFormValid = OwnershipsListSchema.safeParse(saleForm.getValues("ownerships")).success;

    // Disable the saving button when the form has errors or when there is no valid calculation
    const isSavingDisabled = false; // FIXME

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

                <MaximumPriceCalculationFieldSet
                    apartment={apartment}
                    setMaximumPrices={setMaximumPrices}
                    saleForm={saleForm}
                />
                <OwnershipsListFieldSet formObject={saleForm} />
            </div>

            <div className="row row--buttons">
                <NavigateBackButton />
                <SaveButton
                    onClick={handleSaveButtonClick}
                    isLoading={isCreateSaleLoading}
                    disabled={!isDirty || isSavingDisabled}
                />
            </div>

            <ConfirmDialogModal
                successText="Kauppa tallennettu varoituksesta huolimatta"
                isLoading={isCreateSaleLoading}
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
