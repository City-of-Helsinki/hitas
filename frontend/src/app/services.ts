import {createApi, fetchBaseQuery} from "@reduxjs/toolkit/query/react";

import {IApartment, IHousingCompany, IHousingCompanyDetails, PageInfo} from "../common/models";

interface IHousingCompaniesListResponse {
    page: PageInfo;
    contents: IHousingCompany[];
}

interface IApartmentsListResponse {
    page: PageInfo;
    contents: IApartment[];
}

export const hitasApi = createApi({
    reducerPath: "hitasApi",
    baseQuery: fetchBaseQuery({baseUrl: "http://localhost:8000/api/v1/"}),
    endpoints: (builder) => ({
        // HousingCompany
        getHousingCompanies: builder.query<IHousingCompaniesListResponse, string>({query: () => "housing-companies"}),
        getHousingCompanyDetail: builder.query<IHousingCompanyDetails, string>({
            query: (id) => `housing-companies/${id}`,
        }),
        // Apartments
        getApartments: builder.query<IApartmentsListResponse, string>({query: () => "apartments"}),
    }),
});

export const {
    useGetHousingCompaniesQuery,
    useGetHousingCompanyDetailQuery,
    useGetApartmentsQuery,
} = hitasApi;
