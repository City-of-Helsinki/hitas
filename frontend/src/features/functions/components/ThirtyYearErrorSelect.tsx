import {Select} from "../../../common/components/form";

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

export default function ThirtyYearErrorSelect({formObject}) {
    return (
        <form className="error-test-form">
            <Select
                label="Simuloitu virhe"
                options={testOptions}
                name="testSelection"
                formObject={formObject}
                defaultValue="result_noProblems"
                setDirectValue={true}
            />
        </form>
    );
}
