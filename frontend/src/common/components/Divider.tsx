import React from "react";

export default function Divider({size = "s"}: {size: "s" | "m" | "l" | "xl"}): React.JSX.Element {
    return <div className={`divider-horizontal divider-horizontal-${size}`} />;
}
