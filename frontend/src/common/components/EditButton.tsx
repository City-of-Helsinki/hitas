import {Button, IconPen} from "hds-react";
import React from "react";
import {Link} from "react-router-dom";

interface EditButtonProps {
    pathname?: string;
    className?: string;
    disabled?: boolean;
}

export default function EditButton({
    pathname = "edit",
    className,
    disabled = false,
}: EditButtonProps): React.JSX.Element {
    return (
        <Link
            to={{pathname: pathname}}
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
