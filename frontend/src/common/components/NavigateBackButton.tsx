import {Button, ButtonPresetTheme, ButtonVariant, IconArrowLeft} from "hds-react";
import React from "react";
import {useNavigate} from "react-router-dom";

export default function NavigateBackButton({disabled = false}: {disabled?: boolean}): React.JSX.Element {
    const navigate = useNavigate();
    return (
        <Button
            iconStart={<IconArrowLeft />}
            theme={ButtonPresetTheme.Black}
            variant={ButtonVariant.Secondary}
            className="back-button"
            onClick={() => navigate(-1)}
            disabled={disabled}
        >
            Takaisin
        </Button>
    );
}
