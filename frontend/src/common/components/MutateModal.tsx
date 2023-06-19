import {Dialog} from "hds-react";
import React from "react";

interface IMutateModalProps<T> {
    defaultObject?: T;
    MutateFormComponent: React.FC<{
        defaultObject?: T;
        closeModalAction: () => void;
        setDefaultFilterParams?: () => void;
    }>;
    dialogTitles?: {modify?: string; new?: string};
    isVisible: boolean;
    closeModalAction: () => void;
    setDefaultFilterParams?: () => void;
}

export default function MutateModal<T>({
    defaultObject,
    MutateFormComponent,
    dialogTitles,
    isVisible,
    closeModalAction,
    setDefaultFilterParams,
}: IMutateModalProps<T>): React.ReactElement {
    return (
        <Dialog
            id="mutate-info-modal"
            closeButtonLabelText=""
            aria-labelledby=""
            isOpen={isVisible}
            close={closeModalAction}
            boxShadow
        >
            <Dialog.Header
                id="mutate-info-modal__header"
                title={defaultObject ? dialogTitles?.modify ?? "Muokkaa tietoja" : dialogTitles?.new ?? "Lisää uusi"}
            />
            <Dialog.Content>
                <MutateFormComponent
                    {...(defaultObject && {defaultObject: defaultObject})}
                    closeModalAction={closeModalAction}
                    setDefaultFilterParams={setDefaultFilterParams}
                />
            </Dialog.Content>
        </Dialog>
    );
}
