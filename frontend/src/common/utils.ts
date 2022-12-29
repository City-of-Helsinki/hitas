import toast, {ToastOptions} from "react-hot-toast";

import {IAddress, IApartmentAddress, IOwner} from "./models";

function dotted(obj: object, path: string | string[], value?: number | string | null | object) {
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
    else if (path.length && obj === null) return null; // Don't crash hard when there is path left and obj is null
    else return dotted(obj[path[0]], path.slice(1), value);
}

function formatAddress(address: IAddress | IApartmentAddress): string {
    return `${address.street_address}, ${address.postal_code}, ${address.city}`;
}

function formatOwner(owner: IOwner): string {
    return `${owner.name} (${owner.identifier})`;
}

function formatMoney(value: number | null, forceDecimals = false): string {
    if (value === null) return "-";

    const formatOptions = {
        style: "currency",
        currency: "EUR",
        minimumFractionDigits: value === 0 ? 0 : 2,
        maximumFractionDigits: value === 0 ? 0 : 2,
        trailingZeroDisplay: forceDecimals ? "auto" : "stripIfInteger", // Strip decimals if they are all zero
    };
    return new Intl.NumberFormat("fi-FI", formatOptions).format(value);
}

function formatDate(value: string | null): string {
    if (value === null) return "-";

    return new Date(value).toLocaleDateString("fi-FI");
}

function validateBusinessId(value: string): boolean {
    // e.g. '1234567-8'
    return !!value.match(/^(\d{7})-(\d)$/);
}

// Toast hook with easier Notification typing
function hitasToast(message: string, type?: "success" | "info" | "error" | "alert", opts?: ToastOptions) {
    toast(message, {...opts, className: type});
}

export {dotted, formatAddress, formatOwner, formatMoney, formatDate, validateBusinessId, hitasToast};
