import {createApi, fetchBaseQuery} from "@reduxjs/toolkit/query/react";

import {
    IApartmentDetails,
    IApartmentListResponse,
    IApartmentQuery,
    IApartmentWritable,
    IBuilding,
    IBuildingWritable,
    ICodeResponse,
    IHousingCompanyApartmentQuery,
    IHousingCompanyDetails,
    IHousingCompanyListResponse,
    IHousingCompanyWritable,
    IIndexResponse,
    IPostalCodeResponse,
    IRealEstate,
} from "../common/models";

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

export const hitasApi = createApi({
    reducerPath: "hitasApi",
    baseQuery: fetchBaseQuery({
        baseUrl: Config.api_url,
        prepareHeaders: (headers) => {
            headers.set("Authorization", "Bearer " + Config.token);
            return headers;
        },
    }),
    tagTypes: ["HousingCompany", "Apartment"],
    endpoints: (builder) => ({}),
});

export const listApi = hitasApi.injectEndpoints({
    endpoints: (builder) => ({
        getHousingCompanies: builder.query<IHousingCompanyListResponse, object>({
            query: (params: object) => ({
                url: "housing-companies",
                params: params,
            }),
            providesTags: [
                {
                    type: "HousingCompany",
                    id: "LIST",
                },
            ],
        }),
        getApartments: builder.query<IApartmentListResponse, object>({
            query: (params: object) => ({
                url: "apartments",
                params: params,
            }),
            providesTags: [
                {
                    type: "Apartment",
                    id: "LIST",
                },
            ],
        }),
        getHousingCompanyApartments: builder.query<IApartmentListResponse, IHousingCompanyApartmentQuery>({
            query: (params: IHousingCompanyApartmentQuery) => ({
                url: `housing-companies/${params.housingCompanyId}/apartments`,
                params: params.params,
            }),
            providesTags: [
                {
                    type: "Apartment",
                    id: "LIST",
                },
            ],
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
        getIndices: builder.query<IIndexResponse, {indexType: string}>({
            query: ({indexType}) => ({
                url: `indices/${indexType}`,
            }),
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
    }),
});

export const detailApi = hitasApi.injectEndpoints({
    endpoints: (builder) => ({
        getHousingCompanyDetail: builder.query<IHousingCompanyDetails, string>({
            query: (id) => `housing-companies/${id}`,
            providesTags: (result, error, arg) => [
                {
                    type: "HousingCompany",
                    id: arg,
                },
            ],
        }),
        getApartmentDetail: builder.query<IApartmentDetails, IApartmentQuery>({
            query: (params: IApartmentQuery) => ({
                url: `housing-companies/${params.housingCompanyId}/apartments/${params.apartmentId}`,
                params: params,
            }),
            providesTags: (result, error, arg) => [
                {
                    type: "Apartment",
                    id: arg.apartmentId,
                },
            ],
        }),
    }),
});

export const mutationApi = hitasApi.injectEndpoints({
    endpoints: (builder) => ({
        saveHousingCompany: builder.mutation<IHousingCompanyDetails, {data: IHousingCompanyWritable; id?: string}>({
            query: ({data, id}) => ({
                url: `housing-companies${idOrBlank(id)}`,
                method: id === undefined ? "POST" : "PUT",
                body: data,
                headers: {"Content-type": "application/json; charset=UTF-8"},
            }),
            invalidatesTags: (result, error, arg) => [
                {
                    type: "HousingCompany",
                    id: "LIST",
                },
                {
                    type: "HousingCompany",
                    id: arg.id,
                },
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
            invalidatesTags: (result, error, arg) => [
                {
                    type: "HousingCompany",
                    id: arg.housingCompanyId,
                },
            ],
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
                {
                    type: "Apartment",
                    id: "LIST",
                },
                {
                    type: "HousingCompany",
                    id: arg.housingCompanyId,
                },
            ],
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
} = listApi;

export const {useGetHousingCompanyDetailQuery, useGetApartmentDetailQuery} = detailApi;

export const {
    useSaveHousingCompanyMutation,
    useCreateRealEstateMutation,
    useCreateBuildingMutation,
    useSaveApartmentMutation,
} = mutationApi;
