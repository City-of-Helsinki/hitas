import {Button, IconPen} from "hds-react";
import React from "react";
import {Link} from "react-router-dom";

interface EditButtonProps {
    state?: object;
    pathname?: string;
    className?: string;
    disabled?: boolean;
}

export default function EditButton({
    state,
    pathname = "edit",
    className,
    disabled = false,
}: EditButtonProps): React.JSX.Element {
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
                disabled={disabled}
            >
                Muokkaa
            </Button>
        </Link>
    );
}
