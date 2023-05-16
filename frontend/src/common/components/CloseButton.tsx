import {Button, IconCross} from "hds-react";

interface CloseButtonProps {
    onClick?: (unknown) => unknown;
    isLoading?: boolean;
    disabled?: boolean;
}

export default function CloseButton({onClick, isLoading = false, disabled = false}: CloseButtonProps): JSX.Element {
    return (
        <Button
            iconLeft={<IconCross />}
            theme="black"
            onClick={onClick}
            isLoading={isLoading}
            disabled={disabled}
        >
            Sulje
        </Button>
    );
}
