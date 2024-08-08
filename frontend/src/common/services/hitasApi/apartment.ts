import {
    IApartmentDetails,
    IApartmentListResponse,
    IApartmentMaximumPriceCalculationDetails,
    IApartmentMaximumPriceWritable,
    IApartmentQuery,
    IApartmentSale,
    IApartmentSaleCreated,
    IApartmentUnconfirmedMaximumPriceIndices,
    IApartmentWritable,
    ICodeResponse,
    IConditionOfSale,
    ICreateConditionOfSale,
    IDocument,
    IOwner,
    IDocumentWritable,
} from "../../schemas";
import {idOrBlank, safeInvalidate} from "../utils";

import {hitasApi} from "../apis";
import {FetchBaseQueryError} from "@reduxjs/toolkit/dist/query/react";
import {QueryReturnValue} from "@reduxjs/toolkit/dist/query/baseQueryTypes";

const apartmentApi = hitasApi.injectEndpoints({
    endpoints: (builder) => ({
        getApartments: builder.query<IApartmentListResponse, object>({
            query: (params: object) => ({
                url: "apartments",
                params: params,
            }),
            providesTags: [{type: "Apartment", id: "LIST"}],
        }),
        getApartmentTypes: builder.query<ICodeResponse, object>({
            query: (params: object) => ({
                url: "apartment-types",
                params: params,
            }),
        }),
        getApartmentDetail: builder.query<IApartmentDetails, IApartmentQuery>({
            query: (params: IApartmentQuery) => ({
                url: `housing-companies/${params.housingCompanyId}/apartments/${params.apartmentId}`,
            }),
            providesTags: (result, error, arg) => [{type: "Apartment", id: arg.apartmentId}, {type: "Owner"}],
        }),
        getObfuscatedOwner: builder.query<IOwner, string>({
            query: (ownerId) => ({
                url: `owners/deobfuscated/${ownerId}`,
            }),
            providesTags: (result, error, arg) => [
                {type: "ObfuscatedOwner", id: arg},
                {type: "Owner", id: arg},
            ],
        }),
        getObfuscatedOwners: builder.query<{data: IOwner[]; error: FetchBaseQueryError[]}, string[]>({
            queryFn: async (ids, _queryApi, _extraOptions, baseQuery) => {
                const results: QueryReturnValue<unknown, FetchBaseQueryError>[] = await Promise.all(
                    ids.map((id) => baseQuery(`owners/deobfuscated/${id}`))
                );
                const emptyObfuscatedOwnersData = [] as IOwner[];
                const obfuscatedOwnersData = results.map((result) => result.data) as IOwner[];
                const obfuscatedOwners = emptyObfuscatedOwnersData.concat(...obfuscatedOwnersData);

                const emptyErrorsData = [] as FetchBaseQueryError[];
                const errorsData = results
                    .filter((result) => result.error !== null)
                    .map((result) => result.error) as FetchBaseQueryError[];
                const mergedErrorsData = emptyErrorsData.concat(...errorsData);
                const errors = mergedErrorsData.length > 0 ? mergedErrorsData : undefined;

                return {data: {data: obfuscatedOwners, error: errors}} as {
                    data: {error: FetchBaseQueryError[]; data: IOwner[]};
                };
            },
            providesTags: () => [{type: "ObfuscatedOwners", id: "LIST"}],
        }),
        saveApartment: builder.mutation<
            IApartmentDetails,
            {data: IApartmentWritable; id?: string; housingCompanyId: string}
        >({
            query: ({data, id, housingCompanyId}) => ({
                url: `housing-companies/${housingCompanyId}/apartments${idOrBlank(id)}`,
                method: id === undefined ? "POST" : "PUT",
                body: data,
            }),
            invalidatesTags: (result, error, arg) =>
                safeInvalidate(error, [
                    {type: "Apartment", id: "LIST"},
                    {type: "Apartment", id: arg.id},
                    {type: "HousingCompany", id: arg.housingCompanyId},
                ]),
        }),
        patchApartment: builder.mutation<
            IApartmentDetails,
            {housingCompanyId: string; id: string; data: Partial<IApartmentWritable>}
        >({
            query: ({data, id, housingCompanyId}) => ({
                url: `housing-companies/${housingCompanyId}/apartments/${id}`,
                method: "PATCH",
                body: data,
            }),
            invalidatesTags: (result, error, arg) =>
                safeInvalidate(error, [
                    {type: "Apartment", id: "LIST"},
                    {type: "Apartment", id: arg.id},
                    {type: "HousingCompany", id: arg.housingCompanyId},
                ]),
        }),
        deleteApartment: builder.mutation<
            IApartmentDetails,
            {
                id: string | undefined;
                housingCompanyId: string;
            }
        >({
            query: ({id, housingCompanyId}) => ({
                url: `housing-companies/${housingCompanyId}/apartments/${id}`,
                method: "DELETE",
            }),
            invalidatesTags: (result, error, arg) =>
                safeInvalidate(error, [
                    {type: "Apartment", id: "LIST"},
                    {type: "Apartment", id: arg.id},
                    {type: "HousingCompany", id: arg.housingCompanyId},
                ]),
        }),
        createSale: builder.mutation<
            IApartmentSaleCreated,
            {
                data: IApartmentSale;
                housingCompanyId: string;
                apartmentId: string;
            }
        >({
            query: ({data, housingCompanyId, apartmentId}) => ({
                url: `housing-companies/${housingCompanyId}/apartments/${apartmentId}/sales`,
                method: "POST",
                body: data,
            }),
            invalidatesTags: (result, error, arg) =>
                safeInvalidate(error, [{type: "Apartment"}, {type: "HousingCompany", id: arg.housingCompanyId}]),
        }),
        deleteSale: builder.mutation<unknown, {housingCompanyId: string; apartmentId: string; saleId: string}>({
            query: ({housingCompanyId, apartmentId, saleId}) => ({
                url: `housing-companies/${housingCompanyId}/apartments/${apartmentId}/sales/${saleId}`,
                method: "DELETE",
            }),
            invalidatesTags: (result, error, arg) =>
                safeInvalidate(error, [{type: "Apartment"}, {type: "HousingCompany", id: arg.housingCompanyId}]),
        }),
        saveApartmentDocument: builder.mutation<
            IDocument,
            {
                data: IDocumentWritable;
                id?: string;
                housingCompanyId: string;
                apartmentId: string;
            }
        >({
            query: ({data, id, housingCompanyId, apartmentId}) => ({
                url: `housing-companies/${housingCompanyId}/apartments/${apartmentId}/documents${idOrBlank(id)}`,
                method: id === undefined ? "POST" : "PUT",
                body: data,
            }),
            extraOptions: {
                isFormDataFileUpload: true,
            },
            invalidatesTags: (result, error, arg) =>
                safeInvalidate(error, [
                    {type: "Apartment", id: arg.apartmentId},
                    {type: "HousingCompany", id: arg.housingCompanyId},
                ]),
        }),
        deleteApartmentDocument: builder.mutation<
            unknown,
            {housingCompanyId: string; apartmentId: string; documentId: string}
        >({
            query: ({housingCompanyId, apartmentId, documentId}) => ({
                url: `housing-companies/${housingCompanyId}/apartments/${apartmentId}/documents/${documentId}`,
                method: "DELETE",
            }),
            invalidatesTags: (result, error, arg) =>
                safeInvalidate(error, [
                    {type: "Apartment", id: arg.apartmentId},
                    {type: "HousingCompany", id: arg.housingCompanyId},
                ]),
        }),
    }),
});

