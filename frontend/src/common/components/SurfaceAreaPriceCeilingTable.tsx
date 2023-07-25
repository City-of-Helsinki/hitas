import {Table} from "hds-react";
import {useState} from "react";
import {IIndex} from "../schemas";
import {useGetIndicesQuery} from "../services";
import {tableThemeBlack} from "../themes";
import {getHitasQuarterFullLabel} from "../utils";
import {FilterTextInputField} from "./filters";
import {QueryStateHandler} from "./index";

const LoadedSurfaceAreaPriceCeilingResultsList = ({data, tableColumns}: {data: IIndex[]; tableColumns}) => {
    // Parse the indices data into quarters
    const tableData = data
        .map((item) => {
            const timePeriodString = getHitasQuarterFullLabel(item.month, true);
            if (timePeriodString === undefined) return;

            return {
                period: timePeriodString,
                month: item.month,
                value: item.value,
            };
        })
        .filter((item) => item !== undefined) as {period: string; value: number; month: string}[];
    // Sort table data by month in ascending order
    tableData.sort((a, b) => (a.month > b.month ? 1 : -1));

    return (
        <>
            <Table
                cols={tableColumns}
                rows={tableData.length ? tableData : [{period: "Ei tuloksia"}]}
                indexKey="period"
                theme={tableThemeBlack}
                zebra
            />
        </>
    );
};

const SurfaceAreaPriceCeilingTable = ({tableColumns, helpText}: {tableColumns; helpText?: string}) => {
    const [filterParams, setFilterParams] = useState({year: new Date().getFullYear().toString()});

    const {
        currentData: sapcIndices,
        error: sapcIndicesError,
        isFetching: isSapcIndicesLoading,
    } = useGetIndicesQuery(
        {
            indexType: "surface-area-price-ceiling",
            params: {...filterParams, limit: 12, page: 1},
        },
        {skip: !filterParams.year}
    );

    return (
        <div className="surface-area-price-ceiling-container">
            <div className="filter-container">
                <FilterTextInputField
                    label="Vuosi"
                    filterFieldName="year"
                    defaultValue={filterParams.year}
                    filterParams={filterParams}
                    setFilterParams={setFilterParams}
                    minLength={4}
                    maxLength={4}
                    tooltipText="Syötä vuosiluku nähdäksesi sille lasketut rajaneliöhintaraportit"
                    required
                />
                {helpText && <p className="help-text">{helpText}</p>}
            </div>
            <QueryStateHandler
                data={{contents: [true]}} // Always render the table, even if there is no data
                error={sapcIndicesError}
                isLoading={isSapcIndicesLoading}
            >
                <LoadedSurfaceAreaPriceCeilingResultsList
                    data={(filterParams.year ? sapcIndices?.contents : []) as unknown as IIndex[]}
                    tableColumns={tableColumns}
                />
            </QueryStateHandler>
        </div>
    );
};

export default SurfaceAreaPriceCeilingTable;
