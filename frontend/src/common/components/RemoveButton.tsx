import {Button, IconCrossCircleFill} from "hds-react";

interface RemoveButtonProps {
    onClick: () => void;
    isLoading: boolean;
    buttonText?: string;
    disabled?: boolean;
}

export default function RemoveButton({
    onClick,
    isLoading,
    disabled = false,
    buttonText = "Poista",
}: RemoveButtonProps): JSX.Element {
    return (
        <Button
            iconLeft={<IconCrossCircleFill />}
            theme="black"
            onClick={onClick}
            isLoading={isLoading}
            disabled={disabled}
        >
            {buttonText}
        </Button>
    );
}
