import React from "react";

import {Button, IconArrowLeft} from "hds-react";
import {useNavigate} from "react-router-dom";

export default function NavigateBackButton({disabled = false}: {disabled?: boolean}): JSX.Element {
    const navigate = useNavigate();
    return (
        <Button
            iconLeft={<IconArrowLeft />}
            theme="black"
            variant="secondary"
            className="back-button"
            onClick={() => navigate(-1)}
            disabled={disabled}
        >
            Takaisin
        </Button>
    );
}
