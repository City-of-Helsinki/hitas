import {LoadingSpinner} from "hds-react";
import React from "react";

export const Spinner = (): React.JSX.Element => {
    return (
        <main>
            <div className="spinner-wrap-color">
                <LoadingSpinner />
            </div>
        </main>
    );
};
