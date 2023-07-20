import {downloadMultipleOwnershipsReportPDF} from "../../../app/services";
import {DownloadButton} from "../../../common/components";

const OwnerReports = () => {
    return (
        <div className="report-container">
            <p>Listaus henkilöistä jotka omistavat useampia kuin yhden hitas-asunnon sekä heidän omistuksistaan.</p>
            <DownloadButton
                buttonText="Lataa listaus"
                onClick={() => downloadMultipleOwnershipsReportPDF()}
            />
        </div>
    );
};

export default OwnerReports;
