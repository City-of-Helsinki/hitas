import {boolean, literal, number, object, string, z} from "zod";
import {
    AddressSchema,
    APIDateSchema,
    APIIdString,
    CodeSchema,
    errorMessages,
    nullishDecimal,
    nullishNumber,
    nullishPositiveNumber,
    PageInfoSchema,
    writableRequiredNumber,
} from "./common";
import {indexNames} from "./enums";
import {HousingCompanyRegulationStatusSchema} from "./housingCompany";
import {ApartmentConstructionPriceIndexImprovementSchema, MarketPriceIndexImprovementSchema} from "./improvements";
import {OwnerSchema, OwnershipSchema, OwnershipsListSchema} from "./owner";

// ********************************
// * Unconfirmed maximum price
// ********************************

const ApartmentUnconfirmedMaximumPriceSchema = object({maximum: boolean(), value: number()});
export type IApartmentUnconfirmedMaximumPrice = z.infer<typeof ApartmentUnconfirmedMaximumPriceSchema>;

export const ApartmentUnconfirmedMaximumPriceIndicesSchema = object({
    construction_price_index: ApartmentUnconfirmedMaximumPriceSchema,
    market_price_index: ApartmentUnconfirmedMaximumPriceSchema,
    surface_area_price_ceiling: ApartmentUnconfirmedMaximumPriceSchema,
});
export type IApartmentUnconfirmedMaximumPriceIndices = z.infer<typeof ApartmentUnconfirmedMaximumPriceIndicesSchema>;

// ********************************
// * Confirmed maximum price
// ********************************

// Common schemas

const IndexCalculationSchema = object({
    maximum_price: number(),
    valid_until: string(),
    maximum: boolean(),
    calculation_variables: z.unknown(),
});
const CommonCalculationVarsSchema = object({
    debt_free_price: number(),
    debt_free_price_m2: number(),
    apartment_share_of_housing_company_loans: number(),
    apartment_share_of_housing_company_loans_date: string(),
    completion_date: string(),
    completion_date_index: number(),
    calculation_date: string(),
    calculation_date_index: number(),
});

export const ApartmentConfirmedMaximumPriceSchema = object({
    id: string().optional(),
    calculation_date: string(),
    confirmed_at: string(),
    created_at: string(),
    maximum_price: number(),
    valid: object({is_valid: boolean(), valid_until: string()}),
});
export type IApartmentConfirmedMaximumPrice = z.infer<typeof ApartmentConfirmedMaximumPriceSchema>;

const CalculationVars2011OnwardsSchema = object({
    first_sale_acquisition_price: number(),
    additional_work_during_construction: number(),
    basic_price: number(),
    index_adjustment: number(),
    housing_company_improvements: object({
        items: object({
            name: string(),
            value: number(),
            value_added: number(),
            completion_date: string(),
            value_for_apartment: number(),
            value_for_housing_company: number(),
        }).array(),
        summary: object({
            value: number(),
            value_added: number(),
            excess: object({
                total: number(),
                surface_area: number(),
                value_per_square_meter: number(),
            }),
            value_for_housing_company: number(),
            value_for_apartment: number(),
        }),
    }),
});

const IndexCalculation2011OnwardsSchema = IndexCalculationSchema.and(
    object({
        calculation_variables: CommonCalculationVarsSchema.and(CalculationVars2011OnwardsSchema),
    })
);
export type IIndexCalculation2011Onwards = z.infer<typeof IndexCalculation2011OnwardsSchema>;

// ********************************
// * Market price index
// ********************************

const IndexCalculationMarketPriceIndexBefore2011Schema = IndexCalculationSchema.and(
    object({
        calculation_variables: CommonCalculationVarsSchema.and(
            object({
                first_sale_acquisition_price: number(),
                interest_during_construction: number(),
                interest_during_construction_percentage: number(),
                additional_work_during_construction: number(),
                basic_price: number(),
                index_adjustment: number(),
                apartment_improvements: object({
                    items: object({
                        name: string(),
                        value: number(),
                        depreciation: object({
                            time: object({
                                years: number(),
                                months: number(),
                            }),
                            amount: number(),
                        }),
                        accepted_value: number(),
                        completion_date: string(),
                        value_without_excess: number(),
                    }).array(),
                    summary: object({
                        value: number(),
                        excess: object({
                            total: number(),
                            surface_area: number(),
                            value_per_square_meter: number(),
                        }),
                        depreciation: number(),
                        accepted_value: number(),
                        value_without_excess: number(),
                    }),
                }),
                housing_company_improvements: object({
                    items: object({
                        name: string(),
                        value: number(),
                        depreciation: object({
                            time: object({
                                years: number(),
                                months: number(),
                            }),
                            amount: number(),
                        }),
                        accepted_value: number(),
                        completion_date: string(),
                        value_without_excess: number(),
                        accepted_value_for_housing_company: number(),
                    }).array(),
                    summary: object({
                        value: number(),
                        excess: object({
                            total: number(),
                            surface_area: number(),
                            value_per_square_meter: number(),
                        }),
                        depreciation: number(),
                        accepted_value: number(),
                        value_without_excess: number(),
                        accepted_value_for_housing_company: number(),
                    }),
                }),
            })
        ),
    })
);
export type IIndexCalculationMarketPriceIndexBefore2011 = z.infer<
    typeof IndexCalculationMarketPriceIndexBefore2011Schema
