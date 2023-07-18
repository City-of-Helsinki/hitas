import {Button, IconCrossCircleFill} from "hds-react";
import React from "react";

interface RemoveButtonProps {
    onClick: () => void;
    isLoading: boolean;
    buttonText?: string;
    disabled?: boolean;
    variant?: "primary" | "secondary" | "success" | "danger";
    className?: string;
    size?: "small" | "default";
    iconLeft?: React.ReactNode;
}

export default function RemoveButton({
    onClick,
    isLoading,
    disabled = false,
    buttonText,
    iconLeft,
    ...rest
}: RemoveButtonProps): React.JSX.Element {
    return (
        <Button
            iconLeft={iconLeft ?? <IconCrossCircleFill />}
            theme="black"
            onClick={onClick}
            isLoading={isLoading}
            disabled={disabled}
            {...rest}
        >
            {buttonText}
        </Button>
    );
}