export const {
    useCreateSaleMutation,
    useDeleteApartmentMutation,
    useDeleteSaleMutation,
    useGetApartmentDetailQuery,
    useGetApartmentTypesQuery,
    useGetApartmentsQuery,
    useGetObfuscatedOwnerQuery,
    useGetObfuscatedOwnersQuery,
    usePatchApartmentMutation,
    useSaveApartmentMutation,
    useSaveApartmentDocumentMutation,
    useDeleteApartmentDocumentMutation,
} = apartmentApi;

const apartmentMaximumPriceApi = hitasApi.injectEndpoints({
    endpoints: (builder) => ({
        getApartmentMaximumPrice: builder.query<
            IApartmentMaximumPriceCalculationDetails,
            {
                housingCompanyId: string;
                apartmentId: string;
                priceId: string;
            }
        >({
            query: ({
                housingCompanyId,
                apartmentId,
                priceId,
            }: {
                housingCompanyId: string;
                apartmentId: string;
                priceId: string;
            }) => ({
                url: `housing-companies/${housingCompanyId}/apartments/${apartmentId}/maximum-prices/${priceId}`,
            }),
            providesTags: (result, error, arg) => [{type: "Apartment", id: arg.apartmentId}],
        }),
        getApartmentUnconfirmedMaximumPriceForDate: builder.query<
            IApartmentUnconfirmedMaximumPriceIndices,
            {
                housingCompanyId: string;
                apartmentId: string;
                date?: string;
            }
        >({
            query: ({
                housingCompanyId,
                apartmentId,
                date,
            }: {
                housingCompanyId: string;
                apartmentId: string;
                date: string;
            }) => ({
                url: `housing-companies/${housingCompanyId}/apartments/${apartmentId}/retrieve-unconfirmed-prices-for-date`,
                params: {calculation_date: date},
            }),
        }),
        saveApartmentMaximumPrice: builder.mutation<
            IApartmentMaximumPriceCalculationDetails,
            {
                data: IApartmentMaximumPriceWritable | {confirm: true};
                id?: string;
                apartmentId: string;
                housingCompanyId: string;
            }
        >({
            query: ({data, id, apartmentId, housingCompanyId}) => ({
                url: `housing-companies/${housingCompanyId}/apartments/${apartmentId}/maximum-prices${idOrBlank(id)}`,
                method: id === undefined ? "POST" : "PUT",
                body: data,
            }),
            // Invalidate Apartment Details only when confirming a maximum price, don't invalidate if confirmed_at
            // is not set (e.g. when creating a new maximum price)
            invalidatesTags: (result, error, arg) =>
                safeInvalidate(error || (result && !result.confirmed_at), [{type: "Apartment", id: arg.apartmentId}]),
        }),
    }),
});

