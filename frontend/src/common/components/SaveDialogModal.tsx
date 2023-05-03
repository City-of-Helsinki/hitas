import {SerializedError} from "@reduxjs/toolkit";
import {FetchBaseQueryError} from "@reduxjs/toolkit/query";
import {Accordion, Button, Dialog} from "hds-react";
import {Link} from "react-router-dom";

import {
    IApartmentDetails,
    IBuilding,
    IExternalSalesDataResponse,
    IHousingCompanyDetails,
    IRealEstate,
} from "../schemas";
import {NavigateBackButton, QueryStateHandler} from "./index";

interface SaveStateProps {
    data: IHousingCompanyDetails | IApartmentDetails | IRealEstate | IBuilding | IExternalSalesDataResponse | undefined;
    error: FetchBaseQueryError | SerializedError | undefined;
    baseURL?: string;
    linkURL?: string;
    linkText?: string;
    isLoading: boolean;
    isVisible: boolean;
    setIsVisible;
    title?: string;
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
    const errorStatus = error?.data?.status + ":" ?? "";
    const errorFields = error?.data?.fields ?? [];
    const nonFieldError = ((error as FetchBaseQueryError)?.data as {message?: string})?.message || "";
    return (
        <Dialog.Content>
            <h3>
                {errorStatus} {nonFieldError}
            </h3>
            {errorFields.length > 1 ? (
                <Accordion
                    size="s"
                    heading="Virheelliset kentät"
                    closeButton={false}
                    initiallyOpen={true}
                >
                    <ul>
                        {errorFields.map((field, idx) => {
                            return (
                                <li key={idx}>
                                    <span>{field.field}</span>: {field.message}
                                </li>
                            );
                        })}
                    </ul>
                </Accordion>
            ) : (
                errorFields.length > 0 && (
                    <ul>
                        <li>
                            <span>{errorFields[0].field}</span>: {errorFields[0].message}
                        </li>
                    </ul>
                )
            )}
        </Dialog.Content>
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
    title,
}: SaveStateProps): JSX.Element {
    return (
        <Dialog
            id="save-modal"
            closeButtonLabelText="args.closeButtonLabelText"
            aria-labelledby="finish-modal"
            isOpen={isVisible}
            close={() => setIsVisible(false)}
            className={error && "error-modal"}
            boxShadow
        >
            <Dialog.Header
                id="save-modal__header"
                title={error ? "Virhe tallentaessa" : title ?? "Tallennetaan tietokantaan"}
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
            <Dialog.ActionButtons>
                <Button
                    onClick={() => setIsVisible(false)}
                    variant="secondary"
                    theme="black"
                >
                    Sulje
                </Button>
            </Dialog.ActionButtons>
        </Dialog>
    );
}
