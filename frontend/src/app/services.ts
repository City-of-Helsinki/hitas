import {createApi, fetchBaseQuery} from "@reduxjs/toolkit/query/react";

import {
    IApartmentDetails,
    IApartmentListResponse,
    IHousingCompanyDetails,
    IHousingCompanyListResponse,
} from "../common/models";

export const hitasApi = createApi({
    reducerPath: "hitasApi",
    baseQuery: fetchBaseQuery({baseUrl: "http://localhost:8000/api/v1/"}),
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
        getDevelopers: builder.query<IApartmentListResponse, object>({
            query: (params: object) => ({
                url: "developers",
                params: params,
            }),
        }),
    }),
});

export const {
    useGetHousingCompaniesQuery,
    useGetHousingCompanyDetailQuery,
    useGetApartmentsQuery,
    useGetApartmentDetailQuery,
    useGetPropertyManagersQuery,
    useGetDevelopersQuery,
} = hitasApi;
