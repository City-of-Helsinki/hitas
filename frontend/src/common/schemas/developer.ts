import {number, object, string, z} from "zod";
import {APIIdString, errorMessages} from "./common";

// ********************************
// * Developer
// ********************************

export const DeveloperSchema = object({
    id: APIIdString.optional(),
    value: string().nonempty(errorMessages.required).min(2, errorMessages.stringLength),
    description: string()
        .nonempty(errorMessages.required)
        .min(2, errorMessages.stringLength)
        .max(256, errorMessages.stringMaxIs + "256")
        .nullable(),
});
export type IDeveloper = z.infer<typeof DeveloperSchema>;

// ********************************
// * API
// ********************************

export const FilterDevelopersQuerySchema = object({
    value: string().optional(),
    limit: number().int().optional(),
    page: number().int().optional(),
});
export type IFilterDevelopersQuery = z.infer<typeof FilterDevelopersQuerySchema>;
