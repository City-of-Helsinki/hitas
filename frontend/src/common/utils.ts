import toast, {ToastOptions} from "react-hot-toast";

import React from "react";
import {
    hitasQuarters,
    IAddress,
    IApartmentAddress,
    IApartmentDetails,
    IApartmentUnconfirmedMaximumPriceIndices,
    IOwner,
} from "./schemas";
import {Config} from "./services";

export function dotted(obj: object, path: string | string[], value?: number | string | null | object): unknown {
    /*
     Dotted getter and setter
     refs. https://stackoverflow.com/a/6394168/12730861

     Demo:
     obj = {a: {b: {etc: 5}}};
     > dotted(obj, "a.b.etc"); // Getter with a dotted string
     5
     > dotted(obj, ["a", "b", "etc"]); // Getter with an array
     5
     > dotted(obj, "a.b.etc", 123); // Setter
     123
     */
    if (typeof path == "string") return dotted(obj, path.split("."), value);
    else if (path.length === 1 && value !== undefined) return (obj[path[0]] = value);
    else if (path.length === 0) return obj;
    else if (path.length && (obj === null || obj === undefined))
        return null; // Don't crash hard when there is path left and obj is null
    else return dotted(obj[path[0]], path.slice(1), value);
}

export function formatAddress(address: IAddress | IApartmentAddress): string {
    if ("apartment_number" in address) {
        return `${address.street_address} ${address.stair} ${address.apartment_number}, ${address.postal_code}, ${address.city}`;
    }
    return `${address.street_address}, ${address.postal_code}, ${address.city}`;
}

export function formatApartmentAddressShort(address: IApartmentAddress): string {
    return `${address.street_address} ${address.stair} ${address.apartment_number}`;
}

export function formatOwner(owner: IOwner): string {
    if (owner.name === "" && owner.non_disclosure === true) return "TURVAKIELTO";

    return `${owner.name}${owner.identifier ? ` (${owner.identifier})` : ""}`;
}

export function formatMoney(value: number | undefined | null, forceDecimals = false): string {
    if (!value) return "-";

    const formatOptions = {
        style: "currency",
        currency: "EUR",
        minimumFractionDigits: value === 0 ? 0 : 2,
        maximumFractionDigits: value === 0 ? 0 : 2,
        trailingZeroDisplay: forceDecimals ? "auto" : "stripIfInteger", // Strip decimals if they are all zero
    };
    return new Intl.NumberFormat("fi-FI", formatOptions).format(value);
}

export function formatDate(value: string | null): string {
    if (value === null) return "-";

    return new Date(value).toLocaleDateString("fi-FI");
}

export function validateBusinessId(value: string): boolean {
    // This does not validate the check digit (last number), only the format
    // e.g. '1234567-8'
    // Returns true if the format is valid
    return !!value.match(/^(\d{7})-(\d)$/);
}

export function validatePropertyId(value: string): boolean {
    // e.g. '1-1234-321-56'
    // Returns true if the format is valid
    return !!value.match(/^\d{1,4}-\d{1,4}-\d{1,4}-\d{1,4}$/);
}

export function validateSocialSecurityNumber(value: string): boolean {
    if (value === null) return false;
    if (!value.match(/^(\d{6})([A-FYXWVU+-])(\d{3})([\dA-Z])$/)) {
        return false;
    }
    // Validate date
    const centuryChar = value.split("")[6];
    if (centuryChar === undefined) return false;
    let century;
    switch (centuryChar) {
        case "A":
        case "B":
        case "C":
        case "D":
        case "E":
        case "F":
            century = "20";
            break;
        case "-":
        case "Y":
        case "X":
        case "W":
        case "V":
        case "U":
            century = "19";
            break;
        case "+":
            century = "18";
            break;
    }
    const dateValue = value.substring(0, 4);
    const yearString = century + value.substring(4, 6);
    const dateString = `${yearString}-${dateValue.substring(2, 4)}-${dateValue.substring(0, 2)}`;
    if (isNaN(Date.parse(dateString))) return false;
    // validate individual number
    const idNumber = value.substring(7, 10);
    if (Number(idNumber) < 2 || Number(idNumber) > 899) return false;
    // validate checkDigit
    const checkDigit = value.substring(10, 11);
    const checkDigits = [
        "0",
        "1",
        "2",
        "3",
        "4",
        "5",
        "6",
        "7",
        "8",
        "9",
        "A",
        "B",
        "C",
        "D",
        "E",
        "F",
        "H",
        "J",
        "K",
        "L",
        "M",
        "N",
        "P",
        "R",
        "S",
        "T",
        "U",
        "V",
        "W",
        "X",
        "Y",
    ];
    return checkDigits[Number(value.substring(0, 6) + idNumber) % 31] === checkDigit;
}

export const today = () => new Date().toISOString().split("T")[0]; // Today's date in YYYY-MM-DD format

