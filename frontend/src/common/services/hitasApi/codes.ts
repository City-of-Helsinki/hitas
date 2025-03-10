import {
    ICodeResponse,
    IDeveloper,
    IFilterDevelopersQuery,
    IFilterOwnersQuery,
    IFilterPropertyManagersQuery,
    IIndex,
    IIndexListQuery,
    IIndexListResponse,
    IIndexQuery,
    IIndexResponse,
    IOwner,
    IOwnerMergeData,
    IOwnersResponse,
    IPostalCodeResponse,
    IPropertyManager,
    IPropertyManagersResponse,
} from "../../schemas";
import {idOrBlank, safeInvalidate} from "../utils";

import {hitasApi} from "../apis";

const postalCodeApi = hitasApi.injectEndpoints({
    endpoints: (builder) => ({
        getPostalCodes: builder.query<IPostalCodeResponse, object>({
            query: (params: object) => ({
                url: "postal-codes",
                params: params,
            }),
        }),
    }),
});

export const {useGetPostalCodesQuery} = postalCodeApi;

const indexApi = hitasApi.injectEndpoints({
    endpoints: (builder) => ({
        getIndices: builder.query<IIndexListResponse, IIndexListQuery>({
            query: (params: IIndexListQuery) => ({
                url: `indices/${params.indexType}`,
                params: params.params,
            }),
            providesTags: [{type: "Index"}],
        }),
        getIndex: builder.query<IIndexResponse, IIndexQuery>({
            query: (params: IIndexQuery) => ({
                url: `indices/${params.indexType}/${params.month}`,
            }),
            providesTags: [{type: "Index"}],
        }),
        saveIndex: builder.mutation<IIndex, {data: IIndex; index: string; month: string}>({
            query: ({data, index, month}) => ({
                url: `indices/${index}/${month}`,
                method: "PUT",
                body: data,
            }),
            invalidatesTags: (result, error) => safeInvalidate(error, [{type: "Apartment"}, {type: "Index"}]),
        }),
    }),
});

export const {useGetIndexQuery, useGetIndicesQuery, useSaveIndexMutation} = indexApi;

const developerApi = hitasApi.injectEndpoints({
    endpoints: (builder) => ({
        getDevelopers: builder.query<ICodeResponse, IFilterDevelopersQuery>({
            query: (params) => ({
                url: "developers",
                params: params,
            }),
            providesTags: [{type: "Developer", id: "LIST"}],
        }),
        saveDeveloper: builder.mutation<IDeveloper, IDeveloper>({
            query: (data) => ({
                url: `developers${idOrBlank(data.id)}`,
                method: data.id === undefined ? "POST" : "PUT",
                body: data,
            }),
            invalidatesTags: (result, error) => safeInvalidate(error, [{type: "Developer"}]),
        }),
    }),
});

export const {useGetDevelopersQuery, useSaveDeveloperMutation} = developerApi;
export const {getDevelopers} = developerApi.endpoints;

const propertyManagerApi = hitasApi.injectEndpoints({
    endpoints: (builder) => ({
        getPropertyManagers: builder.query<IPropertyManagersResponse, IFilterPropertyManagersQuery>({
            query: (params) => ({
                url: "property-managers",
                params: params,
            }),
            providesTags: [{type: "PropertyManager", id: "LIST"}],
        }),
        savePropertyManager: builder.mutation<IPropertyManager, IPropertyManager>({
            query: (data) => ({
                url: `property-managers${idOrBlank(data.id)}`,
                method: data.id === undefined ? "POST" : "PUT",
                body: data,
            }),
            invalidatesTags: (result, error) => safeInvalidate(error, [{type: "PropertyManager"}]),
        }),
        deletePropertyManager: builder.mutation<
            IPropertyManager,
            {
                id: string;
            }
        >({
            query: ({id}) => ({
                url: `property-managers/${id}`,
                method: "DELETE",
            }),
            invalidatesTags: (result, error, arg) =>
                safeInvalidate(error, [
                    {type: "PropertyManager", id: "LIST"},
                    {type: "PropertyManager", id: arg.id},
                    {type: "HousingCompany"},
                ]),
        }),
    }),
});

export const {useGetPropertyManagersQuery, useSavePropertyManagerMutation, useDeletePropertyManagerMutation} =
    propertyManagerApi;
export const {getPropertyManagers} = propertyManagerApi.endpoints;

const ownerApi = hitasApi.injectEndpoints({
    endpoints: (builder) => ({
        getOwners: builder.query<IOwnersResponse, IFilterOwnersQuery>({
            query: (params) => ({
                url: "owners",
                params: params,
            }),
            providesTags: [{type: "Owner", id: "LIST"}],
        }),
        saveOwner: builder.mutation<IOwner, {data: IOwner}>({
            query: ({data}) => ({
                url: `owners${idOrBlank(data.id)}`,
                method: data.id === undefined ? "POST" : "PUT",
                body: data,
            }),
            invalidatesTags: (result, error, arg) => {
                if (arg.data.id !== undefined) {
                    return safeInvalidate(error, [
                        {type: "Owner"},
                        {type: "ObfuscatedOwners"},
                        {type: "ObfuscatedOwner"},
                        {type: "Apartment"},
                    ]);
                } else {
                    return safeInvalidate(error, [
                        {type: "Owner"},
                        {type: "ObfuscatedOwners"},
                        {type: "ObfuscatedOwner"},
                    ]);
                }
            },
        }),
        mergeOwners: builder.mutation<IOwner, {data: IOwnerMergeData}>({
            query: ({data}) => ({
                url: `owners/merge`,
                method: "POST",
                body: data,
            }),
            invalidatesTags: (result, error) => {
                return safeInvalidate(error, [
                    {type: "Owner"},
                    {type: "ObfuscatedOwners"},
                    {type: "ObfuscatedOwner"},
                    {type: "Apartment"},
                ]);
            },
        }),
    }),
});

export const {useGetOwnersQuery, useSaveOwnerMutation, useMergeOwnersMutation} = ownerApi;
