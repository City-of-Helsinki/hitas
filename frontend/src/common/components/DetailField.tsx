interface DetailFieldProps {
    label: string;
    value: JSX.Element | string | number | null | undefined;
}

export default function DetailField({label, value}: DetailFieldProps): JSX.Element {
    return (
        <>
            <label className="detail-field-label">{label}</label>
            <div className="detail-field-value">{value || "-"}</div>
        </>
    );
}
