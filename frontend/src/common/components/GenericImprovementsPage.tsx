import {Button, Fieldset, IconCrossCircle, IconPlus, Tooltip} from "hds-react";
import {useState} from "react";
import {SubmitHandler, useFieldArray, useForm, useFormContext} from "react-hook-form";
import {
    ApartmentImprovementsFormSchema,
    HousingCompanyImprovementsFormSchema,
    IApartmentConstructionPriceIndexImprovement,
    IApartmentDetails,
    IApartmentImprovementsForm,
    IHousingCompanyDetails,
    IHousingCompanyImprovementsForm,
} from "../schemas";
import {CheckboxInput, FormProviderForm, NumberInput, SelectInput, TextInput} from "./forms";
import {ConfirmDialogModal, NavigateBackButton, SaveButton} from "./index";

import {zodResolver} from "@hookform/resolvers/zod";
import {useNavigate} from "react-router-dom";
import {v4 as uuidv4} from "uuid";
import {usePatchApartmentMutation, usePatchHousingCompanyMutation} from "../../app/services";
import {hdsToast} from "../utils";

type IWritableImprovement = Omit<IApartmentConstructionPriceIndexImprovement, "value"> & {
    value: number | null;
    key: string;
    saved: boolean;
};

const depreciationChoices = [
    {label: "0%", value: "0.0"},
    {label: "2.5%", value: "2.5"},
    {label: "10.0%", value: "10.0"},
];

const emptyImprovement = {
    saved: false,
    name: "",
    value: null,
    completion_date: "",
    no_deductions: false,
    depreciation_percentage: null,
};

const ImprovementAddEmptyLineButton = ({append}) => {
    return (
        <Button
            onClick={() =>
                append({
                    key: uuidv4(),
                    ...emptyImprovement,
                })
            }
            iconLeft={<IconPlus />}
            theme="black"
        >
            Lisää parannus
        </Button>
    );
};

const ImprovementRemoveLineButton = ({name, index, remove}) => {
    const formObject = useFormContext();
    const [isConfirmVisible, setIsConfirmVisible] = useState(false);

    const handleRemoveButtonPress = () => {
        const improvementValues = formObject.getValues(`${name}.${index}`);

        // If all fields are empty, remove the improvement without confirmation
        if (!improvementValues.name && !improvementValues.value && !improvementValues.completion_date) {
            remove(index);
            return;
        } else {
            setIsConfirmVisible(true);
        }
    };

    return (
        <div className="icon--remove">
            <IconCrossCircle
                size="m"
                onClick={handleRemoveButtonPress}
            />

            <ConfirmDialogModal
                modalText="Haluatko varmasti poistaa parannuksen?"
                buttonText="Poista"
                successText="Parannus poistettu"
                isVisible={isConfirmVisible}
                setIsVisible={setIsConfirmVisible}
                confirmAction={() => remove(index)}
                cancelAction={() => setIsConfirmVisible(false)}
            />
        </div>
    );
};

const ImprovementsListHeaders = ({showNoDeductions, showDeprecationPercentage}) => {
    return (
        <li className="improvement-headers">
            <header>
                Nimi <span>*</span>
            </header>
            <header>
                Arvo <span>*</span>
            </header>
            <header>
                Kuukausi <span>*</span>
            </header>
            <Tooltip
                className="header__tooltip"
                placement="left-start"
            >
                Muodossa 'YYYY-MM', esim. '2022-01'
            </Tooltip>
            {showNoDeductions && (
                <>
                    <header>
                        Ei vähennyksiä <span>*</span>
                    </header>
                    <Tooltip
                        className="header__tooltip2"
                        placement="left-start"
                    >
                        Parannuksesta ei vähennetä omavastuu osuutta tai poistoja ja tehdään indeksitarkistus.
                    </Tooltip>
                </>
            )}
            {showDeprecationPercentage && (
                <header>
                    Poistoprosentti <span>*</span>
                </header>
            )}
        </li>
    );
};

const ImprovementsListItems = ({name, showNoDeductions, showDeprecationPercentage, remove}) => {
    const formObject = useFormContext();
    const improvements = formObject.watch(name);
    return (
        <>
            {improvements.map((improvement: IWritableImprovement, index) => (
                <li
                    className="improvements-list-item"
                    key={`improvement-item-${improvement.key}`}
                >
                    <TextInput
                        name={`${name}.${index}.name`}
                        required
                    />
                    <NumberInput
                        name={`${name}.${index}.value`}
                        allowDecimals
                        required
                    />
                    <TextInput
                        name={`${name}.${index}.completion_date`}
                        required
                    />
                    {showNoDeductions && (
                        <CheckboxInput
                            name={`${name}.${index}.no_deductions`}
                            label=""
                        />
                    )}
                    {showDeprecationPercentage && (
                        <SelectInput
                            name={`${name}.${index}.depreciation_percentage`}
                            label=""
                            options={depreciationChoices}
                            setDirectValue
                            required
                        />
                    )}
                    <ImprovementRemoveLineButton
                        name={name}
                        index={index}
                        remove={remove}
                    />
                </li>
            ))}
        </>
    );
};

