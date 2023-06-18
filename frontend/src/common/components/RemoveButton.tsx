import {Button, IconCrossCircleFill} from "hds-react";

interface RemoveButtonProps {
    onClick: () => void;
    isLoading: boolean;
    buttonText?: string;
    disabled?: boolean;
    variant?: "primary" | "secondary" | "success" | "danger";
    className?: string;
    size?: "small" | "default";
}

export default function RemoveButton({
    onClick,
    isLoading,
    disabled = false,
    buttonText,
    ...rest
}: RemoveButtonProps): JSX.Element {
    return (
        <Button
            iconLeft={<IconCrossCircleFill />}
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
