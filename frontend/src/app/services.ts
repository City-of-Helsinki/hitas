import {createApi, fetchBaseQuery} from "@reduxjs/toolkit/query/react";

import {getCookie} from "typescript-cookie";
import {
    IApartmentDetails,
    IApartmentListResponse,
    IApartmentMaximumPriceCalculationDetails,
    IApartmentMaximumPriceWritable,
    IApartmentQuery,
    IApartmentSale,
    IApartmentSaleCreated,
    IApartmentUnconfirmedMaximumPriceIndices,
    IApartmentWritable,
    IBuilding,
    IBuildingWritable,
    ICodeResponse,
    IConditionOfSale,
    ICreateConditionOfSale,
    IDeveloper,
    IExternalSalesDataResponse,
    IFilterDevelopersQuery,
    IFilterOwnersQuery,
    IFilterPropertyManagersQuery,
    IHousingCompanyApartmentQuery,
    IHousingCompanyDetails,
    IHousingCompanyListResponse,
    IHousingCompanyWritable,
    IIndex,
    IIndexListQuery,
    IIndexListResponse,
    IIndexQuery,
    IIndexResponse,
    IOwner,
    IOwnersResponse,
    IPostalCodeResponse,
    IPropertyManager,
    IPropertyManagersResponse,
    IRealEstate,
    IThirtyYearAvailablePostalCodesResponse,
    IThirtyYearRegulationQuery,
    IThirtyYearRegulationResponse,
    IUserInfoResponse,
} from "../common/schemas";
import {hdsToast} from "../common/utils";

// /////////
// Config //
// /////////

declare global {
    interface Window {
        __env: Record<string, string> | undefined;
    }
}

export class Config {
    static token = process.env.REACT_APP_AUTH_TOKEN;
    static api_base_url =
        window.__env !== undefined ? window.__env.API_URL : process.env.REACT_APP_API_URL || "http://localhost:8000";
    // Derived settings
    static api_v1_url = Config.api_base_url + "/api/v1";
    static api_auth_url = Config.api_base_url + "/helauth";
}

// ////////
// Utils //
// ////////

// Helper to return either the passed value prefixed with `/` or an empty string
const idOrBlank = (id: string | undefined) => (id ? `/${id}` : "");

const getFetchInit = () => {
    return {
        headers: new Headers({
            "Content-Type": "application/json",
            ...(getCookie("csrftoken") && {"X-CSRFToken": getCookie("csrftoken")}),
            ...(Config.token && {Authorization: "Bearer " + Config.token}),
        }),
        method: "POST",
        ...(!Config.token && {credentials: "include" as RequestCredentials}),
    };
};

const handleDownloadPDF = (response) => {
    response
        .blob()
        .then((blob) => {
            const filename = response.headers.get("Content-Disposition")?.split("=")[1];
            if (filename === undefined) {
                hdsToast.error("Virhe ladattaessa tiedostoa.");
                return;
            }

            const alink = document.createElement("a");
            alink.href = window.URL.createObjectURL(blob);
            alink.download = `${filename}`;
            alink.click();
        })
        // eslint-disable-next-line no-console
        .catch((error) => console.error(error));
};

const fetchAndDownloadPDF = (url: string, data: object) => {
    const init = {
        ...getFetchInit(),
        body: JSON.stringify(data),
    };
    fetch(url, init)
        .then(handleDownloadPDF)
        // eslint-disable-next-line no-console
        .catch((error) => console.error(error));
};

// ////////////////
// Download PDFs //
// ////////////////

export const downloadApartmentUnconfirmedMaximumPricePDF = (
    apartment: IApartmentDetails,
    requestDate: string,
    additionalInfo?: string,
    calculationDate?: string
) => {
    const url = `${Config.api_v1_url}/housing-companies/${apartment.links.housing_company.id}/apartments/${apartment.id}/reports/download-latest-unconfirmed-prices`;

    const data = {additional_info: additionalInfo, request_date: requestDate, calculation_date: calculationDate};
    fetchAndDownloadPDF(url, data);
};

