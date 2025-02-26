import {Button, ButtonPresetTheme, ButtonSize, ButtonVariant, IconTrash, LoadingSpinner} from "hds-react";
import React from "react";

interface DeleteButtonProps {
    onClick: () => void;
    isLoading?: boolean;
    buttonText?: string;
    disabled?: boolean;
    variant?: ButtonVariant;
    className?: string;
    size?: ButtonSize;
    iconStart?: React.ReactNode;
    iconEnd?: React.ReactNode;
}

export default function DeleteButton({
    onClick,
    isLoading,
    disabled = false,
    buttonText = "Poista",
    iconStart,
    className = "",
    variant = ButtonVariant.Primary,
    ...rest
}: DeleteButtonProps): React.JSX.Element {
    return (
        <Button
            iconStart={isLoading ? <LoadingSpinner small /> : iconStart ?? <IconTrash />}
            theme={ButtonPresetTheme.Black}
            onClick={onClick}
            disabled={disabled}
            className={`delete-button ${className}`}
            variant={variant}
            {...rest}
        >
            {buttonText}
        </Button>
    );
}
