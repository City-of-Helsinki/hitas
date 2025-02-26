import {Button, ButtonPresetTheme, ButtonVariant, IconCross, LoadingSpinner} from "hds-react";
import React from "react";

interface CloseButtonProps {
    onClick?: (unknown) => unknown;
    isLoading?: boolean;
    disabled?: boolean;
}

export default function CloseButton({
    onClick,
    isLoading = false,
    disabled = false,
}: CloseButtonProps): React.JSX.Element {
    return (
        <Button
            iconStart={isLoading ? <LoadingSpinner small /> : <IconCross />}
            variant={ButtonVariant.Secondary}
            theme={ButtonPresetTheme.Black}
            onClick={onClick}
            disabled={disabled}
        >
            Sulje
        </Button>
    );
}
