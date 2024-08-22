import {array, number, object, string, z} from "zod";
import {APIIdString, errorMessages, PageInfoSchema} from "./common";

// ********************************
// * Property manager
// ********************************

export const PropertyManagerSchema = object({
    id: APIIdString.optional(),
    name: string().nonempty(errorMessages.required).min(2, errorMessages.stringLength),
    email: string().email(errorMessages.emailInvalid).or(z.literal("")),
    modified_at: string().optional(),
});
export type IPropertyManager = z.infer<typeof PropertyManagerSchema>;

// ********************************
// * API
// ********************************

export const PropertyManagersResponseSchema = object({
    page: PageInfoSchema,
    contents: array(PropertyManagerSchema.extend({id: string()})),
});
export type IPropertyManagersResponse = z.infer<typeof PropertyManagersResponseSchema>;

export const FilterPropertyManagersQuerySchema = object({
    name: string().optional(),
    email: string().optional(),
    limit: number().int().optional(),
    page: number().int().optional(),
});
export type IFilterPropertyManagersQuery = z.infer<typeof FilterPropertyManagersQuerySchema>;
