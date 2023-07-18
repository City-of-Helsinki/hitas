import {Dialog} from "hds-react";

import React from "react";
import {CloseButton} from "./index";

interface GenericActionModalProps {
    id?: string;
    title: string;
    modalIcon: React.ReactNode;
    isModalOpen: boolean;
    closeModal: () => void | null;
    confirmButton: React.ReactNode;
    danger?: boolean;
    children: React.ReactNode;
}

export default function GenericActionModal({
    id = "generic-action-modal",
    title,
    modalIcon,
    isModalOpen,
    closeModal,
    confirmButton,
    danger = false,
    children,
}: GenericActionModalProps): React.JSX.Element {
    // Simple wrapper for HDS Dialog component with some default props

    return (
        <Dialog
            id={id}
            aria-labelledby={`${id}__title`}
            variant={danger ? "danger" : "primary"}
            isOpen={isModalOpen}
            close={closeModal}
            closeButtonLabelText="Sulje"
            boxShadow
        >
            <Dialog.Header
                id={`${id}__title`}
                title={title}
                iconLeft={modalIcon}
            />
            <Dialog.Content id={`${id}__content`}>{children}</Dialog.Content>
            <Dialog.ActionButtons>
                <CloseButton onClick={closeModal} />
                {confirmButton}
            </Dialog.ActionButtons>
        </Dialog>
    );
}
