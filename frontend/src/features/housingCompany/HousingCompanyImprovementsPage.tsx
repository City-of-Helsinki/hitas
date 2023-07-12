import {useContext, useEffect, useState} from "react";

import {Button, Checkbox, Fieldset, IconCrossCircle, IconPlus, Tooltip} from "hds-react";
import {useNavigate} from "react-router-dom";
import {useImmer} from "use-immer";
import {v4 as uuidv4} from "uuid";

import {useSaveHousingCompanyMutation} from "../../app/services";
import {ConfirmDialogModal, FormInputField, Heading, NavigateBackButton, SaveButton} from "../../common/components";
import {IImprovement, IMarketPriceIndexImprovement} from "../../common/schemas";
import {dotted, hdsToast} from "../../common/utils";
import HousingCompanyViewContextProvider, {
    HousingCompanyViewContext,
} from "./components/HousingCompanyViewContextProvider";

type IWritableMarketImprovement = Omit<IMarketPriceIndexImprovement, "value"> & {
    value: number | null;
    key: string;
    saved: boolean;
};
type IWritableConsImprovement = Omit<IImprovement, "value"> & {value: number | null; key: string; saved: boolean};

const ImprovementAddLineButton = ({onClick}) => {
    return (
        <Button
            onClick={onClick}
            iconLeft={<IconPlus />}
            theme="black"
        >
            Lisää parannus
        </Button>
    );
};

const ImprovementRemoveLineButton = ({onClick}) => {
    return (
        <div className="icon--remove">
            <IconCrossCircle
                size="m"
                onClick={(index) => onClick(index)}
            />
        </div>
    );
};

const ImprovementFieldSet = ({
    fieldsetHeader,
    improvements,
    handleAddImprovementLine,
    handleSetImprovementLine,
    setIndexToRemove,
    error,
    showNoDeductions,
}) => {
    return (
        <Fieldset heading={fieldsetHeader}>
            <ul className="improvements-list">
                {improvements.length ? (
                    <>
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
                                        Parannuksesta ei vähennetä omavastuu osuutta tai poistoja ja tehdään
                                        indeksitarkistus. Käytetään ainoastaan vanhoissa Hitas säännöissä.
                                    </Tooltip>
                                </>
                            )}
                        </li>
                        {improvements.map(
                            (improvement: IWritableMarketImprovement | IWritableConsImprovement, index) => (
                                <li
                                    className="improvements-list-item"
                                    key={`improvement-item-${improvement.key}`}
                                >
                                    <FormInputField
                                        inputType="text"
                                        label=""
                                        fieldPath="name"
                                        formData={improvements[index]}
                                        setterFunction={handleSetImprovementLine(index, "name")}
                                        error={error}
                                        required
                                    />
                                    <FormInputField
                                        inputType="number"
                                        fractionDigits={2}
                                        label=""
                                        fieldPath="value"
                                        formData={improvements[index]}
                                        setterFunction={handleSetImprovementLine(index, "value")}
                                        error={error}
                                        required
                                    />
                                    <FormInputField
                                        inputType="text"
                                        label=""
                                        fieldPath="completion_date"
                                        tooltipText={"Muodossa 'YYYY-MM', esim. '2022-01'"}
                                        formData={improvements[index]}
                                        setterFunction={handleSetImprovementLine(index, "completion_date")}
                                        error={error}
                                        required
                                    />
                                    {showNoDeductions && (
                                        <Checkbox
                                            id={`input-no_deductions-${index}`}
                                            checked={improvements[index].no_deductions}
                                            onChange={(e) =>
                                                handleSetImprovementLine(index, "no_deductions")(e.target.checked)
                                            }
                                        />
                                    )}
                                    <ImprovementRemoveLineButton onClick={() => setIndexToRemove(index)} />
                                </li>
                            )
                        )}
                    </>
                ) : (
                    <div>Ei parannuksia</div>
                )}
                <li className="row row--buttons">
                    <ImprovementAddLineButton onClick={handleAddImprovementLine} />
                </li>
            </ul>
        </Fieldset>
    );
};

