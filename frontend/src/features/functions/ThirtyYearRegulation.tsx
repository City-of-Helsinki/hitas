import {Button, Tooltip} from "hds-react";
import {useForm} from "react-hook-form";
import {hitasQuarters} from "../../common/schemas";

import {useState} from "react";
import {
    downloadRegulationResults,
    useCreateThirtyYearRegulationMutation,
    useGetExternalSalesDataQuery,
    useGetThirtyYearRegulationQuery,
    useSaveExternalSalesDataMutation,
} from "../../app/services";
import {Divider, Heading, QueryStateHandler, SaveDialogModal} from "../../common/components";
import {FileInput, Select, ToggleInput} from "../../common/components/form";
import {hdsToast} from "../../common/utils";
import {ThirtyYearErrorModal, ThirtyYearLoadedResults} from "./components";
import {priceCeilings, regulationAPIResponses} from "./simulatedResponses";

const ThirtyYearRegulation = () => {
    const currentTime = new Date();
    const [, forceRender] = useState(false);
    const [isSaveModalOpen, setIsSaveModalOpen] = useState(false);
    const [isErrorModalOpen, setIsErrorModalOpen] = useState(false);
    const years = [
        {label: "2023", value: "2023"},
        {label: "2022", value: "2022"},
        {label: "2021", value: "2021"},
    ];
    let defaultQuarter = {label: "1.2. - 30.4.", value: "02-01"};
    // set the correct selected quarter based on date
    switch (currentTime.getMonth()) {
        case 0:
        case 10:
        case 11:
            defaultQuarter = {label: "1.11. - 31.1.", value: "11-01"};
            break;
        case 4:
        case 5:
        case 6:
            defaultQuarter = {label: "1.5. - 31.7.", value: "05-01"};
            break;
        case 7:
        case 8:
        case 9:
            defaultQuarter = {label: "1.8. - 31.10.", value: "08-01"};
            break;
    }

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
        defaultValues: {
            year: years[0],
            quarter: defaultQuarter,
            file: undefined,
            test: false,
            testSelect: testOptions[0],
        },
        mode: "all",
    });
    const {watch, handleSubmit} = formObject;
    const formTimePeriod: {label: string; value: string} = watch("quarter");
    const formYear: {label: string; value: string} = watch("year");
    const formDate = `${formYear.value}-${formTimePeriod.value}`;
    const formFile: File | undefined = watch("file");
    const isTestMode: boolean = watch("test");
    const testSelection: {label: string; value: string} | null = watch("testSelect");

    // Populate the time quarter select with options, if current year is selected in the year selector
    const hitasQuarterOptions: {label: string; value: string}[] = [];
    // If the current year is not selected, add all quarters to the time period select options...
    if (currentTime.getFullYear().toString() !== formYear.value) {
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
    const [
        saveExternalSalesData,
        {data: savedExternalSalesData, isLoading: isExternalSalesDataSaving, error: saveExternalSalesDataError},
    ] = useSaveExternalSalesDataMutation();
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

    // Simulated API responses for the get/post thirty year regulation queries
    const priceCeiling = priceCeilings[formYear.value][formTimePeriod.value];
    let regulationData: object | undefined = getRegulationData ?? makeRegulationData;
    const isRegulationLoading = isTestMode ? false : isGetRegulationLoading ?? isMakeRegulationLoading;
    let regulationError = getRegulationError ?? makeRegulationError;
    // If test mode is on, use the selected test option to simulate a response or error
    if (isTestMode) {
        if (testSelection?.value.split("_")[0] === "result") {
            console.log("show non-error result");
            regulationData = regulationAPIResponses[formTimePeriod.value];
            regulationError = undefined;
        } else {
            regulationData = undefined;
            regulationError = regulationAPIResponses[formTimePeriod.value];
            setIsErrorModalOpen(() => true);
        }
    }

    // ******************
    // * Event handlers *
    // ******************

    const onCompareButtonClick = (data) => {
        // format eventual skipped data to match the API format
        const skippedArray: {postalCode: string; replacements: string[]}[] = [];
        if (data.skipped) {
            data.skipped.forEach((skipped) => {
                skippedArray.push({
                    postalCode: skipped.missingCode,
                    replacements: [skipped.postalCode1, skipped.postalCode2],
                });
            });
        }
        if (isTestMode && !data.skipped) {
            if (testSelection?.value.split("_")[0] === "result") {
                regulationData = regulationAPIResponses[testSelection?.value];
                regulationError = {};
                console.log(regulationData);
                forceRender((v) => !v);
            } else {
                regulationData = {};
                regulationError = regulationAPIResponses[testSelection?.value];
            }
            if (testSelection?.value.split("_")[0] === "error") setIsErrorModalOpen(true);
        } else
            makeRegulation({
                data: {
                    calculationDate: formDate,
                    replacementPostalCodes: skippedArray,
                },
            })
                .unwrap()
                .then((data) => {
                    hdsToast.success("Vertailu suoritettu  onnistuneesti!");
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
        saveExternalSalesData(fileWithDate)
            .unwrap()
            .then((data) => {
                if ("error" in (data as object)) {
                    console.warn("Uncaught error:", data.error);
                    setIsSaveModalOpen(true);
                } else {
                    // Successful upload
                    hdsToast.success("Postinumeroalueiden keskinumerohinnat ladattu onnistuneesti");
                    formObject.setValue("file", undefined, {shouldValidate: true});
                }
            })
            .catch((error) => {
                console.warn("Caught error:", error);
                setIsSaveModalOpen(true);
            });
    };
    const hasRegulationResults =
        (!isGetRegulationLoading && !getRegulationError && !!getRegulationData) || !!regulationData;
    console.log("show queryStateHandler:", hasRegulationResults, regulationData);
    const hasExternalSalesData = !isExternalSalesDataLoading && !externalSalesDataLoadError && !!externalSalesData;
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
                            defaultValue={
                                isTestMode ? testOptions[0] : hitasQuarterOptions[hitasQuarterOptions.length - 1]
                            }
                            value={formTimePeriod}
                            required
                        />
                    </div>
                    <div className="price-ceiling">
                        <label>
                            Rajaneliöhinta
                            {` (${formObject.getValues("quarter").label}${formObject.getValues("year").label})`}
                        </label>
                        <div className="value">{priceCeiling ?? "---"} €/m²</div>
                        {hasRegulationResults && (
                            <Button
                                theme="black"
                                onClick={() => downloadRegulationResults(formDate)}
                            >
                                Lataa kokonaisraportti
                            </Button>
                        )}
                    </div>
                </form>
                <Divider size="l" />
                {!hasExternalSalesData ? (
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
                            onChange={() => onSubmit(formObject.getValues())}
                        />
                    </form>
                ) : (
                    <h3 className="external-sales-data-exists">{`Ajanjaksolle ${formTimePeriod.label} on tallennettu postinumeroalueiden keskineliöhinnat.`}</h3>
                )}
            </div>
            {hasExternalSalesData && hasRegulationResults && (
                <QueryStateHandler
                    data={regulationData}
                    error={regulationData ? undefined : regulationError}
                    isLoading={isRegulationLoading}
                    attemptedAction="hae suoritetun vertailun tulokset"
                >
                    <ThirtyYearLoadedResults
                        data={regulationData}
                        calculationDate={formDate}
                        reCalculateFn={onCompareButtonClick}
                    />
                </QueryStateHandler>
            )}
            {!hasRegulationResults && !(regulationData as {skipped: object[]})?.skipped && (
                <div className="row row--buttons test-toggle">
                    <ToggleInput
                        name="test"
                        label="Testitila"
                        formObject={formObject}
                    />
                    {isTestMode && (
                        <Select
                            label="Vertailun lopputulos (simuloitu)"
                            tooltipText="Valitse lopputulos jota haluat testata. Huom! Testitilan ollessa päällä, todellista vertailua ei suoriteta."
                            options={testOptions}
                            name="testSelect"
                            formObject={formObject}
                            className="test-select"
                            defaultValue={testOptions[0]}
                        />
                    )}
                    <Button
                        theme="black"
                        onClick={onCompareButtonClick}
                        type="submit"
                        disabled={(!priceCeiling || !hasExternalSalesData) && !isTestMode}
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
            <ThirtyYearErrorModal
                isOpen={isErrorModalOpen}
                setIsOpen={setIsErrorModalOpen}
                response={regulationError}
            />
        </div>
    );
};

export default ThirtyYearRegulation;
