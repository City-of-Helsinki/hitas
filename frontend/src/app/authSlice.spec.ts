import authReducer, {
    IAuthState,
    initialState as defaultState,
    setIsAuthenticated,
    setIsAuthenticating,
} from "./authSlice";

describe("auth reducer", () => {
    const initialState: IAuthState = {
        isAuthenticated: false,
        isAuthenticating: false,
    };

    it("should handle initial state", () => {
        expect(authReducer(undefined, {type: "unknown"})).toEqual(defaultState);
    });

    it("should handle setIsAuthenticated", () => {
        const actual = authReducer(initialState, setIsAuthenticated(true));
        expect(actual.isAuthenticated).toEqual(true);
    });

    it("should handle setIsAuthenticating", () => {
        const actual = authReducer(initialState, setIsAuthenticating(true));
        expect(actual.isAuthenticating).toEqual(true);
    });
});
