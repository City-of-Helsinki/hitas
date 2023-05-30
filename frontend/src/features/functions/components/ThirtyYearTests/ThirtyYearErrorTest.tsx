import {useForm} from "react-hook-form";
import {ThirtyYearErrorSelect, ThirtyYearErrorTestResult} from "../index";

export default function ThirtyYearErrorTest() {
    const testForm = useForm({
        defaultValues: {
            testSelection: "result_noProblems",
        },
        mode: "all",
    });
    const selection = testForm.watch("testSelection");
    const testType = selection.split("_")[0];
    return (
        <>
            <ThirtyYearErrorSelect formObject={testForm} />
            <ThirtyYearErrorTestResult
                testType={testType}
                selection={selection}
                calculationDate="2023-05-02"
            />
        </>
    );
}
