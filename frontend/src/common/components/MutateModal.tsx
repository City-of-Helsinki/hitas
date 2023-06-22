import {Dialog} from "hds-react";
import React from "react";
import MutateForm from "./MutateForm";

interface IMutateModalProps<TDefaultObject, TFormFieldsWithTitles extends object> {
    defaultObject?: TDefaultObject;
    MutateFormComponent;
    dialogTitles?: {modify?: string; new?: string};
    isVisible: boolean;
    closeModalAction: () => void;
    setEmptyFilterParams?: () => void;
    formObjectSchema?;
    useSaveMutation?;
    successMessage?: string;
    errorMessage?: string;
    notModifiedMessage?: string;
    defaultFocusFieldName?: string;
    formFieldsWithTitles?: TFormFieldsWithTitles;
    requiredFields?: string[];
}

// Opens a modal for adding or modifying data defined by the MutateFormComponent prop
export default function MutateModal<TDefaultObject, TFormFieldsWithTitles extends object>({
    defaultObject,
    MutateFormComponent,
    dialogTitles,
    isVisible,
    closeModalAction,
    setEmptyFilterParams,
    formObjectSchema,
    useSaveMutation,
    successMessage,
    errorMessage,
    notModifiedMessage,
    defaultFocusFieldName,
    formFieldsWithTitles,
    requiredFields,
}: IMutateModalProps<TDefaultObject, TFormFieldsWithTitles>): React.ReactElement {
    // generic MutateForm component -specific props
    const mutateFormProps = {
        formObjectSchema,
        useSaveMutation,
        successMessage,
        errorMessage,
        notModifiedMessage,
        defaultFocusFieldName,
        formFieldsWithTitles,
        requiredFields,
    };

    // check if the MutateFormComponent is MutateForm
    const isMutateForm = (<MutateForm />).type === (<MutateFormComponent />).type;

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
