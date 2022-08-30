import {createApi, fetchBaseQuery} from "@reduxjs/toolkit/query/react";

import {
    IApartmentDetails,
    IApartmentListResponse,
    IApartmentQuery,
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
    useGetHousingCompanyApartmentsQuery,
    useGetPostalCodesQuery,
    useGetApartmentsQuery,
    useGetApartmentDetailQuery,
    useGetPropertyManagersQuery,
    useGetDevelopersQuery,
    useGetBuildingTypesQuery,
    useGetFinancingMethodsQuery,
} = hitasApi;
