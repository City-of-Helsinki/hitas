import React from "react";

import {SerializedError} from "@reduxjs/toolkit";
import {FetchBaseQueryError} from "@reduxjs/toolkit/query";
import {Button, Dialog, LoadingSpinner} from "hds-react";
import {Link} from "react-router-dom";

import {IApartmentDetails, IBuilding, IHousingCompanyDetails, IRealEstate} from "../models";
import {NavigateBackButton} from "./index";

interface SaveStateProps {
    data: IHousingCompanyDetails | IApartmentDetails | IRealEstate | IBuilding | undefined;
    error: FetchBaseQueryError | SerializedError | undefined;
    baseURL?: string;
    linkURL?: string;
    linkText?: string;
    isLoading: boolean;
    isVisible: boolean;
    setIsVisible;
}

export default function SaveDialogModal({
    data,
    error,
    baseURL,
    linkText,
    linkURL,
    isLoading,
    isVisible,
    setIsVisible,
}: SaveStateProps): JSX.Element {
    return (
        <Dialog
            id="modification__end-modal"
            closeButtonLabelText={"args.closeButtonLabelText"}
            aria-labelledby={"finish-modal"}
            isOpen={isVisible}
            close={() => setIsVisible(false)}
            boxShadow={true}
        >
            <Dialog.Header
                id="modification__end-modal__header"
                title={`Tallennetaan tietokantaan`}
            />
            {isLoading ? (
                <LoadingSpinner />
            ) : !error && data ? (
                <>
                    <Dialog.Content>{`Tiedot tallennettu onnistuneesti!`}</Dialog.Content>
                    <Dialog.ActionButtons>
                        <>
                            <Link to={linkURL ? linkURL : (baseURL as string) + data?.id}>
                                <Button
                                    variant="secondary"
                                    theme={"black"}
                                >
                                    {linkText}
                                </Button>
                            </Link>
                            <Button
                                onClick={() => window.location.reload()}
                                variant="secondary"
                                theme={"black"}
                            >
                                Syötä uusi
                            </Button>
                            <NavigateBackButton />
                        </>
                    </Dialog.ActionButtons>
                </>
            ) : (
                <>
                    <Dialog.Content>
                        <p>Virhe: {(error as FetchBaseQueryError)?.status}</p>
                        <p>{((error as FetchBaseQueryError)?.data as {message?: string})?.message || ""}</p>
                    </Dialog.Content>
                    <Dialog.ActionButtons>
                        <Button
                            onClick={() => setIsVisible(false)}
                            variant="secondary"
                            theme={"black"}
                        >
                            Sulje
                        </Button>
                    </Dialog.ActionButtons>
                </>
            )}
        </Dialog>
    );
}
