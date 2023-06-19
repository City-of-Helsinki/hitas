import {SerializedError} from "@reduxjs/toolkit";
import {FetchBaseQueryError} from "@reduxjs/toolkit/query";
import {Button, Dialog} from "hds-react";
import {Link} from "react-router-dom";

import React, {ReactNode} from "react";
import {NavigateBackButton, QueryStateHandler} from "./index";

interface ConfirmDialogModalProps {
    data?;
    modalText?: string | ReactNode;
    modalHeader?: string;
    successText?: string;
    error?: FetchBaseQueryError | SerializedError | undefined;
    linkURL?: string;
    linkText?: string;
    buttonText?: string;
    isLoading?: boolean;
    isVisible?: boolean;
    setIsVisible?;
    confirmAction?;
    cancelAction?;
    children?: React.ReactNode;
    className?: string;
}

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

const ActionSuccess = ({successText, linkURL, linkText}) => {
    return (
        <>
            <Dialog.Content>{successText}</Dialog.Content>
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

const ConfirmDialogModal = ({
    data,
    modalHeader = "Vahvista toiminto",
    modalText,
    successText,
    linkURL,
    linkText,
    buttonText,
    error,
    isLoading,
    isVisible,
    setIsVisible,
    confirmAction,
    cancelAction,
    className,
    children,
}: ConfirmDialogModalProps) => {
    const DefaultDialogContent = () => (
        <>
            <Dialog.Content>
                <p>{modalText}</p>
                <div className="row row--buttons">
                    <Button
                        theme="black"
                        variant="secondary"
                        onClick={cancelAction}
                    >
                        Peruuta
                    </Button>
                    <Button
                        theme="black"
                        onClick={() => {
                            confirmAction();
                        }}
                    >
                        {buttonText}
                    </Button>
                </div>
            </Dialog.Content>
        </>
    );
    return (
        <Dialog
            id="confirmation-modal"
            closeButtonLabelText="args.closeButtonLabelText"
            aria-labelledby="confirm-modal"
            isOpen={isVisible || false}
            close={() => setIsVisible(false)}
            className={error ? "error-modal " + className : className}
            boxShadow
        >
            <Dialog.Header
                id="confirmation-modal__header"
                title={modalHeader}
            />
            {error ? (
                <QueryStateHandler
                    data={data}
                    error={error}
                    isLoading={isLoading || false}
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
                        successText={successText}
                    />
                </QueryStateHandler>
            ) : (
                children ?? <DefaultDialogContent />
            )}
        </Dialog>
    );
};

export default ConfirmDialogModal;
