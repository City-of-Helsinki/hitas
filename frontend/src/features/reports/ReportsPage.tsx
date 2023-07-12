import {Accordion} from "hds-react";
import {downloadSurfaceAreaPriceCeilingResults} from "../../app/services";
import {Heading} from "../../common/components";
import PriceCeilingsList from "../../common/components/PriceCeilingsList";
import HousingCompanyReports from "./HousingCompanyReports";
import OwnerReports from "./OwnerReports";
import SalesReports from "./SalesReports";

const ReportsPage = () => {
    return (
        <div className="view--reports">
            <Heading>Raportit</Heading>
            <div className="reports-card">
                <Accordion
                    heading="Kaupat"
                    closeButton={false}
                >
                    <SalesReports />
                </Accordion>
                <Accordion
                    heading="Taloyhtiöt"
                    closeButton={false}
                >
                    <HousingCompanyReports />
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
                    <OwnerReports />
                </Accordion>
            </div>
        </div>
    );
};

export default ReportsPage;
