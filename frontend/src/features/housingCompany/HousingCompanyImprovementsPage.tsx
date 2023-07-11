import {useEffect, useState} from "react";

import {Button, Checkbox, Fieldset, IconCrossCircle, IconPlus, Tooltip} from "hds-react";
import {useNavigate, useParams} from "react-router-dom";
import {useImmer} from "use-immer";
import {v4 as uuidv4} from "uuid";

import {useGetHousingCompanyDetailQuery, useSaveHousingCompanyMutation} from "../../app/services";
import {
    ConfirmDialogModal,
    FormInputField,
    Heading,
    NavigateBackButton,
    QueryStateHandler,
    SaveButton,
} from "../../common/components";
import {
    IHousingCompanyDetails,
    IHousingCompanyWritable,
    IImprovement,
    IMarketPriceIndexImprovement,
} from "../../common/schemas";
import {dotted, hitasToast} from "../../common/utils";

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

const LoadedHousingCompanyImprovementsPage = ({housingCompany}: {housingCompany: IHousingCompanyDetails}) => {
    const navigate = useNavigate();
    const [saveHousingCompany, {data, error, isLoading}] = useSaveHousingCompanyMutation();
    const [isConfirmVisible, setIsConfirmVisible] = useState(false);
    const [marketIndexToRemove, setMarketIndexToRemove] = useState<number | null>(null);
    const [constructionIndexToRemove, setConstructionIndexToRemove] = useState<number | null>(null);
    const housingCompanyData: IHousingCompanyWritable = housingCompany;
    const [marketIndexImprovements, setMarketIndexImprovements] = useImmer<IWritableMarketImprovement[]>(
        housingCompanyData.improvements.market_price_index.map((i) => ({key: uuidv4(), saved: true, ...i})) || []
    );
    const [constructionIndexImprovements, setConstructionIndexImprovements] = useImmer<IWritableConsImprovement[]>(
        housingCompanyData.improvements.construction_price_index.map((i) => ({key: uuidv4(), saved: true, ...i})) || []
    );

    const handleSaveButtonClicked = () => {
        const formData = {
            ...housingCompanyData,
            // Don't send empty improvements to the API
            improvements: {
                market_price_index: marketIndexImprovements.filter((i) => i.value) as IMarketPriceIndexImprovement[],
                construction_price_index: constructionIndexImprovements.filter((i) => i.value) as IImprovement[],
            },
        };

        saveHousingCompany({
            data: formData,
            id: housingCompany.id,
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

    // Handle saving flow when editing
    useEffect(() => {
        if (!isLoading && !error && data && data.id) {
            hitasToast("Parannukset tallennettu onnistuneesti!");
            navigate(-1); // get the user back to where they opened this view
        } else if (error) {
            hitasToast("Virhe tallentaessa parannuksia!", "error");
        }
    }, [isLoading, error, data, navigate]);

    return (
        <>
            <Heading>{housingCompanyData.name.display} Parannukset</Heading>
            <div className="field-sets">
                <Fieldset heading="Markkinahintaindeksillä laskettavat parannukset">
                    <ul className="improvements-list">
                        {marketIndexImprovements.length ? (
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
                                </li>
                                {marketIndexImprovements.map((improvement: IWritableMarketImprovement, index) => (
                                    <li
                                        className="improvements-list-item"
                                        key={`market-improvement-item-${improvement.key}`}
                                    >
                                        <FormInputField
                                            inputType="text"
                                            label=""
                                            fieldPath="name"
                                            formData={marketIndexImprovements[index]}
                                            setterFunction={handleSetMarketImprovementLine(index, "name")}
                                            error={error}
                                            required
                                        />
                                        <FormInputField
                                            inputType="number"
                                            fractionDigits={2}
                                            label=""
                                            fieldPath="value"
                                            formData={marketIndexImprovements[index]}
                                            setterFunction={handleSetMarketImprovementLine(index, "value")}
                                            error={error}
                                            required
                                        />
                                        <FormInputField
                                            inputType="text"
                                            label=""
                                            fieldPath="completion_date"
                                            tooltipText={"Muodossa 'YYYY-MM', esim. '2022-01'"}
                                            formData={marketIndexImprovements[index]}
                                            setterFunction={handleSetMarketImprovementLine(index, "completion_date")}
                                            error={error}
                                            required
                                        />
                                        <Checkbox
                                            id={`input-no_deductions-${index}`}
                                            checked={marketIndexImprovements[index].no_deductions}
                                            onChange={(e) =>
                                                handleSetMarketImprovementLine(index, "no_deductions")(e.target.checked)
                                            }
                                        />
                                        <ImprovementRemoveLineButton onClick={() => setMarketIndexToRemove(index)} />
                                    </li>
                                ))}
                            </>
                        ) : (
                            <div>Ei parannuksia</div>
                        )}
                        <li className="row row--buttons">
                            <ImprovementAddLineButton onClick={handleAddMarketImprovementLine} />
                        </li>
                    </ul>
                </Fieldset>
                <Fieldset heading="Rakennuskustannusindeksillä laskettavat parannukset">
                    <ul className="improvements-list">
                        {constructionIndexImprovements.length ? (
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
                                </li>
                                {constructionIndexImprovements.map((improvement: IWritableConsImprovement, index) => (
                                    <li
                                        className="improvements-list-item"
                                        key={improvement.key}
                                    >
                                        <FormInputField
                                            inputType="text"
                                            label=""
                                            fieldPath="name"
                                            formData={constructionIndexImprovements[index]}
                                            setterFunction={handleSetConstructionImprovementLine(index, "name")}
                                            error={error}
                                            required
                                        />
                                        <FormInputField
                                            inputType="number"
                                            fractionDigits={2}
                                            label=""
                                            fieldPath="value"
                                            formData={constructionIndexImprovements[index]}
                                            setterFunction={handleSetConstructionImprovementLine(index, "value")}
                                            error={error}
                                            required
                                        />
                                        <FormInputField
                                            inputType="text"
                                            label=""
                                            fieldPath="completion_date"
                                            tooltipText={"Muodossa 'YYYY-MM', esim. '2022-01'"}
                                            formData={constructionIndexImprovements[index]}
                                            setterFunction={handleSetConstructionImprovementLine(
                                                index,
                                                "completion_date"
                                            )}
                                            error={error}
                                            required
                                        />
                                        <ImprovementRemoveLineButton
                                            onClick={() => setConstructionIndexToRemove(index)}
                                        />
                                    </li>
                                ))}
                            </>
                        ) : (
                            <div>Ei parannuksia</div>
                        )}
                        <li className="row row--buttons">
                            <ImprovementAddLineButton onClick={handleAddConstructionImprovementLine} />
                        </li>
                    </ul>
                </Fieldset>
            </div>
            <div className="row row--buttons">
                <NavigateBackButton />
                <SaveButton
                    onClick={handleSaveButtonClicked}
                    isLoading={isLoading}
                />
            </div>
            <ConfirmDialogModal
                isLoading={false}
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
    const params = useParams() as {readonly housingCompanyId: string};
    const {data, error, isLoading} = useGetHousingCompanyDetailQuery(params.housingCompanyId);

    return (
        <div className="view--create view--create-improvements">
            <QueryStateHandler
                data={data}
                error={error}
                isLoading={isLoading}
            >
                <LoadedHousingCompanyImprovementsPage housingCompany={data as IHousingCompanyDetails} />
            </QueryStateHandler>
        </div>
    );
};

export default HousingCompanyImprovementsPage;
