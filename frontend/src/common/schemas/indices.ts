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

const IndexCalculationDataSchema = object({
    calculation_month: string(),
    data: object({
        housing_company_data: object({
            name: string(),
            completion_date: string(),
            surface_area: number(),
            realized_acquisition_price: number(),
            unadjusted_average_price_per_square_meter: number(),
            adjusted_average_price_per_square_meter: number(),
            completion_month_index: number(),
            calculation_month_index: number(),
        }).array(),
        created_surface_area_price_ceilings: object({
            month: string(),
            value: number(),
        }).array(),
    }),
});
export type IIndexCalculationData = z.infer<typeof IndexCalculationDataSchema>;

export const IIndexCalculationDataResponseSchema = object({
    page: PageInfoSchema,
    contents: IndexCalculationDataSchema.array(),
});
export type IIndexCalculationDataResponse = z.infer<typeof IIndexCalculationDataResponseSchema>;
