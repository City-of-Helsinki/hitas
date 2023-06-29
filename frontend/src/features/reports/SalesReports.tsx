import {useForm} from "react-hook-form";
import {downloadSalesByPostalCodeAndAreaReportPDF, downloadSalesReportPDF} from "../../app/services";
import {Divider} from "../../common/components";
import DownloadButton from "../../common/components/DownloadButton";
import {DateInput} from "../../common/components/form";
import {today} from "../../common/utils";

const SalesReports = () => {
    const salesReportForm = useForm({
        defaultValues: {
            startDate: "",
            endDate: today(),
        },
        mode: "all",
    });
    const {handleSubmit: handleSaleSubmit, watch: watchSale} = salesReportForm;
    const amountReportForm = useForm({
        defaultValues: {
            startDate: "",
            endDate: today(),
        },
        mode: "all",
    });
    const {handleSubmit, watch} = amountReportForm;
    return (
        <>
            <Divider size="s" />
            <form onSubmit={handleSaleSubmit((data) => downloadSalesReportPDF(data.startDate, data.endDate))}>
                <h3>Raportti kaikista kaupoista aikavälillä</h3>
                <div className="date-input-wrap">
                    <DateInput
                        name="startDate"
                        label="Alkupäivämäärä"
                        formObject={salesReportForm}
                        tooltipText="Ensimmäinen päivä, jolta raportti lasketaan."
                        maxDate={new Date()}
                        required
                    />
                    <DateInput
                        name="endDate"
                        label="Loppupäivämäärä"
                        formObject={salesReportForm}
                        tooltipText="Viimeinen päivä, jolta raportti lasketaan."
                        maxDate={new Date()}
                        required
                    />
                </div>
                <DownloadButton
                    buttonText="Lataa raportti"
                    type="submit"
                    disabled={!watchSale("startDate") || !watchSale("endDate")}
                />
            </form>
            <Divider size="s" />
            <form
                onSubmit={handleSubmit((data) =>
                    downloadSalesByPostalCodeAndAreaReportPDF(data.startDate, data.endDate)
                )}
            >
                <h3>Raportti kaupoista postinumeroittain ja alueittain</h3>
                <div className="date-input-wrap">
                    <DateInput
                        name="startDate"
                        label="Alkaen pvm"
                        formObject={amountReportForm}
                        tooltipText="Ensimmäinen päivä, jolta raportti lasketaan."
                        required
                    />
                    <DateInput
                        name="endDate"
                        label="Päättyen pvm"
                        formObject={amountReportForm}
                        tooltipText="Viimeinen päivä, jolta raportti lasketaan."
                        required
                    />
                </div>
                <DownloadButton
                    buttonText="Lataa raportti"
                    type="submit"
                    disabled={!watch("startDate") || !watch("endDate")}
                />
            </form>
            <Divider size="s" />
        </>
    );
};

export default SalesReports;
