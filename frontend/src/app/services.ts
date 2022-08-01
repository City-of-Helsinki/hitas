import {createApi, fetchBaseQuery} from "@reduxjs/toolkit/query/react";

import {IHousingCompany, IHousingCompanyDetails, PageInfo} from "../common/models";

interface IHousingCompaniesListResponse {
    page: PageInfo;
    contents: IHousingCompany[];
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
    }),
});

export const {useGetHousingCompaniesQuery, useGetHousingCompanyDetailQuery} = hitasApi;
