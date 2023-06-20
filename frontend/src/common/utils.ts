import toast, {ToastOptions} from "react-hot-toast";

import {Config} from "../app/services";
import {
    IAddress,
    IApartmentAddress,
    IApartmentDetails,
    IApartmentUnconfirmedMaximumPriceIndices,
    IOwner,
} from "./schemas";

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

export function formatOwner(owner: IOwner): string {
    return `${owner.name} (${owner.identifier})`;
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
    // e.g. '1234567-1'
    // This does not validate the check digit (last number), only the format
    return !!value.match(/^(\d{7})-(\d)$/);
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
    const dateString = `${yearString}-${dateValue.substring(3, 4)}-${dateValue.substring(0, 2)}`;
    if (isNaN(Date.parse(dateString))) return false;
    // validate individual number
    const idNumber = Number(value.substring(7, 10));
    if (idNumber < 2 || idNumber > 899) return false;
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
export function hitasToast(
    message: string | JSX.Element,
    type?: "success" | "info" | "error" | "alert",
    opts?: ToastOptions
) {
    toast(message, {...opts, className: type});
}

export const hdsToast = {
    success: (message: string | JSX.Element, opts?: ToastOptions) => toast(message, {...opts, className: "success"}),
    info: (message: string | JSX.Element, opts?: ToastOptions) => toast(message, {...opts, className: "info"}),
    error: (message: string | JSX.Element, opts?: ToastOptions) => toast(message, {...opts, className: "error"}),
    alert: (message: string | JSX.Element, opts?: ToastOptions) => toast(message, {...opts, className: "alert"}),
};

// Returns true if obj1 contains the same key/value pairs as obj2. Note that this is non-exclusive, so obj1 doesn't
// have to be identical to obj2, as it can contain more data than only the ones from obj2.
export function doesAContainB(A: object, B: object): boolean {
    const AProps = Object.getOwnPropertyNames(A);
    const BProps = Object.getOwnPropertyNames(B);
    if (AProps.length < BProps.length) {
        return false;
    }
    for (const prop of BProps) {
        if (!Object.prototype.hasOwnProperty.call(A, prop) || A[prop] !== B[prop]) {
            return false;
        }
    }
    return true;
}

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

export const getApartmentUnconfirmedPrices = (
    apartment: IApartmentDetails
): IApartmentUnconfirmedMaximumPriceIndices => {
    const isPre2011 = apartment.prices.maximum_prices.unconfirmed.pre_2011 !== null;
    if (isPre2011) return apartment.prices.maximum_prices.unconfirmed.pre_2011;
    else return apartment.prices.maximum_prices.unconfirmed.onwards_2011;
};

// Takes a date and returns the hitasQuarter it belongs to. Returns current quarter if no date is given.
export const getHitasQuarter = (date?) => {
    const time = date ? Number(date.slice("-")[1]) : new Date().getMonth() + 1;
    let defaultQuarter = {label: "1.2. - 30.4.", value: "02-01"};
    // FIXME: The +2 is a hack to get the next quarter as a return value for testing. Remove before commit!
    switch (time + 2) {
        case 0:
        case 10:
        case 11:
            defaultQuarter = {label: "1.11. - 31.1.", value: "11-01"};
            break;
        case 4:
        case 5:
        case 6:
            defaultQuarter = {label: "1.5. - 31.7.", value: "05-01"};
            break;
        case 7:
        case 8:
        case 9:
            defaultQuarter = {label: "1.8. - 31.10.", value: "08-01"};
            break;
    }
    return defaultQuarter;
};
