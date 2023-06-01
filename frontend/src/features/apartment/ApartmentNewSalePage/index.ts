import {createContext} from "react";
import {IApartmentDetails} from "../../../common/schemas";
import ApartmentNewSalePage from "./ApartmentNewSalePage";

export default ApartmentNewSalePage;

export const ApartmentSaleContext = createContext<{
    apartment?: IApartmentDetails;
    saleForm?;
    formExtraFieldErrorMessages?;
}>({});
