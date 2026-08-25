import {getCookie} from "typescript-cookie";

import {fetchAndDownloadPDF} from "./utils";

jest.mock("typescript-cookie", () => ({
    getCookie: jest.fn(),
}));

jest.mock("../utils", () => ({
    hdsToast: {
        error: jest.fn(),
    },
}));

describe("fetchAndDownloadPDF", () => {
    afterEach(() => {
        jest.restoreAllMocks();
        jest.resetAllMocks();
    });

    test("refreshes csrf cookie and retries a failed PDF request once", async () => {
        const getCookieMock = getCookie as jest.MockedFunction<typeof getCookie>;
        getCookieMock.mockReturnValueOnce("stale-token").mockReturnValue("fresh-token");

        const fetchMock = jest
            .spyOn(global, "fetch")
            .mockResolvedValueOnce(
                new Response(JSON.stringify({detail: "CSRF Failed: CSRF token incorrect."}), {
                    status: 403,
                    headers: {"Content-Type": "application/json"},
                })
            )
            .mockResolvedValueOnce(new Response(null, {status: 204}))
            // A non-success response avoids invoking the browser download helper; this test only verifies CSRF recovery.
            .mockResolvedValueOnce(new Response(null, {status: 500, statusText: "Internal Server Error"}));
        jest.spyOn(console, "error").mockImplementation(() => undefined);

        await fetchAndDownloadPDF("/test.pdf", "POST", {hello: "world"});

        expect(fetchMock).toHaveBeenCalledTimes(3);
        expect(fetchMock.mock.calls[1][0].toString()).toContain("/helauth/csrf/");

        const retryInit = fetchMock.mock.calls[2][1] as RequestInit;
        expect((retryInit.headers as Headers).get("X-CSRFToken")).toBe("fresh-token");
    });
});
