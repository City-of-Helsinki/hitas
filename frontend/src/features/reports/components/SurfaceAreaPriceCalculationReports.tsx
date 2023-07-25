import {Table} from "hds-react";
import {useState} from "react";
import {Heading, QueryStateHandler} from "../../../common/components";
import DownloadButton from "../../../common/components/DownloadButton";
import {FilterTextInputField} from "../../../common/components/filters";
import {IIndex} from "../../../common/schemas";
import {downloadSurfaceAreaPriceCeilingResults, useGetIndicesQuery} from "../../../common/services";
import {tableThemeBlack} from "../../../common/themes";
import {getHitasQuarter} from "../../../common/utils";

const DownloadSurfaceAreaPriceCeilingReportButton = ({index}: {index: IIndex}) => {
    if (!index.value) return <></>;

    return (
        <div className="text-right">
            <DownloadButton
                onClick={() => downloadSurfaceAreaPriceCeilingResults(index.month + "-01")}
                buttonText="Lataa raportti"
                size="small"
            />
        </div>
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
        transform: (obj) => <DownloadSurfaceAreaPriceCeilingReportButton index={obj} />,
    },
];

const getSurfaceAreaPriceCeilingLabel = (month: string) => {
    const [yearString, monthString] = month.split("-");

    const hitasQuarter = getHitasQuarter(month).label;

    switch (monthString) {
        case "01":
            // add the previous year in the start date for january, as its quarter begins in the previous year
            return `${hitasQuarter.split(" ")[0]}${Number(yearString) - 1} - ${
                hitasQuarter.split("-")[1]
            }${yearString} (Q4)`;
        // for the months which start a new quarter, simply add the year to the end of the quarter label
        case "02":
            return `${hitasQuarter}${yearString} (Q1)`;
        case "05":
            return `${hitasQuarter}${yearString} (Q2)`;
        case "08":
            return `${hitasQuarter}${yearString} (Q3)`;
        case "11":
            // add the next year in the end date for the last quarter, as the quarter ends in the next year
            return `${hitasQuarter.split(" ")[0]}${yearString} - ${hitasQuarter.split("-")[1]}${
                Number(yearString) + 1
            } (Q4)`;
        default:
            // for the months which are not the start of a new quarter (or year), do not display the value
            break;
    }
};

const LoadedSurfaceAreaPriceCeilingResultsList = ({data}: {data: IIndex[]}) => {
    // Parse the indices data into quarters
    const tableData = data
        .map((item) => {
            const timePeriodString = getSurfaceAreaPriceCeilingLabel(item.month);
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
                cols={sapcTableColumns}
                rows={tableData.length ? tableData : [{period: "Ei tuloksia"}]}
                indexKey="period"
                theme={tableThemeBlack}
                zebra
            />
        </>
    );
};

export const SurfaceAreaPriceCalculationReport = () => {
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
        <div className="report-container surface-area-price-ceiling-report-container">
            <Heading type="sub">Raportit rajaneliöhintalaskelmista</Heading>
            <div className="surface-area-price-ceiling-list">
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
                        Rajaneliöhinnan raportti on saatavilla ainoastaan kuukausille, joiden indeksin arvo on laskettu
                        tässä Hitas-järjestelmässä.
                    </p>
                </div>
                <QueryStateHandler
                    data={{contents: [true]}} // Always render the table, even if there is no data
                    error={sapcIndicesError}
                    isLoading={isSapcIndicesLoading}
                >
                    <LoadedSurfaceAreaPriceCeilingResultsList
                        data={(filterParams.year ? sapcIndices?.contents : []) as unknown as IIndex[]}
                    />
                </QueryStateHandler>
            </div>
        </div>
    );
};
