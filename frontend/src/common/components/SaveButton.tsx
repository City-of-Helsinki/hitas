import React from "react";

import {Button, IconSaveDisketteFill} from "hds-react";

interface SaveButtonProps {
    onClick: () => void;
    isLoading?: boolean;
    disabled?: boolean;
}

export default function SaveButton({onClick, isLoading = false, disabled = false}: SaveButtonProps): JSX.Element {
    return (
        <Button
            iconLeft={<IconSaveDisketteFill />}
            theme="black"
            onClick={onClick}
            isLoading={isLoading}
            disabled={disabled}
        >
            Tallenna
        </Button>
    );
}
