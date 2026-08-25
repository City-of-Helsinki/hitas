import {BaseQueryApi} from "@reduxjs/toolkit/query";

import {baseQueryWithReAuth, refreshCsrfCookie} from "./apis";

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
        expect(fetchMock.mock.calls[1][0].toString()).toContain("/helauth/csrf/");
        expect(windowOpenMock).not.toHaveBeenCalled();
    });

    test("refreshes csrf cookie when Django returns an HTML csrf error", async () => {
        const fetchMock = jest
            .spyOn(global, "fetch")
            .mockResolvedValueOnce(
                new Response("<html><body>CSRF verification failed. Request aborted.</body></html>", {
                    status: 403,
                    headers: {"Content-Type": "text/html"},
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
        expect(windowOpenMock).not.toHaveBeenCalled();
    });
});

describe("refreshCsrfCookie", () => {
    afterEach(() => {
        jest.restoreAllMocks();
    });

    test("coalesces concurrent csrf refreshes", async () => {
        let resolveFetch: (response: Response) => void = () => undefined;
        const fetchMock = jest.spyOn(global, "fetch").mockImplementation(
            () =>
                new Promise<Response>((resolve) => {
                    resolveFetch = resolve;
                })
        );

        const firstRefresh = refreshCsrfCookie();
        const secondRefresh = refreshCsrfCookie();

        expect(fetchMock).toHaveBeenCalledTimes(1);

        resolveFetch(new Response(null, {status: 204}));

        await expect(Promise.all([firstRefresh, secondRefresh])).resolves.toEqual([true, true]);
    });
});
