import {createApi, fetchBaseQuery} from "@reduxjs/toolkit/query/react";

import {
    IApartmentDetails,
    IApartmentListResponse,
    IApartmentQuery,
    IApartmentWritable,
    ICodeResponse,
    IHousingCompanyApartmentQuery,
    IHousingCompanyDetails,
    IHousingCompanyListResponse,
    IHousingCompanyWritable,
    IPostalCodeResponse,
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

export const hitasApi = createApi({
    reducerPath: "hitasApi",
    baseQuery: fetchBaseQuery({
        baseUrl: Config.api_url,
        prepareHeaders: (headers) => {
            headers.set("Authorization", "Bearer " + Config.token)
            return headers;
        },
    }),
    endpoints: (builder) => ({
        // HousingCompany
        getHousingCompanies: builder.query<IHousingCompanyListResponse, object>({
            query: (params: object) => ({
                url: "housing-companies",
                params: params,
            }),
        }),
        getHousingCompanyDetail: builder.query<IHousingCompanyDetails, string>({
            query: (id) => `housing-companies/${id}`,
        }),
        createHousingCompany: builder.mutation<IHousingCompanyDetails, IHousingCompanyWritable>({
            query: (data) => ({
                url: "housing-companies",
                method: "POST",
                body: data,
                headers: {
                    "Content-type": "application/json; charset=UTF-8",
                },
            }),
        }),
        // Postal codes
        getPostalCodes: builder.query<IPostalCodeResponse, object>({
            query: (params: object) => ({
                url: "postal-codes",
                params: params,
            }),
        }),

        // Apartments
        getApartments: builder.query<IApartmentListResponse, object>({
            query: (params: object) => ({
                url: "apartments",
                params: params,
            }),
        }),
        getHousingCompanyApartments: builder.query<IApartmentListResponse, IHousingCompanyApartmentQuery>({
            query: (params: IHousingCompanyApartmentQuery) => ({
                url: `housing-companies/${params.housingCompanyId}/apartments`,
                params: params.params,
            }),
        }),
        getApartmentDetail: builder.query<IApartmentDetails, IApartmentQuery>({
            query: (params: IApartmentQuery) => ({
                url: `housing-companies/${params.housingCompanyId}/apartments/${params.apartmentId}`,
                params: params,
            }),
        }),
        createApartment: builder.mutation<IApartmentDetails, IApartmentWritable>({
            query: (data) => ({
                url: "apartments",
                method: "POST",
                body: data,
                headers: {
                    "Content-type": "application/json; charset=UTF-8",
                },
            }),
        }),
        // Property Manager
        getPropertyManagers: builder.query<IApartmentListResponse, object>({
            query: (params: object) => ({
                url: "property-managers",
                params: params,
            }),
        }),
        // Codes
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
        getPersons: builder.query<ICodeResponse, object>({
            query: (params: object) => ({
                url: "persons",
                params: params,
            }),
        }),
    }),
});

export const {
    useGetHousingCompaniesQuery,
    useGetHousingCompanyDetailQuery,
    useCreateHousingCompanyMutation,
    useGetHousingCompanyApartmentsQuery,
    useGetPostalCodesQuery,
    useGetApartmentsQuery,
    useGetApartmentDetailQuery,
    useCreateApartmentMutation,
    useGetPropertyManagersQuery,
    useGetDevelopersQuery,
    useGetBuildingTypesQuery,
    useGetApartmentTypesQuery,
    useGetFinancingMethodsQuery,
    useGetPersonsQuery,
} = hitasApi;