export const downloadApartmentMaximumPricePDF = (apartment: IApartmentDetails, requestDate?: string) => {
    if (!apartment.prices.maximum_prices.confirmed) {
        hdsToast.error("Enimmäishintalaskelmaa ei ole olemassa.");
        return;
    }
    const url = `${Config.api_v1_url}/housing-companies/${apartment.links.housing_company.id}/apartments/${apartment.id}/reports/download-latest-confirmed-prices`;
    const data = {request_date: requestDate};
    fetchAndDownloadPDF(url, data);
};

export const downloadRegulationResults = (calculationDate?: string) => {
    const params = `calculation_date=${calculationDate}`;
    const url = `${Config.api_v1_url}/thirty-year-regulation/reports/download-regulation-results?${params}`;
    const init = {
        ...getFetchInit(),
        method: "GET",
    };
    fetch(url, init)
        .then(handleDownloadPDF)
        // eslint-disable-next-line no-console
        .catch((error) => console.error(error));
};

export const downloadSurfaceAreaPriceCeilingResults = (calculationDate?: string) => {
    const params = `calculation_date=${calculationDate}`;
    const url = `${Config.api_v1_url}/indices/surface-area-price-ceiling/reports/download-surface-area-price-ceiling-results?${params}`;
    const init = {
        ...getFetchInit(),
        method: "GET",
    };
    fetch(url, init)
        .then(handleDownloadPDF)
        // eslint-disable-next-line no-console
        .catch((error) => console.error(error));
};

export const downloadSalesReportPDF = (startDate: string, endDate: string) => {
    const params = `start_date=${startDate}&end_date=${endDate}`;
    const url = `${Config.api_v1_url}/reports/download-sales-report?${params}`;
    const init = {
        ...getFetchInit(),
        method: "GET",
    };
    fetch(url, init)
        .then(handleDownloadPDF)
        // eslint-disable-next-line no-console
        .catch((error) => console.error(error));
};

export const downloadSalesByPostalCodeAndAreaReportPDF = (startDate: string, endDate: string) => {
    const params = `start_date=${startDate}&end_date=${endDate}`;
    const url = `${Config.api_v1_url}/reports/download-sales-by-postal-code-and-area-report?${params}`;
    const init = {
        ...getFetchInit(),
        method: "GET",
    };
    fetch(url, init)
        .then(handleDownloadPDF)
        // eslint-disable-next-line no-console
        .catch((error) => console.error(error));
};

const noParamsPDFDownload = (url: string) => {
    const init = {
        ...getFetchInit(),
        method: "GET",
    };
    fetch(url, init)
        .then(handleDownloadPDF)
        // eslint-disable-next-line no-console
        .catch((error) => console.error(error));
};

export const downloadRegulatedHousingCompaniesPDF = () =>
    noParamsPDFDownload(`${Config.api_v1_url}/reports/download-regulated-housing-companies-report`);

export const downloadUnregulatedHousingCompaniesPDF = () =>
    noParamsPDFDownload(`${Config.api_v1_url}/reports/download-unregulated-housing-companies-report`);

export const downloadHousingCompanyStatesReportPDF = () =>
    noParamsPDFDownload(`${Config.api_v1_url}/reports/download-housing-company-states-report`);

export const downloadMultipleOwnershipsReportPDF = () =>
    noParamsPDFDownload(`${Config.api_v1_url}/reports/download-multiple-ownerships-report`);

// ///////////
// Auth API //
// ///////////

export const authApi = createApi({
    reducerPath: "authApi",
    baseQuery: fetchBaseQuery({
        baseUrl: Config.api_auth_url,
        credentials: "include",
    }),
    endpoints: (builder) => ({
        getUserInfo: builder.query<IUserInfoResponse, null>({
            query: () => ({
                url: "userinfo/",
            }),
        }),
    }),
});

export const {useGetUserInfoQuery} = authApi;

// ////////////
// Hitas API //
// ////////////

export const hitasApi = createApi({
    reducerPath: "hitasApi",
    baseQuery: fetchBaseQuery({
        baseUrl: Config.api_v1_url,
        prepareHeaders: (headers) => {
            Config.token && headers.set("Authorization", "Bearer " + Config.token);
            return headers;
        },
        ...(!Config.token && {credentials: "include"}),
    }),
    tagTypes: [
        "HousingCompany",
        "ConditionOfSale",
        "Apartment",
        "Index",
        "Owner",
        "PropertyManager",
        "Developer",
        "ExternalSaleData",
        "ThirtyYearRegulation",
    ],
    endpoints: () => ({}),
});

