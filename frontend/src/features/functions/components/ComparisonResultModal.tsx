import {Dialog} from "hds-react";
import {Dispatch, SetStateAction} from "react";
import {CloseButton} from "../../../common/components";
import {ErrorResponse} from "../../../common/schemas";

interface ComparisonResultModalProps {
    isOpen: boolean;
    setIsOpen: Dispatch<SetStateAction<boolean>>;
    response: ErrorResponse | object | undefined;
}

export default function ComparisonResultModal({isOpen, setIsOpen, response}: ComparisonResultModalProps) {
    if (!response) return <></>;
    const error = response as ErrorResponse;
    return (
        <Dialog
            id="comparison-result-modal"
            aria-labelledby="comparison-result-modal"
            isOpen={isOpen}
            className="error-modal"
        >
            <Dialog.Header
                id="error-notification-modal-header"
                title={`Virhe ${error?.status ? error.status + ": " : ""}${error?.reason ? error?.reason : ""}!`}
            />
            <Dialog.Content>{error?.message}</Dialog.Content>
            <Dialog.ActionButtons>
                <CloseButton onClick={() => setIsOpen(false)} />
            </Dialog.ActionButtons>
        </Dialog>
    );
}
