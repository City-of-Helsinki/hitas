import {createApi, fetchBaseQuery} from "@reduxjs/toolkit/query/react";

import {
    IApartmentDetails,
    IApartmentListResponse,
    ICodeResponse,
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
}

export const hitasApi = createApi({
    reducerPath: "hitasApi",
    baseQuery: fetchBaseQuery({baseUrl: Config.api_url}),
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
        getApartmentDetail: builder.query<IApartmentDetails, string>({
            query: (id) => `apartments/${id}`,
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
        getFinancingMethods: builder.query<ICodeResponse, object>({
            query: (params: object) => ({
                url: "financing-methods",
                params: params,
            }),
        }),
    }),
});

export const {
    useGetHousingCompaniesQuery,
    useGetHousingCompanyDetailQuery,
    useCreateHousingCompanyMutation,
    useGetApartmentsQuery,
    useGetApartmentDetailQuery,
    useGetPostalCodesQuery,
    useGetPropertyManagersQuery,
    useGetDevelopersQuery,
    useGetBuildingTypesQuery,
    useGetFinancingMethodsQuery,
} = hitasApi;
