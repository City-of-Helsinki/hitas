import {IUserInfoResponse} from "../schemas";
import {authApi} from "./apis";

const userApi = authApi.injectEndpoints({
    endpoints: (builder) => ({
        getUserInfo: builder.query<IUserInfoResponse, null>({
            query: () => ({
                url: "userinfo/",
            }),
        }),
    }),
});

export const {useGetUserInfoQuery} = userApi;
