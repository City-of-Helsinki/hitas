import {SerializedError} from "@reduxjs/toolkit";
import {FetchBaseQueryError} from "@reduxjs/toolkit/query";
import {Button, Dialog} from "hds-react";
import {Link} from "react-router-dom";

import {IApartmentDetails, IBuilding, IHousingCompanyDetails, IRealEstate} from "../schemas";
import {NavigateBackButton, QueryStateHandler} from "./index";

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

const ActionSuccess = ({linkURL, linkText, baseURL, data}) => {
    return (
        <>
            <Dialog.Content>Tiedot tallennettu onnistuneesti!</Dialog.Content>
            <Dialog.ActionButtons>
                <>
                    <Link to={linkURL || baseURL + data.id}>
                        <Button
                            variant="secondary"
                            theme="black"
                        >
                            {linkText}
                        </Button>
                    </Link>
                    <Button
                        onClick={() => window.location.reload()}
                        variant="secondary"
                        theme="black"
                    >
                        Syötä uusi
                    </Button>
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
            closeButtonLabelText="args.closeButtonLabelText"
            aria-labelledby="finish-modal"
            isOpen={isVisible}
            close={() => setIsVisible(false)}
            boxShadow
        >
            <Dialog.Header
                id="modification__end-modal__header"
                title="Tallennetaan tietokantaan"
            />
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
                    baseURL={baseURL}
                    data={data}
                />
            </QueryStateHandler>
        </Dialog>
    );
}