// Mutations are used to allow invalidating cache when PDF is downloaded
const pdfApi = hitasApi.injectEndpoints({
    endpoints: (builder) => ({
        downloadThirtyYearRegulationLetter: builder.mutation<object, {id: string; calculationDate: string}>({
            query: ({id, calculationDate}) => {
                return {
                    url: `thirty-year-regulation/reports/download-regulation-letter?housing_company_id=${id}&calculation_date=${calculationDate}`,
                    method: "GET",
                    responseHandler: async (response) => {
                        await handleDownloadPDF(response);
                    },
                    cache: "no-cache",
                };
            },
            invalidatesTags: (result, error, arg) => [{type: "ThirtyYearRegulation", id: arg.calculationDate}],
        }),
    }),
});

const listApi = hitasApi.injectEndpoints({
    endpoints: (builder) => ({
        getHousingCompanies: builder.query<IHousingCompanyListResponse, object>({
            query: (params: object) => ({
                url: "housing-companies",
                params: params,
            }),
            providesTags: [{type: "HousingCompany", id: "LIST"}],
        }),
        getApartments: builder.query<IApartmentListResponse, object>({
            query: (params: object) => ({
                url: "apartments",
                params: params,
            }),
            providesTags: [{type: "Apartment", id: "LIST"}],
        }),
        getHousingCompanyApartments: builder.query<IApartmentListResponse, IHousingCompanyApartmentQuery>({
            query: (params: IHousingCompanyApartmentQuery) => ({
                url: `housing-companies/${params.housingCompanyId}/apartments`,
                params: params.params,
            }),
            providesTags: (result, error, arg) => [
                {type: "Apartment", id: "LIST"},
                {type: "HousingCompany", id: arg.housingCompanyId},
            ],
        }),
        getOwners: builder.query<IOwnersResponse, IFilterOwnersQuery>({
            query: (params) => ({
                url: "owners",
                params: params,
            }),
            providesTags: [{type: "Owner", id: "LIST"}],
        }),
        getPropertyManagers: builder.query<IPropertyManagersResponse, IFilterPropertyManagersQuery>({
            query: (params) => ({
                url: "property-managers",
                params: params,
            }),
            providesTags: [{type: "PropertyManager", id: "LIST"}],
        }),
        // Codes
        getPostalCodes: builder.query<IPostalCodeResponse, object>({
            query: (params: object) => ({
                url: "postal-codes",
                params: params,
            }),
        }),
        getIndices: builder.query<IIndexListResponse, IIndexListQuery>({
            query: (params: IIndexListQuery) => ({
                url: `indices/${params.indexType}`,
                params: params.params,
            }),
            providesTags: [{type: "Index", id: "LIST"}],
        }),
        getDevelopers: builder.query<ICodeResponse, IFilterDevelopersQuery>({
            query: (params) => ({
                url: "developers",
                params: params,
            }),
            providesTags: [{type: "Developer", id: "LIST"}],
        }),
        getBuildingTypes: builder.query<ICodeResponse, object>({
            query: (params: object) => ({
                url: "building-types",
                params: params,
            }),
        }),
        getApartmentTypes: builder.query<ICodeResponse, object>({
            query: (params: object) => ({
                url: "apartment-types",
                params: params,
            }),
        }),
        getAvailablePostalCodes: builder.query<IThirtyYearAvailablePostalCodesResponse, object>({
            query: (params: object) => ({
                url: "thirty-year-regulation/postal-codes",
                params: params,
            }),
        }),
        getHousingCompanyStates: builder.query({
            query: (arg) => ({
                url: "reports/housing-company-states",
                params: arg,
            }),
        }),
    }),
});

