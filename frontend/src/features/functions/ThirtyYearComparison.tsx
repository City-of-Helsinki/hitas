import {Button, Tooltip} from "hds-react";
import {useForm} from "react-hook-form";
import {hitasQuarters} from "../../common/schemas";

import {useEffect, useState} from "react";
import {Link} from "react-router-dom";
import {
    useCreateThirtyYearComparisonMutation,
    useGetExternalSalesDataQuery,
    useGetThirtyYearRegulationQuery,
    useSaveExternalSalesDataMutation,
} from "../../app/services";
import {Divider, Heading, QueryStateHandler, SaveButton, SaveDialogModal} from "../../common/components";
import ErrorNotificationModal from "../../common/components/ErrorNotificationModal";
import {FileInput, Select} from "../../common/components/form";
import {formatDate, hdsToast} from "../../common/utils";
import {comparisonResponses, priceCeilings} from "./simulatedResponses";

const LoadedThirtyYearComparison = ({data}) => {
    if (data?.error !== undefined) return <h3>Error: {data.error}</h3>; // For testing purposes - error's shouldn't get here
    const automaticallyReleased = data?.automatically_released ?? [];
    const releasedFromRegulation = data?.released_from_regulation ?? [];
    const releasedCompanies = [...automaticallyReleased, ...releasedFromRegulation];
    const stayingCompanies = data?.stays_regulated ?? [];

    const ListItem = ({company}) => (
        <Link to={`/housing-companies/${company.id}`}>
            <li className="results-list__item">
                <div className="name">{company.display_name}</div>
                <div className="address">
                    {company.address.street_address}
                    <br />
                    {company.address.postal_code}, {company.address.city}
                </div>
                <div className="date">{formatDate(company.completion_date)}</div>
            </li>
        </Link>
    );

    const ListItems = ({list}) => {
        if (list.length < 1) return <p>Ei yhtiöitä!</p>;
        return list.map((item, idx) => (
            <ListItem
                company={item}
                key={idx}
            />
        ));
    };

    const ResultsList = ({category}) => (
        <div className={`companies companies--${category}`}>
            <Heading type="body">
                {category === "freed" ? "Vapautuneet " : "Valvonnan piiriin jäävät "}
                yhtiöt
            </Heading>
            <div className="list">
                <div className="list-headers">
                    <div className="list-header name">Nimi</div>
                    <div className="list-header address">Osoite</div>
                    <div className="list-header date">Valmistunut</div>
                </div>
                {releasedCompanies.length > 0 ? (
                    <ul className="results-list">
                        {category === "freed" ? (
                            <ListItems list={releasedCompanies} />
                        ) : (
                            <ListItems list={stayingCompanies} />
                        )}
                    </ul>
                ) : (
                    <p>Ei vapautuvia yhtiöitä</p>
                )}
            </div>
        </div>
    );

    return (
        <>
            <ResultsList category="freed" />
            <ResultsList category="remaining" />
        </>
    );
};
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
        {label: "Onnistunut vertailu", value: "noProblems"},
        {label: "Yhtiöta ei pystytty vertailemaan", value: "skippedCompany"},
        {label: "Ei yhtiöitä", value: "noCompanies"},
        {label: "Indeksi puuttuu", value: "missingIndex"},
        {label: "Excel-tiedosto puuttuu", value: "missingExcel"},
        {label: "Rajahinta puuttuu", value: "missingPriceCeiling"},
        {label: "Yhtiöltä puuttuu pinta-alaa", value: "missingSurfaceArea"},
        {label: "Jonkin yhtiön pinta-ala on 0", value: "zeroSurfaceArea"},
        {label: "Saman vertailun toisto", value: "alreadyCompared"},
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
    const comparisonData = isValidTestMode ? comparisonResponses.success : getComparisonData ?? makeComparisonData;
    const isComparisonLoading = isValidTestMode ? false : isGetComparisonLoading ?? isMakeComparisonLoading;
    const comparisonError = isValidTestMode
        ? comparisonResponses.failure[formTimePeriod.value]
        : getComparisonError ?? makeComparisonError;

    // ******************
    // * Event handlers *
    // ******************

    const onCompareButtonClick = (result) => {
        if (isTestMode) {
            if (formTimePeriod.value === "noProblems") {
                setHasComparison(true);
                hdsToast.success("Vertailu suoritettu onnistuneesti.");
            } else {
                setHasComparison(false);
                hdsToast.error("Vertailua ei voitu suorittaa!");
                setIsErrorModalOpen(true);
            }
            return;
        }
        makeComparison({data: {calculation_date: formDate}})
            .then(() => {
                setHasComparison(true);
                hdsToast.success("Vertailu suoritettu onnistuneesti.");
            })
            .catch((error) => {
                console.warn("Error:", error);
                setIsErrorModalOpen(true);
            });
    };

    // Submit = upload file
    const onSubmit = (data) => {
        if (isTestMode) {
            console.log("onSubmit event, with data.file:", data.file, "formFile:", formFile);
            return;
        }
        const fileWithDate = {
            data: data.file,
            calculation_date: formDate,
        };
        console.log("File + date:", fileWithDate);
        saveExternalSalesData(fileWithDate)
            .catch((error) => {
                console.warn("Caught error:", error);
                setIsSaveModalOpen(true);
            })
            .then((data) => {
                if ("error" in (data as object)) {
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
            console.log("Test mode ON!");
            setIsTestMode((prev) => true);
            formObject.setValue("quarter", testOptions[0], {shouldValidate: true});
        } else if (isTestMode) {
            console.log("Test mode OFF!");
            setIsTestMode((prev) => false);
        }
    }, [formYear]);

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
                        />
                        <Select
                            label=""
                            options={isTestMode ? testOptions : hitasQuarterOptions}
                            name="quarter"
                            formObject={formObject}
                            defaultValue={isTestMode ? testOptions[0] : hitasQuarterOptions[0]}
                            value={formTimePeriod}
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
                <Divider size="l" />
                {!hasTimePeriodFile ? (
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
            </div>
            {!hasComparison && (
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
            <QueryStateHandler
                data={comparisonData}
                error={comparisonError}
                isLoading={isComparisonLoading}
                attemptedAction="hae vertailun tulokset, tai suorita vertailu"
            >
                <LoadedThirtyYearComparison data={comparisonData} />
            </QueryStateHandler>
            <SaveDialogModal
                title="Tallennetaan excel-tiedostoa"
                data={savedExternalSalesData}
                error={saveExternalSalesDataError}
                isLoading={isExternalSalesDataSaving}
                isVisible={isSaveModalOpen}
                setIsVisible={setIsSaveModalOpen}
            />
            <ErrorNotificationModal
                isOpen={isErrorModalOpen}
                setIsOpen={setIsErrorModalOpen}
                error={comparisonError}
            />
        </div>
    );
};

export default ThirtyYearComparison;
