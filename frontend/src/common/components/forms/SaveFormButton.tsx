import {SaveButton} from "../index";

interface SaveFormButtonProps {
    formRef;
    buttonText?: string;
    isLoading?: boolean;
    disabled?: boolean;
}

const SaveFormButton = ({formRef, buttonText, isLoading, disabled}: SaveFormButtonProps) => {
    // Simple SaveButton which triggers a form submit event.

    const handleSaveButtonClick = () => {
        formRef.current && formRef.current.dispatchEvent(new Event("submit", {cancelable: true, bubbles: true}));
    };

    return (
        <SaveButton
            onClick={handleSaveButtonClick}
            buttonText={buttonText}
            isLoading={isLoading}
            disabled={disabled}
        />
    );
};

export default SaveFormButton;
