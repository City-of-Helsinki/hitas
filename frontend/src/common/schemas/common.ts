import {number, object, string, z} from "zod";
import {CostAreas} from "./enums";

// ********************************
// * Error messages
// ********************************

export const errorMessages = {
    required: "Pakollinen kenttä",
    postalCodeFormat: "Virheellinen postinumero",
    stringLength: "Liian lyhyt arvo",
    stringMin: "Liian lyhyt arvo",
    stringMax: "Liian monta merkkiä",
    stringMaxIs: "Maksimimerkkimäärä on ",
    numberLength: "Liian lyhyt arvo",
    numberType: "Arvon pitää olla numero",
    numberMin: "Liian pieni arvo",
    numberMax: "Liian suuri arvo",
    numberPositive: "Arvon täytyy olla positiivinen luku",
    dateFormat: "Virheellinen päivämäärä",
    dateMin: "Liian aikainen päivämäärä",
    dateMax: "Liian myöhäinen päivämäärä",
    noOwnerships: "Asunnolla täytyy olla omistaja",
    ownershipPercent: "Asunnon omistajuusprosentin tulee olla yhteensä 100%",
    ownershipDuplicate: "Samaa henkilöä ei voi valita useaan kertaan",
    priceMin: "Kauppahinta ei saa olla tyhjä",
    priceMax: "Kauppahinta ei saa ylittää 999 999 €",
    loanShareMin: "Lainaosuus ei voi olla alle 0 €",
    emailInvalid: "Virheellinen sähköpostiosoite",
    urlInvalid: "Virheellinen www-osoite",
    APIIdMin: "Rajapinnan palauttamassa ID-arvossa liian vähän merkkejä",
    APIIdMax: "Rajapinnan palauttamassa ID-arvossa on liian monta merkkiä",
    overMaxPrice: "Kauppahinta ylittää enimmäishinnan",
    priceHigherThanUnconfirmedMaxPrice: "Velaton kauppahinta ylittää rajaneliöhinnan.",
    loanShareChanged: "Lainaosuus muuttunut laskelmasta",
    loanShareChangedCatalog: "Lainaosuus muuttunut myyntihintaluettelon tiedoista",
    catalogOverMaxPrice: "Kauppahinta ylittää myyntihintaluettelon hinnan",
    catalogUnderMaxPrice: "Kauppahinta alittaa myyntihintaluettelon hinnan",
    catalogPricesMissing: "Myyntihintaluettelon hinnat puuttuvat",
    sharesEmpty: "Toinen osakekenttä on tyhjä",
    sharesStartGreaterThanEnd: "Osakkeiden lopun on oltava suurempi kuin alun",
    constructionInterestEmpty: "Toinen korkokenttä on tyhjä",
    constructionInterest6GreaterThan14: "14% koron on oltava suurempi kuin 6% koron",
    maxTwoDecimalPlaces: "Anna arvo enintän kahden desimaalin tarkkuudella",
    noDecimalPlaces: "Anna arvo kokonaislukuna",
};

const customErrorMap: z.ZodErrorMap = (issue, ctx) => {
    let returnValue = {message: ctx.defaultError};
    if (issue.code === z.ZodIssueCode.invalid_type) {
        if (issue.expected === "number") {
            returnValue = {message: errorMessages.numberType};
        }
    }
    if (issue.code === z.ZodIssueCode.too_small || issue.code === z.ZodIssueCode.too_big) {
        const isMin = issue.code === z.ZodIssueCode.too_small;
        if (issue.type !== "set" && issue.type !== "array") {
            returnValue = {
                message: `${errorMessages[`${issue.type + isMin ? "Min" : "Max"}`]} (${
                    isMin ? `min ${issue.minimum}` : `max ${issue.maximum}`
                })`,
            };
        }
    }
    if (issue.code === z.ZodIssueCode.invalid_string) {
        if (issue.validation !== "uuid") {
            returnValue = {message: errorMessages[`${issue.validation}Invalid`]};
        }
    }
    if (issue.code === z.ZodIssueCode.invalid_date) {
        returnValue = {message: errorMessages.dateFormat};
    }
    return returnValue;
};

z.setErrorMap(customErrorMap);

// ********************************
// * Field schemas
// ********************************

export const APIIdString = string().min(32, errorMessages.APIIdMin).max(32, errorMessages.APIIdMax);

export const nullishNumber = number({
    invalid_type_error: errorMessages.numberType,
    required_error: errorMessages.required,
})
    .nonnegative(errorMessages.numberPositive)
    .nullish();

export const nullishDecimal = number({
    invalid_type_error: errorMessages.numberType,
    required_error: errorMessages.required,
})
    .multipleOf(0.01, errorMessages.maxTwoDecimalPlaces)
    .nonnegative(errorMessages.numberPositive)
    .nullish();

export const nullishPositiveNumber = number({
    invalid_type_error: errorMessages.numberType,
    required_error: errorMessages.required,
})
    .positive(errorMessages.numberPositive)
    .nullish();

export const writableRequiredNumber = number({
    invalid_type_error: errorMessages.required,
    required_error: errorMessages.required,
})
    .nonnegative(errorMessages.numberPositive)
    .optional(); // allow undefined but no null

export const APIDateSchema = string({required_error: errorMessages.required}).regex(
    /^\d{4}-\d{2}-\d{2}$/,
    errorMessages.dateFormat
);

// ********************************
// * Basic common schemas
// ********************************

export const CodeSchema = object({
    id: APIIdString,
    value: string(),
    description: string().nullable(),
});
export type ICode = z.infer<typeof CodeSchema>;

export const PostalCodeSchema = object({
    value: string(),
    city: string(),
    cost_area: z.enum(CostAreas),
});
export type IPostalCode = z.infer<typeof PostalCodeSchema>;

export const AddressSchema = object({
    street_address: string({required_error: errorMessages.required}).min(2, errorMessages.stringLength),
    postal_code: z
        .number({invalid_type_error: errorMessages.numberType, required_error: errorMessages.required})
        .refine((val) => val.toString().match(/^\d{5}$/), errorMessages.postalCodeFormat)
        .or(string().length(5)),
    city: string().min(2, errorMessages.stringLength).optional(), // Read only
});
export type IAddress = z.infer<typeof AddressSchema>;

export const UserInfoSchema = object({
    first_name: string(),
    last_name: string(),
    email: string(),
});
export type IUserInfoResponse = z.infer<typeof UserInfoSchema>;

// ********************************
// * Request / Response schemas
// ********************************

// General

export const PageInfoSchema = object({
    size: number(),
    total_items: number(),
    current_page: number(),
    total_pages: number(),
    links: object({
        next: string().nullable(),
        previous: string().nullable(),
    }),
});
export type PageInfo = z.infer<typeof PageInfoSchema>;

// Error

const ErrorResponseSchema = object({
    error: string(),
    status: number(),
    reason: string(),
    message: string(),
    fields: object({
        field: string(),
        message: string(),
    })
        .array()
        .optional(),
    data: object({
        status: number(),
        data: object({
            error: string(),
            message: string(),
            reason: string(),
            status: number(),
        }),
    }).optional(),
});
export type ErrorResponse = z.infer<typeof ErrorResponseSchema>;

// List responses

export const CodeResponseSchema = object({
    page: PageInfoSchema,
    contents: CodeSchema.array(),
});
export type ICodeResponse = z.infer<typeof CodeResponseSchema>;

export const PostalCodeResponseSchema = object({
    page: PageInfoSchema,
    contents: PostalCodeSchema.array(),
});
export type IPostalCodeResponse = z.infer<typeof PostalCodeResponseSchema>;
