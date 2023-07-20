import {number, object, string, z} from "zod";
import {PageInfoSchema} from "./common";

// ********************************
// * Index
// ********************************

const IndexSchema = object({indexType: string(), month: string(), value: number().nullable()});
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
    month: string(),
});
export type IIndexQuery = z.infer<typeof IndexQuerySchema>;
