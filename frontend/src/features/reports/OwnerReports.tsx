import {useForm} from "react-hook-form";
import {downloadMultipleOwnershipsReportPDF} from "../../app/services";
import {Divider} from "../../common/components";
import DownloadButton from "../../common/components/DownloadButton";

const OwnerReports = () => {
    const multipleOwnersForm = useForm();
    const {handleSubmit} = multipleOwnersForm;
    return (
        <>
            <Divider size="s" />
            <form onSubmit={handleSubmit(downloadMultipleOwnershipsReportPDF)}>
                <p>Listaus henkilöistä jotka omistavat useampia kuin yhden hitas-asunnon sekä heidän omistuksistaan.</p>
                <DownloadButton
                    buttonText="Lataa listaus"
                    type="submit"
                />
            </form>
        </>
    );
};

export default OwnerReports;
