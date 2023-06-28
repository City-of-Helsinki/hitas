import {Button} from "hds-react";
import {useForm} from "react-hook-form";
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
            <Button
                theme="black"
                type="submit"
                disabled={!watch("startDate") || !watch("endDate")}
            >
                Lataa raportti
            </Button>
        </form>
    );
};

export default SalesReports;
