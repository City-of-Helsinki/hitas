import React, {useEffect} from "react";

import {Button, Fieldset, IconCrossCircle, IconPlus, Tooltip} from "hds-react";
import {useLocation, useNavigate} from "react-router-dom";
import {useImmer} from "use-immer";
import {v4 as uuidv4} from "uuid";

import {useSaveHousingCompanyMutation} from "../../app/services";
import {FormInputField, NavigateBackButton, SaveButton} from "../../common/components";
import {IHousingCompanyDetails, IHousingCompanyWritable, IImprovement} from "../../common/models";
import {dotted, hitasToast} from "../../common/utils";

type IWritableImprovement = Omit<IImprovement, "value"> & {value: number | null; key: string; saved: boolean};

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

const HousingCompanyImprovementsPage = () => {
    const navigate = useNavigate();
    const {state}: {state: {housingCompany: IHousingCompanyDetails}} = useLocation();

    const [saveHousingCompany, {data, error, isLoading}] = useSaveHousingCompanyMutation();

    const housingCompanyData: IHousingCompanyWritable = state.housingCompany;
    const [marketIndexImprovements, setMarketIndexImprovements] = useImmer<IWritableImprovement[]>(
        housingCompanyData.improvements.market_price_index.map((i) => ({key: uuidv4(), saved: true, ...i})) || []
    );
    const [constructionIndexImprovements, setConstructionIndexImprovements] = useImmer<IWritableImprovement[]>(
        housingCompanyData.improvements.construction_price_index.map((i) => ({key: uuidv4(), saved: true, ...i})) || []
    );

    const handleSaveButtonClicked = () => {
        const formData = {
            ...housingCompanyData,
            // Don't send empty improvements to the API
            improvements: {
                market_price_index: marketIndexImprovements.filter((i) => i.value) as IImprovement[],
                construction_price_index: constructionIndexImprovements.filter((i) => i.value) as IImprovement[],
            },
        };

        saveHousingCompany({
            data: formData,
            id: state?.housingCompany.id,
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
            });
        });
    };
    const handleSetMarketImprovementLine = (index, fieldPath) => (value) => {
        setMarketIndexImprovements((draft) => {
            dotted(draft[index], fieldPath, value);
        });
    };
    const handleRemoveMarketImprovementLine = (index) => {
        if (!marketIndexImprovements[index].saved || window.confirm("Haluatko poistaa tallennetun parannuksen?")) {
            setMarketIndexImprovements((draft) => {
                draft.splice(index, 1);
            });
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
    const handleRemoveConstructionImprovementLine = (index) => {
        if (
            !constructionIndexImprovements[index].saved ||
            window.confirm("Haluatko poistaa tallennetun parannuksen?")
        ) {
            setConstructionIndexImprovements((draft) => {
                draft.splice(index, 1);
            });
        }
    };

    // Handle saving flow when editing
    useEffect(() => {
        if (!isLoading && !error && data && data.id) {
            hitasToast("Parannukset tallennettu onnistuneesti!");
            navigate(-1); // get the user back to where they opened this view
        } else if (error) {
            hitasToast("Virhe tallentaessa parannuksia!", "error");
        }
    }, [isLoading, error, data, navigate]);

    // Redirect user to detail page if state is missing HousingCompany data and user is trying to edit the it
    // FIXME: Currently does not work, as the page crashes on load due to accessing properties of null
    useEffect(() => {
        if (state === null) navigate("..");
    }, [navigate, state]);

    return (
        <div className="view--create view--create-improvements">
            <h1 className="main-heading">{housingCompanyData.name.display} Parannukset</h1>
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
                                </li>
                                {marketIndexImprovements.map((improvement: IWritableImprovement, index) => (
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
                                        <ImprovementRemoveLineButton
                                            onClick={() => handleRemoveMarketImprovementLine(index)}
                                        />
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
                                {constructionIndexImprovements.map((improvement: IWritableImprovement, index) => (
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
                                            onClick={() => handleRemoveConstructionImprovementLine(index)}
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
        </div>
    );
};

export default HousingCompanyImprovementsPage;
