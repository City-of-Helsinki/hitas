import {Button} from "hds-react";
import {useState} from "react";
import {QueryStateHandler} from "../../../common/components";
import {ThirtyYearLoadedResults} from "./index";

export default function ThirtyYearErrorTestResult({data, error, calculationDate, showTest}) {
    const [isShowingResult, setIsShowingResult] = useState(false);
    const handleSubmitClick = () => {
        console.log("handleSubmitClick");
        setIsShowingResult(true);
        console.log(data, error);
        showTest();
    };
    return (
        <>
            {isShowingResult && (
                <QueryStateHandler
                    data={data}
                    error={error}
                    isLoading={false}
                >
                    <ThirtyYearLoadedResults
                        data={data}
                        calculationDate={calculationDate}
                        reCalculateFn={showTest}
                    />
                </QueryStateHandler>
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
        </>
    );
}
