import {Dialog} from "hds-react";
import {CloseButton} from "../../../common/components";

export default function ComparisonResultModal({isOpen, setIsOpen, error}) {
    if (!error) {
        return null;
    }
    return (
        <Dialog
            id="error-notification-modal"
            aria-labelledby="error-notification-modal"
            isOpen={isOpen}
        >
            <Dialog.Header
                id="error-notification-modal-header"
                title={`Virhe ${error?.data?.status && error.status + ": "}${error?.reason}!`}
            />
            <Dialog.Content>
                <ul>
                    {error?.fields?.map((error, idx) => {
                        <li key={idx}>
                            <span>{error.field}</span>: {error.message}
                        </li>;
                    })}
                </ul>
            </Dialog.Content>
            <Dialog.ActionButtons>
                <CloseButton onClick={() => setIsOpen(false)} />
            </Dialog.ActionButtons>
        </Dialog>
    );
}
