import {createApi, fetchBaseQuery} from "@reduxjs/toolkit/query/react";

import {
    IApartmentDetails,
    IApartmentListResponse,
    IApartmentMaximumPrice,
    IApartmentMaximumPriceWritable,
    IApartmentQuery,
    IApartmentSale,
    IApartmentWritable,
    IBuilding,
    IBuildingWritable,
    ICodeResponse,
    IConditionOfSale,
    ICreateConditionOfSale,
    IHousingCompanyApartmentQuery,
    IHousingCompanyDetails,
    IHousingCompanyListResponse,
    IHousingCompanyWritable,
    IIndex,
    IIndexQuery,
    IIndexResponse,
    IOwner,
    IPostalCodeResponse,
    IRealEstate,
} from "../common/schemas";
import {hitasToast} from "../common/utils";

declare global {
    interface Window {
        __env: Record<string, string> | undefined;
    }
}

export class Config {
    static api_url =
        window.__env !== undefined
            ? window.__env.API_URL
            : process.env.REACT_APP_API_URL || "http://localhost:8000/api/v1";
    static token =
        window.__env !== undefined
            ? window.__env.AUTH_TOKEN
            : process.env.REACT_APP_AUTH_TOKEN || "52bf0606e0a0075c990fecc0afa555e5dae56404";
}

// Helper to return either the passed value prefixed with `/` or an empty string
const idOrBlank = (id: string | undefined) => (id ? `/${id}` : "");

const handleDownloadPDF = (response) => {
    response.blob().then((blob) => {
        const filename = response.headers.get("Content-Disposition")?.split("=")[1];
        if (filename === undefined) {
            hitasToast("Virhe tiedostoa ladattaessa.", "error");
            return;
        }

        const alink = document.createElement("a");
        alink.href = window.URL.createObjectURL(blob);
        alink.download = `${filename}`;
        alink.click();
    });
};

const getFetchInit = () => {
    return {
        headers: new Headers({Authorization: "Bearer " + Config.token, "Content-Type": "application/json"}),
        method: "POST",
    };
};
export const downloadApartmentUnconfirmedMaximumPricePDF = (apartment: IApartmentDetails, additionalInfo?: string) => {
    const url = `${Config.api_url}/housing-companies/${apartment.links.housing_company.id}/apartments/${apartment.id}/reports/download-latest-unconfirmed-prices`;
    const init = {
        ...getFetchInit(),
        body: JSON.stringify({additional_info: additionalInfo}),
    };
    fetch(url, init).then(handleDownloadPDF);
};

export const downloadApartmentMaximumPricePDF = (apartment: IApartmentDetails) => {
    if (!apartment.prices.maximum_prices.confirmed) {
        hitasToast("Enimmäishintalaskelmaa ei ole olemassa", "error");
        return;
    }
    const url = `${Config.api_url}/housing-companies/${apartment.links.housing_company.id}/apartments/${apartment.id}/reports/download-latest-confirmed-prices`;
    fetch(url, getFetchInit()).then(handleDownloadPDF);
};

export const hitasApi = createApi({
    reducerPath: "hitasApi",
    baseQuery: fetchBaseQuery({
        baseUrl: Config.api_url,
        prepareHeaders: (headers) => {
            headers.set("Authorization", "Bearer " + Config.token);
            return headers;
        },
    }),
    tagTypes: ["HousingCompany", "Apartment", "Index", "Owner"],
    endpoints: (builder) => ({}),
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
            providesTags: [{type: "Apartment", id: "LIST"}],
        }),
        getOwners: builder.query<ICodeResponse, object>({
            query: (params: object) => ({
                url: "owners",
                params: params,
            }),
        }),
        getPropertyManagers: builder.query<IApartmentListResponse, object>({
            query: (params: object) => ({
                url: "property-managers",
                params: params,
            }),
        }),
        // Codes
        getPostalCodes: builder.query<IPostalCodeResponse, object>({
            query: (params: object) => ({
                url: "postal-codes",
                params: params,
            }),
        }),
        getIndices: builder.query<IIndexResponse, IIndexQuery>({
            query: (params: IIndexQuery) => ({
                url: `indices/${params.indexType}`,
                params: params.params,
            }),
            providesTags: [{type: "Index", id: "LIST"}],
        }),
        getDevelopers: builder.query<ICodeResponse, object>({
            query: (params: object) => ({
                url: "developers",
                params: params,
            }),
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
        getFinancingMethods: builder.query<ICodeResponse, object>({
            query: (params: object) => ({
                url: "financing-methods",
                params: params,
            }),
        }),
        getApartmentMaximumPrice: builder.query({
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
    }),
});

const detailApi = hitasApi.injectEndpoints({
    endpoints: (builder) => ({
        getHousingCompanyDetail: builder.query<IHousingCompanyDetails, string>({
            query: (id) => `housing-companies/${id}`,
            providesTags: (result, error, arg) => [{type: "HousingCompany", id: arg}],
        }),
        getApartmentDetail: builder.query<IApartmentDetails, IApartmentQuery>({
            query: (params: IApartmentQuery) => ({
                url: `housing-companies/${params.housingCompanyId}/apartments/${params.apartmentId}`,
            }),
            providesTags: (result, error, arg) => [{type: "Apartment", id: arg.apartmentId}],
        }),
    }),
});

