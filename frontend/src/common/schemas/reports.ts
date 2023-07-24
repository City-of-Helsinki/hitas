import {object} from "zod";
import {APIDateSchema} from "./common";

export const SalesReportFormSchema = object({
    startDate: APIDateSchema,
    endDate: APIDateSchema,
});
