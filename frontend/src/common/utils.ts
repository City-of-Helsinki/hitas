import {IAddress} from "./models";

function formatAddress(address: IAddress): string {
    return `${address.street_address}, ${address.postal_code}, ${address.city}`;
}

export {formatAddress};
