import {Table} from "hds-react";
import {DownloadButton, Heading, QueryStateHandler} from "../../../common/components";
import {IHousingCompanyState} from "../../../common/schemas";
import {
    downloadHousingCompanyStatesReportPDF,
    downloadHalfHitasHousingCompaniesExcel,
    downloadRegulatedHousingCompaniesPDF,
    downloadUnregulatedHousingCompaniesPDF,
    downloadPropertyManagersReport,
    useGetHousingCompanyStatesQuery,
} from "../../../common/services";
import {tableThemeBlack} from "../../../common/themes";

const statusTableColumns = [
    {
        key: "status",
        headerName: "Tila",
    },
    {
        key: "housing_company_count",
        headerName: "Yhtiöitä",
        transform: (obj) => <div className="text-right">{obj.housing_company_count} kpl</div>,
    },
    {
        key: "apartment_count",
        headerName: "Asuntoja",
        transform: (obj) => <div className="text-right">{obj.apartment_count} kpl</div>,
    },
];

export const HousingCompanyStatusTable = () => {
    const {data, error, isLoading} = useGetHousingCompanyStatesQuery({});

    return (
        <div className="report-container">
            <Heading type="sub">Taloyhtiöiden tilat</Heading>
            <QueryStateHandler
                data={data}
                error={error}
                isLoading={isLoading}
            >
                <div className="housing-company-status-table">
                    <Table
                        cols={statusTableColumns}
                        rows={data as IHousingCompanyState[]}
                        indexKey="status"
                        theme={tableThemeBlack}
                        zebra
                    />
                </div>
                <DownloadButton
                    buttonText="Lataa raportti"
                    onClick={downloadHousingCompanyStatesReportPDF}
                />
            </QueryStateHandler>
        </div>
    );
};

export const HousingCompanyReportRegulated = () => {
    return (
        <div className="report-container">
            <div className="column">
                <Heading type="sub">Säännellyt yhtiöt</Heading>
                <span>Listaus sääntelyn piirissä olevista taloyhtiöistä</span>
                <div>
                    <DownloadButton
                        buttonText="Lataa raportti"
                        onClick={downloadRegulatedHousingCompaniesPDF}
                    />
                </div>
            </div>
        </div>
    );
};

export const HousingCompanyReportReleased = () => {
    return (
        <div className="report-container">
            <div className="column">
                <Heading type="sub">Vapautuneet yhtiöt</Heading>
                <span>Listaus sääntelystä piiristä vapautuneista taloyhtiöistä</span>
                <div>
                    <DownloadButton
                        buttonText="Lataa raportti"
                        onClick={downloadUnregulatedHousingCompaniesPDF}
                    />
                </div>
            </div>
        </div>
    );
};

export const HousingCompanyReportHalfHitas = () => {
    return (
        <div className="report-container">
            <div className="column">
                <Heading type="sub">Puolihitas-yhtiöt</Heading>
                <span>Listaus Puolihitas-taloyhtiöistä</span>
                <div>
                    <DownloadButton
                        buttonText="Lataa raportti"
                        onClick={downloadHalfHitasHousingCompaniesExcel}
                    />
                </div>
            </div>
        </div>
    );
};

export const PropertyManagerReport = () => {
    return (
        <div className="report-container">
            <div className="column">
                <Heading type="sub">Isännöitsijät</Heading>
                <span>Listaus isännöitsijöistä ja heidän isännöimistään taloyhtiöistä</span>
                <div>
                    <DownloadButton
                        buttonText="Lataa raportti"
                        onClick={downloadPropertyManagersReport}
                    />
                </div>
            </div>
        </div>
    );
};