export const ImprovementFieldSet = ({fieldsetHeader, name, showNoDeductions, showDeprecationPercentage}) => {
    const formObject = useFormContext();
    const {fields, append, remove} = useFieldArray({
        name: name,
        control: formObject.control,
    });
    formObject.register(name);

    return (
        <Fieldset heading={fieldsetHeader}>
            <ul className="improvements-list">
                {fields.length ? (
                    <>
                        <ImprovementsListHeaders
                            showNoDeductions={showNoDeductions}
                            showDeprecationPercentage={showDeprecationPercentage}
                        />
                        <ImprovementsListItems
                            name={name}
                            showNoDeductions={showNoDeductions}
                            showDeprecationPercentage={showDeprecationPercentage}
                            remove={remove}
                        />
                    </>
                ) : (
                    <div>Ei parannuksia</div>
                )}
                <li className="row row--buttons">
                    <ImprovementAddEmptyLineButton append={append} />
                </li>
            </ul>
        </Fieldset>
    );
};

const ImprovementFieldSets = ({housingCompany, apartment}) => {
    // New Hitas Housing Company
    if (apartment === undefined && housingCompany.new_hitas) {
        return (
            <div className="field-sets">
                <ImprovementFieldSet
                    fieldsetHeader="Taloyhtiön parannukset"
                    name="market_price_index" // New Hitas uses only MPI-improvements
                    showNoDeductions={true}
                    showDeprecationPercentage={false}
                />
            </div>
        );
    }

    // Old Hitas Housing Company and Apartment
    return (
        <div className="field-sets">
            <ImprovementFieldSet
                fieldsetHeader="Markkinakustannusindeksillä laskettavat parannukset"
                name="market_price_index"
                showNoDeductions={true} // Always enabled for MPI-improvements
                showDeprecationPercentage={false}
            />
            <ImprovementFieldSet
                fieldsetHeader="Rakennuskustannusindeksillä laskettavat parannukset"
                name="construction_price_index"
                showNoDeductions={false}
                showDeprecationPercentage={apartment !== undefined} // Only enabled for Apartment CPI-improvements
            />
        </div>
    );
};

type IGenericImprovementsPage = {
    housingCompany: IHousingCompanyDetails;
    apartment?: IApartmentDetails;
};

const GenericImprovementsPage = ({housingCompany, apartment}: IGenericImprovementsPage) => {
    const navigate = useNavigate();

    // Select either apartment or housing company
    let formSchema;
    let patchFunctionHook;
    let patchFunctionArguments;
    let rawImprovements;

    if (apartment !== undefined) {
        formSchema = ApartmentImprovementsFormSchema;
        patchFunctionHook = usePatchApartmentMutation;
        patchFunctionArguments = {
            housingCompanyId: housingCompany.id,
            id: apartment.id,
        };
        rawImprovements = apartment.improvements;
    } else {
        formSchema = HousingCompanyImprovementsFormSchema;
        patchFunctionHook = usePatchHousingCompanyMutation;
        patchFunctionArguments = {
            id: housingCompany.id,
        };
        rawImprovements = housingCompany.improvements;
    }

    // Form
    const initialFormData = {
        market_price_index: rawImprovements.market_price_index.map((i) => ({
            key: uuidv4(),
            saved: true,
            ...i,
        })),
        construction_price_index: rawImprovements.construction_price_index.map((i) => ({
            key: uuidv4(),
            saved: true,
            ...i,
        })),
    };

    const formObject = useForm({
        resolver: zodResolver(formSchema),
        defaultValues: initialFormData,
        mode: "all",
    });

    // API Handling
    const [patchFunction, {isLoading}] = patchFunctionHook();

    const onSubmit: SubmitHandler<IApartmentImprovementsForm | IHousingCompanyImprovementsForm> = (formData) => {
        const formattedData = {
            // Filter empty improvements away (no value entered)
            improvements: {
                market_price_index: formData.market_price_index.filter((i) => i.name || i.value),
                construction_price_index: formData.construction_price_index.filter((i) => i.name || i.value),
            },
        };

        patchFunction({
            ...patchFunctionArguments,
            data: formattedData,
        })
            .unwrap()
            .then(() => {
                hdsToast.success("Parannukset tallennettu onnistuneesti!");
                navigate(-1); // get the user back to where they opened this view
            })
            .catch(() => hdsToast.error("Virhe tallentaessa parannuksia!"));
    };

    return (
        <FormProviderForm
            formObject={formObject}
            onSubmit={onSubmit}
        >
            <ImprovementFieldSets
                housingCompany={housingCompany}
                apartment={apartment}
            />

            <div className="row row--buttons">
                <NavigateBackButton />
                <SaveButton
                    type="submit"
                    isLoading={isLoading}
                />
            </div>
        </FormProviderForm>
    );
};

export default GenericImprovementsPage;
