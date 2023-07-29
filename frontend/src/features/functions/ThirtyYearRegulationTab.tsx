import {ToggleButton, Tooltip} from "hds-react";
import {FormProvider, useForm} from "react-hook-form";

import {useState} from "react";
import {Divider, DownloadButton, Heading, QueryStateHandler} from "../../common/components";
import {SelectInput} from "../../common/components/forms";
import {hitasQuarters} from "../../common/schemas";
import {
    downloadRegulationResults,
    useCreateThirtyYearRegulationMutation,
    useGetExternalSalesDataQuery,
    useGetIndexQuery,
    useGetThirtyYearRegulationQuery,
} from "../../common/services";
import {getHitasQuarter, getHitasQuarterFullLabel, hdsToast} from "../../common/utils";
import {
    ExternalSalesDataImport,
    ThirtyYearErrorModal,
    ThirtyYearErrorTest,
    ThirtyYearResults,
} from "./ThirtyYearRegulationTabComponents";

const yearChoices = [
    {label: "2023", value: "2023"},
    {label: "2022", value: "2022"},
    {label: "2021", value: "2021"},
];

const ThirtyYearRegulationSurfaceAreaPriceCeiling = ({
    priceCeilingData,
    isPriceCeilingLoading,
    priceCeilingError,
    calculationMonth,
}) => {
    return (
        <QueryStateHandler
            data={priceCeilingData}
            error={priceCeilingError}
            isLoading={isPriceCeilingLoading}
            spinnerWrapClassName="spinner-wrap-color"
        >
            <div className="surface-area-price-ceiling-value-container">
                <div className="surface-area-price-ceiling-value">
                    <label>Rajaneliöhinta {getHitasQuarterFullLabel(calculationMonth)}</label>
                    <span>{priceCeilingData?.value ?? "---"}</span>
                </div>
            </div>
        </QueryStateHandler>
    );
};

const ThirtyYearRegulationDateSelection = ({formObject, hasSkippedCompanies}) => {
    // TODO: populate the years options with years starting from 2023, when testing is done

    const currentTime = new Date();

    // Populate the time quarter select with options, if current year is selected in the year selector
    let hitasQuarterOptions: {label: string; value: string}[] = [];
    if (currentTime.getFullYear().toString() !== formObject.getValues("year")) {
        // If the current year is not selected, add all quarters to the time period select options...
        hitasQuarterOptions = hitasQuarters;
    } else {
        // ...otherwise add only the quarters that have passed
        const month = currentTime.getMonth();
        if (month > 1) hitasQuarterOptions.push(hitasQuarters[0]);
        if (month > 4) hitasQuarterOptions.push(hitasQuarters[1]);
        if (month > 7) hitasQuarterOptions.push(hitasQuarters[2]);
        if (month > 10) hitasQuarterOptions.push(hitasQuarters[3]);
    }

    return (
        <div className="hitas-quarter-selection-container">
            <label>
                Vuosineljännes
                <Tooltip placement="bottom-start">
                    Valitse vuosi ja neljännes jonka vapautumisia haluat tarkastella, tai jolle haluat suorittaa
                    vertailun mikäli sitä ei ole vielä tehty.
                </Tooltip>
            </label>
            <FormProvider {...formObject}>
                <SelectInput
                    label=""
                    name="year"
                    options={yearChoices}
                    defaultValue={yearChoices[0].value}
                    disabled={hasSkippedCompanies}
                    setDirectValue
                    required
                />
                <SelectInput
                    label=""
                    name="quarter"
                    options={hitasQuarterOptions}
                    defaultValue={hitasQuarterOptions[hitasQuarterOptions.length - 1].value}
                    disabled={hasSkippedCompanies}
                    required
                />
            </FormProvider>
        </div>
    );
};

