import {IUserInfoResponse} from "../schemas";
import {hitasApi} from "./apis";

const userApi = hitasApi.injectEndpoints({
    endpoints: (builder) => ({
        getUserInfo: builder.query<IUserInfoResponse, null>({
            query: () => ({
                url: "userinfo/",
            }),
        }),
    }),
});

export const {useGetUserInfoQuery} = userApi;