const detailApi = hitasApi.injectEndpoints({
    endpoints: (builder) => ({
        getHousingCompanyDetail: builder.query<IHousingCompanyDetails, string>({
            query: (id) => `housing-companies/${id}`,
            providesTags: (result, error, arg) => [
                {type: "HousingCompany", id: arg},
                {type: "PropertyManager", id: result?.property_manager?.id},
            ],
        }),
        getApartmentDetail: builder.query<IApartmentDetails, IApartmentQuery>({
            query: (params: IApartmentQuery) => ({
                url: `housing-companies/${params.housingCompanyId}/apartments/${params.apartmentId}`,
            }),
            providesTags: (result, error, arg) => [{type: "Apartment", id: arg.apartmentId}, {type: "Owner"}],
        }),
        getConditionOfSale: builder.query<IConditionOfSale, string>({
            query: (id) => ({
                url: `conditions-of-sale/${id}`,
            }),
            providesTags: (result, error, arg) => [{type: "ConditionOfSale", id: arg}],
        }),
        getApartmentMaximumPrice: builder.query<IApartmentMaximumPriceCalculationDetails, object>({
            query: ({
                housingCompanyId,
                apartmentId,
                priceId,
            }: {
                housingCompanyId: string;
                apartmentId: string;
                priceId: string;
            }) => ({
                url: `housing-companies/${housingCompanyId}/apartments/${apartmentId}/maximum-prices/${priceId}`,
            }),
        }),
        getApartmentUnconfirmedMaximumPriceForDate: builder.query<IApartmentUnconfirmedMaximumPriceIndices, object>({
            query: ({
                housingCompanyId,
                apartmentId,
                date,
            }: {
                housingCompanyId: string;
                apartmentId: string;
                date: string;
            }) => ({
                url: `housing-companies/${housingCompanyId}/apartments/${apartmentId}/retrieve-unconfirmed-prices-for-date`,
                params: {request_date: date},
            }),
        }),
        getExternalSalesData: builder.query<IExternalSalesDataResponse, {calculation_date: string}>({
            query: (params: {calculation_date: string}) => ({
                url: "external-sales-data",
                params: params,
            }),
            providesTags: (result, error, arg) => [{type: "ExternalSaleData", id: arg.calculation_date}],
        }),
        getThirtyYearRegulation: builder.query<IThirtyYearRegulationResponse, IThirtyYearRegulationQuery>({
            query: (params: IThirtyYearRegulationQuery) => ({
                url: "thirty-year-regulation",
                params: {
                    calculation_date: params.calculationDate,
                },
            }),
            providesTags: (result, error, arg) => [{type: "ThirtyYearRegulation", id: arg.calculationDate}],
        }),
        getIndex: builder.query<IIndexResponse, IIndexQuery>({
            query: (params: IIndexQuery) => ({
                url: `indices/${params.indexType}/${params.month}`,
            }),
        }),
        getPriceCeilingCalculationData: builder.query<{calculationMonth: string}, object>({
            query: (params: {calculationMonth: string}) => ({
                url: `indices/surface-area-price-ceiling-calculation-data/${params.calculationMonth}-01`,
            }),
        }),
    }),
});

const mutationApiJsonHeaders = () => {
    return new Headers({
        "Content-type": "application/json; charset=UTF-8",
        ...(getCookie("csrftoken") && {"X-CSRFToken": getCookie("csrftoken")}),
    });
};

const mutationApiExcelHeaders = () => {
    return new Headers({
        "Content-type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        ...(getCookie("csrftoken") && {"X-CSRFToken": getCookie("csrftoken")}),
    });
};

