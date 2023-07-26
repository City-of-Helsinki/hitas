import {IconAlertCircleFill} from "hds-react";
import {Dispatch, SetStateAction} from "react";
import {GenericActionModal} from "../../../common/components";
import {ErrorResponse} from "../../../common/schemas";

interface ComparisonResultModalProps {
    isOpen: boolean;
    setIsOpen: Dispatch<SetStateAction<boolean>>;
    response: ErrorResponse | object | undefined;
}

const ThirtyYearErrorModal = ({isOpen, setIsOpen, response}: ComparisonResultModalProps) => {
    if (!response) return <></>;
    const error = response as ErrorResponse;
    return (
        <GenericActionModal
            title={`Virhe ${error?.status ? error.status + ": " : ""}${error?.reason ? error?.reason : ""}!`}
            modalIcon={<IconAlertCircleFill />}
            isModalOpen={isOpen}
            closeModal={() => setIsOpen(false)}
            confirmButton={null}
            danger
        >
            {error?.message}
        </GenericActionModal>
    );
};

export default ThirtyYearErrorModal;
