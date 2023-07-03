import {createContext} from "react";
import {z, ZodSchema} from "zod";
import {
    ApartmentSaleFormSchema,
    ApartmentSaleSchema,
    errorMessages,
    IApartmentDetails,
    indexNames,
} from "../../../common/schemas";

export interface ISalesPageMaximumPrices {
    maximumPrice: number | null;
    debtFreePurchasePrice: number | null;
    apartmentShareOfHousingCompanyLoans: number | null;
    index: (typeof indexNames)[number] | "";
}

export const ApartmentSaleContext = createContext<{
    apartment: IApartmentDetails;
    formExtraFieldErrorMessages?;
    setMaximumPrices: React.Dispatch<React.SetStateAction<ISalesPageMaximumPrices>>;
}>({
    apartment: undefined as unknown as IApartmentDetails,
    setMaximumPrices: undefined as unknown as React.Dispatch<React.SetStateAction<ISalesPageMaximumPrices>>,
});

export const isApartmentMaxPriceCalculationValid = (apartment, purchaseDate: string | undefined | null) => {
    if (apartment.prices.maximum_prices.confirmed) {
        const comparisonDate = purchaseDate ? new Date(purchaseDate) : new Date();
        const calculationDate = new Date(apartment.prices.maximum_prices.confirmed.calculation_date);
        const validUntil = new Date(apartment.prices.maximum_prices.confirmed.valid.valid_until);
        return calculationDate <= comparisonDate && comparisonDate <= validUntil;
    }
    return false;
};

export const getRefinedApartmentSaleFormSchema = (apartment, maximumPrices, warningsGiven) => {
    // superRefine does not run if the schema validation fails early.
    // Use as simple as possible schemas for the form to allow superRefine to always run.

    const ApartmentFirstSaleFormSchema: ZodSchema = ApartmentSaleFormSchema.pick({
        purchase_price: true,
        apartment_share_of_housing_company_loans: true,
    }).superRefine((data, ctx) => {
        if (maximumPrices.debtFreePurchasePrice === null || maximumPrices.maximumPrice === null) return;
        const debtFreePurchasePrice = (data.purchase_price ?? 0) + (data.apartment_share_of_housing_company_loans ?? 0);

        // We should show a warning and ask for confirmation if catalog prices are missing
        if (!warningsGiven.catalog_acquisition_price) {
            if (apartment.prices.catalog_acquisition_price === null) {
                ctx.addIssue({
                    code: z.ZodIssueCode.custom,
                    path: ["catalog_acquisition_price"],
                    message: errorMessages.catalogPricesMissing,
                });
            } else if (debtFreePurchasePrice < apartment.prices.catalog_acquisition_price) {
                ctx.addIssue({
                    code: z.ZodIssueCode.custom,
                    path: ["catalog_acquisition_price"],
                    message: errorMessages.catalogUnderMaxPrice,
                });
            } else if (debtFreePurchasePrice > apartment.prices.catalog_acquisition_price) {
                ctx.addIssue({
                    code: z.ZodIssueCode.custom,
                    path: ["catalog_acquisition_price"],
                    message: errorMessages.catalogOverMaxPrice,
                });
            }
        }

        // The apartment share of housing company loans must match the sales catalog price.
        if (
            !warningsGiven.maximum_price_calculation &&
            data.apartment_share_of_housing_company_loans !== null &&
            data.apartment_share_of_housing_company_loans !== maximumPrices.apartmentShareOfHousingCompanyLoans
        ) {
            ctx.addIssue({
                code: z.ZodIssueCode.custom,
                path: ["apartment_share_of_housing_company_loans"],
                message: errorMessages.loanShareChangedCatalog,
            });
        }
    });

    const ApartmentReSaleFormSchema: ZodSchema = ApartmentSaleFormSchema.pick({
        purchase_date: true,
        purchase_price: true,
        apartment_share_of_housing_company_loans: true,
        exclude_from_statistics: true,
    }).superRefine((data, ctx) => {
        // Price can be zero only if sale is excluded from statistics.
        if (!data.exclude_from_statistics && data.purchase_price === 0) {
            ctx.addIssue({
                code: z.ZodIssueCode.custom,
                path: ["purchase_price"],
                message: "Pakollinen jos kauppa tilastoidaan.",
            });
        }

        if (data.exclude_from_statistics) return; // No need to validate further.

        if (maximumPrices.debtFreePurchasePrice === null || maximumPrices.maximumPrice === null) return;
        const debtFreePurchasePrice = (data.purchase_price ?? 0) + (data.apartment_share_of_housing_company_loans ?? 0);

        const isCalculationValid = isApartmentMaxPriceCalculationValid(apartment, data.purchase_date);

        if (!warningsGiven.maximum_price_calculation) {
            // Normal apartment sale without confirmed maximum price calculation
            if (!isCalculationValid) {
                if (debtFreePurchasePrice > maximumPrices.debtFreePurchasePrice) {
                    ctx.addIssue({
                        code: z.ZodIssueCode.custom,
                        path: ["maximum_price_calculation"],
                        message: errorMessages.priceHigherThanUnconfirmedMaxPrice,
                    });
                    ctx.addIssue({
                        code: z.ZodIssueCode.custom,
                        path: ["purchase_price"],
                        message: errorMessages.overMaxPrice,
                    });
                }
            }
            // Normal apartment sale with confirmed maximum price calculation
            else {
                // Price can not be bigger than the maximum price calculations maximum price.
                if (data.purchase_price && data.purchase_price > maximumPrices.maximumPrice) {
                    ctx.addIssue({
                        code: z.ZodIssueCode.custom,
                        path: ["maximum_price_calculation"],
                        message: errorMessages.overMaxPrice,
                    });
                    ctx.addIssue({
                        code: z.ZodIssueCode.custom,
                        path: ["purchase_price"],
                        message: errorMessages.overMaxPrice,
                    });
                }
            }
        }

        // The apartment share of housing company loans must match the maximum price calculations value
        if (
            isCalculationValid &&
            data.apartment_share_of_housing_company_loans !== null &&
            data.apartment_share_of_housing_company_loans !== maximumPrices.apartmentShareOfHousingCompanyLoans
        ) {
            ctx.addIssue({
                code: z.ZodIssueCode.custom,
                path: ["apartment_share_of_housing_company_loans"],
                message: errorMessages.loanShareChanged,
            });
        }
    });

    const isApartmentFirstSale = !apartment.prices.first_purchase_date;

    // Merge the schemas to get access to all the errors at the same time.
    const RefinedApartmentSaleSchema: ZodSchema = z.intersection(
        ApartmentSaleSchema,
        isApartmentFirstSale ? ApartmentFirstSaleFormSchema : ApartmentReSaleFormSchema
    );

    return RefinedApartmentSaleSchema;
};
