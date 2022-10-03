import React from "react";

import {Button, IconPen} from "hds-react";
import {Link} from "react-router-dom";

interface EditButtonProps {
    state: object;
}

export default function EditButton({state}: EditButtonProps): JSX.Element {
    return (
        <Link
            to={{pathname: "edit"}}
            state={state}
        >
            <Button
                theme="black"
                size="small"
                iconLeft={<IconPen />}
            >
                Muokkaa
            </Button>
        </Link>
    );
}
