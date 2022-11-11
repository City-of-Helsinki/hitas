import React, {useState} from "react";

import {SerializedError} from "@reduxjs/toolkit";
import {FetchBaseQueryError} from "@reduxjs/toolkit/query";
import {Button, Dialog} from "hds-react";
import {Link} from "react-router-dom";

import RemoveButton from "./RemoveButton";
import {NavigateBackButton, QueryStateHandler} from "./index";

interface RemoveStateProps {
    data;
    error: FetchBaseQueryError | SerializedError | undefined;
    linkURL?: string;
    linkText?: string;
    buttonText?: string;
    isLoading: boolean;
    isVisible: boolean;
    setIsVisible;
    confirmAction;
    cancelAction;
}

const ActionSuccess = ({linkURL, linkText}) => {
    return (
        <>
            <Dialog.Content>Tiedot poistettu onnistuneesti!</Dialog.Content>
            <Dialog.ActionButtons>
                <>
                    <Link to={linkURL}>
                        <Button
                            variant="secondary"
                            theme="black"
                        >
                            {linkText}
                        </Button>
                    </Link>
                    <NavigateBackButton />
                </>
            </Dialog.ActionButtons>
        </>
    );
};

const ActionFailed = ({error, setIsVisible}) => {
    const nonFieldError = ((error as FetchBaseQueryError)?.data as {message?: string})?.message || "";
    return (
        <>
            <Dialog.Content>
                <p>Virhe: {(error as FetchBaseQueryError)?.status}</p>
                <p>{nonFieldError}</p>
            </Dialog.Content>
            <Dialog.ActionButtons>
                <Button
                    onClick={() => setIsVisible(false)}
                    variant="secondary"
                    theme="black"
                >
                    Sulje
                </Button>
            </Dialog.ActionButtons>
        </>
    );
};

export default function RemoveDialogModal({
    data,
    error,
    linkText,
    linkURL,
    isLoading,
    isVisible,
    setIsVisible,
    confirmAction,
    cancelAction,
}: RemoveStateProps): JSX.Element {
    const [isConfirmed, setIsConfirmed] = useState(false);
    return (
        <Dialog
            id="modification__end-modal"
            closeButtonLabelText="args.closeButtonLabelText"
            aria-labelledby="finish-modal"
            isOpen={isVisible}
            close={() => setIsVisible(false)}
            boxShadow
        >
            <Dialog.Header
                id="modification__end-modal__header"
                title="Poistetaan tietokannasta"
            />
            {isConfirmed ? (
                <QueryStateHandler
                    data={data}
                    error={error}
                    isLoading={isLoading}
                    errorComponent={
                        <ActionFailed
                            error={error}
                            setIsVisible={setIsVisible}
                        />
                    }
                >
                    <ActionSuccess
                        linkURL={linkURL}
                        linkText={linkText}
                    />
                </QueryStateHandler>
            ) : (
                <Dialog.Content>
                    <p>Haluatko varmasti poistaa asunnon?</p>
                    <div className="row row--buttons">
                        <Button
                            theme="black"
                            variant="secondary"
                            onClick={cancelAction}
                        >
                            Peruuta
                        </Button>
                        <RemoveButton
                            onClick={() => {
                                setIsConfirmed(true);
                                confirmAction();
                            }}
                            isLoading={isLoading}
                        />
                    </div>
                </Dialog.Content>
            )}
        </Dialog>
    );
}
