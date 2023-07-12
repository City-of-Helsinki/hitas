import {Button, IconSaveDisketteFill} from "hds-react";
import React from "react";

type SaveButtonProps = {
    isLoading?: boolean;
    disabled?: boolean;
    buttonText?: string;
    size?: "small" | "default";
} & (
    | {
          type: "submit";
          onClick?: undefined;
      }
    | {
          type?: "button";
          onClick: (unknown) => unknown;
      }
);

export default function SaveButton({
    onClick,
    isLoading = false,
    disabled = false,
    type = "button",
    buttonText,
    size = "default",
}: SaveButtonProps): React.JSX.Element {
    return (
        <Button
            iconLeft={<IconSaveDisketteFill />}
            theme="black"
            onClick={
                type === "submit" // If the type is set (to "submit"), we don't want another onClick to happen here
                    ? () => {
                          return;
                      }
                    : onClick
            }
            isLoading={isLoading}
            disabled={disabled}
            type={type}
            size={size}
        >
            {buttonText ?? "Tallenna"}
        </Button>
    );
}
