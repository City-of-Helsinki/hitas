import {Button} from "hds-react";
import {useEffect, useState} from "react";
import {useForm} from "react-hook-form";
import {FormProviderForm, SelectInput} from "../../../common/components/forms";
import {regulationAPIResponses} from "../simulatedResponses";
import {ThirtyYearErrorModal, ThirtyYearLoadedResults} from "./index";

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

const ThirtyYearErrorTestResult = ({testType, selection, calculationDate}) => {
    const [isShowingResult, setIsShowingResult] = useState(false);
    const [isModalOpen, setIsModalOpen] = useState(false);
    const handleSubmitClick = () => {
        if (testType === "result") {
            setIsShowingResult(true);
        } else {
            setIsModalOpen(true);
        }
    };
    useEffect(() => {
        setIsShowingResult(false);
        setIsModalOpen(false);
    }, [selection]);
    return (
        <>
            {isShowingResult && (
                <ThirtyYearLoadedResults
                    data={testType === "result" ? regulationAPIResponses[selection] : {}}
                    calculationDate={calculationDate}
                    reCalculateFn={() => {
                        return;
                    }}
                />
            )}
            <div className="row row--buttons">
                <Button
                    theme="black"
                    onClick={handleSubmitClick}
                    type="submit"
                >
                    Aja testivertailu
                </Button>
            </div>
            <ThirtyYearErrorModal
                isOpen={isModalOpen}
                setIsOpen={setIsModalOpen}
                response={testType !== "result" ? regulationAPIResponses[selection] : {}}
            />
        </>
    );
};

const ThirtyYearErrorTest = () => {
    const formObject = useForm({
        defaultValues: {
            testSelection: "result_noProblems",
        },
        mode: "all",
    });

    const selection = formObject.watch("testSelection");
    const testType = selection.split("_")[0];

    return (
        <>
            <FormProviderForm
                formObject={formObject}
                onSubmit={() => null} // Test form does not need to submit
                className="error-test-form"
            >
                <SelectInput
                    label="Simuloitu virhe"
                    name="testSelection"
                    options={testOptions}
                    defaultValue="result_noProblems"
                    setDirectValue
                    required
                />
            </FormProviderForm>
            <ThirtyYearErrorTestResult
                testType={testType}
                selection={selection}
                calculationDate="2023-05-02"
            />
        </>
    );
};

export default ThirtyYearErrorTest;
