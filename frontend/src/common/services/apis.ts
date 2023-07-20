import {createApi, fetchBaseQuery} from "@reduxjs/toolkit/dist/query/react";

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

export const authApi = createApi({
    reducerPath: "authApi",
    baseQuery: fetchBaseQuery({
        baseUrl: Config.api_auth_url,
        credentials: "include",
    }),
    endpoints: () => ({}),
});

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
