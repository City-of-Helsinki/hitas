import {Button, IconCross} from "hds-react";
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
            iconLeft={<IconCross />}
            variant="secondary"
            theme="black"
            onClick={onClick}
            isLoading={isLoading}
            disabled={disabled}
        >
            Sulje
        </Button>
    );
}
