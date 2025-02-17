import {
    ApartmentSalesJobPerformanceResponse,
    IAPIIdString,
    IApartmentDetails,
    JobPerformanceResponse,
} from "../../schemas";
import {hdsToast} from "../../utils";
import {fetchAndDownloadPDF, handleDownloadPDF, safeInvalidate} from "../utils";
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

export const downloadSalesAndMaximumPricesReportPDF = ({startDate, endDate}: {startDate: string; endDate: string}) => {
    const params = `start_date=${startDate}&end_date=${endDate}`;
    const url = `/reports/download-sales-and-maximum-prices-report?${params}`;
    fetchAndDownloadPDF(url);
};

export const downloadSalesByPostalCodeAndAreaReportPDF = ({
    startDate,
    endDate,
    filter,
}: {
    startDate: string;
    endDate: string;
    filter?: string;
}) => {
    const params = `start_date=${startDate}&end_date=${endDate}` + (filter ? `&filter=${filter}` : "");
    const url = `/reports/download-sales-by-postal-code-and-area-report?${params}`;
    fetchAndDownloadPDF(url);
};

export const downloadReSalesByPostalCodeAndAreaReportPDF = ({
    startDate,
    endDate,
}: {
    startDate: string;
    endDate: string;
}) => {
    downloadSalesByPostalCodeAndAreaReportPDF({startDate, endDate, filter: "resale"});
};

export const downloadFirstSalesByPostalCodeAndAreaReportPDF = ({
    startDate,
    endDate,
}: {
    startDate: string;
    endDate: string;
}) => {
    downloadSalesByPostalCodeAndAreaReportPDF({startDate, endDate, filter: "firstsale"});
};

export const downloadRegulatedHousingCompaniesPDF = () =>
    fetchAndDownloadPDF("/reports/download-regulated-housing-companies-report");

export const downloadHalfHitasHousingCompaniesExcel = () =>
    fetchAndDownloadPDF("/reports/download-half-hitas-housing-companies-report");

export const downloadUnregulatedHousingCompaniesPDF = () =>
    fetchAndDownloadPDF("/reports/download-unregulated-housing-companies-report");

export const downloadHousingCompanyStatesReportPDF = () =>
    fetchAndDownloadPDF("/reports/download-housing-company-states-report");

export const downloadRegulatedOwnershipsReportExcel = () =>
    fetchAndDownloadPDF("/reports/download-regulated-ownerships-report");

export const downloadMultipleOwnershipsReportPDF = () =>
    fetchAndDownloadPDF("/reports/download-multiple-ownerships-report");

export const downloadHousingCompanyWithOwnersExcel = (id: IAPIIdString) =>
    fetchAndDownloadPDF(`/reports/download-ownership-by-housing-company-report/${id}`);

export const downloadPropertyManagersReport = () => fetchAndDownloadPDF("/reports/download-property-managers-report");

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
            invalidatesTags: (result, error, arg) =>
                safeInvalidate(error, [{type: "ThirtyYearRegulation", id: arg.calculationDate}]),
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
        savePDFTemplate: builder.mutation({
            query: (arg) => ({
                url: `pdf-bodies${arg.createTemplate ? "" : `/${arg.name}`}`,
                method: arg.createTemplate ? "POST" : "PUT",
                body: {name: arg.name, texts: arg.texts},
            }),
        }),
    }),
});

export const {
    useDownloadThirtyYearRegulationLetterMutation,
    useSavePDFTemplateMutation,
    useGetHousingCompanyStatesQuery,
    useGetPDFBodiesQuery,
} = reportsApi;

// Mutations are used to allow invalidating cache when PDF is downloaded
export const jobPerformanceApi = hitasApi.injectEndpoints({
    endpoints: (builder) => ({
        getConfirmedMaximumPriceJobPerformance: builder.query<
            JobPerformanceResponse,
            {params: {start_date: string; end_date: string}}
        >({
            query: ({params}) => ({
                url: "job-performance/confirmed-maximum-price",
                params: params,
            }),
        }),
        getUnconfirmedMaximumPriceJobPerformance: builder.query<
            JobPerformanceResponse,
            {params: {start_date: string; end_date: string}}
        >({
            query: ({params}) => ({
                url: "job-performance/unconfirmed-maximum-price",
                params: params,
            }),
        }),
        getApartmentSalesJobPerformance: builder.query<
            ApartmentSalesJobPerformanceResponse,
            {params: {start_date: string; end_date: string}}
        >({
            query: ({params}) => ({
                url: "job-performance/apartment-sales",
                params: params,
            }),
        }),
    }),
});

export const {
    useGetConfirmedMaximumPriceJobPerformanceQuery,
    useGetUnconfirmedMaximumPriceJobPerformanceQuery,
    useGetApartmentSalesJobPerformanceQuery,
} = jobPerformanceApi;
