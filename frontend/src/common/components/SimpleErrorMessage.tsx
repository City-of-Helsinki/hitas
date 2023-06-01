import {IconAlertCircleFill} from "hds-react";

export default function SimpleErrorMessage({errorMessage, ...rest}: {errorMessage?: string}) {
    if (errorMessage) {
        return (
            <p
                className="error-text"
                {...rest}
            >
                <IconAlertCircleFill />
                {errorMessage}
            </p>
        );
    }
    return null;
}
