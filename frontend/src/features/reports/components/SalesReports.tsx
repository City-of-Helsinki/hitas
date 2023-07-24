import {useForm} from "react-hook-form";
import {DownloadButton, Heading} from "../../../common/components";
import {DateInput, FormProviderForm} from "../../../common/components/forms";
import {SalesReportFormSchema} from "../../../common/schemas";
import {downloadSalesByPostalCodeAndAreaReportPDF, downloadSalesReportPDF} from "../../../common/services";
import {today} from "../../../common/utils";

const BaseSalesReport = ({header, downloadReportFunction}) => {
    const formObject = useForm({
        defaultValues: {
            startDate: "",
            endDate: today(),
        },
        mode: "all",
    });

    const formParse = SalesReportFormSchema.safeParse(formObject.watch());

    return (
        <div className="report-container">
            <FormProviderForm
                formObject={formObject}
                onSubmit={downloadReportFunction}
            >
                <Heading type="sub">{header}</Heading>
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
                <DownloadButton
                    buttonText="Lataa raportti"
                    disabled={!formParse.success}
                    type="submit"
                />
            </FormProviderForm>
        </div>
    );
};

export const SalesReportAll = () => {
    return (
        <BaseSalesReport
            header="Raportti kaikista kaupoista"
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
