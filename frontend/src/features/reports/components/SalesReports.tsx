import {useForm} from "react-hook-form";
import {downloadSalesByPostalCodeAndAreaReportPDF, downloadSalesReportPDF} from "../../../app/services";
import {DownloadButton} from "../../../common/components";
import {DateInput, FormProviderForm} from "../../../common/components/forms";
import {today} from "../../../common/utils";

const BaseSalesReport = ({header, downloadReportFunction}) => {
    const formObject = useForm({
        defaultValues: {
            startDate: "",
            endDate: today(),
        },
        mode: "all",
    });

    const values = formObject.watch();

    return (
        <div className="report-container">
            <FormProviderForm
                formObject={formObject}
                onSubmit={downloadReportFunction}
            >
                <h3>{header}</h3>
                <div className="date-input-wrap">
                    <DateInput
                        name="startDate"
                        label="Alkupäivämäärä"
                        tooltipText="Ensimmäinen päivä, jolta raportti lasketaan."
                        maxDate={new Date()}
                        required
                    />
                    <DateInput
                        name="endDate"
                        label="Loppupäivämäärä"
                        tooltipText="Viimeinen päivä, jolta raportti lasketaan."
                        maxDate={new Date()}
                        required
                    />
                </div>
            </FormProviderForm>
            <DownloadButton
                buttonText="Lataa raportti"
                onClick={() => downloadReportFunction(values)}
                disabled={!values.startDate || !values.endDate}
            />
        </div>
    );
};

export const SalesReportAll = () => {
    return (
        <BaseSalesReport
            header="Raportti kaikista kaupoista aikavälillä"
            downloadReportFunction={downloadSalesReportPDF}
        />
    );
};

export const SalesReportByAreas = () => {
    return (
        <BaseSalesReport
            header="Raportti kaupoista postinumeroittain ja alueittain"
            downloadReportFunction={downloadSalesByPostalCodeAndAreaReportPDF}
        />
    );
};
