import {IApartmentDetails} from "../../schemas";
import {hdsToast} from "../../utils";
import {fetchAndDownloadPDF, handleDownloadPDF, mutationApiJsonHeaders} from "../utils";

import {hitasApi} from "../apis";

export const downloadApartmentUnconfirmedMaximumPricePDF = (
    apartment: IApartmentDetails,
    requestDate: string,
    additionalInfo?: string,
    calculationDate?: string
) => {
    const url = `/housing-companies/${apartment.links.housing_company.id}/apartments/${apartment.id}/reports/download-latest-unconfirmed-prices`;
    const data = {additional_info: additionalInfo, request_date: requestDate, calculation_date: calculationDate};
    fetchAndDownloadPDF(url, "POST", data);
};

export const downloadApartmentMaximumPricePDF = (apartment: IApartmentDetails, requestDate?: string) => {
    if (!apartment.prices.maximum_prices.confirmed) {
        hdsToast.error("Enimmäishintalaskelmaa ei ole olemassa.");
        return;
    }
    const url = `/housing-companies/${apartment.links.housing_company.id}/apartments/${apartment.id}/reports/download-latest-confirmed-prices`;
    const data = {request_date: requestDate};
    fetchAndDownloadPDF(url, "POST", data);
};

export const downloadRegulationResults = (calculationDate?: string) => {
    const params = `calculation_date=${calculationDate}`;
    const url = `/thirty-year-regulation/reports/download-regulation-results?${params}`;
    fetchAndDownloadPDF(url);
};

export const downloadSurfaceAreaPriceCeilingResults = (calculationDate?: string) => {
    const params = `calculation_date=${calculationDate}`;
    const url = `/indices/surface-area-price-ceiling/reports/download-surface-area-price-ceiling-results?${params}`;
    fetchAndDownloadPDF(url);
};

export const downloadSalesReportPDF = ({startDate, endDate}: {startDate: string; endDate: string}) => {
    const params = `start_date=${startDate}&end_date=${endDate}`;
    const url = `/reports/download-sales-report?${params}`;
    fetchAndDownloadPDF(url);
};

export const downloadSalesByPostalCodeAndAreaReportPDF = ({
    startDate,
    endDate,
}: {
    startDate: string;
    endDate: string;
}) => {
    const params = `start_date=${startDate}&end_date=${endDate}`;
    const url = `/reports/download-sales-by-postal-code-and-area-report?${params}`;
    fetchAndDownloadPDF(url);
};

export const downloadRegulatedHousingCompaniesPDF = () =>
    fetchAndDownloadPDF("/reports/download-regulated-housing-companies-report");

export const downloadUnregulatedHousingCompaniesPDF = () =>
    fetchAndDownloadPDF("/reports/download-unregulated-housing-companies-report");

export const downloadHousingCompanyStatesReportPDF = () =>
    fetchAndDownloadPDF("/reports/download-housing-company-states-report");

export const downloadMultipleOwnershipsReportPDF = () =>
    fetchAndDownloadPDF("/reports/download-multiple-ownerships-report");

// Mutations are used to allow invalidating cache when PDF is downloaded
export const reportsApi = hitasApi.injectEndpoints({
    endpoints: (builder) => ({
        downloadThirtyYearRegulationLetter: builder.mutation<object, {id: string; calculationDate: string}>({
            query: ({id, calculationDate}) => {
                return {
                    url: `thirty-year-regulation/reports/download-regulation-letter?housing_company_id=${id}&calculation_date=${calculationDate}`,
                    method: "GET",
                    responseHandler: async (response) => handleDownloadPDF(response),
                    cache: "no-cache",
                };
            },
            invalidatesTags: (result, error, arg) => [{type: "ThirtyYearRegulation", id: arg.calculationDate}],
        }),
        getPDFBodies: builder.query({
            query: (arg) => ({
                url: "/pdf-bodies",
                params: arg,
            }),
        }),
        getHousingCompanyStates: builder.query({
            query: (arg) => ({
                url: "reports/housing-company-states",
                params: arg,
            }),
        }),
        editPDFTemplate: builder.mutation({
            query: (arg) => ({
                url: `pdf-bodies/${arg.name}`,
                method: "PUT",
                headers: mutationApiJsonHeaders(),
                body: arg,
            }),
        }),
    }),
});

export const {
    useDownloadThirtyYearRegulationLetterMutation,
    useEditPDFTemplateMutation,
    useGetHousingCompanyStatesQuery,
    useGetPDFBodiesQuery,
} = reportsApi;