const mutationApi = hitasApi.injectEndpoints({
    endpoints: (builder) => ({
        saveHousingCompany: builder.mutation<IHousingCompanyDetails, {data: IHousingCompanyWritable; id?: string}>({
            query: ({data, id}) => ({
                url: `housing-companies${idOrBlank(id)}`,
                method: id === undefined ? "POST" : "PUT",
                body: data,
                headers: {"Content-type": "application/json; charset=UTF-8"},
            }),
            invalidatesTags: (result, error, arg) => [
                {type: "HousingCompany", id: "LIST"},
                {type: "HousingCompany", id: arg.id},
            ],
        }),
        createRealEstate: builder.mutation<IRealEstate, {data: IRealEstate; housingCompanyId: string}>({
            query: ({data, housingCompanyId}) => ({
                url: `housing-companies/${housingCompanyId}/real-estates`,
                method: "POST",
                body: data,
                headers: {"Content-type": "application/json; charset=UTF-8"},
            }),
            invalidatesTags: (result, error, arg) => [
                {
                    type: "HousingCompany",
                    id: arg.housingCompanyId,
                },
            ],
        }),
        removeRealEstate: builder.mutation<IRealEstate, {id: string; housingCompanyId: string}>({
            query: ({id, housingCompanyId}) => ({
                url: `housing-companies/${housingCompanyId}/real-estates/${id}`,
                method: "DELETE",
                headers: {"Content-type": "application/json; charset=UTF-8"},
            }),
            invalidatesTags: (result, error, arg) => [{type: "HousingCompany", id: arg.housingCompanyId}],
        }),
        createBuilding: builder.mutation<
            IBuilding,
            {data: IBuildingWritable; housingCompanyId: string; realEstateId: string}
        >({
            query: ({data, housingCompanyId, realEstateId}) => ({
                url: `housing-companies/${housingCompanyId}/real-estates/${realEstateId}/buildings`,
                method: "POST",
                body: data,
                headers: {"Content-type": "application/json; charset=UTF-8"},
            }),
            invalidatesTags: (result, error, arg) => [{type: "HousingCompany", id: arg.housingCompanyId}],
        }),
        removeBuilding: builder.mutation<IBuilding, {id: string; housingCompanyId: string; realEstateId: string}>({
            query: ({id, housingCompanyId, realEstateId}) => ({
                url: `housing-companies/${housingCompanyId}/real-estates/${realEstateId}/buildings/${id}`,
                method: "DELETE",
                headers: {"Content-type": "application/json; charset=UTF-8"},
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
                headers: {"Content-type": "application/json; charset=UTF-8"},
            }),
            invalidatesTags: (result, error, arg) => [
                {type: "Apartment", id: "LIST"},
                {type: "Apartment", id: arg.id},
                {type: "HousingCompany", id: arg.housingCompanyId},
            ],
        }),
        saveApartmentMaximumPrice: builder.mutation<
            IApartmentMaximumPrice,
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
                headers: {"Content-type": "application/json; charset=UTF-8"},
            }),
            invalidatesTags: (result, error, arg) => {
                // Invalidate Apartment Details only when confirming a maximum price
                if (result && result.confirmed_at) {
                    return [{type: "Apartment", id: arg.apartmentId}];
                }
                return [];
            },
        }),
        removeApartment: builder.mutation<
            IApartmentDetails,
            {
                id: string | undefined;
                housingCompanyId: string;
            }
        >({
            query: ({id, housingCompanyId}) => ({
                url: `housing-companies/${housingCompanyId}/apartments/${id}`,
                method: "DELETE",
                headers: {"Content-type": "application/json; charset=UTF-8"},
            }),
            invalidatesTags: (result, error, arg) => [
                {type: "Apartment", id: "LIST"},
                {type: "Apartment", id: arg.id},
                {type: "HousingCompany", id: arg.housingCompanyId},
            ],
        }),
        createOwner: builder.mutation<IOwner, {data: IOwner}>({
            query: ({data}) => ({
                url: `owners`,
                method: "POST",
                body: data,
                headers: {"Content-type": "application/json; charset=UTF-8"},
            }),
            invalidatesTags: () => [{type: "Owner"}],
        }),
        saveIndex: builder.mutation<IIndex, {data: IIndex; index: string; month: string}>({
            query: ({data, index, month}) => ({
                url: `indices/${index}/${month}`,
                method: "PUT",
                body: data,
                headers: {"Content-type": "application/json; charset=UTF-8"},
            }),
            invalidatesTags: (result, error, arg) => [{type: "Apartment"}, {type: "Index", id: "LIST"}],
        }),
        createSale: builder.mutation<
            IApartmentSale,
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
                headers: {"Content-type": "application/json; charset=UTF-8"},
            }),
            invalidatesTags: (result, error, arg) => [
                {type: "Apartment", id: "LIST"},
                {type: "Apartment", id: arg.apartmentId},
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
                headers: {"Content-type": "application/json; charset=UTF-8"},
            }),
            invalidatesTags: (result, error) =>
                !error && result && result.conditions_of_sale.length ? [{type: "Apartment"}] : [],
        }),
    }),
});

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
    useGetFinancingMethodsQuery,
    useGetApartmentMaximumPriceQuery,
} = listApi;

export const {useGetHousingCompanyDetailQuery, useGetApartmentDetailQuery} = detailApi;

export const {
    useSaveHousingCompanyMutation,
    useCreateRealEstateMutation,
    useRemoveRealEstateMutation,
    useCreateBuildingMutation,
    useRemoveBuildingMutation,
    useSaveApartmentMutation,
    useRemoveApartmentMutation,
    useCreateOwnerMutation,
    useSaveApartmentMaximumPriceMutation,
    useSaveIndexMutation,
    useCreateSaleMutation,
    useCreateConditionOfSaleMutation,
} = mutationApi;
