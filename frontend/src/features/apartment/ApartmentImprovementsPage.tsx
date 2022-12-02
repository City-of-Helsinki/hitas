import React, {useEffect} from "react";

import {Button, Fieldset, IconCrossCircle, IconPlus, Tooltip} from "hds-react";
import {useLocation, useNavigate, useParams} from "react-router-dom";
import {useImmer} from "use-immer";
import {v4 as uuidv4} from "uuid";

import {useSaveApartmentMutation} from "../../app/services";
import {FormInputField, NavigateBackButton, SaveButton} from "../../common/components";
import {
    IApartmentConstructionPriceIndexImprovement,
    IApartmentDetails,
    IApartmentWritable,
    IImprovement,
} from "../../common/models";
import {dotted, hitasToast} from "../../common/utils";

type IWritableImprovement = Omit<IImprovement, "value"> & {value: number | null; key: string; saved: boolean};
type IWritableConsImprovement = Omit<IApartmentConstructionPriceIndexImprovement, "value"> & {
    value: number | null;
    key: string;
    saved: boolean;
};

const convertApartmentDetailToWritable = (ap: IApartmentDetails): IApartmentWritable => {
    return {
        ...ap,
        shares: ap.shares || {start: null, end: null},
        building: {id: ap.links.building.id},
        address: {
            ...ap.address,
            street_address: ap.links.building.street_address,
        },
    };
};

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

const depreciationChoices = [{label: "0.0"}, {label: "2.5"}, {label: "10.0"}];

const ApartmentImprovementsPage = () => {
    const navigate = useNavigate();
    const {state}: {state: {apartment: IApartmentDetails}} = useLocation();
    const params = useParams() as {readonly housingCompanyId: string};

    const [saveApartment, {data, error, isLoading}] = useSaveApartmentMutation();

    const apartmentData: IApartmentWritable = convertApartmentDetailToWritable(state.apartment);
    const [marketIndexImprovements, setMarketIndexImprovements] = useImmer<IWritableImprovement[]>(
        apartmentData.improvements.market_price_index.map((i) => ({key: uuidv4(), saved: true, ...i})) || []
    );
    const [constructionIndexImprovements, setConstructionIndexImprovements] = useImmer<IWritableConsImprovement[]>(
        apartmentData.improvements.construction_price_index.map((i) => ({key: uuidv4(), saved: true, ...i})) || []
    );

    const handleSaveButtonClicked = () => {
        const formData = {
            ...apartmentData,
            // Don't send empty improvements to the API
            improvements: {
                market_price_index: marketIndexImprovements.filter((i) => i.value) as IImprovement[],
                construction_price_index: constructionIndexImprovements
                    .filter((i) => i.value)
                    .map((i) => {
                        return {...i, depreciation_percentage: parseFloat(`${i.depreciation_percentage}`)};
                    }) as IApartmentConstructionPriceIndexImprovement[],
            },
        };

        saveApartment({
            data: formData,
            id: state?.apartment.id,
            housingCompanyId: params.housingCompanyId,
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
                depreciation_percentage: 2.5,
            });
        });
    };
    const handleSetConstructionImprovementLine = (index, fieldPath) => (value) => {
        setConstructionIndexImprovements((draft) => {
            dotted(draft[index], fieldPath, value);
        });
    };
    const handleRemoveConstructionImprovementLine = (index) => {
        if (!marketIndexImprovements[index].saved || window.confirm("Haluatko poistaa tallennetun parannuksen?")) {
            setConstructionIndexImprovements((draft) => {
                draft.splice(index, 1);
            });
        }
    };

    // Handle saving flow when editing
    useEffect(() => {
        if (!isLoading && !error && data && data.id) {
            hitasToast("Parannukset tallennettu onnistuneesti!");
            navigate(`/housing-companies/${data.links.housing_company.id}/apartments/${data.id}`);
        } else if (error) {
            hitasToast("Virhe tallentaessa parannuksia!", "error");
        }
    }, [isLoading, error, data, navigate]);

    // Redirect user to detail page if state is missing Apartment data and user is trying to edit the apartment
    // FIXME: Currently does not work, as the page crashes on load due to accessing properties of null
    useEffect(() => {
        if (state === null) navigate("..");
    }, [navigate, state]);

    return (
        <div className="view--create view--create-improvements">
            <h1 className="main-heading">
                {apartmentData.address.street_address} - {apartmentData.address.stair}
                {apartmentData.address.apartment_number} Parannukset
            </h1>
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
                                        <div className="input-wrap--name">
                                            <FormInputField
                                                inputType="text"
                                                label=""
                                                fieldPath="name"
                                                formData={marketIndexImprovements[index]}
                                                setterFunction={handleSetMarketImprovementLine(index, "name")}
                                                error={error}
                                                required
                                            />
                                        </div>
                                        <div className="input-wrap--value">
                                            <FormInputField
                                                inputType="number"
                                                label=""
                                                fieldPath="value"
                                                formData={marketIndexImprovements[index]}
                                                setterFunction={handleSetMarketImprovementLine(index, "value")}
                                                error={error}
                                                required
                                            />
                                        </div>
                                        <div className="input-wrap--date">
                                            <FormInputField
                                                inputType="text"
                                                label=""
                                                fieldPath="completion_date"
                                                formData={marketIndexImprovements[index]}
                                                setterFunction={handleSetMarketImprovementLine(
                                                    index,
                                                    "completion_date"
                                                )}
                                                error={error}
                                                required
                                            />
                                        </div>
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
                    <ul className="improvements-list improvements-list--construction-index">
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
                                    <header>
                                        Poistoprosentti <span>*</span>
                                    </header>
                                    <Tooltip
                                        className="header__tooltip"
                                        placement="left-start"
                                    >
                                        Muodossa 'YYYY-MM', esim. '2022-01'
                                    </Tooltip>
                                </li>
                                {constructionIndexImprovements.map((improvement: IWritableConsImprovement, index) => (
                                    <div key={improvement.key}>
                                        <li className="improvements-list-item">
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
                                                tooltipText="Muodossa 'YYYY-MM', esim. '2022-01'"
                                                formData={constructionIndexImprovements[index]}
                                                setterFunction={handleSetConstructionImprovementLine(
                                                    index,
                                                    "completion_date"
                                                )}
                                                error={error}
                                                required
                                            />
                                            <FormInputField
                                                inputType="select"
                                                label=""
                                                fieldPath="depreciation_percentage"
                                                options={depreciationChoices}
                                                placeholder={improvement.depreciation_percentage.toString()}
                                                formData={constructionIndexImprovements[index]}
                                                setterFunction={handleSetConstructionImprovementLine(
                                                    index,
                                                    "depreciation_percentage"
                                                )}
                                                error={error}
                                                required
                                            />
                                            <ImprovementRemoveLineButton
                                                onClick={() => handleRemoveConstructionImprovementLine(index)}
                                            />
                                        </li>
                                    </div>
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

export default ApartmentImprovementsPage;
