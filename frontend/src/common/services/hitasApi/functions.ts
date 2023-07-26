import {
    IExternalSalesDataResponse,
    IIndexCalculationDataResponse,
    IThirtyYearAvailablePostalCodesResponse,
    IThirtyYearRegulationQuery,
    IThirtyYearRegulationResponse,
} from "../../schemas";
import {mutationApiExcelHeaders, mutationApiJsonHeaders, safeInvalidate} from "../utils";

import {hitasApi} from "../apis";

const functionsApi = hitasApi.injectEndpoints({
    endpoints: (builder) => ({
        // Thirty year regulation
        getAvailablePostalCodes: builder.query<IThirtyYearAvailablePostalCodesResponse, object>({
            query: (params: object) => ({
                url: "thirty-year-regulation/postal-codes",
                params: params,
            }),
        }),
        getThirtyYearRegulation: builder.query<IThirtyYearRegulationResponse, IThirtyYearRegulationQuery>({
            query: (params: IThirtyYearRegulationQuery) => ({
                url: "thirty-year-regulation",
                params: {
                    calculation_date: params.calculationDate,
                },
            }),
            providesTags: (result, error, arg) => [{type: "ThirtyYearRegulation", id: arg.calculationDate}],
        }),
        createThirtyYearRegulation: builder.mutation<IThirtyYearRegulationResponse, {data: IThirtyYearRegulationQuery}>(
            {
                query: ({data}) => ({
                    url: `thirty-year-regulation`,
                    method: "POST",
                    body: {
                        calculation_date: data.calculationDate,
                        replacement_postal_codes: data.replacementPostalCodes?.map((p) => {
                            return {postal_code: p.postalCode, replacements: p.replacements};
                        }),
                    },
                    headers: {"Content-type": "application/json; charset=UTF-8"},
                }),
                invalidatesTags: (result, error, arg) =>
                    safeInvalidate(error, [{type: "ThirtyYearRegulation", id: arg.data.calculationDate}]),
            }
        ),
        getExternalSalesData: builder.query<IExternalSalesDataResponse, {calculation_date: string}>({
            query: (params: {calculation_date: string}) => ({
                url: "external-sales-data",
                params: params,
            }),
            providesTags: (result, error, arg) => [{type: "ExternalSaleData", id: arg.calculation_date}],
        }),
        saveExternalSalesData: builder.mutation({
            query: (arg) => ({
                url: "external-sales-data",
                method: "POST",
                body: arg.data,
                params: {calculation_date: arg.calculation_date},
                headers: mutationApiExcelHeaders(),
            }),
            invalidatesTags: (result, error, arg) =>
                safeInvalidate(error, [{type: "ExternalSaleData", id: arg.calculation_date}, {type: "Index"}]),
        }),
        // Surface area price ceiling
        calculatePriceCeiling: builder.mutation({
            query: (params: {calculation_date: string}) => ({
                url: "indices/surface-area-price-ceiling",
                method: "POST",
                headers: mutationApiJsonHeaders(),
                params: params,
            }),
            invalidatesTags: (result, error) =>
                safeInvalidate(error, [{type: "Index"}, {type: "SurfaceAreaPriceCeilingCalculation"}]),
        }),
        getSurfaceAreaPriceCeilingCalculationData: builder.query<
            IIndexCalculationDataResponse,
            {params: {year?: string; limit?: number; page?: number}}
        >({
            query: ({params}) => ({
                url: "indices/surface-area-price-ceiling-calculation-data",
                params: params,
            }),
            providesTags: () => [{type: "SurfaceAreaPriceCeilingCalculation"}],
        }),
    }),
});

export const {
    useCalculatePriceCeilingMutation,
    useCreateThirtyYearRegulationMutation,
    useGetAvailablePostalCodesQuery,
    useGetExternalSalesDataQuery,
    useGetThirtyYearRegulationQuery,
    useSaveExternalSalesDataMutation,
    useGetSurfaceAreaPriceCeilingCalculationDataQuery,
} = functionsApi;
