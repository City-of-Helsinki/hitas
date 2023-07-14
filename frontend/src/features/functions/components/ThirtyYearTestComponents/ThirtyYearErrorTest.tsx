import {useForm} from "react-hook-form";
import {FormProviderForm, SelectInput} from "../../../../common/components/forms";
import {ThirtyYearErrorTestResult} from "../index";

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

export default function ThirtyYearErrorTest() {
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
                />
            </FormProviderForm>
            <ThirtyYearErrorTestResult
                testType={testType}
                selection={selection}
                calculationDate="2023-05-02"
            />
        </>
    );
}
