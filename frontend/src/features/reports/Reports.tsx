import {Accordion} from "hds-react";
import {Heading} from "../../common/components";
import HousingCompanyReports from "./HousingCompanyReports";
import SalesReports from "./SalesReports";

const Reports = () => {
    return (
        <div className="view--reports">
            <Heading>Raportit</Heading>
            <div className="reports-card">
                <Accordion
                    closeButton={false}
                    heading="Toteutuneet kauppahinnat"
                >
                    <SalesReports />
                </Accordion>
                <Accordion
                    closeButton={false}
                    heading="Yhtiön ja asuntojen raportit"
                >
                    <HousingCompanyReports />
                </Accordion>
                <Accordion
                    closeButton={false}
                    heading="Rajahintalaskelmat"
                >
                    <h2>Raportit 3</h2>
                </Accordion>
                <Accordion
                    closeButton={false}
                    heading="Enimmäishintojen vertailu"
                >
                    <h2>Raportit 4</h2>
                </Accordion>
            </div>
        </div>
    );
};

export default Reports;
