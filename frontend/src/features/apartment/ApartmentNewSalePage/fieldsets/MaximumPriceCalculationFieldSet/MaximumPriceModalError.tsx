import {FetchBaseQueryError} from "@reduxjs/toolkit/query";
import {Button, Dialog} from "hds-react";

const MaximumPriceModalError = ({error, closeModal}) => {
    const nonFieldError = error?.data?.message ?? "";
    const errorCode = error?.data?.error ?? "";
    return (
        <>
            <Dialog.Content>
                <p>Virhe: {(error as FetchBaseQueryError)?.status}</p>
                <p>
                    {nonFieldError} {errorCode ? `(${errorCode})` : ""}
                </p>
            </Dialog.Content>
            <Dialog.ActionButtons>
                <Button
                    onClick={closeModal}
                    variant="secondary"
                    theme="black"
                >
                    Sulje
                </Button>
            </Dialog.ActionButtons>
        </>
    );
};

export default MaximumPriceModalError;
