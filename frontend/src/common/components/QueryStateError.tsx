import {FetchBaseQueryError} from "@reduxjs/toolkit/query";
import {Accordion, AccordionSize, Dialog} from "hds-react";
import React from "react";
import {CloseButton} from "./index";

interface QueryStateErrorProps {
    open: boolean;
    close: () => void;
    attemptedAction: string | undefined;
    error: object | undefined;
}

export default function QueryStateError({
    open,
    close,
    attemptedAction,
    error,
}: QueryStateErrorProps): React.JSX.Element {
    const nonFieldError = ((error as FetchBaseQueryError)?.data as {message?: string})?.message || "";
    const errorFields = (error as {fields: []})?.fields || [];
    return (
        <Dialog
            className="query-handler-error"
            aria-labelledby="query-handler-error"
            id="query-handler-error"
            isOpen={open}
            close={close}
            closeButtonLabelText="Sulje virheilmoitus"
        >
            <Dialog.Header
                id="query-handler-error-header"
                title="Tallennusvirhe"
            />
            <Dialog.Content>
                Virhe rajapintakutsussa{attemptedAction ? ` (yritetty: ${attemptedAction})!` : "!"} 😞
                {nonFieldError !== "" && <code className="query-error-message">Non-field error: {nonFieldError}</code>}
                {errorFields.length > 0 && (
                    <Accordion
                        size={AccordionSize.Small}
                        heading="Virheelliset kentät"
                        className="query-error-fields"
                    >
                        <ul>
                            {errorFields.map((field: {field: string; message: string}, idx) => {
                                return (
                                    <li key={idx}>
                                        <span>{field.field}</span>: {field.message}
                                    </li>
                                );
                            })}
                        </ul>
                    </Accordion>
                )}
            </Dialog.Content>
            <Dialog.ActionButtons>
                <CloseButton onClick={close} />
            </Dialog.ActionButtons>
        </Dialog>
    );
}
