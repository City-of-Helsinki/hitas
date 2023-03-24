interface DetailFieldProps {
    label: string;
    value: JSX.Element | string | number | null | undefined;
    horizontal?: boolean;
}

export default function DetailField({label, value, horizontal = false}: DetailFieldProps): JSX.Element {
    return (
        <div className={horizontal ? "detail-field-horizontal" : ""}>
            <label className="detail-field-label">{label}</label>
            <div className="detail-field-value">{value || "-"}</div>
        </div>
    );
}
