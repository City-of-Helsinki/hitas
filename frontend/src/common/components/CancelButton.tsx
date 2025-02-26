import {Button, ButtonPresetTheme, ButtonSize, ButtonVariant, LoadingSpinner} from "hds-react";

interface CancelButtonProps {
    onClick?: (unknown) => unknown;
    isLoading?: boolean;
    disabled?: boolean;
    buttonText?: string;
    size?: ButtonSize;
}

export default function CancelButton({
    onClick,
    isLoading = false,
    disabled = false,
    buttonText,
    size = ButtonSize.Medium,
}: CancelButtonProps) {
    return (
        <Button
            className="cancel-button"
            theme={ButtonPresetTheme.Black}
            variant={ButtonVariant.Secondary}
            iconStart={isLoading ? <LoadingSpinner small /> : undefined}
            size={size}
            onClick={onClick}
            disabled={disabled}
        >
            {buttonText ?? "Peruuta"}
        </Button>
    );
}
