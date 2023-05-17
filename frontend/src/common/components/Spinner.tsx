import {LoadingSpinner} from "hds-react";

export default function Spinner(): JSX.Element {
    return (
        <main>
            <div className="spinner-wrap-color">
                <LoadingSpinner />
            </div>
        </main>
    );
}