>;

// ********************************
// * Construction price index
// ********************************

const IndexCalculationConstructionPriceIndexBefore2011Schema = IndexCalculationSchema.and(
    object({
        calculation_variables: CommonCalculationVarsSchema.and(
            object({
                interest_during_construction: number(),
                interest_during_construction_percentage: number(),
                housing_company_acquisition_price: number(),
                housing_company_assets: number(),
                apartment_share_of_housing_company_assets: number(),
                additional_work_during_construction: number(),
                index_adjusted_additional_work_during_construction: number(),
                apartment_improvements: object({
                    items: object({
                        name: string(),
                        value: number(),
                        depreciation: object({
                            time: object({
                                years: number(),
                                months: number(),
                            }),
                            amount: number(),
                            percentage: number(),
                        }),
                        index_adjusted: number(),
                        completion_date: string(),
                        value_for_apartment: number(),
                        completion_date_index: number(),
                        calculation_date_index: number(),
                    }).array(),
                    summary: object({
                        value: number(),
                        depreciation: number(),
                        index_adjusted: number(),
                        value_for_apartment: number(),
                    }),
                }),
                housing_company_improvements: object({
                    items: object({
                        name: string(),
                        value: number(),
                        value_for_apartment: number(),
                    }).array(),
                    summary: object({
                        value: number(),
                        value_for_apartment: number(),
                    }),
                }),
            })
        ),
    })
);
export type IIndexCalculationConstructionPriceIndexBefore2011 = z.infer<
    typeof IndexCalculationConstructionPriceIndexBefore2011Schema
>;

// ********************************
// * Surface area price ceiling
// ********************************

const SurfaceAreaPriceCeilingCalculationSchema = IndexCalculationSchema.and(
    object({
        calculation_variables: object({
            calculation_date: string(),
            calculation_date_value: number(),
            debt_free_price: number(),
            surface_area: number(),
            apartment_share_of_housing_company_loans: number(),
            apartment_share_of_housing_company_loans_date: string(),
        }),
    })
);
export type SurfaceAreaPriceCeilingCalculation = z.infer<typeof SurfaceAreaPriceCeilingCalculationSchema>;

// ********************************
// * Apartment fields
// ********************************

export const ApartmentAddressSchema = AddressSchema.extend({
    apartment_number: writableRequiredNumber,
    floor: nullishNumber,
    stair: string().min(1, "Pakollinen kenttä!"),
});
export type IApartmentAddress = z.infer<typeof ApartmentAddressSchema>;

const ApartmentLinkedModelSchema = object({id: string(), link: string()});
const ApartmentLinkedModelsSchema = object({
    housing_company: ApartmentLinkedModelSchema.merge(
        object({display_name: string(), regulation_status: HousingCompanyRegulationStatusSchema})
    ),
    real_estate: ApartmentLinkedModelSchema,
    building: ApartmentLinkedModelSchema.merge(object({street_address: string()})),
    apartment: ApartmentLinkedModelSchema,
});

export const ApartmentPricesSchema = object({
    first_sale_purchase_price: number().nullable(), // Read only
    first_sale_share_of_housing_company_loans: number().nullable(), // Read only
    first_sale_acquisition_price: number().optional(), // Read only (purchase_price + share_of_housing_company_loans)
    first_purchase_date: string().nullable(), // Read only
    current_sale_id: string().nullable(), // Read only
    latest_sale_purchase_price: number().nullable(), // Read only
    latest_purchase_date: string().nullable(), // Read only
    catalog_purchase_price: number().nullable(), // Read only
    catalog_share_of_housing_company_loans: number().nullable(), // Read only
    catalog_acquisition_price: number().nullable(), // Read only (purchase_price + share_of_hosing_company_loans)
    construction: object({
        loans: nullishDecimal,
        additional_work: nullishDecimal,
        interest: object({
            rate_mpi: nullishDecimal,
            rate_cpi: nullishDecimal,
        }).optional(),
        debt_free_purchase_price: nullishDecimal,
    }),
    maximum_prices: object({
        confirmed: ApartmentConfirmedMaximumPriceSchema.nullable(), // Read only
        unconfirmed: object({
            onwards_2011: ApartmentUnconfirmedMaximumPriceIndicesSchema, // Read only
            pre_2011: ApartmentUnconfirmedMaximumPriceIndicesSchema, // Read only
        }),
    }),
});
const ApartmentWritablePricesSchema = ApartmentPricesSchema.pick({
    construction: true,
});

