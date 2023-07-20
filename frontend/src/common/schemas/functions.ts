import {boolean, number, object, string, z} from "zod";
import {APIIdString} from "./common";
import {OwnerSchema} from "./owner";

// ********************************
// * Thirty Year Regulation
// ********************************

const ThirtyYearRegulationCompanySchema = object({
    id: string(),
    display_name: string(),
    price: number(),
    old_ruleset: boolean(),
    property_manager: object({
        email: string(),
        id: APIIdString,
        name: string(),
    }),
});

const ThirtyYearRegulationResponseSchema = object({
    automatically_released: ThirtyYearRegulationCompanySchema.array(),
    released_from_regulation: ThirtyYearRegulationCompanySchema.array(),
    stays_regulated: ThirtyYearRegulationCompanySchema.array(),
    skipped: ThirtyYearRegulationCompanySchema.array(),
    obfuscated_owners: OwnerSchema.array(),
});
export type IThirtyYearRegulationResponse = z.infer<typeof ThirtyYearRegulationResponseSchema>;

const ThirtyYearAvailablePostalCodeSchema = object({
    postal_code: string(),
    price_by_area: number(),
    cost_area: number(),
});

const ThirtyYearAvailablePostalCodesResponseSchema = ThirtyYearAvailablePostalCodeSchema.array();
export type IThirtyYearAvailablePostalCodesResponse = z.infer<typeof ThirtyYearAvailablePostalCodesResponseSchema>;

// ********************************
// * External Sales Data
// ********************************

const QuarterSchema = string().regex(/\d{4}Q\d/);
const ExternalSalesQuarterSchema = object({
    quarter: QuarterSchema,
    areas: object({
        postal_code: string().regex(/\d{3}/),
        sale_count: number(),
        price: number(),
    }).array(),
});

// ********************************
// * API
// ********************************

const ThirtyYearRegulationQuerySchema = object({
    calculationDate: string(),
    replacementPostalCodes: object({
        postalCode: string(),
        replacements: string().array(),
    })
        .array()
        .optional(),
});
export type IThirtyYearRegulationQuery = z.infer<typeof ThirtyYearRegulationQuerySchema>;

const ExternalSalesDataResponseSchema = object({
    calculation_quarter: QuarterSchema,
    quarter_1: ExternalSalesQuarterSchema,
    quarter_2: ExternalSalesQuarterSchema,
    quarter_3: ExternalSalesQuarterSchema,
    quarter_4: ExternalSalesQuarterSchema,
});
export type IExternalSalesDataResponse = z.infer<typeof ExternalSalesDataResponseSchema>;
