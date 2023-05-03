import {Tooltip} from "hds-react";
import {useForm} from "react-hook-form";
import {hitasQuarters} from "../../common/schemas";

import {useState} from "react";

import {useGetExternalSalesDataQuery, useSaveExternalSalesDataMutation} from "../../app/services";
import {Divider, Heading, SaveButton, SaveDialogModal} from "../../common/components";

import {FileInput, Select} from "../../common/components/form";
import {hdsToast} from "../../common/utils";
import {priceCeilings} from "./simulatedResponses";

const ThirtyYearComparison = () => {
    const [isSaveModalOpen, setIsSaveModalOpen] = useState(false);
    const years = [
        {label: "2023", value: "2023"},
        {label: "2022", value: "2022"},
        {label: "2021", value: "2021"},
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

    const hasTimePeriodFile = !isExternalSalesDataLoading && !externalSalesDataLoadError && !!externalSalesData;

    // Simulated comparison API responses
    const priceCeiling = priceCeilings[formYear.value][formTimePeriod.value];

    // ******************
    // * Event handlers *
    // ******************

    // Submit = upload file
    const onSubmit = (data) => {
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
                            options={hitasQuarterOptions}
                            name="quarter"
                            formObject={formObject}
                            defaultValue={hitasQuarterOptions[0]}
                            value={formTimePeriod}
                        />
                    </div>
                    <div className="price-ceiling">
                        <label>
                            Rajaneliöhinta
                            {` (${formObject.getValues("quarter").label}${formObject.getValues("year").label})`}
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
            <SaveDialogModal
                title="Tallennetaan excel-tiedostoa"
                data={savedExternalSalesData}
                error={saveExternalSalesDataError}
                isLoading={isExternalSalesDataSaving}
                isVisible={isSaveModalOpen}
                setIsVisible={setIsSaveModalOpen}
            />
        </div>
    );
};

export default ThirtyYearComparison;
