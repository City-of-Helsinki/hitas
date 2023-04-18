import {SerializedError} from "@reduxjs/toolkit";
import {FetchBaseQueryError} from "@reduxjs/toolkit/query";
import {LoadingSpinner} from "hds-react";

import {PageInfo} from "../schemas";

interface QueryLoadingProps {
    data:
        | {
              page: PageInfo;
              contents: unknown[];
          }
        | object
        | undefined;
    error: FetchBaseQueryError | SerializedError | undefined;
    isLoading: boolean;
    errorComponent?: JSX.Element;
    children: JSX.Element | JSX.Element[];
}

export default function QueryStateHandler({
    data,
    error,
    isLoading,
    errorComponent,
    children,
}: QueryLoadingProps): JSX.Element {
    // When loading or an error has occurred, show an appropriate message, otherwise return children
    const errorMessage = error ? (error as {error: string}).error : "";
    if (errorComponent === undefined) {
        errorComponent = (
            <p className="query-handler-error">
                Ladattaessa tapahtui virhe 😞
                {error !== undefined && <code className="query-error-message">{errorMessage as string}</code>}
            </p>
        );
    }

    if (error) {
        return errorComponent;
    } else if (isLoading) {
        return (
            <div className="spinner-wrap">
                <div className="spinner-container">
                    <LoadingSpinner />
                </div>
            </div>
        );
    } else if (data && (!("contents" in data) || data.contents.length)) {
        return <>{children}</>;
    } else {
        return <p>Ei tuloksia</p>;
    }
}
