import {Button} from "hds-react";
import {useState} from "react";
import {QueryStateHandler} from "../../../common/components";
import {ThirtyYearLoadedResults} from "./index";

export default function ThirtyYearResults({
    hasResults,
    hasExternalSalesData,
    data,
    error,
    isLoading,
    date,
    priceCeilingValue,
    compareFn,
}) {
    // Because the compareFn doesn't play ball with isLoading, we need to keep track of whether the button has been
    // clicked. Clicking it again while the comparison is running results in errors.
    const [isButtonClicked, setIsButtonClicked] = useState(false);
    let req;
    const handleCompareButton = () => {
        setIsButtonClicked(true);
        compareFn()
            .then(() => setIsButtonClicked(false)) // wait until the comparison is done before re-enabling the button
            .catch((e) => {
                // eslint-disable-next-line no-console
                console.warn(e);
                setIsButtonClicked(false); // in the event of an error, re-enable the button
            });
    };
    return (
        <>
            {req?.status === "pending" ||
                (hasExternalSalesData && hasResults && (
                    <QueryStateHandler
                        data={data}
                        error={error}
                        isLoading={isLoading}
                        attemptedAction="hae suoritetun vertailun tulokset"
                    >
                        <ThirtyYearLoadedResults
                            data={data}
                            calculationDate={date}
                            reCalculateFn={compareFn}
                        />
                    </QueryStateHandler>
                ))}
            {!hasResults && !(data as unknown as {skipped: object[]})?.skipped && (
                <div className="row row--buttons ">
                    <Button
                        theme="black"
                        onClick={handleCompareButton}
                        type="submit"
                        disabled={!priceCeilingValue || !hasExternalSalesData || isButtonClicked} // Disable button if no price ceiling or no external sales data, or it has been clicked
                        isLoading={isButtonClicked} // show loading spinner while the comparison is running
                    >
                        Aloita vertailu
                    </Button>
                </div>
            )}
        </>
    );
}
