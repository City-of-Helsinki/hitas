import {Dialog} from "hds-react";
import React from "react";
import {IMutateFormProps, MutateForm} from "./index";

interface IMutateModalProps<TDefaultObject, TFormFieldsWithTitles extends object> {
    defaultObject?: TDefaultObject;
    dialogTitles?: {modify?: string; new?: string};
    isVisible: boolean;
    closeModalAction: () => void;
    setEmptyFilterParams?: () => void;
    MutateFormComponent;
    mutateFormProps?: IMutateFormProps<TFormFieldsWithTitles>;
}

// Opens a modal for adding or modifying data defined by the MutateFormComponent prop
export default function MutateModal<TDefaultObject, TFormFieldsWithTitles extends object>({
    defaultObject,
    MutateFormComponent,
    dialogTitles,
    isVisible,
    closeModalAction,
    setEmptyFilterParams,
    mutateFormProps,
}: IMutateModalProps<TDefaultObject, TFormFieldsWithTitles>): React.ReactElement {
    // check if the MutateFormComponent is MutateForm
    const isMutateForm =
        !!mutateFormProps && (<MutateForm {...mutateFormProps} />).type === (<MutateFormComponent />).type;

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
                    {...(defaultObject && {defaultObject})}
                    closeModalAction={closeModalAction}
                    {...(setEmptyFilterParams && {setEmptyFilterParams})}
                    {...(isMutateForm && mutateFormProps)}
                />
            </Dialog.Content>
        </Dialog>
    );
}
