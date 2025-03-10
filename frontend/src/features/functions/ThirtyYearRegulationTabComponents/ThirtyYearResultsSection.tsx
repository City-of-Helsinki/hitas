import {QueryStateHandler} from "../../../common/components";
import {ThirtyYearLoadedResults} from "./index";
import {Button, ButtonPresetTheme, LoadingSpinner} from "hds-react";
import {IThirtyYearRegulationResponse} from "../../../common/schemas";

const RunThirtyYearRegulationButton = ({
    hasResults,
    regulationData,
    handleCompareButtonClick,
    priceCeilingValue,
    hasExternalSalesData,
    isRegulationLoading,
}) => {
    if (hasResults || regulationData?.skipped?.length > 0) {
        return null;
    }

    return (
        <div className="row row--buttons">
            <div className="column">
                <Button
                    theme={ButtonPresetTheme.Black}
                    onClick={handleCompareButtonClick}
                    type="submit"
                    disabled={!priceCeilingValue || !hasExternalSalesData || isRegulationLoading}
                    iconStart={isRegulationLoading ? <LoadingSpinner small /> : undefined}
                >
                    Aloita vertailu
                </Button>
            </div>
        </div>
    );
};

interface ThirtyYearResultsSectionProps {
    hasExternalSalesData: boolean;
    hasResults: boolean;
    regulationData?: IThirtyYearRegulationResponse;
    regulationError;
    isRegulationLoading: boolean;
    calculationMonth: string;
    priceCeilingValue?: number;
    handleCompareButtonClick;
}

const ThirtyYearResultsSection = ({
    hasExternalSalesData,
    hasResults,
    regulationData,
    regulationError,
    isRegulationLoading,
    calculationMonth,
    priceCeilingValue,
    handleCompareButtonClick,
}: ThirtyYearResultsSectionProps) => {
    return (
        <>
            {hasExternalSalesData && hasResults && (
                <QueryStateHandler
                    data={regulationData}
                    error={regulationError}
                    isLoading={isRegulationLoading}
                    attemptedAction="hae suoritetun vertailun tulokset"
                >
                    <ThirtyYearLoadedResults
                        data={regulationData}
                        calculationDate={calculationMonth}
                        reCalculateFn={handleCompareButtonClick}
                    />
                </QueryStateHandler>
            )}

            <RunThirtyYearRegulationButton
                hasExternalSalesData={hasExternalSalesData}
                hasResults={hasResults}
                regulationData={regulationData}
                isRegulationLoading={isRegulationLoading}
                priceCeilingValue={priceCeilingValue}
                handleCompareButtonClick={handleCompareButtonClick}
            />
        </>
    );
};

export default ThirtyYearResultsSection;
