import {Link} from "hds-react";
import useAuthentication from "../../app/useAuthentication";

export default function Unauthorized(): JSX.Element {
    const {signIn} = useAuthentication();
    return (
        <main>
            <p style={{padding: "6rem 1rem"}}>
                Sisältöä ei voida hakea, koska et ole kirjautunut sivustolle.{" "}
                <Link
                    href="#"
                    onClick={signIn}
                >
                    Kirjaudu sisään
                </Link>
            </p>
        </main>
    );
}
