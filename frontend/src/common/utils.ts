import {IAddress, IApartmentAddress, IPerson} from "./models";

function dotted(obj: object, path: string | string[], value?: number | string | null) {
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
    else return dotted(obj[path[0]], path.slice(1), value);
}

function formatAddress(address: IAddress | IApartmentAddress): string {
    return `${address.street_address}, ${address.postal_code}, ${address.city}`;
}

function formatPerson(person: IPerson): string {
    return `${person.last_name}, ${person.first_name} (${person.social_security_number})`;
}

function validateBusinessId(value: string): boolean {
    // e.g. '1234567-8'
    return !!value.match(/^(\d{7})-(\d)$/);
}

export {dotted, formatAddress, formatPerson, validateBusinessId};
