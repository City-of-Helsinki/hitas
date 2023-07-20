import {
    IExternalSalesDataResponse,
    IThirtyYearAvailablePostalCodesResponse,
    IThirtyYearRegulationQuery,
    IThirtyYearRegulationResponse,
} from "../../schemas";
import {mutationApiExcelHeaders, mutationApiJsonHeaders} from "../utils";

import {hitasApi} from "../apis";

const functionsApi = hitasApi.injectEndpoints({
    endpoints: (builder) => ({
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
                    !error && result ? [{type: "ThirtyYearRegulation", id: arg.data.calculationDate}] : [],
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
                !error && result ? [{type: "ExternalSaleData", id: arg.calculation_date}] : [],
        }),
        getPriceCeilingCalculationData: builder.query<{calculationMonth: string}, object>({
            query: (params: {calculationMonth: string}) => ({
                url: `indices/surface-area-price-ceiling-calculation-data/${params.calculationMonth}-01`,
            }),
        }),
        calculatePriceCeiling: builder.mutation({
            query: ({data}) => ({
                url: "indices/surface-area-price-ceiling",
                method: "POST",
                headers: mutationApiJsonHeaders(),
                body: data,
            }),
            invalidatesTags: (result, error) => (!error && result ? [{type: "Index", id: "LIST"}] : []),
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
} = functionsApi;
