import React from "react";

import {SerializedError} from "@reduxjs/toolkit";
import {FetchBaseQueryError} from "@reduxjs/toolkit/query";
import {Button, Dialog, LoadingSpinner} from "hds-react";
import {Link, useNavigate} from "react-router-dom";

import {IApartmentDetails, IBuilding, IHousingCompanyDetails, IRealEstate} from "../models";

interface SaveStateProps {
    data: IHousingCompanyDetails | IApartmentDetails | IRealEstate | IBuilding | undefined;
    error: FetchBaseQueryError | SerializedError | undefined;
    baseURL: string;
    itemName: string;
    isLoading: boolean;
    isVisible: boolean;
    setIsVisible;
}

export default function SaveDialogModal({
    data,
    error,
    baseURL,
    itemName,
    isLoading,
    isVisible,
    setIsVisible,
}: SaveStateProps): JSX.Element {
    const navigate = useNavigate();
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
                    <Dialog.Content>{`${itemName} tiedot tallennettu!`}</Dialog.Content>
                    <Dialog.ActionButtons>
                        <Link to={baseURL + data.id}>
                            <Button
                                variant="secondary"
                                theme={"black"}
                            >
                                {itemName} sivulle
                            </Button>
                        </Link>
                        <Button
                            onClick={() => navigate(-1)}
                            variant="secondary"
                            theme={"black"}
                        >
                            Palaa edelliselle sivulle
                        </Button>
                    </Dialog.ActionButtons>
                </>
            ) : (
                <>
                    <Dialog.Content>
                        <>{`Virhe: ${(error as FetchBaseQueryError)?.status}`}</>
                    </Dialog.Content>
                    <Dialog.ActionButtons>
                        <Button
                            onClick={() => navigate(-1)}
                            variant="secondary"
                            theme={"black"}
                        >
                            Palaa edelliselle sivulle
                        </Button>
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
