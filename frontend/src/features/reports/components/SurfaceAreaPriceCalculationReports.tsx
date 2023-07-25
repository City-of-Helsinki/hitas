import {Heading, SurfaceAreaPriceCeilingTable} from "../../../common/components";
import DownloadButton from "../../../common/components/DownloadButton";
import {IIndex} from "../../../common/schemas";
import {downloadSurfaceAreaPriceCeilingResults} from "../../../common/services";

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

export const SurfaceAreaPriceCeilingCalculationReport = () => {
    return (
        <div className="report-container surface-area-price-ceiling-report">
            <Heading type="sub">Raportit rajaneliöhintalaskelmista</Heading>
            <SurfaceAreaPriceCeilingTable
                tableColumns={sapcTableColumns}
                helpText={
                    "Rajaneliöhinnan raportti on saatavilla ainoastaan kuukausille," +
                    " joiden indeksin arvo on laskettu tässä Hitas-järjestelmässä."
                }
            />
        </div>
    );
};
