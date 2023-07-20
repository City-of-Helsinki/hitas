// Helper to return either the passed value prefixed with `/` or an empty string
import {getCookie} from "typescript-cookie";
import {hdsToast} from "../utils";
import {Config} from "./apis";

export const idOrBlank = (id: string | undefined) => (id ? `/${id}` : "");

export const mutationApiJsonHeaders = () => {
    return new Headers({
        "Content-type": "application/json; charset=UTF-8",
        ...(getCookie("csrftoken") && {"X-CSRFToken": getCookie("csrftoken")}),
    });
};

export const mutationApiExcelHeaders = () => {
    return new Headers({
        "Content-type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        ...(getCookie("csrftoken") && {"X-CSRFToken": getCookie("csrftoken")}),
    });
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
export const fetchAndDownloadPDF = (url: string, method: "GET" | "POST" = "GET", data?: object) => {
    const init = {
        method: method,
        headers: new Headers({
            "Content-Type": "application/json",
            ...(getCookie("csrftoken") && {"X-CSRFToken": getCookie("csrftoken")}),
            ...(Config.token && {Authorization: "Bearer " + Config.token}),
        }),
        ...(!Config.token && {credentials: "include" as RequestCredentials}),
        ...(data && {body: JSON.stringify(data)}),
    };

    url = Config.api_v1_url + url;
    fetch(url, init)
        .then(handleDownloadPDF)
        // eslint-disable-next-line no-console
        .catch((error) => console.error(error));
};