export const {
    useGetApartmentMaximumPriceQuery,
    useGetApartmentUnconfirmedMaximumPriceForDateQuery,
    useSaveApartmentMaximumPriceMutation,
} = apartmentMaximumPriceApi;

const apartmentConditionsOfSaleApi = hitasApi.injectEndpoints({
    endpoints: (builder) => ({
        createConditionOfSale: builder.mutation<
            {conditions_of_sale: IConditionOfSale[]},
            {data: ICreateConditionOfSale}
        >({
            query: ({data}) => ({
                url: `conditions-of-sale`,
                method: "POST",
                body: data,
            }),
            invalidatesTags: (result, error) =>
                safeInvalidate(error || (result && !result.conditions_of_sale.length), [{type: "Apartment"}]),
        }),
        patchConditionOfSale: builder.mutation<IConditionOfSale, Partial<IConditionOfSale>>({
            query: (conditionOfSale) => ({
                url: `conditions-of-sale/${conditionOfSale.id}`,
                method: "PATCH",
                body: conditionOfSale,
            }),
            invalidatesTags: (result, error, arg) =>
                safeInvalidate(error, [{type: "Apartment"}, {type: "ConditionOfSale", id: arg.id}]),
        }),
        deleteConditionOfSale: builder.mutation<object, {id: string}>({
            query: ({id}) => ({
                url: `conditions-of-sale/${id}`,
                method: "DELETE",
            }),
            invalidatesTags: (result, error) => safeInvalidate(error, [{type: "Apartment"}]),
        }),
    }),
});

export const {useCreateConditionOfSaleMutation, useDeleteConditionOfSaleMutation, usePatchConditionOfSaleMutation} =
    apartmentConditionsOfSaleApi;
