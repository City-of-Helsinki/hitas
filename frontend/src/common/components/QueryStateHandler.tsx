import {SerializedError} from "@reduxjs/toolkit";
import {FetchBaseQueryError} from "@reduxjs/toolkit/query";
import {LoadingSpinner} from "hds-react";

import {useState} from "react";
import {PageInfo} from "../schemas";
import {QueryStateError} from "./index";

interface QueryLoadingProps {
    data:
        | {
              page: PageInfo;
              contents: unknown[];
          }
        | object
        | undefined;
    error: FetchBaseQueryError | SerializedError | object | undefined;
    isLoading: boolean;
    errorComponent?: JSX.Element;
    children: JSX.Element | JSX.Element[];
    attemptedAction?: string;
}

export default function QueryStateHandler({
    data,
    error,
    isLoading,
    attemptedAction,
    errorComponent,
    children,
}: QueryLoadingProps): JSX.Element {
    // When loading or an error has occurred, show an appropriate message, otherwise return children
    const [isErrorModalOpen, setIsErrorModalOpen] = useState(error !== undefined);
    if (error) {
        return (
            errorComponent ?? (
                <QueryStateError
                    open={isErrorModalOpen}
                    close={() => setIsErrorModalOpen(false)}
                    attemptedAction={attemptedAction}
                    error={error}
                />
            )
        );
    } else if (isLoading) {
        return (
            <div className="spinner-wrap">
                <LoadingSpinner />
            </div>
        );
    } else if (data && (!("contents" in data) || data.contents.length)) {
        return <>{children}</>;
    } else {
        console.warn(`${attemptedAction ? attemptedAction + ": " : ""}Ei tuloksia!`);
        return <></>;
    }
}
