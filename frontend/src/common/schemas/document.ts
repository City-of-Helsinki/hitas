import {object, string, z} from "zod";
import {APIIdString} from "./common";

// ********************************
// * Document schemas
// ********************************

export const DocumentSchema = object({
    id: APIIdString.optional(),
    display_name: string(),
    file_type_display: string(),
    file_link: string(),
    created_at: string(),
    modified_at: string(),
});
export type IDocument = z.infer<typeof DocumentSchema>;

export const WritableDocumentSchema = object({
    id: APIIdString.optional(),
    display_name: string(),
    file_object: z.custom<File>().optional(),
});
export type IDocumentWritable = z.infer<typeof WritableDocumentSchema>;

// ********************************
// * Document form schemas
// ********************************

export const ApartmentDocumentsFormSchema = z.object({
    documents: WritableDocumentSchema.array(),
    removedDocumentIds: APIIdString.array(),
});
export type IApartmentDocumentsForm = z.infer<typeof ApartmentDocumentsFormSchema>;

export const HousingCompanyDocumentsFormSchema = z.object({
    documents: WritableDocumentSchema.array(),
    removedDocumentIds: APIIdString.array(),
});
export type IHousingCompanyDocumentsForm = z.infer<typeof HousingCompanyDocumentsFormSchema>;
