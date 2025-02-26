import {Button, ButtonPresetTheme, ButtonSize, IconSaveDisketteFill, LoadingSpinner} from "hds-react";
import React from "react";

type SaveButtonProps = {
    isLoading?: boolean;
    disabled?: boolean;
    buttonText?: string;
    size?: ButtonSize;
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
    size = ButtonSize.Medium,
}: SaveButtonProps): React.JSX.Element {
    return (
        <Button
            iconStart={isLoading ? <LoadingSpinner small /> : <IconSaveDisketteFill />}
            theme={ButtonPresetTheme.Black}
            onClick={
                type === "submit" // If the type is set (to "submit"), we don't want another onClick to happen here
                    ? () => {
                          return;
                      }
                    : onClick
            }
            disabled={disabled}
            type={type}
            size={size}
        >
            {buttonText ?? "Tallenna"}
        </Button>
    );
}
