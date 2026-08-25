// Helper to return either the passed value prefixed with `/` or an empty string
import {getCookie} from "typescript-cookie";
import {hdsToast} from "../utils";
import {Config, refreshCsrfCookie} from "./apis";

export const idOrBlank = (id: string | undefined) => (id ? `/${id}` : "");

export const mutationApiExcelHeaders = () => {
    return new Headers({"Content-type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"});
};

// PDF Helpers
export const handleDownloadPDF = (response) => {
    response
        .blob()
        .then((blob) => {
            const filename = response.headers.get("Content-Disposition")?.split("=")[1];
            if (filename === undefined) {
                hdsToast.error("Virhe ladattaessa tiedostoa.");
                return;
            }

            const alink = document.createElement("a");
            alink.href = window.URL.createObjectURL(blob);
            alink.download = `${filename}`;
            alink.click();
        })
        .catch((error) => {
            // eslint-disable-next-line no-console
            console.error(error);
        });
};

const isCsrfResponse = async (response: Response): Promise<boolean> => {
    if (response.status !== 403) {
        return false;
    }

    const body = await response.clone().text();
    return body.includes("CSRF Failed:") || body.includes("CSRF verification failed");
};

const createPDFRequestInit = (method: "GET" | "POST", data?: object): RequestInit => {
    const csrfToken = getCookie("csrftoken");

    return {
        method: method,
        headers: new Headers({
            "Content-Type": "application/json",
            ...(csrfToken && {"X-CSRFToken": csrfToken}),
            ...(Config.token && {Authorization: "Bearer " + Config.token}),
        }),
        ...(!Config.token && {credentials: "include" as RequestCredentials}),
        ...(data && {body: JSON.stringify(data)}),
    };
};

export const fetchAndDownloadPDF = async (url: string, method: "GET" | "POST" = "GET", data?: object) => {
    const requestUrl = Config.api_v1_url + url;
    const request = () => fetch(requestUrl, createPDFRequestInit(method, data));

    try {
        let response = await request();

        if ((await isCsrfResponse(response)) && (await refreshCsrfCookie())) {
            // Build the request again so the retry reads the refreshed csrftoken cookie.
            response = await request();
        }

        if (response.ok) {
            handleDownloadPDF(response);
        } else {
            // eslint-disable-next-line no-console
            console.error(response);
            hdsToast.error(`Virhe ladattaessa tiedostoa. (${response.status} ${response.statusText})`);
        }
    } catch (error) {
        // eslint-disable-next-line no-console
        console.error(error);
        hdsToast.error(`Virhe ladattaessa tiedostoa. (${error instanceof Error ? error.message : error})`);
    }
};

export const safeInvalidate = (error, tags) => (!error ? tags : []);
