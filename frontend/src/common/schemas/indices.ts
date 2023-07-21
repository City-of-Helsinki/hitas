import {number, object, string, z} from "zod";
import {errorMessages, PageInfoSchema} from "./common";

const IndexMonth = string().regex(/\d{4}-\d{2}/, "Kuukauden täytyy olla muotoa VVVV-KK, esim. 2021-01");

// ********************************
// * Index
// ********************************

export const IndexSchema = object({month: IndexMonth, value: number().min(1, errorMessages.numberMin).nullable()});
export type IIndex = z.infer<typeof IndexSchema>;

// ********************************
// * API
// ********************************

export const IndexResponseSchema = object({indexType: string(), value: number(), valid_until: string()});
export type IIndexResponse = z.infer<typeof IndexResponseSchema>;

export const IndexListResponseSchema = object({
    page: PageInfoSchema,
    contents: IndexSchema.array(),
});
export type IIndexListResponse = z.infer<typeof IndexListResponseSchema>;

export const IndexListQuerySchema = object({
    indexType: string(),
    params: object({
        page: number(),
        limit: number(),
        year: string(),
    }),
});
export type IIndexListQuery = z.infer<typeof IndexListQuerySchema>;

const IndexQuerySchema = object({
    indexType: string(),
    month: IndexMonth,
});
export type IIndexQuery = z.infer<typeof IndexQuerySchema>;
