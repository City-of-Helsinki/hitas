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
import {getHitasQuarter, hdsToast} from "../../common/utils";
import {
    ExternalSalesDataImport,
    ThirtyYearErrorModal,
    ThirtyYearErrorTest,
    ThirtyYearResults,
} from "./ThirtyYearRegulationTabComponents";

const ThirtyYearRegulationContainer = () => {
    const [isErrorModalOpen, setIsErrorModalOpen] = useState(false);
    // TODO: populate the years options with years starting from 2023, when testing is done
    const years = [
        {label: "2023", value: "2023"},
        {label: "2022", value: "2022"},
        {label: "2021", value: "2021"},
    ];

    // React hook form
    const formObject = useForm({
        defaultValues: {
            year: years[0].value,
            quarter: getHitasQuarter(),
            file: undefined,
            test: false,
        },
        mode: "all",
    });

    const {watch} = formObject;
    const formTimePeriod: {label: string; value: string} = watch("quarter");
    const formYear: string = watch("year");
    const formDate = `${formYear}-${formTimePeriod.value}`;

    const currentTime = new Date();
    // Populate the time quarter select with options, if current year is selected in the year selector
    let hitasQuarterOptions: {label: string; value: string}[] = [];
    // If the current year is not selected, add all quarters to the time period select options...
    if (currentTime.getFullYear().toString() !== formYear) {
        hitasQuarterOptions = hitasQuarters;
    } else {
        // ...otherwise add only the quarters that have passed
        const month = currentTime.getMonth();
        if (month > 1) hitasQuarterOptions.push(hitasQuarters[0]);
        if (month > 4) hitasQuarterOptions.push(hitasQuarters[1]);
        if (month > 7) hitasQuarterOptions.push(hitasQuarters[2]);
        if (month > 10) hitasQuarterOptions.push(hitasQuarters[3]);
    }

    // Queries and mutations
    const {
        currentData: externalSalesData,
        isFetching: isExternalSalesDataLoading,
        error: externalSalesDataLoadError,
    } = useGetExternalSalesDataQuery({
        calculation_date: formDate,
    });

    const {
        currentData: getRegulationData,
        isFetching: isGetRegulationLoading,
        error: getRegulationError,
    } = useGetThirtyYearRegulationQuery(
        {
            calculationDate: formDate,
        },
        {skip: !externalSalesData || !!isExternalSalesDataLoading || !!externalSalesDataLoadError}
    );

    const [makeRegulation, {data: makeRegulationData, isLoading: isMakeRegulationLoading, error: makeRegulationError}] =
        useCreateThirtyYearRegulationMutation();

    const {
        currentData: priceCeilingData,
        isFetching: isPriceCeilingLoading,
        error: priceCeilingError,
    } = useGetIndexQuery({
        indexType: "surface-area-price-ceiling",
        month: formDate.substring(0, 7),
    });

    const hasSkippedCompanies = makeRegulationData?.skipped?.length;
    const regulationData: object | undefined = hasSkippedCompanies ? makeRegulationData : getRegulationData;
    const isRegulationLoading = isGetRegulationLoading ?? isMakeRegulationLoading;
    const regulationError = getRegulationError ?? makeRegulationError;
    const hasRegulationResults = (!getRegulationError && !!getRegulationData) || !!regulationData;
    const hasExternalSalesData = !isExternalSalesDataLoading && !externalSalesDataLoadError && !!externalSalesData;

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
                    calculationDate: formDate,
                    replacementPostalCodes: skippedArray,
                },
            })
                .unwrap()
                .then(() => {
                    hdsToast.success("Vertailu suoritettu onnistuneesti!");
                })
                .catch((error) => {
                    // eslint-disable-next-line no-console
                    console.warn("Error:", error);
                    setIsErrorModalOpen(true);
                });
    };

    return (
        <>
            <div className="actions">
                <div className="time-period">
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
                            options={years}
                            defaultValue={years[0].value}
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
                <div className="price-ceiling">
                    <label>
                        Rajaneliöhinta
                        {` (${formObject.getValues("quarter").label}${formYear})`}
                    </label>
                    <QueryStateHandler
                        data={priceCeilingData}
                        error={priceCeilingError}
                        isLoading={isPriceCeilingLoading}
                    >
                        <div className="value">
                            <>{(priceCeilingData?.value ?? "---") + " "}</>
                            €/m²
                        </div>
                    </QueryStateHandler>
                    {hasRegulationResults && (
                        <DownloadButton
                            downloadFn={() => downloadRegulationResults(formDate)}
                            buttonText="Lataa kokonaisraportti"
                        />
                    )}
                </div>
            </div>
            {!hasExternalSalesData && (
                <>
                    <Divider size="l" />
                    <ExternalSalesDataImport formDate={formDate} />
                </>
            )}
            <ThirtyYearResults
                hasResults={hasRegulationResults}
                hasExternalSalesData={hasExternalSalesData}
                data={regulationData}
                error={regulationError}
                isLoading={isRegulationLoading}
                date={formDate}
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