const LoadedHousingCompanyImprovementsPage = () => {
    const navigate = useNavigate();
    const {housingCompany} = useContext(HousingCompanyViewContext);
    if (!housingCompany) throw new Error("Housing company not found");

    const [isConfirmVisible, setIsConfirmVisible] = useState(false);
    const [marketIndexToRemove, setMarketIndexToRemove] = useState<number | null>(null);
    const [constructionIndexToRemove, setConstructionIndexToRemove] = useState<number | null>(null);

    const [marketIndexImprovements, setMarketIndexImprovements] = useImmer<IWritableMarketImprovement[]>(
        housingCompany.improvements.market_price_index.map((i) => ({key: uuidv4(), saved: true, ...i})) || []
    );
    const [constructionIndexImprovements, setConstructionIndexImprovements] = useImmer<IWritableConsImprovement[]>(
        housingCompany.improvements.construction_price_index.map((i) => ({key: uuidv4(), saved: true, ...i})) || []
    );

    const [saveHousingCompany, {error, isLoading}] = useSaveHousingCompanyMutation();

    const handleSaveButtonClicked = () => {
        const formData = {
            ...housingCompany,
            // Don't send empty improvements to the API
            improvements: {
                market_price_index: marketIndexImprovements.filter((i) => i.value) as IMarketPriceIndexImprovement[],
                construction_price_index: constructionIndexImprovements.filter((i) => i.value) as IImprovement[],
            },
        };

        saveHousingCompany({
            data: formData,
            id: housingCompany.id,
        })
            .unwrap()
            .then(() => {
                hdsToast.success("Parannukset tallennettu onnistuneesti!");
                navigate(-1); // get the user back to where they opened this view
            })
            .catch(() => {
                hdsToast.error("Virhe tallentaessa parannuksia!");
            });
    };

    // Market
    const handleAddMarketImprovementLine = () => {
        setMarketIndexImprovements((draft) => {
            draft.push({
                key: uuidv4(),
                saved: false,
                name: "",
                value: null,
                completion_date: "",
                no_deductions: false,
            });
        });
    };
    const handleSetMarketImprovementLine = (index, fieldPath) => (value) => {
        setMarketIndexImprovements((draft) => {
            dotted(draft[index], fieldPath, value);
        });
    };
    const handleConfirmedRemoveMarketImprovementLine = () => {
        if (marketIndexToRemove !== null) {
            setMarketIndexImprovements((draft) => {
                draft.splice(marketIndexToRemove, 1);
            });
            setIsConfirmVisible(false);
            setMarketIndexToRemove(null);
        }
    };

    // Construction
    const handleAddConstructionImprovementLine = () => {
        setConstructionIndexImprovements((draft) => {
            draft.push({
                key: uuidv4(),
                saved: false,
                name: "",
                value: null,
                completion_date: "",
            });
        });
    };
    const handleSetConstructionImprovementLine = (index, fieldPath) => (value) => {
        setConstructionIndexImprovements((draft) => {
            dotted(draft[index], fieldPath, value);
        });
    };
    const handleConfirmedRemoveConstructionImprovementLine = () => {
        if (constructionIndexToRemove !== null) {
            setConstructionIndexImprovements((draft) => {
                draft.splice(constructionIndexToRemove, 1);
            });
            setIsConfirmVisible(false);
            setConstructionIndexToRemove(null);
        }
    };

    // Handle confirm remove modal
    useEffect(() => {
        if (marketIndexToRemove !== null || constructionIndexToRemove !== null) {
            setIsConfirmVisible(true);
        }
    }, [marketIndexToRemove, constructionIndexToRemove, setIsConfirmVisible]);

    return (
        <>
            <Heading>{housingCompany.name.display} Parannukset</Heading>
            <div className="field-sets">
                <ImprovementFieldSet
                    fieldsetHeader="Markkinakustannusindeksillä laskettavat parannukset"
                    improvements={marketIndexImprovements}
                    handleAddImprovementLine={handleAddMarketImprovementLine}
                    handleSetImprovementLine={handleSetMarketImprovementLine}
                    setIndexToRemove={setMarketIndexToRemove}
                    error={error}
                    showNoDeductions={true}
                />
                <ImprovementFieldSet
                    fieldsetHeader="Rakennuskustannusindeksillä laskettavat parannukset"
                    improvements={constructionIndexImprovements}
                    handleAddImprovementLine={handleAddConstructionImprovementLine}
                    handleSetImprovementLine={handleSetConstructionImprovementLine}
                    setIndexToRemove={setConstructionIndexToRemove}
                    error={error}
                    showNoDeductions={false}
                />
            </div>

            <div className="row row--buttons">
                <NavigateBackButton />
                <SaveButton
                    onClick={handleSaveButtonClicked}
                    isLoading={isLoading}
                />
            </div>

            <ConfirmDialogModal
                modalText="Haluatko varmasti poistaa parannuksen?"
                buttonText="Poista"
                successText="Parannus poistettu"
                isVisible={isConfirmVisible}
                setIsVisible={setIsConfirmVisible}
                confirmAction={
                    marketIndexToRemove === null
                        ? handleConfirmedRemoveConstructionImprovementLine
                        : handleConfirmedRemoveMarketImprovementLine
                }
                cancelAction={() => setIsConfirmVisible(false)}
            />
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
