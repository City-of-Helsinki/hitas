import {useContext, useRef, useState} from "react";

import {Button, Fieldset, IconCrossCircle, IconPlus, Tooltip} from "hds-react";
import {useNavigate} from "react-router-dom";
import {v4 as uuidv4} from "uuid";

import {zodResolver} from "@hookform/resolvers/zod";
import {FormProvider, SubmitHandler, useFieldArray, useForm, useFormContext} from "react-hook-form";
import {usePatchHousingCompanyMutation} from "../../app/services";
import {ConfirmDialogModal, Heading, NavigateBackButton, SaveButton} from "../../common/components";
import {NumberInput, TextInput} from "../../common/components/form";
import CheckboxInput from "../../common/components/form/CheckboxInput";
import {
    HousingCompanyImprovementsFormSchema,
    IHousingCompanyImprovementsForm,
    IImprovement,
    IMarketPriceIndexImprovement,
} from "../../common/schemas";
import {hdsToast} from "../../common/utils";
import HousingCompanyViewContextProvider, {
    HousingCompanyViewContext,
} from "./components/HousingCompanyViewContextProvider";

type IWritableMarketImprovement = Omit<IMarketPriceIndexImprovement, "value"> & {
    value: number | null;
    key: string;
    saved: boolean;
};
type IWritableConsImprovement = Omit<IImprovement, "value"> & {value: number | null; key: string; saved: boolean};

const emptyImprovement = {
    saved: false,
    name: "",
    value: null,
    completion_date: "",
    no_deductions: false,
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

const ImprovementsListHeaders = ({showNoDeductions}) => {
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
                        Parannuksesta ei vähennetä omavastuu osuutta tai poistoja ja tehdään indeksitarkistus. Käytetään
                        ainoastaan vanhoissa Hitas säännöissä.
                    </Tooltip>
                </>
            )}
        </li>
    );
};

const ImprovementsListItems = ({name, showNoDeductions, remove}) => {
    const formObject = useFormContext();
    const improvements = formObject.watch(name);
    return (
        <>
            {improvements.map((improvement: IWritableMarketImprovement | IWritableConsImprovement, index) => (
                <li
                    className="improvements-list-item"
                    key={`improvement-item-${improvement.key}`}
                >
                    <TextInput
                        name={`${name}.${index}.name`}
                        formObject={formObject}
                        required
                    />
                    <NumberInput
                        name={`${name}.${index}.value`}
                        allowDecimals
                        formObject={formObject}
                        required
                    />
                    <TextInput
                        name={`${name}.${index}.completion_date`}
                        formObject={formObject}
                        required
                    />
                    {showNoDeductions ? (
                        <CheckboxInput
                            name={`${name}.${index}.no_deductions`}
                            label=""
                            formObject={formObject}
                        />
                    ) : null}
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

const ImprovementFieldSet = ({fieldsetHeader, name, showNoDeductions}) => {
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
                        <ImprovementsListHeaders showNoDeductions={showNoDeductions} />
                        <ImprovementsListItems
                            name={name}
                            showNoDeductions={showNoDeductions}
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

const LoadedHousingCompanyImprovementsPage = () => {
    const navigate = useNavigate();
    const {housingCompany} = useContext(HousingCompanyViewContext);
    if (!housingCompany) throw new Error("Housing company not found");

    const [patchHousingCompany, {isLoading}] = usePatchHousingCompanyMutation();

    const initialFormData = {
        market_price_index: housingCompany.improvements.market_price_index.map((i) => ({
            key: uuidv4(),
            saved: true,
            ...i,
        })),
        construction_price_index: housingCompany.improvements.construction_price_index.map((i) => ({
            key: uuidv4(),
            saved: true,
            ...i,
        })),
    };

    const formRef = useRef<HTMLFormElement | null>(null);
    const formObject = useForm({
        resolver: zodResolver(HousingCompanyImprovementsFormSchema),
        defaultValues: initialFormData,
        mode: "all",
    });

    // Format and send data to the API
    const onSubmit: SubmitHandler<IHousingCompanyImprovementsForm> = (formData) => {
        const formattedData = {
            // Filter empty improvements away (no value entered)
            improvements: {
                market_price_index: formData.market_price_index.filter((i) => i.name || i.value),
                construction_price_index: formData.construction_price_index.filter((i) => i.name || i.value),
            },
        };

        patchHousingCompany({
            id: housingCompany.id,
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
        <>
            <Heading>{housingCompany.name.display} Parannukset</Heading>
            <form
                ref={formRef}
                // eslint-disable-next-line no-console
                onSubmit={formObject.handleSubmit(onSubmit, (errors) => console.warn(formObject, errors))}
            >
                <FormProvider {...formObject}>
                    <div className="field-sets">
                        <ImprovementFieldSet
                            fieldsetHeader="Markkinakustannusindeksillä laskettavat parannukset"
                            name="market_price_index"
                            showNoDeductions={true}
                        />
                        <ImprovementFieldSet
                            fieldsetHeader="Rakennuskustannusindeksillä laskettavat parannukset"
                            name="construction_price_index"
                            showNoDeductions={false}
                        />
                    </div>

                    <div className="row row--buttons">
                        <NavigateBackButton />
                        <SaveButton
                            type="submit"
                            isLoading={isLoading}
                        />
                    </div>
                </FormProvider>
            </form>
        </>
    );
};

const HousingCompanyImprovementsPage = () => {
    return (
        <HousingCompanyViewContextProvider viewClassName="view--create view--create-improvements">
            <LoadedHousingCompanyImprovementsPage />
        </HousingCompanyViewContextProvider>
    );
};

export default HousingCompanyImprovementsPage;
