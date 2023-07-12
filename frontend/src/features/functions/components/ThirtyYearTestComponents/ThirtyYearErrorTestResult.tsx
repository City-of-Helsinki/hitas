import {Button} from "hds-react";
import {useEffect, useState} from "react";
import {regulationAPIResponses} from "../../simulatedResponses";
import {ThirtyYearErrorModal, ThirtyYearLoadedResults} from "../index";

export default function ThirtyYearErrorTestResult({testType, selection, calculationDate}) {
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
}