// Toast hook with easier Notification typing
export const hdsToast = {
    success: (message: string | React.JSX.Element, opts?: ToastOptions) =>
        toast(message, {...opts, className: "success"}),
    info: (message: string | React.JSX.Element, opts?: ToastOptions) => toast(message, {...opts, className: "info"}),
    error: (message: string | React.JSX.Element, opts?: ToastOptions) => toast(message, {...opts, className: "error"}),
    alert: (message: string | React.JSX.Element, opts?: ToastOptions) => toast(message, {...opts, className: "alert"}),
};

// Returns true if obj is empty, false otherwise. Returns true if obj is undefined or null.
export function isEmpty(obj: object | undefined | null): boolean {
    if (obj === undefined || obj === null) return true;
    return Object.keys(obj).length === 0;
}

// Returns href url for sign in dialog when given redirect url as parameter
export const getSignInUrl = (callBackUrl: string): string => {
    const baseUrl = new URL(callBackUrl).origin;

    if (callBackUrl === baseUrl + `/logout`) {
        return Config.api_auth_url + "/login?next=" + baseUrl;
    }
    return Config.api_auth_url + "/login?next=" + callBackUrl;
};

// Returns href url for logging out with redirect url to /logout
export const getLogOutUrl = (): string => {
    const baseUrl = new URL(window.location.href).origin;
    const callBackUrl = baseUrl + `/logout`;
    return Config.api_auth_url + "/logout?next=" + callBackUrl;
};

// Returns apartment's maximum unconfirmed prices, whether they are pre-2011 or onwards-2011
export const getApartmentUnconfirmedPrices = (
    apartment: IApartmentDetails
): IApartmentUnconfirmedMaximumPriceIndices => {
    const isPre2011 = apartment.prices.maximum_prices.unconfirmed.pre_2011 !== null;
    if (isPre2011) return apartment.prices.maximum_prices.unconfirmed.pre_2011;
    else return apartment.prices.maximum_prices.unconfirmed.onwards_2011;
};

// Takes a date in YYYY-MM-DD format (with the day being optional), and returns the hitas-quarter the date belongs to.
// Returns the current hitas-quarter if no date is supplied.
export const getHitasQuarter = (date?) => {
    // Extract month from date, or use current month if there's no date (getMonth returns a 0-indexed value, so add 1)
    const month = date ? Number(date.split("-")[1]) : new Date().getMonth() + 1;
    const quarter: Record<"number", number> = {number: 0};
    switch (month) {
        case 11:
        case 12:
        case 1:
            quarter.number = 3;
            break;
        case 2:
        case 3:
        case 4:
            quarter.number = 0;
            break;
        case 5:
        case 6:
        case 7:
            quarter.number = 1;
            break;
        case 8:
        case 9:
        case 10:
            quarter.number = 2;
            break;
        default:
            return {label: "Virheellinen kuukausi!", value: "---"};
    }
    return hitasQuarters[quarter.number];
};

export const getHitasQuarterFullLabel = (
    month: string,
    onlyCalculationMonths = false // Do not return a value for the months which are not the start of a new quarter/year
) => {
    const [yearString, monthString] = month.split("-");
    const hitasQuarter = getHitasQuarter(month).label;

    // For the months which start and end the same year, simply add the year to the end of the quarter
    const formatQuarter = (quarter) => `${hitasQuarter}${yearString} (Q${quarter})`;

    // Add last year for the start date, as January's quarter begins in the previous year
    const formatJan = () =>
        `${hitasQuarter.split(" ")[0]}${Number(yearString) - 1} - ${hitasQuarter.split("-")[1]}${yearString} (Q3)`;

    // Add the next year in the end date for the last quarter, as the quarter ends in the next year
    const formatNovDec = () =>
        `${hitasQuarter.split(" ")[0]}${yearString} - ${hitasQuarter.split("-")[1]}${Number(yearString) + 1} (Q3)`;

    switch (monthString) {
        case "01":
            return formatJan();
        case "02":
            return formatQuarter(4);
        case "03":
        case "04":
            return onlyCalculationMonths ? undefined : formatQuarter(4);
        case "05":
            return formatQuarter(1);
        case "06":
        case "07":
            return onlyCalculationMonths ? undefined : formatQuarter(1);
        case "08":
            return formatQuarter(2);
        case "09":
        case "10":
            return onlyCalculationMonths ? undefined : formatQuarter(2);
        case "11":
            return formatNovDec();
        case "12":
            return onlyCalculationMonths ? undefined : formatNovDec();
        default:
            break;
    }
};

// Set errors returned from an API request for form fields
// Does not work well with useFieldArray fields, as the API does not return the index of the field, only the field name
export const setAPIErrorsForFormFields = (formObject, error) => {
    if (error?.data?.fields) {
        for (const fieldError of error.data.fields) {
            formObject.setError(fieldError.field, {type: "custom", message: fieldError.message});
        }
    }
};