export const ApartmentSharesSchema = object({
    start: nullishPositiveNumber,
    end: nullishPositiveNumber,
    total: number(), // Read only
});

// ********************************
// * Condition of Sale
// ********************************

const CreateConditionOfSaleSchema = object({
    household: string().array(), // List of owner IDs
});
export type ICreateConditionOfSale = z.infer<typeof CreateConditionOfSaleSchema>;

const ApartmentConditionOfSaleSchema = object({
    id: string(),
    owner: OwnerSchema.omit({id: true}).and(object({id: string()})),
    apartment: object({
        id: string(),
        address: ApartmentAddressSchema,
        housing_company: ApartmentLinkedModelSchema.and(object({display_name: string()})),
    }),
    grace_period: z.enum(["not_given", "three_months", "six_months"]),
    fulfilled: string().nullable(),
    sell_by_date: string().nullable(), // Read only
});
export type IApartmentConditionOfSale = z.infer<typeof ApartmentConditionOfSaleSchema>;

const ConditionOfSaleSchema = object({
    id: string().optional(),
    new_ownership: OwnershipSchema.and(
        object({
            apartment: object({
                id: string(),
                address: ApartmentAddressSchema,
                housing_company: ApartmentLinkedModelSchema.and(object({display_name: string()})),
            }),
        })
    ),
    old_ownership: OwnershipSchema.and(
        object({
            apartment: object({
                id: string(),
                address: ApartmentAddressSchema,
                housing_company: ApartmentLinkedModelSchema.and(object({display_name: string()})),
            }),
        })
    ),
    grace_period: z.enum(["not_given", "three_months", "six_months"]),
    fulfilled: string().nullable().optional(),
});
export type IConditionOfSale = z.infer<typeof ConditionOfSaleSchema>;

// ********************************
// * Apartment
// ********************************

export const ApartmentSchema = object({
    id: string().nullable(),
    is_sold: boolean(),
    type: string(),
    surface_area: number(),
    rooms: number().nullable(),
    address: ApartmentAddressSchema,
    completion_date: string().nullable(),
    housing_company: string(),
    ownerships: OwnershipSchema.array(),
    links: ApartmentLinkedModelsSchema,
    has_conditions_of_sale: boolean(),
    has_grace_period: boolean(),
    sell_by_date: string().nullable(),
});
export type IApartment = z.infer<typeof ApartmentSchema>;

export const ApartmentDetailsSchema = object({
    id: APIIdString,
    is_sold: boolean(),
    type: CodeSchema,
    surface_area: number(),
    rooms: number().nullable(),
    shares: ApartmentSharesSchema,
    address: ApartmentAddressSchema,
    prices: ApartmentPricesSchema,
    completion_date: string().nullable(),
    ownerships: OwnershipSchema.array(),
    notes: string(),
    improvements: object({
        market_price_index: MarketPriceIndexImprovementSchema.array(),
        construction_price_index: ApartmentConstructionPriceIndexImprovementSchema.array(),
    }),
    links: ApartmentLinkedModelsSchema,
    conditions_of_sale: ApartmentConditionOfSaleSchema.array(),
    sell_by_date: string().nullable(),
});
export type IApartmentDetails = z.infer<typeof ApartmentDetailsSchema>;

export const ApartmentWritableSchema = object({
    id: APIIdString.optional(),
    type: object({id: string()}).nullable(),
    surface_area: nullishDecimal,
    rooms: nullishNumber,
    shares: ApartmentSharesSchema.omit({total: true}),
    address: ApartmentAddressSchema.omit({street_address: true, city: true, postal_code: true}),
    prices: ApartmentWritablePricesSchema,
    completion_date: string().nullish(),
    building: object({id: string()}),
    notes: string(),
    improvements: object({
        market_price_index: MarketPriceIndexImprovementSchema.array(),
        construction_price_index: ApartmentConstructionPriceIndexImprovementSchema.array(),
    }),
});
export type IApartmentWritable = z.infer<typeof ApartmentWritableSchema>;

export const ApartmentWritableFormSchema = ApartmentWritableSchema.omit({
    building: true,
    address: true,
}).and(
    object({
        building: object({label: string(), value: string()}),
        address: ApartmentAddressSchema.omit({street_address: true, city: true, postal_code: true}),
    })
);
export type IApartmentWritableForm = z.infer<typeof ApartmentWritableFormSchema>;

