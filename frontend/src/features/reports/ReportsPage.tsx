import {Accordion} from "hds-react";
import {downloadSurfaceAreaPriceCeilingResults} from "../../app/services";
import {Divider, Heading} from "../../common/components";
import PriceCeilingsList from "../../common/components/PriceCeilingsList";
import {
    HousingCompanyReportRegulated,
    HousingCompanyReportReleased,
    HousingCompanyStatusTable,
} from "./components/HousingCompanyReports";
import OwnerReports from "./components/OwnerReports";
import {SalesReportAll, SalesReportByAreas} from "./components/SalesReports";

const ReportsPage = () => {
    return (
        <div className="view--reports">
            <Heading>Raportit</Heading>
            <div className="reports-card">
                <Accordion
                    heading="Kaupat"
                    closeButton={false}
                >
                    <Divider size="s" />
                    <SalesReportAll />
                    <Divider size="s" />
                    <SalesReportByAreas />
                </Accordion>

                <Accordion
                    heading="Taloyhtiöt"
                    closeButton={false}
                >
                    <Divider size="s" />
                    <HousingCompanyStatusTable />
                    <Divider size="s" />
                    <HousingCompanyReportRegulated />
                    <Divider size="s" />
                    <HousingCompanyReportReleased />
                </Accordion>

                <Accordion
                    heading="Rajahintalaskelmat"
                    closeButton={false}
                >
                    <PriceCeilingsList callbackFn={downloadSurfaceAreaPriceCeilingResults} />
                </Accordion>

                <Accordion
                    heading="Omistajien raportit"
                    closeButton={false}
                >
                    <Divider size="s" />
                    <OwnerReports />
                </Accordion>
            </div>
        </div>
    );
};

export default ReportsPage;
