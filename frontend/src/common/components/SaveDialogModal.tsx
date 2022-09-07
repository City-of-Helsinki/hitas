import React from "react";

import {SerializedError} from "@reduxjs/toolkit";
import {FetchBaseQueryError} from "@reduxjs/toolkit/query";
import {Button, Dialog, LoadingSpinner} from "hds-react";
import {Link, useNavigate} from "react-router-dom";

import {IApartmentDetails, IHousingCompanyDetails} from "../models";

interface SaveStateProps {
    data: IHousingCompanyDetails | IApartmentDetails | undefined;
    error: FetchBaseQueryError | SerializedError | undefined;
    isLoading: boolean;
    isVisible: boolean;
    setIsVisible;
}

export default function SaveDialogModal({
    data,
    error,
    isLoading,
    isVisible,
    setIsVisible,
}: SaveStateProps): JSX.Element {
    const navigate = useNavigate();
    const isHousingCompany = (data) => {
        return data && "name" in data;
    };
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
                    <Dialog.Content>
                        {`${
                            isHousingCompany(data)
                                ? (data as IHousingCompanyDetails).name.official
                                : (data as IApartmentDetails).address.stair +
                                  (data as IApartmentDetails).address.apartment_number
                        } tallennettu!`}
                    </Dialog.Content>
                    <Dialog.ActionButtons>
                        <Link to={isHousingCompany(data) ? `/housing-companies/${data.id}` : `/apartments/${data.id}`}>
                            <Button
                                variant="secondary"
                                theme={"black"}
                            >
                                {isHousingCompany(data) ? "Yhtiön" : "Asunnon"} sivulle
                            </Button>
                        </Link>
                        <Link to={isHousingCompany(data) ? `/housing-companies/` : `/apartments/`}>
                            <Button
                                variant="secondary"
                                theme={"black"}
                            >
                                Takaisin {isHousingCompany(data) ? "yhtiö" : "asunto"}listaukseen
                            </Button>
                        </Link>
                    </Dialog.ActionButtons>
                </>
            ) : (
                <>
                    <Dialog.Content>Virhe</Dialog.Content>
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