const mutationApi = hitasApi.injectEndpoints({
    endpoints: (builder) => ({
        saveHousingCompany: builder.mutation<IHousingCompanyDetails, {data: IHousingCompanyWritable; id?: string}>({
            query: ({data, id}) => ({
                url: `housing-companies${idOrBlank(id)}`,
                method: id === undefined ? "POST" : "PUT",
                body: data,
                headers: mutationApiJsonHeaders(),
            }),
            invalidatesTags: (result, error, arg) => [
                {type: "HousingCompany", id: "LIST"},
                {type: "HousingCompany", id: arg.id},
            ],
        }),
        releaseHousingCompanyFromRegulation: builder.mutation<
            IHousingCompanyDetails,
            {housingCompanyId: string; calculationDate: string}
        >({
            query: ({housingCompanyId}) => ({
                url: `housing-companies/${housingCompanyId}`,
                method: "PATCH",
                body: {regulation_status: "released_by_plot_department"},
                headers: mutationApiJsonHeaders(),
            }),
            invalidatesTags: (result, error, arg) => [
                {type: "HousingCompany", id: "LIST"},
                {type: "HousingCompany", id: arg.housingCompanyId},
                {type: "ThirtyYearRegulation", id: arg.calculationDate},
            ],
        }),
        createRealEstate: builder.mutation<IRealEstate, {data: IRealEstate; housingCompanyId: string}>({
            query: ({data, housingCompanyId}) => ({
                url: `housing-companies/${housingCompanyId}/real-estates`,
                method: "POST",
                body: data,
                headers: mutationApiJsonHeaders(),
            }),
            invalidatesTags: (result, error, arg) => [
                {
                    type: "HousingCompany",
                    id: arg.housingCompanyId,
                },
            ],
        }),
        deleteRealEstate: builder.mutation<IRealEstate, {id: string; housingCompanyId: string}>({
            query: ({id, housingCompanyId}) => ({
                url: `housing-companies/${housingCompanyId}/real-estates/${id}`,
                method: "DELETE",
                headers: mutationApiJsonHeaders(),
            }),
            invalidatesTags: (result, error, arg) => [{type: "HousingCompany", id: arg.housingCompanyId}],
        }),
        saveBuilding: builder.mutation<
            IBuilding,
            {data: IBuildingWritable; housingCompanyId: string; realEstateId: string}
        >({
            query: ({data, housingCompanyId, realEstateId}) => ({
                url: `housing-companies/${housingCompanyId}/real-estates/${realEstateId}/buildings${idOrBlank(
                    data.id
                )}`,
                method: data.id === undefined ? "POST" : "PUT",
                body: data,
                headers: mutationApiJsonHeaders(),
            }),
            invalidatesTags: (result, error, arg) => [{type: "HousingCompany", id: arg.housingCompanyId}],
        }),
        deleteBuilding: builder.mutation<IBuilding, {id: string; housingCompanyId: string; realEstateId: string}>({
            query: ({id, housingCompanyId, realEstateId}) => ({
                url: `housing-companies/${housingCompanyId}/real-estates/${realEstateId}/buildings/${id}`,
                method: "DELETE",
                headers: mutationApiJsonHeaders(),
            }),
            invalidatesTags: (result, error, arg) => [{type: "HousingCompany", id: arg.housingCompanyId}],
        }),
        saveApartment: builder.mutation<
            IApartmentDetails,
            {data: IApartmentWritable; id?: string; housingCompanyId: string}
        >({
            query: ({data, id, housingCompanyId}) => ({
                url: `housing-companies/${housingCompanyId}/apartments${idOrBlank(id)}`,
                method: id === undefined ? "POST" : "PUT",
                body: data,
                headers: mutationApiJsonHeaders(),
            }),
            invalidatesTags: (result, error, arg) => [
                {type: "Apartment", id: "LIST"},
                {type: "Apartment", id: arg.id},
                {type: "HousingCompany", id: arg.housingCompanyId},
            ],
        }),
        saveApartmentMaximumPrice: builder.mutation<
            IApartmentMaximumPriceCalculationDetails,
            {
                data: IApartmentMaximumPriceWritable | {confirm: true};
                id?: string;
                apartmentId: string;
                housingCompanyId: string;
            }
        >({
            query: ({data, id, apartmentId, housingCompanyId}) => ({
                url: `housing-companies/${housingCompanyId}/apartments/${apartmentId}/maximum-prices${idOrBlank(id)}`,
                method: id === undefined ? "POST" : "PUT",
                body: data,
                headers: mutationApiJsonHeaders(),
            }),
            invalidatesTags: (result, error, arg) => {
                // Invalidate Apartment Details only when confirming a maximum price
                if (result && result.confirmed_at) {
                    return [{type: "Apartment", id: arg.apartmentId}];
                }
                return [];
            },
        }),
        deleteApartment: builder.mutation<
            IApartmentDetails,
            {
                id: string | undefined;
                housingCompanyId: string;
            }
        >({
            query: ({id, housingCompanyId}) => ({
                url: `housing-companies/${housingCompanyId}/apartments/${id}`,
                method: "DELETE",
                headers: mutationApiJsonHeaders(),
            }),
            invalidatesTags: (result, error, arg) => [
                {type: "Apartment", id: "LIST"},
                {type: "Apartment", id: arg.id},
                {type: "HousingCompany", id: arg.housingCompanyId},
            ],
        }),
        saveOwner: builder.mutation<IOwner, {data: IOwner}>({
            query: ({data}) => ({
                url: `owners${idOrBlank(data.id)}`,
                method: data.id === undefined ? "POST" : "PUT",
                body: data,
                headers: mutationApiJsonHeaders(),
            }),
            invalidatesTags: () => [{type: "Owner"}],
        }),
        savePropertyManager: builder.mutation<IPropertyManager, IPropertyManager>({
            query: (data) => ({
                url: `property-managers${idOrBlank(data.id)}`,
                method: data.id === undefined ? "POST" : "PUT",
                body: data,
                headers: mutationApiJsonHeaders(),
            }),
            invalidatesTags: (response) => [
                {type: "PropertyManager", id: response?.id},
                {type: "PropertyManager", id: "LIST"},
            ],
        }),
        saveDeveloper: builder.mutation<IDeveloper, IDeveloper>({
            query: (data) => ({
                url: `developers${idOrBlank(data.id)}`,
                method: data.id === undefined ? "POST" : "PUT",
                body: data,
                headers: mutationApiJsonHeaders(),
            }),
            invalidatesTags: (response) => [
                {type: "Developer", id: response?.id},
                {type: "Developer", id: "LIST"},
            ],
        }),
        saveIndex: builder.mutation<IIndex, {data: IIndex; index: string; month: string}>({
            query: ({data, index, month}) => ({
                url: `indices/${index}/${month}`,
                method: "PUT",
                body: data,
                headers: mutationApiJsonHeaders(),
            }),
            invalidatesTags: () => [{type: "Apartment"}, {type: "Index", id: "LIST"}],
        }),
        createSale: builder.mutation<
            IApartmentSaleCreated,
            {
                data: IApartmentSale;
                housingCompanyId: string;
                apartmentId: string;
            }
        >({
            query: ({data, housingCompanyId, apartmentId}) => ({
                url: `housing-companies/${housingCompanyId}/apartments/${apartmentId}/sales`,
                method: "POST",
                body: data,
                headers: mutationApiJsonHeaders(),
            }),
            invalidatesTags: (result, error, arg) => [
                {type: "Apartment"},
                {type: "HousingCompany", id: arg.housingCompanyId},
            ],
        }),
        deleteSale: builder.mutation<unknown, {housingCompanyId: string; apartmentId: string; saleId: string}>({
            query: ({housingCompanyId, apartmentId, saleId}) => ({
                url: `housing-companies/${housingCompanyId}/apartments/${apartmentId}/sales/${saleId}`,
                method: "DELETE",
                headers: mutationApiJsonHeaders(),
            }),
            invalidatesTags: (result, error, arg) => [
                {type: "Apartment"},
                {type: "HousingCompany", id: arg.housingCompanyId},
            ],
        }),
        createConditionOfSale: builder.mutation<
            {conditions_of_sale: IConditionOfSale[]},
            {data: ICreateConditionOfSale}
        >({
            query: ({data}) => ({
                url: `conditions-of-sale`,
                method: "POST",
                body: data,
                headers: mutationApiJsonHeaders(),
            }),
            invalidatesTags: (result, error) =>
                !error && result && result.conditions_of_sale.length ? [{type: "Apartment"}] : [],
        }),
        updateConditionOfSale: builder.mutation<IConditionOfSale, IConditionOfSale>({
            query: (conditionOfSale) => ({
                url: `conditions-of-sale${idOrBlank(conditionOfSale.id)}`,
                method: "PUT",
                body: conditionOfSale,
                headers: mutationApiJsonHeaders(),
            }),
            invalidatesTags: (result, error, arg) =>
                !error && result ? [{type: "Apartment"}, {type: "ConditionOfSale", id: arg.id}] : [],
        }),
        deleteConditionOfSale: builder.mutation<object, {id: string}>({
            query: ({id}) => ({
                url: `conditions-of-sale/${id}`,
                method: "DELETE",
                headers: mutationApiJsonHeaders(),
            }),
            invalidatesTags: () => [{type: "Apartment"}],
        }),
        createThirtyYearRegulation: builder.mutation<IThirtyYearRegulationResponse, {data: IThirtyYearRegulationQuery}>(
            {
                query: ({data}) => ({
                    url: `thirty-year-regulation`,
                    method: "POST",
                    body: {
                        calculation_date: data.calculationDate,
                        replacement_postal_codes: data.replacementPostalCodes?.map((p) => {
                            return {postal_code: p.postalCode, replacements: p.replacements};
                        }),
                    },
                    headers: {"Content-type": "application/json; charset=UTF-8"},
                }),
                invalidatesTags: (result, error, arg) =>
                    !error && result ? [{type: "ThirtyYearRegulation", id: arg.data.calculationDate}] : [],
            }
        ),
        saveExternalSalesData: builder.mutation({
            query: (arg) => ({
                url: "external-sales-data",
                method: "POST",
                body: arg.data,
                params: {calculation_date: arg.calculation_date},
                headers: mutationApiExcelHeaders(),
            }),
            invalidatesTags: (result, error, arg) =>
                !error && result ? [{type: "ExternalSaleData", id: arg.calculation_date}] : [],
        }),
        validateSalesCatalog: builder.mutation({
            query: ({data, housingCompanyId}) => ({
                url: `housing-companies/${housingCompanyId}/sales-catalog-validate`,
                method: "POST",
                body: data,
                headers: mutationApiExcelHeaders(),
            }),
        }),
        createFromSalesCatalog: builder.mutation({
            query: ({data, housingCompanyId}) => ({
                url: `housing-companies/${housingCompanyId}/sales-catalog-create`,
                method: "POST",
                body: data,
                headers: mutationApiJsonHeaders(),
            }),
            invalidatesTags: (result, error, arg) =>
                !error ? [{type: "HousingCompany", id: arg.housingCompanyId}, {type: "Apartment"}] : [],
        }),
        batchCompleteApartments: builder.mutation({
            query: (arg) => ({
                url: `housing-companies/${arg.housing_company_id}/batch-complete-apartments`,
                method: "PATCH",
                headers: mutationApiJsonHeaders(),
                body: arg.data,
            }),
            invalidatesTags: (result, error) => (!error && result ? [{type: "Apartment"}] : []),
        }),
        calculatePriceCeiling: builder.mutation({
            query: ({data}) => ({
                url: "indices/surface-area-price-ceiling",
                method: "POST",
                headers: mutationApiJsonHeaders(),
                body: data,
            }),
            invalidatesTags: (result, error) => (!error && result ? [{type: "Index", id: "LIST"}] : []),
        }),
    }),
});