const ThirtyYearRegulationContainer = () => {
    const [isErrorModalOpen, setIsErrorModalOpen] = useState(false);

    // React hook form
    const formObject = useForm({
        defaultValues: {year: yearChoices[0].value, quarter: getHitasQuarter()},
        mode: "all",
    });

    const {watch} = formObject;
    const formTimePeriod: {label: string; value: string} = watch("quarter");
    const formYear: string = watch("year");
    const calculationMonth = `${formYear}-${formTimePeriod.value}`;

    // Queries and mutations

    // Get current SAPC value
    const {
        currentData: priceCeilingData,
        isFetching: isPriceCeilingLoading,
        error: priceCeilingError,
    } = useGetIndexQuery({indexType: "surface-area-price-ceiling", month: calculationMonth.substring(0, 7)});

    const {
        currentData: externalSalesData,
        isFetching: isExternalSalesDataLoading,
        error: externalSalesDataError,
    } = useGetExternalSalesDataQuery({calculation_date: calculationMonth});
    const hasExternalSalesData = !isExternalSalesDataLoading && !externalSalesDataError && !!externalSalesData;

    const {
        currentData: getRegulationData,
        isFetching: isGetRegulationLoading,
        error: getRegulationError,
    } = useGetThirtyYearRegulationQuery({calculationDate: calculationMonth}, {skip: !hasExternalSalesData});

    const [makeRegulation, {data: makeRegulationData, isLoading: isMakeRegulationLoading, error: makeRegulationError}] =
        useCreateThirtyYearRegulationMutation();

    const hasSkippedCompanies = makeRegulationData?.skipped?.length;
    const regulationData: object | undefined = hasSkippedCompanies ? makeRegulationData : getRegulationData;
    const isRegulationLoading = isGetRegulationLoading ?? isMakeRegulationLoading;
    const regulationError = getRegulationError ?? makeRegulationError;
    const hasRegulationResults = (!getRegulationError && !!getRegulationData) || !!regulationData;

    // ******************
    // * Event handlers *
    // ******************

    const onCompareButtonClick = (data) => {
        // format eventual skipped data to match the API format
        const skippedArray: {postalCode: string; replacements: string[]}[] = [];
        if (data?.skipped) {
            data?.skipped.forEach((skipped) => {
                skippedArray.push({
                    postalCode: skipped.missingCode,
                    replacements: [skipped.postalCode1, skipped.postalCode2],
                });
            });
        } else
            return makeRegulation({
                data: {
                    calculationDate: calculationMonth,
                    replacementPostalCodes: skippedArray,
                },
            })
                .unwrap()
                .then(() => {
                    hdsToast.success("Vertailu suoritettu onnistuneesti!");
                })
                .catch((error) => {
                    // eslint-disable-next-line no-console
                    console.error("Error:", error);
                    setIsErrorModalOpen(true);
                    hdsToast.error("Virhe vertailun suorittamisessa!");
                });
    };

    return (
        <>
            <div className="actions-row">
                <ThirtyYearRegulationDateSelection
                    formObject={formObject}
                    hasSkippedCompanies={hasSkippedCompanies}
                />
                <ThirtyYearRegulationSurfaceAreaPriceCeiling
                    priceCeilingData={priceCeilingData}
                    isPriceCeilingLoading={isPriceCeilingLoading}
                    priceCeilingError={priceCeilingError}
                    calculationMonth={calculationMonth}
                />
                {hasRegulationResults && (
                    <div className="download-button-container">
                        <DownloadButton
                            onClick={() => downloadRegulationResults(calculationMonth)}
                            buttonText="Lataa kokonaisraportti"
                        />
                    </div>
                )}
            </div>

            {!hasRegulationResults ? (
                <>
                    <Divider size="l" />

                    <ExternalSalesDataImport
                        calculationMonth={calculationMonth}
                        hasExternalSalesData={hasExternalSalesData}
                        isExternalSalesDataLoading={isExternalSalesDataLoading}
                    />
                </>
            ) : null}

            <Divider size="l" />

            <ThirtyYearResults
                hasResults={hasRegulationResults}
                hasExternalSalesData={hasExternalSalesData}
                data={regulationData}
                error={regulationError}
                isLoading={isRegulationLoading}
                date={calculationMonth}
                priceCeilingValue={priceCeilingData?.value}
                compareFn={onCompareButtonClick}
            />

            <ThirtyYearErrorModal
                isOpen={isErrorModalOpen}
                setIsOpen={setIsErrorModalOpen}
                response={regulationError}
            />
        </>
    );
};

const ThirtyYearRegulationTab = () => {
    const [isTestModeEnabled, setIsTestModeEnabled] = useState(false);

    return (
        <div className="view--functions__thirty-year-regulation">
            <Heading type="body">
                <span>Vapautumisen tarkistus</span>
                <div className="test-toggle">
                    <ToggleButton
                        id="testMode-Toggle"
                        label="Virhetila -testi"
                        checked={isTestModeEnabled}
                        onChange={() => {
                            setIsTestModeEnabled((prevState) => !prevState);
                        }}
                        variant="inline"
                    />
                </div>
            </Heading>
            {isTestModeEnabled ? <ThirtyYearErrorTest /> : <ThirtyYearRegulationContainer />}
        </div>
    );
};

export default ThirtyYearRegulationTab;
