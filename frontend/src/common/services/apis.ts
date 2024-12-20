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
            if ((api.extra as {isFormDataFileUpload?: boolean})?.isFormDataFileUpload) {
                // File uploads require content type `multipart/form-data`.
                // The header must be set by the browser so that it includes the correct boundary string.
                headers.delete("Content-type");
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
    // File uploads need to know they are file uploads so that the headers are set correctly by the browser.
    // One way to pass information to `prepareHeaders` is through `api.extra`. The payload is not available.
    // The official RTK documentation on how `api.extra` is supposed to be populated is lacking, at the time of writing.
    // According to this stackoverflow https://stackoverflow.com/a/77153535 the `api.extra` is supposed to be populated
    // by setting the `extraOptions` property in the query builder. In practice `api.extra` stays `undefined`.
    // Since we have access to both `api.extra` and `extraOptions` here, we can emulate that behavior by applying the `extraOptions`.
    api.extra = {...(api.extra ?? {}), ...extraOptions};

    const result = await baseQuery(args, api, extraOptions);

    // Handle CSRF errors by redirecting to login page
    if (result.error && result.error.status === 403) {
        const errorMessage = (result.error?.data as {detail: string})?.detail;
        if (errorMessage?.startsWith("CSRF Failed:")) {
            hdsToast.error("CSRF Virhe. Uudelleenohjataan kirjautumissivulle.");
            setTimeout(() => {
                // Open login in a new window/tab to avoid losing form data
                const callBackUrl = new URL("/window-close", window.location.origin).toString();
                window.open(getSignInUrl(callBackUrl), "_blank");
            }, 1000);
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
