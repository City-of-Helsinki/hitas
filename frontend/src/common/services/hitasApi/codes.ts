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
    IOwnersResponse,
    IPostalCodeResponse,
    IPropertyManager,
    IPropertyManagersResponse,
} from "../../schemas";
import {idOrBlank, mutationApiJsonHeaders} from "../utils";

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
            providesTags: [{type: "Index", id: "LIST"}],
        }),
        getIndex: builder.query<IIndexResponse, IIndexQuery>({
            query: (params: IIndexQuery) => ({
                url: `indices/${params.indexType}/${params.month}`,
            }),
        }),
        saveIndex: builder.mutation<IIndex, {data: IIndex; index: string; month: string}>({
            query: ({data, index, month}) => ({
                url: `indices/${index}/${month}`,
                method: "PUT",
                body: data,
                headers: mutationApiJsonHeaders(),
            }),
            invalidatesTags: () => [{type: "Apartment"}, {type: "Index", id: "LIST"}],
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
                headers: mutationApiJsonHeaders(),
            }),
            invalidatesTags: (response) => [
                {type: "Developer", id: response?.id},
                {type: "Developer", id: "LIST"},
            ],
        }),
    }),
});

export const {useGetDevelopersQuery, useSaveDeveloperMutation} = developerApi;

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
                headers: mutationApiJsonHeaders(),
            }),
            invalidatesTags: (response) => [
                {type: "PropertyManager", id: response?.id},
                {type: "PropertyManager", id: "LIST"},
            ],
        }),
    }),
});

export const {useGetPropertyManagersQuery, useSavePropertyManagerMutation} = propertyManagerApi;

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
                headers: mutationApiJsonHeaders(),
            }),
            invalidatesTags: () => [{type: "Owner"}],
        }),
    }),
});

export const {useGetOwnersQuery, useSaveOwnerMutation} = ownerApi;
