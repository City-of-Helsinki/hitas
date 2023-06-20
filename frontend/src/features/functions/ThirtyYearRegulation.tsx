import {Button, Tooltip} from "hds-react";
import {useForm} from "react-hook-form";
import {hitasQuarters} from "../../common/schemas";

import {useState} from "react";
import {
    downloadRegulationResults,
    useCreateThirtyYearRegulationMutation,
    useGetExternalSalesDataQuery,
    useGetIndexQuery,
    useGetThirtyYearRegulationQuery,
} from "../../app/services";
import {Divider, Heading, QueryStateHandler} from "../../common/components";
import {Select, ToggleInput} from "../../common/components/form";
import {getHitasQuarter, hdsToast} from "../../common/utils";
import {ExternalSalesDataImport, ThirtyYearErrorModal, ThirtyYearErrorTest, ThirtyYearResults} from "./components";

const ThirtyYearRegulation = () => {
    const currentTime = new Date();
    const [isErrorModalOpen, setIsErrorModalOpen] = useState(false);
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
    const testForm = useForm({
        defaultValues: {
            testMode: false,
            selection: "result_noProblems",
        },
        mode: "all",
    });
    const {watch: testWatch} = testForm;
    const {watch} = formObject;
    const formTimePeriod: {label: string; value: string} = watch("quarter");
    const formYear: string = watch("year");
    const formDate = `${formYear}-${formTimePeriod.value}`;
    const isTestMode: boolean = testWatch("testMode");

    // Populate the time quarter select with options, if current year is selected in the year selector
    const hitasQuarterOptions: {label: string; value: string}[] = [];
    // If the current year is not selected, add all quarters to the time period select options...
    if (currentTime.getFullYear().toString() !== formYear) {
        hitasQuarters.forEach((quarter) => hitasQuarterOptions.push({value: quarter.value, label: quarter.label}));
    } else {
        // ...otherwise add only the quarters that have passed
        for (let i = 0; i < 4; i++) {
            if (currentTime.getMonth() + 1 >= (i + 1) * 3 - 1) {
                hitasQuarterOptions.push(hitasQuarters[i]);
            }
        }
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
        <div className="view--functions__thirty-year-regulation">
            <div className="regulation">
                <Heading
                    type="body"
                    className="page-heading"
                >
                    <span>Vapautumisen tarkistus</span>
                    <div className="test-toggle">
                        <ToggleInput
                            name="testMode"
                            label="Virhetila -testi"
                            formObject={testForm}
                        />
                    </div>
                </Heading>
                {isTestMode ? (
                    <>
                        <ThirtyYearErrorTest />
                    </>
                ) : (
                    <>
                        <div className="actions">
                            <div className="time-period">
                                <label>
                                    Ajanjakso
                                    <Tooltip placement="bottom-start">
                                        Valitse vuosi ja jakso jonka vapautumisia haluat tarkastella, tai jolle haluat
                                        suorittaa vertailun mikäli sitä ei ole vielä tehty.
                                    </Tooltip>
                                </label>
                                <Select
                                    label=""
                                    options={years}
                                    name="year"
                                    formObject={formObject}
                                    defaultValue={years[0]}
                                    setDirectValue={true}
                                    disabled={hasSkippedCompanies}
                                    required
                                />
                                <Select
                                    label=""
                                    options={hitasQuarterOptions}
                                    name="quarter"
                                    formObject={formObject}
                                    defaultValue={hitasQuarterOptions[hitasQuarterOptions.length - 1]}
                                    value={formTimePeriod}
                                    disabled={hasSkippedCompanies}
                                    required
                                />
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
                                    <Button
                                        theme="black"
                                        onClick={() => downloadRegulationResults(formDate)}
                                    >
                                        Lataa kokonaisraportti
                                    </Button>
                                )}
                            </div>
                        </div>
                        <Divider size="l" />
                        <div className="external-sales-data-import">
                            {hasExternalSalesData ? (
                                <h3 className="external-sales-data-exists">{`Ajanjaksolle ${formTimePeriod.label} on tallennettu postinumeroalueiden keskineliöhinnat.`}</h3>
                            ) : (
                                <ExternalSalesDataImport formDate={formDate} />
                            )}
                        </div>
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
                )}
            </div>
        </div>
    );
};

export default ThirtyYearRegulation;
