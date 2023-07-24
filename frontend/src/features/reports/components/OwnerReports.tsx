import {DownloadButton, Heading} from "../../../common/components";
import {downloadMultipleOwnershipsReportPDF} from "../../../common/services";

const OwnerReports = () => {
    return (
        <div className="report-container">
            <div className="column">
                <Heading type="sub">Usean Hitas-asunnon omistajat</Heading>
                <span>
                    Listaus henkilöistä, jotka omistavat useamman kuin yhden Hitas-asunnon, sekä heidän omistuksistaan.
                </span>
                <div>
                    <DownloadButton
                        buttonText="Lataa raportti"
                        onClick={downloadMultipleOwnershipsReportPDF}
                    />
                </div>
            </div>
        </div>
    );
};

export default OwnerReports;
