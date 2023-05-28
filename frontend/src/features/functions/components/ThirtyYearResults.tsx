import {Button} from "hds-react";
import {QueryStateHandler} from "../../../common/components";
import {ThirtyYearLoadedResults} from "./index";

export default function ThirtyYearResults({
    hasResults,
    hasData,
    data,
    error,
    isLoading,
    date,
    priceCeiling,
    compareFn,
}) {
    return (
        <>
            {hasData && hasResults && (
                <QueryStateHandler
                    data={data}
                    error={data ? undefined : error}
                    isLoading={isLoading}
                    attemptedAction="hae suoritetun vertailun t ulokset"
                >
                    <ThirtyYearLoadedResults
                        data={data}
                        calculationDate={date}
                        reCalculateFn={compareFn}
                    />
                </QueryStateHandler>
            )}
            {!hasResults && !(data as unknown as {skipped: object[]})?.skipped && (
                <div className="row row--buttons">
                    <Button
                        theme="black"
                        onClick={compareFn}
                        type="submit"
                        disabled={!priceCeiling || !hasData}
                    >
                        Aloita vertailu
                    </Button>
                </div>
            )}
        </>
    );
}
