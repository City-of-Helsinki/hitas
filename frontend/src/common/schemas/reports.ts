import {number, object, string, z} from "zod";
import {APIDateSchema} from "./common";

export const SalesReportFormSchema = object({
    startDate: APIDateSchema,
    endDate: APIDateSchema,
});

export const JobPerformanceSchema = object({
    totals: object({
        count: number(),
        average_days: number(),
        maximum_days: number(),
    }),
    per_user: object({
        full_name: string(),
        job_performance_count: number(),
    }).array(),
});

const ApartmentSalesJobPerformanceSchema = object({
    count: number(),
});

export type ApartmentSalesJobPerformanceResponse = z.infer<typeof ApartmentSalesJobPerformanceSchema>;

export type JobPerformanceResponse = z.infer<typeof JobPerformanceSchema>;
