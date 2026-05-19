import {BaseQueryApi} from "@reduxjs/toolkit/query";

import {baseQueryWithReAuth} from "./apis";

jest.mock("typescript-cookie", () => ({
    getCookie: jest.fn(() => "csrf-token"),
}));

jest.mock("../utils", () => ({
    getSignInUrl: jest.fn(() => "https://example.com/login"),
    hdsToast: {
        error: jest.fn(),
    },
}));

describe("baseQueryWithReAuth", () => {
    afterEach(() => {
        jest.restoreAllMocks();
    });

    test("refreshes csrf cookie and retries a failed mutation once", async () => {
        const fetchMock = jest
            .spyOn(global, "fetch")
            .mockResolvedValueOnce(
                new Response(JSON.stringify({detail: "CSRF Failed: CSRF token missing."}), {
                    status: 403,
                    headers: {"Content-Type": "application/json"},
                })
            )
            .mockResolvedValueOnce(new Response(null, {status: 204}))
            .mockResolvedValueOnce(
                new Response(JSON.stringify({ok: true}), {
                    status: 200,
                    headers: {"Content-Type": "application/json"},
                })
            );
        const windowOpenMock = jest.spyOn(window, "open").mockImplementation(() => null);
        const api = {
            type: "mutation",
            endpoint: "testMutation",
            forced: false,
            dispatch: jest.fn(),
            getState: jest.fn(),
            signal: new AbortController().signal,
            abort: jest.fn(),
            extra: undefined,
        } as BaseQueryApi;

        const result = await baseQueryWithReAuth({url: "/test", method: "POST", body: {hello: "world"}}, api, {});

        expect(result).toEqual({data: {ok: true}, meta: expect.any(Object)});
        expect(fetchMock).toHaveBeenCalledTimes(3);
        expect((fetchMock.mock.calls[1][0] as Request).url).toContain("/helauth/csrf/");
        expect(windowOpenMock).not.toHaveBeenCalled();
    });
});
