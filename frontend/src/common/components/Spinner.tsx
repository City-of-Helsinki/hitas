import {LoadingSpinner} from "hds-react";

export default function Spinner(): JSX.Element {
    return (
        <main>
            <div className="spinner-wrap-color">
                <div className="spinner-container">
                    <LoadingSpinner />
                </div>
            </div>
        </main>
    );
}
