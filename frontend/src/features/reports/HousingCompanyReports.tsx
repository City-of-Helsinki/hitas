import {useForm} from "react-hook-form";
import DownloadButton from "../../common/components/DownloadButton";

const HousingCompanyReports = () => {
    const amountReportForm = useForm({
        mode: "all",
    });
    const {handleSubmit} = amountReportForm;
    return (
        <form onSubmit={handleSubmit((data) => console.log(data))}>
            <p>Lataa taloyhtiöiden ja asuntojen lukumäärät yhtiön tilan mukaan.</p>
            <DownloadButton
                buttonText="Lataa yhtiöraportti"
                type="submit"
            />
        </form>
    );
};

export default HousingCompanyReports;
