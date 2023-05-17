import {Button} from "hds-react";

interface CancelButtonProps {
    onClick?: (unknown) => unknown;
    isLoading?: boolean;
    disabled?: boolean;
    buttonText?: string;
    size?: "small" | "default";
}

export default function CancelButton({
    onClick,
    isLoading = false,
    disabled = false,
    buttonText,
    size = "default",
}: CancelButtonProps): JSX.Element {
    return (
        <Button
            className="cancel-button"
            theme="black"
            variant="secondary"
            isLoading={isLoading}
            size={size}
            onClick={onClick}
        >
            {buttonText ?? "Peruuta"}
        </Button>
    );
}