export const {useDownloadThirtyYearRegulationLetterMutation} = pdfApi;

export const {
    useGetHousingCompaniesQuery,
    useGetApartmentsQuery,
    useGetHousingCompanyApartmentsQuery,
    useGetOwnersQuery,
    useGetPropertyManagersQuery,
    useGetPostalCodesQuery,
    useGetIndicesQuery,
    useGetDevelopersQuery,
    useGetBuildingTypesQuery,
    useGetApartmentTypesQuery,
    useGetAvailablePostalCodesQuery,
    useGetHousingCompanyStatesQuery,
} = listApi;

export const {
    useGetHousingCompanyDetailQuery,
    useLazyGetConditionOfSaleQuery,
    useGetApartmentDetailQuery,
    useGetApartmentMaximumPriceQuery,
    useGetApartmentUnconfirmedMaximumPriceForDateQuery,
    useGetExternalSalesDataQuery,
    useGetThirtyYearRegulationQuery,
    useGetIndexQuery,
    useGetPriceCeilingCalculationDataQuery,
} = detailApi;

export const {
    useSaveHousingCompanyMutation,
    useReleaseHousingCompanyFromRegulationMutation,
    useCreateRealEstateMutation,
    useDeleteRealEstateMutation,
    useSaveBuildingMutation,
    useDeleteBuildingMutation,
    useSaveApartmentMutation,
    useDeleteApartmentMutation,
    useSaveOwnerMutation,
    useSavePropertyManagerMutation,
    useSaveDeveloperMutation,
    useSaveApartmentMaximumPriceMutation,
    useSaveIndexMutation,
    useCreateSaleMutation,
    useDeleteSaleMutation,
    useCreateConditionOfSaleMutation,
    useUpdateConditionOfSaleMutation,
    useDeleteConditionOfSaleMutation,
    useCreateThirtyYearRegulationMutation,
    useSaveExternalSalesDataMutation,
    useValidateSalesCatalogMutation,
    useCreateFromSalesCatalogMutation,
    useBatchCompleteApartmentsMutation,
    useCalculatePriceCeilingMutation,
} = mutationApi;
