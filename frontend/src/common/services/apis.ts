import {BaseQueryFn, createApi, FetchArgs, fetchBaseQuery} from "@reduxjs/toolkit/dist/query/react";
import {FetchBaseQueryError} from "@reduxjs/toolkit/query";
import {getCookie} from "typescript-cookie";
import {getSignInUrl, hdsToast} from "../utils";

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

const baseQuery = fetchBaseQuery({
    baseUrl: Config.api_v1_url,
    prepareHeaders: (headers, api) => {
        Config.token && headers.set("Authorization", "Bearer " + Config.token);
        if (api.type === "mutation") {
            if (!headers.has("Content-Type")) {
                headers.set("Content-type", "application/json; charset=UTF-8");
            }
            const csrfToken = getCookie("csrftoken");
            csrfToken && headers.set("X-CSRFToken", csrfToken);
        }

        return headers;
    },
    ...(!Config.token && {credentials: "include"}),
});

const baseQueryWithReAuth: BaseQueryFn<string | FetchArgs, unknown, FetchBaseQueryError> = async (
    args,
    api,
    extraOptions
) => {
    const result = await baseQuery(args, api, extraOptions);

    // Handle CSRF errors by redirecting to login page
    if (result.error && result.error.status === 403) {
        const errorMessage = (result.error?.data as {detail: string})?.detail;
        if (errorMessage?.startsWith("CSRF Failed:")) {
            hdsToast.error("CSRF Virhe. Uudelleenohjataan kirjautumissivulle.");
            window.location.href = getSignInUrl(window.location.href);
        }
    }
    return result;
};

export const hitasApi = createApi({
    reducerPath: "hitasApi",
    baseQuery: baseQueryWithReAuth,
    tagTypes: [
        "HousingCompany",
        "ConditionOfSale",
        "Apartment",
        "Index",
        "Owner",
        "ObfuscatedOwner",
        "ObfuscatedOwners",
        "PropertyManager",
        "Developer",
        "ExternalSaleData",
        "ThirtyYearRegulation",
        "SurfaceAreaPriceCeilingCalculation",
    ],
    endpoints: () => ({}),
});
