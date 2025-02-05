import {useForm} from "react-hook-form";
import {DownloadButton, Heading} from "../../../common/components";
import {DateInput, FormProviderForm} from "../../../common/components/forms";
import {SalesReportFormSchema} from "../../../common/schemas";
import {
    downloadFirstSalesByPostalCodeAndAreaReportPDF,
    downloadReSalesByPostalCodeAndAreaReportPDF,
    downloadSalesAndMaximumPricesReportPDF,
    downloadSalesByPostalCodeAndAreaReportPDF,
    downloadSalesReportPDF,
} from "../../../common/services";
import {getLatestFullMonth} from "../../../common/utils";
import {format} from "date-fns";

const BaseSalesReport = ({header, downloadReportFunction}) => {
    const defaultDates = getLatestFullMonth();
    const formObject = useForm({
        defaultValues: {
            startDate: format(defaultDates.start, "yyyy-MM-dd"),
            endDate: format(defaultDates.end, "yyyy-MM-dd"),
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

export const SalesAndMaximumPricesReport = () => {
    return (
        <BaseSalesReport
            header="Vertailu toteutuneet velattomat kauppa- ja enimmäishinnat"
            downloadReportFunction={downloadSalesAndMaximumPricesReportPDF}
        />
    );
};

export const SalesReportByAreas = () => {
    return (
        <BaseSalesReport
            header="Kaikki kaupat postinumeroittain ja alueittain"
            downloadReportFunction={downloadSalesByPostalCodeAndAreaReportPDF}
        />
    );
};

export const ReSalesReportByAreas = () => {
    return (
        <BaseSalesReport
            header="Jälleenmyynnit postinumeroittain ja alueittain"
            downloadReportFunction={downloadReSalesByPostalCodeAndAreaReportPDF}
        />
    );
};

export const FirstSalesReportByAreas = () => {
    return (
        <BaseSalesReport
            header="Uudiskohteet postinumeroittain ja alueittain"
            downloadReportFunction={downloadFirstSalesByPostalCodeAndAreaReportPDF}
        />
    );
};
