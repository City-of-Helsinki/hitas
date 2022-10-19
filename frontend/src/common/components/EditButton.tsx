import React from "react";

import {Button, IconPen} from "hds-react";
import {Link} from "react-router-dom";

interface EditButtonProps {
    state: object;
    pathname?: string;
    className?: string;
}

export default function EditButton({state, pathname = "edit", className}: EditButtonProps): JSX.Element {
    return (
        <Link
            to={{pathname: pathname}}
            state={state}
            className={className}
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
