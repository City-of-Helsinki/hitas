import {useState} from "react";
import {Select} from "../../../common/components/form";
import {regulationAPIResponses} from "../simulatedResponses";
import {ThirtyYearErrorModal} from "./index";

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

export default function ThirtyYearErrorSelect({formObject, testObject}) {
    const [isModalOpen, setIsModalOpen] = useState(false);
    const {watch, handleSubmit} = formObject;
    const testSelection = watch("testSelect");
    const onChange = (data) => {
        console.log(data);
    };
    const onSubmit = () => {
        if (testSelection?.split("_")[0] === "result") {
            testObject.data = regulationAPIResponses[testSelection];
            testObject.error = {};
        } else {
            testObject.data = {};
            testObject.error = regulationAPIResponses[testSelection];
        }
        if (testSelection?.split("_")[0] === "error") setIsModalOpen(true);
    };
    return (
        <form
            className="error-test-form"
            onSubmit={handleSubmit(onSubmit)}
        >
            <Select
                label="Simuloitu virhe"
                options={testOptions}
                name="testSelect"
                formObject={formObject}
                onChange={onChange}
                setDirectValue={true}
            />
            <ThirtyYearErrorModal
                isOpen={isModalOpen}
                setIsOpen={setIsModalOpen}
                response={testObject.error}
            />
        </form>
    );
}
