import {useForm} from "react-hook-form";
import DownloadButton from "../../common/components/DownloadButton";
import {DateInput} from "../../common/components/form";
import {today} from "../../common/utils";

const SalesReports = () => {
    const salesReportForm = useForm({
        defaultValues: {
            startDate: null,
            endDate: today(),
        },
        mode: "all",
    });
    const {handleSubmit, watch} = salesReportForm;

    return (
        <form
            className="row"
            onSubmit={handleSubmit((data) => console.log(data))}
        >
            <DateInput
                name="startDate"
                label="Alkaen pvm"
                formObject={salesReportForm}
                tooltipText="Ensimmäinen päivä, jolta raportti lasketaan."
                required
            />
            <DateInput
                name="endDate"
                label="Päättyen pvm"
                formObject={salesReportForm}
                tooltipText="Viimeinen päivä, jolta raportti lasketaan."
                required
            />
            <DownloadButton
                buttonText="Lataa raportti"
                type="submit"
                disabled={!watch("startDate") || !watch("endDate")}
            />
        </form>
    );
};

export default SalesReports;
