import {selectIsAuthenticated} from "../../app/authSlice";
import {useAppSelector} from "../../app/hooks";
import {useGetUserInfoQuery} from "../../app/services";

export default function LogoutCallback(): JSX.Element {
    const isAuthenticated = useAppSelector(selectIsAuthenticated);
    const {isLoading: isUserInfoLoading} = useGetUserInfoQuery();
    return isAuthenticated || isUserInfoLoading ? (
        <></>
    ) : (
        <main>
            <p style={{padding: "6rem 1rem"}}>Olet kirjautunut onnistuneesti ulos sivustolta.</p>
        </main>
    );
}
