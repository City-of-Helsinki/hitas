import {boolean, number, object, string, z} from "zod";

// ********************************
// * Improvement schemas
// ********************************

export const ImprovementSchema = object({
    name: string(),
    value: number(),
    completion_date: string(),
});
export const MarketPriceIndexImprovementSchema = ImprovementSchema.and(
    object({
        no_deductions: boolean(),
    })
);

export const ApartmentConstructionPriceIndexImprovementSchema = ImprovementSchema.and(
    object({
        depreciation_percentage: z.enum(["0.0", "2.5", "10.0"]),
    })
);
export type IApartmentConstructionPriceIndexImprovement = z.infer<
    typeof ApartmentConstructionPriceIndexImprovementSchema
>;

// ********************************
// * Improvement form schemas
// ********************************

export const ApartmentImprovementsFormSchema = z.object({
    market_price_index: MarketPriceIndexImprovementSchema.array(),
    construction_price_index: ApartmentConstructionPriceIndexImprovementSchema.array(),
});
export type IApartmentImprovementsForm = z.infer<typeof ApartmentImprovementsFormSchema>;

export const HousingCompanyImprovementsFormSchema = z.object({
    market_price_index: MarketPriceIndexImprovementSchema.array(),
    construction_price_index: ImprovementSchema.array(),
});
export type IHousingCompanyImprovementsForm = z.infer<typeof HousingCompanyImprovementsFormSchema>;
