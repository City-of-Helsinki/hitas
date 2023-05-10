import {Button, IconSaveDisketteFill} from "hds-react";

interface SaveButtonProps {
    onClick?: (unknown) => unknown;
    isLoading?: boolean;
    disabled?: boolean;
    type?: "submit";
    buttonText?: string;
    size?: "small" | "default";
}

export default function SaveButton({
    onClick,
    isLoading = false,
    disabled = false,
    type,
    buttonText,
    size = "default",
}: SaveButtonProps): JSX.Element {
    return (
        <Button
            iconLeft={<IconSaveDisketteFill />}
            theme="black"
            onClick={
                type // If the type is set (to "submit"), we don't want another onClick to happen here
                    ? () => {
                          return;
                      }
                    : onClick
            }
            isLoading={isLoading}
            disabled={disabled}
            type={type || "button"}
            size={size}
        >
            {buttonText ?? "Tallenna"}
        </Button>
    );
}
