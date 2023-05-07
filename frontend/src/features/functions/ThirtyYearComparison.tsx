import {Button, Tooltip} from "hds-react";
import {useForm} from "react-hook-form";
import {hitasQuarters} from "../../common/schemas";

import {useEffect, useState} from "react";
import {
    useCreateThirtyYearComparisonMutation,
    useGetExternalSalesDataQuery,
    useGetThirtyYearRegulationQuery,
    useSaveExternalSalesDataMutation,
} from "../../app/services";
import {Divider, Heading, QueryStateHandler, SaveButton, SaveDialogModal} from "../../common/components";
import {FileInput, Select} from "../../common/components/form";
import {hdsToast} from "../../common/utils";
import {ComparisonErrorModal, LoadedThirtyYearComparison} from "./components";
import {comparisonResponses, priceCeilings} from "./simulatedResponses";

const ThirtyYearComparison = () => {
    const [isTestMode, setIsTestMode] = useState(false);
    const [isSaveModalOpen, setIsSaveModalOpen] = useState(false);
    const [isErrorModalOpen, setIsErrorModalOpen] = useState(false);
    const [hasComparison, setHasComparison] = useState(false);
    const years = [
        {label: "2023", value: "2023"},
        {label: "2022", value: "2022"},
        {label: "2021", value: "2021"},
        {label: "Testaus", value: "TEST"}, // TODO: remove this after testing/before release
    ];
    const testOptions = [
        {label: "Onnistunut vertailu", value: "result_noProblems"},
        {label: "Yhtiöta ei pystytty vertailemaan", value: "result_skippedCompany"},
        {label: "Ei yhtiöitä", value: "result_noCompanies"},
        {label: "Indeksi puuttuu", value: "error_missingIndex"},
        {label: "Excel-tiedosto puuttuu", value: "error_missingExcel"},
        {label: "Rajahinta puuttuu", value: "error_missingPriceCeiling"},
        {label: "Yhtiöltä puuttuu pinta-ala", value: "error_missingSurfaceArea"},
        {label: "Jonkin yhtiön pinta-ala on 0", value: "error_zeroSurfaceArea"},
        {label: "Saman vertailun toisto", value: "error_alreadyCompared"},
    ];

    // React hook form
    const formObject = useForm({
        defaultValues: {year: years[0], quarter: {label: "1.2. - 30.4.", value: "02-01"}, file: undefined},
        mode: "all",
    });
    const {watch, handleSubmit} = formObject;
    const formTimePeriod: {label: string; value: string} = watch("quarter");
    const formYear: {label: string; value: string} = watch("year");
    const formDate = `${formYear.value}-${formTimePeriod.value}`;
    const formFile: File | undefined = watch("file");

    // Function for adding a time period select option
    const addQuarterOption = (option) => {
        // If it's the last quarter, add the years to the date string in the label since the later date is in the next year
        const labelToAdd =
            option.value === "11-01"
                ? `${option.label.split(" ")[0]}${formYear.value} - ${option.label.split(" ")[2]}${
                      Number(formYear.value) + 1
                  }`
                : option.label;
        hitasQuarterOptions.push({value: option.value, label: labelToAdd});
    };

    // Populate the time quarter select with options, if current year is selected in the year selector
    const hitasQuarterOptions: {label: string; value: string}[] = [];
    const currentTime = new Date();
    // If the current year is not selected, add all quarters to the time period select options...
    if (currentTime.getFullYear().toString() !== formYear.value && !isNaN(Number(formYear.label))) {
        hitasQuarters.forEach((quarter) => addQuarterOption(quarter));
    } else {
        // ...otherwise add only the quarters that have passed
        for (let i = 0; i < 4; i++) {
            if (currentTime.getMonth() + 1 >= (i + 1) * 3 - 1) {
                addQuarterOption(hitasQuarters[i]);
            }
        }
    }

    // Queries and mutations
    const {
        data: externalSalesData,
        isLoading: isExternalSalesDataLoading,
        error: externalSalesDataLoadError,
    } = useGetExternalSalesDataQuery({
        calculation_date: formDate,
    });
    const [
        saveExternalSalesData,
        {data: savedExternalSalesData, isLoading: isExternalSalesDataSaving, error: saveExternalSalesDataError},
    ] = useSaveExternalSalesDataMutation();
    const {
        data: getComparisonData,
        isLoading: isGetComparisonLoading,
        error: getComparisonError,
    } = useGetThirtyYearRegulationQuery({
        calculation_date: formDate,
    });
    const [makeComparison, {data: makeComparisonData, isLoading: isMakeComparisonLoading, error: makeComparisonError}] =
        useCreateThirtyYearComparisonMutation();

    const hasTimePeriodFile = !isExternalSalesDataLoading && !externalSalesDataLoadError && !!externalSalesData;
    const isValidTestMode = isTestMode && isNaN(Number(formTimePeriod.value.charAt(0)));

    // Simulated comparison API responses
    const priceCeiling = priceCeilings[formYear.value][formTimePeriod.value];
    let comparisonData: object | undefined = getComparisonData ?? makeComparisonData;
    const isComparisonLoading = isValidTestMode ? false : isGetComparisonLoading ?? isMakeComparisonLoading;
    let comparisonError = getComparisonError ?? makeComparisonError;
    // If test mode is on, use the selected test option to simulate a response or error
    if (isTestMode) {
        if (formTimePeriod.value.split("_")[0] === "result") {
            comparisonData = comparisonResponses[formTimePeriod.value];
            comparisonError = undefined;
        } else {
            comparisonData = undefined;
            comparisonError = comparisonResponses[formTimePeriod.value];
        }
    }

    // ******************
    // * Event handlers *
    // ******************

    const onCompareButtonClick = (data) => {
        // format eventual skipped data to match the API format
        const skippedArray: object[] = [];
        if (data.skipped) {
            data.skipped.forEach((skipped) => {
                skippedArray.push({
                    postal_code: skipped.missingCode,
                    replacements: [skipped.postalCode1, skipped.postalCode2],
                });
            });
        }
        if (isTestMode && !data.skipped) {
            if (formTimePeriod.value.split("_")[0] === "result") {
                comparisonData = comparisonResponses[formTimePeriod.value];
                comparisonError = {};
            } else {
                comparisonData = {};
                comparisonError = comparisonResponses[formTimePeriod.value];
            }
            if (formTimePeriod.value.split("_")[0] === "error") setIsErrorModalOpen(true);
            else setHasComparison(true);
        } else
            makeComparison({
                data: {
                    calculation_date: isNaN(Number(formDate.substring(0, 1))) ? "2023-05-01" : formDate,
                    replacement_postal_codes: skippedArray,
                },
            })
                .unwrap()
                .then((data) => {
                    setHasComparison(true);
                    hdsToast.success("Vertailu suoritettu onnistuneesti!");
                })
                .catch((error) => {
                    console.warn("Error:", error);
                    setIsErrorModalOpen(true);
                });
    };

    // Submit = upload file
    const onSubmit = (data) => {
        const fileWithDate = {
            data: data.file,
            calculation_date: formDate,
        };
        if (isTestMode) {
            console.log("onSubmit event, with data.file:", data.file, "formFile:", formFile);
            return;
        } else
            saveExternalSalesData(fileWithDate)
                .unwrap()
                .catch((error) => {
                    console.warn("Caught error:", error);
                    setIsSaveModalOpen(true);
                })
                .then((data) => {
                    if ("error" in (data as object)) {
                        console.warn("Uncaught error:", data.error);
                        setIsSaveModalOpen(true);
                    } else {
                        // Successful upload
                        hdsToast.success("Postinumeroalueiden keskinumerohinnat ladattu onnistuneesti");
                        formObject.setValue("file", undefined, {shouldValidate: true});
                    }
                });
    };

    // *************
    // * Test mode *
    // *************
    useEffect(() => {
        if (formYear.value === "TEST") {
            setIsTestMode((prev) => true);
            setHasComparison(false);
            // set the value to the first test option if there is a date selected
            if (!isNaN(Number(formTimePeriod.value.charAt(0))))
                formObject.setValue("quarter", testOptions[0], {shouldValidate: true});
        } else if (isTestMode) {
            formObject.setValue("quarter", hitasQuarters[0], {shouldValidate: true});
            setIsTestMode((prev) => false);
        }
    }, [formDate]);

    return (
        <div className="view--functions__thirty-year-regulation">
            <div className="regulation">
                <Heading type="body">Vapautumisen tarkistus</Heading>
                <form
                    className="actions"
                    onSubmit={handleSubmit(onSubmit)}
                >
                    <div className="time-period">
                        <label>
                            Ajanjakso
                            <Tooltip placement="bottom-start">
                                Valitse vuosi ja jakso jonka vapautumisia haluat tarkastella, tai jolle haluat suorittaa
                                vertailun mikäli sitä ei ole vielä tehty.
                            </Tooltip>
                        </label>
                        <Select
                            label=""
                            options={years}
                            name="year"
                            formObject={formObject}
                            defaultValue={years[0]}
                            value={formYear}
                            required
                        />
                        <Select
                            label=""
                            options={isTestMode ? testOptions : hitasQuarterOptions}
                            name="quarter"
                            formObject={formObject}
                            defaultValue={isTestMode ? testOptions[0] : hitasQuarterOptions[0]}
                            value={formTimePeriod}
                            required
                        />
                    </div>
                    <div className="price-ceiling">
                        <label>
                            Rajaneliöhinta
                            {!isTestMode &&
                                ` (${formObject.getValues("quarter").label}${formObject.getValues("year").label})`}
                        </label>
                        <div className="value">{priceCeiling ?? "---"} €/m²</div>
                    </div>
                </form>
                {!isTestMode && (
                    <>
                        <Divider size="l" />
                        {!hasComparison && !hasTimePeriodFile ? (
                            <form
                                className={`file${formFile === undefined ? "" : " file--selected"}`}
                                onSubmit={handleSubmit(onSubmit)}
                            >
                                <FileInput
                                    name="file"
                                    id="file-input"
                                    buttonLabel="Valitse tiedosto"
                                    formObject={formObject}
                                    label="Syötä postinumeroalueiden keskineliöhinnat"
                                    tooltipText="Tilastokeskukselta saatu excel-tiedosto (.xslx)"
                                />
                                <SaveButton
                                    type="submit"
                                    isLoading={isExternalSalesDataSaving}
                                    onClick={(e) => {
                                        e.preventDefault();
                                        return;
                                    }}
                                    disabled={formFile === undefined}
                                    buttonText="Tallenna keskineliöhinnat"
                                />
                            </form>
                        ) : (
                            <h3 className="external-sales-data-exists">{`Ajanjaksolle ${formTimePeriod.label} on tallennettu postinumeroalueiden keskineliöhinnat.`}</h3>
                        )}
                    </>
                )}
            </div>
            {hasComparison ? (
                <QueryStateHandler
                    data={comparisonData}
                    error={comparisonError}
                    isLoading={isComparisonLoading}
                    attemptedAction="hae suoritetun vertailun tulokset"
                >
                    <LoadedThirtyYearComparison
                        data={comparisonData}
                        calculationDate={formDate}
                        reCalculateFn={onCompareButtonClick}
                    />
                </QueryStateHandler>
            ) : (
                <div className="row row--buttons">
                    <Button
                        theme="black"
                        onClick={onCompareButtonClick}
                        type="submit"
                        disabled={(!priceCeiling || !hasTimePeriodFile) && !isTestMode}
                    >
                        Aloita vertailu
                    </Button>
                </div>
            )}
            <SaveDialogModal
                title="Tallennetaan excel-tiedostoa"
                data={savedExternalSalesData}
                error={saveExternalSalesDataError}
                isLoading={isExternalSalesDataSaving}
                isVisible={isSaveModalOpen}
                setIsVisible={setIsSaveModalOpen}
            />
            <ComparisonErrorModal
                isOpen={isErrorModalOpen}
                setIsOpen={setIsErrorModalOpen}
                response={comparisonError}
            />
        </div>
    );
};

export default ThirtyYearComparison;
