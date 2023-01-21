import React from "react";

import {Button, IconCrossCircleFill} from "hds-react";

interface RemoveButtonProps {
    onClick: () => void;
    isLoading: boolean;
    disabled?: boolean;
}

export default function RemoveButton({onClick, isLoading, disabled = false}: RemoveButtonProps): JSX.Element {
    return (
        <Button
            iconLeft={<IconCrossCircleFill />}
            theme="black"
            onClick={onClick}
            isLoading={isLoading}
            disabled={disabled}
        >
            Poista
        </Button>
    );
}
