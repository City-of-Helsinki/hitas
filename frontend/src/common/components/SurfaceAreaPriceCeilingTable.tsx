import {Table} from "hds-react";
import {useState} from "react";
import {IIndexCalculationData} from "../schemas";
import {downloadSurfaceAreaPriceCeilingResults, useGetSurfaceAreaPriceCeilingCalculationDataQuery} from "../services";
import {tableThemeBlack} from "../themes";
import {getHitasQuarterFullLabel} from "../utils";
import DownloadButton from "./DownloadButton";
import {FilterTextInputField} from "./filters";
import {QueryStateHandler} from "./index";

const DownloadSurfaceAreaPriceCeilingReportButton = ({calculation}) => {
    return (
        <div className="text-right">
            <DownloadButton
                onClick={() => downloadSurfaceAreaPriceCeilingResults(calculation.calculation_month)}
                buttonText="Lataa raportti"
                size="small"
            />
        </div>
    );
};

const LoadedSurfaceAreaPriceCeilingResultsList = ({
    data,
    tableColumns,
}: {
    data: IIndexCalculationData[];
    tableColumns;
}) => {
    // Parse the indices data into quarters
    const tableData = data
        .map((item) => {
            const timePeriodString = getHitasQuarterFullLabel(item.calculation_month, true);
            if (timePeriodString === undefined) return;

            return {
                period: timePeriodString,
                calculation_month: item.calculation_month,
                value: item.data.created_surface_area_price_ceilings[0].value,
            };
        })
        .filter((item) => item !== undefined) as {period: string; value: number; calculation_month: string}[];
    // Sort table data by month in ascending order
    tableData.sort((a, b) => (a.calculation_month > b.calculation_month ? 1 : -1));

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

const sapcTableColumns = [
    {
        key: "period",
        headerName: "Hitas-vuosineljännes",
        transform: (obj) => <div className="text-right">{obj.period}</div>,
    },
    {
        key: "value",
        headerName: "Rajaneliöhinta (€/m²)",
        transform: (obj) => <div className="text-right">{obj.value}</div>,
    },
    {
        key: "report",
        headerName: "Raportti",
        transform: (obj) => <DownloadSurfaceAreaPriceCeilingReportButton calculation={obj} />,
    },
];

const SurfaceAreaPriceCeilingTable = () => {
    const [filterParams, setFilterParams] = useState({year: new Date().getFullYear().toString()});

    const {
        currentData: sapcIndices,
        error: sapcIndicesError,
        isFetching: isSapcIndicesLoading,
    } = useGetSurfaceAreaPriceCeilingCalculationDataQuery(
        {
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
                <p className="help-text">
                    Rajaneliöhinnan raportti on saatavilla ainoastaan neljänneksille, joiden indeksin arvo on laskettu
                    tässä Hitas-järjestelmässä.
                </p>
            </div>
            <QueryStateHandler
                data={{contents: [true]}} // Always render the table, even if there is no data
                error={sapcIndicesError}
                isLoading={isSapcIndicesLoading}
            >
                <LoadedSurfaceAreaPriceCeilingResultsList
                    data={(filterParams.year ? sapcIndices?.contents : []) as unknown as IIndexCalculationData[]}
                    tableColumns={sapcTableColumns}
                />
            </QueryStateHandler>
        </div>
    );
};

export default SurfaceAreaPriceCeilingTable;
