import React from "react";

import {Button, IconArrowLeft} from "hds-react";
import {useNavigate} from "react-router-dom";

export default function NavigateBackButton(): JSX.Element {
    const navigate = useNavigate();
    return (
        <Button
            iconLeft={<IconArrowLeft />}
            theme={"black"}
            variant={"secondary"}
            onClick={() => navigate(-1)}
            className={"back-button"}
        >
            Takaisin
        </Button>
    );
}
