import React from "react";

import {SerializedError} from "@reduxjs/toolkit";
import {FetchBaseQueryError} from "@reduxjs/toolkit/query";
import {LoadingSpinner} from "hds-react";

import {PageInfo} from "../models";

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
    children: JSX.Element | JSX.Element[];
}

export default function QueryStateHandler({data, error, isLoading, children}: QueryLoadingProps): JSX.Element {
    // When loading or an error has occurred, show an appropriate message, otherwise return children

    return error ? (
        <p>Virhe</p>
    ) : isLoading ? (
        <LoadingSpinner />
    ) : data && (!("contents" in data) || data.contents.length) ? (
        <>{children}</>
    ) : (
        <p>Ei tuloksia</p>
    );
}
