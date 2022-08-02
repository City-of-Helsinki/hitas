interface IDetailField {
    label: string;
    value: string | number | null | undefined;
}

export default function DetailField({label, value}: IDetailField) {
    return (
        <>
            <label className="detail-field-label">{label}</label>
            <div className="detail-field-value">{value || "-"}</div>
        </>
    );
}
