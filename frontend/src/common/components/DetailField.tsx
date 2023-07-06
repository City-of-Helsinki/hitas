import React from "react";

interface DetailFieldProps {
    label: string;
    value: React.JSX.Element | string | number | null | undefined;
    horizontal?: boolean;
}

export default function DetailField({label, value, horizontal = false}: DetailFieldProps): React.JSX.Element {
    return (
        <div className={horizontal ? "detail-field-horizontal" : ""}>
            <label className="detail-field-label">{label}</label>
            <div className="detail-field-value">{value || "-"}</div>
        </div>
    );
}
