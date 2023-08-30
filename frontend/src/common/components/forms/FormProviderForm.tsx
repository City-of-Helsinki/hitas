import React from "react";
import {FormProvider, UseFormReturn} from "react-hook-form";

interface FormProviderFormProps {
    // eslint-disable-next-line
    formObject: UseFormReturn<any, any, undefined>;
    formRef?;
    onSubmit;
    onSubmitError?;
    className?;
    children: React.ReactNode;
}
const FormProviderForm = ({
    formObject,
    formRef,
    onSubmit,
    onSubmitError,
    className,
    children,
}: FormProviderFormProps): React.JSX.Element => {
    // General purpose form component that wraps the form with FormProvider

    if (onSubmitError === undefined) {
        // eslint-disable-next-line no-console
        onSubmitError = (errors) => console.warn(formObject.getValues(), errors);
    }

    const {handleSubmit} = formObject;

    return (
        <FormProvider {...formObject}>
            <form
                ref={formRef}
                className={className}
                onSubmit={(event: React.FormEvent<HTMLFormElement>) => {
                    // Don't trigger submit of parent form, when using nested forms
                    event.stopPropagation();

                    handleSubmit(onSubmit, onSubmitError)(event);
                }}
            >
                {children}
            </form>
        </FormProvider>
    );
};

export default FormProviderForm;
