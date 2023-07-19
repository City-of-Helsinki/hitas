import {Button, IconTrash} from "hds-react";
import React from "react";

interface DeleteButtonProps {
    onClick: () => void;
    isLoading?: boolean;
    buttonText?: string;
    disabled?: boolean;
    variant?: "primary" | "secondary" | "success" | "danger";
    className?: string;
    size?: "small" | "default";
    iconLeft?: React.ReactNode;
}

export default function DeleteButton({
    onClick,
    isLoading,
    disabled = false,
    buttonText = "Poista",
    iconLeft,
    className = "",
    ...rest
}: DeleteButtonProps): React.JSX.Element {
    return (
        <Button
            iconLeft={iconLeft ?? <IconTrash />}
            theme="black"
            onClick={onClick}
            isLoading={isLoading}
            disabled={disabled}
            className={`delete-button ${className}`}
            {...rest}
        >
            {buttonText}
        </Button>
    );
}