// ********************************
// * Apartment sale
// ********************************

export const ApartmentSaleFormSchema = object({
    key: string().optional(),
    notification_date: APIDateSchema,
    purchase_date: APIDateSchema,
    purchase_price: z
        .number({invalid_type_error: errorMessages.required, required_error: errorMessages.required})
        .nonnegative(errorMessages.priceMin)
        .multipleOf(1, errorMessages.noDecimalPlaces)
        .nullish(),
    apartment_share_of_housing_company_loans: z
        .number({invalid_type_error: errorMessages.required, required_error: errorMessages.required})
        .nonnegative(errorMessages.loanShareMin)
        .multipleOf(1, errorMessages.noDecimalPlaces)
        .nullish(),
    exclude_from_statistics: boolean(),
    ownerships: OwnershipsListSchema.optional(),
});
export type IApartmentSaleForm = z.infer<typeof ApartmentSaleFormSchema>;

export const ApartmentSaleSchema = ApartmentSaleFormSchema.pick({
    notification_date: true,
    purchase_date: true,
}).and(
    object({
        id: string().optional(),
        purchase_price: z
            .number({invalid_type_error: errorMessages.required, required_error: errorMessages.required})
            .nonnegative(errorMessages.priceMin),
        apartment_share_of_housing_company_loans: z
            .number({invalid_type_error: errorMessages.required, required_error: errorMessages.required})
            .nonnegative(errorMessages.priceMin),
        ownerships: OwnershipsListSchema,
    })
);
export type IApartmentSale = z.infer<typeof ApartmentSaleSchema>;

// ********************************
// * Maximum price model
// ********************************

export const ApartmentMaximumPricePre2011Schema = object({
    new_hitas: literal(false),
    calculations: object({
        construction_price_index: IndexCalculationConstructionPriceIndexBefore2011Schema,
        market_price_index: IndexCalculationMarketPriceIndexBefore2011Schema,
        surface_area_price_ceiling: SurfaceAreaPriceCeilingCalculationSchema,
    }),
});

export const ApartmentMaximumPrice2011OnwardsSchema = object({
    new_hitas: literal(true),
    calculations: object({
        construction_price_index: IndexCalculation2011OnwardsSchema,
        market_price_index: IndexCalculation2011OnwardsSchema,
        surface_area_price_ceiling: SurfaceAreaPriceCeilingCalculationSchema,
    }),
});

export const ApartmentMaximumPriceSchema = object({
    id: string(),
    index: z.enum(indexNames),
    maximum_price: number(),
    maximum_price_per_square: number(),
    created_at: string(),
    confirmed_at: string().nullable(),
    calculation_date: string(),
    valid_until: string(),
    additional_info: string(),
    apartment: ApartmentSchema.pick({
        address: true,
        type: true,
        ownerships: true,
        rooms: true,
        shares: true,
        surface_area: true,
    }),
    housing_company: object({
        archive_id: number(),
        official_name: string(),
        property_manager: object({
            name: string(),
            street_address: string(),
        }),
    }),
}).and(ApartmentMaximumPrice2011OnwardsSchema.or(ApartmentMaximumPricePre2011Schema));
export type IApartmentMaximumPriceCalculationDetails = z.infer<typeof ApartmentMaximumPriceSchema>;

export const ApartmentMaximumPriceWritableSchema = object({
    calculation_date: string().nullable(),
    apartment_share_of_housing_company_loans: number().nullable(),
    apartment_share_of_housing_company_loans_date: string().nullable(),
    additional_info: string(),
});
export type IApartmentMaximumPriceWritable = z.infer<typeof ApartmentMaximumPriceWritableSchema>;

// ********************************
// * API
// ********************************

const ApartmentSaleCreatedResponseSchema = object({
    id: string(),
    ownerships: object({owner: object({id: APIIdString}), percentage: number()}).array(),
    notification_date: string(),
    purchase_date: string(),
    purchase_price: number(),
    apartment_share_of_housing_company_loans: number(),
    exclude_from_statistics: boolean(),
    conditions_of_sale_created: boolean(),
});
export type IApartmentSaleCreated = z.infer<typeof ApartmentSaleCreatedResponseSchema>;

export const ApartmentListResponseSchema = object({
    page: PageInfoSchema,
    contents: ApartmentSchema.array(),
});
export type IApartmentListResponse = z.infer<typeof ApartmentListResponseSchema>;

export const ApartmentQuerySchema = object({
    housingCompanyId: string(),
    apartmentId: string(),
});
export type IApartmentQuery = z.infer<typeof ApartmentQuerySchema>;
