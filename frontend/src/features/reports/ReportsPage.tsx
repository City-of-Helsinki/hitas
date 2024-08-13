import {Accordion} from "hds-react";
import {Divider, Heading} from "../../common/components";
import {
    HousingCompanyReportRegulated,
    HousingCompanyReportHalfHitas,
    HousingCompanyReportReleased,
    HousingCompanyStatusTable,
} from "./components/HousingCompanyReports";
import OwnerReports from "./components/OwnerReports";
import {
    FirstSalesReportByAreas,
    ReSalesReportByAreas,
    SalesReportAll,
    SalesReportByAreas,
} from "./components/SalesReports";
import {SurfaceAreaPriceCeilingCalculationReport} from "./components/SurfaceAreaPriceCalculationReports";
import {JobPerformanceReport} from "./components/JobPerformanceReport";

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
                    <Divider size="s" />
                    <ReSalesReportByAreas />
                    <Divider size="s" />
                    <FirstSalesReportByAreas />
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
                    <Divider size="s" />
                    <HousingCompanyReportHalfHitas />
                </Accordion>

                <Accordion
                    heading="Rajahintalaskelmat"
                    closeButton={false}
                >
                    <Divider size="s" />
                    <SurfaceAreaPriceCeilingCalculationReport />
                </Accordion>

                <Accordion
                    heading="Omistajien raportit"
                    closeButton={false}
                >
                    <Divider size="s" />
                    <OwnerReports />
                </Accordion>

                <Accordion
                    heading="Suoritteet"
                    closeButton={false}
                >
                    <Divider size="s" />
                    <JobPerformanceReport />
                </Accordion>
            </div>
        </div>
    );
};

export default ReportsPage;
