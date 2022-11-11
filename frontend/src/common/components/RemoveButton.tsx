import React from "react";

import {Button, IconCrossCircleFill} from "hds-react";

interface RemoveButtonProps {
    onClick: () => void;
    isLoading: boolean;
}

export default function RemoveButton({onClick, isLoading}: RemoveButtonProps): JSX.Element {
    return (
        <Button
            iconLeft={<IconCrossCircleFill />}
            theme="black"
            onClick={onClick}
            isLoading={isLoading}
        >
            Poista
        </Button>
    );
}
