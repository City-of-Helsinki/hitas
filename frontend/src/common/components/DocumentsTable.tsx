import {IApartmentDetails, IHousingCompanyDetails} from "../schemas";
import {formatDate} from "../utils";

interface DocumentsTableProps {
    parentObject: IApartmentDetails | IHousingCompanyDetails;
}

export default function DocumentsTable({parentObject}: DocumentsTableProps): React.JSX.Element {
    return (
        <table className="documents-table">
            <thead>
                <tr>
                    <th>Dokumentti</th>
                    <th>Tyyppi</th>
                    <th>Lisätty</th>
                    <th>Tallennettu viimeksi</th>
                    <th>&nbsp;</th>
                </tr>
            </thead>
            <tbody>
                {parentObject.documents
                    .toSorted((a, b) => a.display_name.localeCompare(b.display_name))
                    .map((document) => (
                        <tr key={document.id}>
                            <td>
                                <a
                                    href={document.file_link}
                                    target="_blank"
                                    rel="noreferrer"
                                >
                                    {document.display_name}
                                </a>
                            </td>
                            <td>{document.file_type_display}</td>
                            <td>{formatDate(document.created_at.split("T")[0])}</td>
                            <td>{formatDate(document.modified_at.split("T")[0])}</td>
                            <td>
                                <a
                                    className="document-table-link"
                                    href={document.file_link}
                                    target="_blank"
                                    rel="noreferrer"
                                >
                                    Avaa dokumentti
                                </a>
                            </td>
                        </tr>
                    ))}
            </tbody>
        </table>
    );
}
