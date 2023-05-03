import {boolean, literal, number, object, string, z} from "zod";

// ********************************
// * Enumerations
// ********************************

export const apartmentStates = ["free", "reserved", "sold"] as const;

export const housingCompanyStates = [
    "not_ready",
    "lt_30_years",
    "gt_30_years_not_free",
    "gt_30_years_free",
    "gt_30_years_plot_department_notification",
    "half_hitas",
    "ready_no_statistics",
] as const;

export const hitasQuarters = [
    {
        value: "02-01",
        label: "1.2. - 30.4.",
    },
    {
        value: "05-01",
        label: "1.5. - 31.7.",
    },
    {
        value: "08-01",
        label: "1.8. - 31.10.",
    },
    {
        value: "11-01",
        label: "1.11. - 31.1.",
    },
] as const;

export const indexNames = ["market_price_index", "construction_price_index", "surface_area_price_ceiling"] as const;

const CostAreas = ["1", "2", "3", "4"] as const;

// ********************************
// * Error messages
// ********************************

export const errorMessages = {
    required: "Pakollinen kenttä",
    postalCodeFormat: "Virheellinen postinumero",
    stringLength: "Liian lyhyt arvo",
    stringMin: "Liian vähän kirjaimia",
    stringMax: "Liian monta kirjainta",
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
    loanShareChanged: "Lainaosuus muuttunut laskelmasta",
    catalogOverMaxPrice: "Kauppahinta ylittää myyntihintaluettelon hinnan",
    catalogUnderMaxPrice: "Kauppahinta alittaa myyntihintaluettelon hinnan",
    catalogPricesMissing: "Myyntihintaluettelon hinnat puuttuvat",
    sharesEmpty: "Toinen osakekenttä on tyhjä",
    sharesStartGreaterThanEnd: "Osakkeiden lopun on oltava suurempi kuin alun",
    constructionInterestEmpty: "Toinen korkokenttä on tyhjä",
    constructionInterest6GreaterThan14: "14% koron on oltava suurempi kuin 6% koron",
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
// * Basic/primitive schemas
// ********************************

const APIIdString = string().min(32, errorMessages.APIIdMin).max(32, errorMessages.APIIdMax);

const addAPIId = (zodObject) => zodObject.merge(APIIdString);

const nullishNumber = number({invalid_type_error: errorMessages.numberType, required_error: errorMessages.required})
    .nonnegative(errorMessages.numberPositive)
    .nullish();

const nullishPositiveNumber = number({
    invalid_type_error: errorMessages.numberType,
    required_error: errorMessages.required,
})
    .positive(errorMessages.numberPositive)
    .nullish();

const writableRequiredNumber = number({
    invalid_type_error: errorMessages.required,
    required_error: errorMessages.required,
})
    .nonnegative(errorMessages.numberPositive)
    .optional(); // allow undefined but no null

const CodeSchema = object({
    id: APIIdString,
    value: string(),
    description: string().nullable(),
    code: string(),
});

const PostalCodeSchema = object({
    value: string(),
    city: string(),
    cost_area: z.enum(CostAreas),
});

const AddressSchema = object({
    street_address: string({required_error: errorMessages.required}).min(2, errorMessages.stringLength),
    postal_code: z
        .number({invalid_type_error: errorMessages.numberType, required_error: errorMessages.required})
        .refine((val) => val.toString().match(/^\d{5}$/), errorMessages.postalCodeFormat)
        .or(string().length(5)),
    city: string().min(2, errorMessages.stringLength).optional(),
});

const PropertyManagerSchema = object({
    id: string(),
    name: string(),
    email: string(),
    address: AddressSchema,
});

const ImprovementSchema = object({
    name: string(),
    value: number(),
    completion_date: string(),
});
const MarketPriceIndexImprovementSchema = ImprovementSchema.and(
    object({
        no_deductions: boolean(),
    })
);
const ApartmentConstructionPriceIndexImprovementSchema = ImprovementSchema.and(
    object({
        depreciation_percentage: number(), // 0.0 | 2.5 | 10.0
    })
);

const UserInfoSchema = object({
    first_name: string(),
    last_name: string(),
    email: string(),
});

// ********************************
// * Housing company schemas
// ********************************

const HousingCompanyAreaSchema = object({name: string(), cost_area: number()});

const HousingCompanyStateSchema = z.enum(housingCompanyStates);

const HousingCompanySchema = object({
    id: APIIdString,
    name: string(),
    state: HousingCompanyStateSchema,
    address: AddressSchema,
    area: HousingCompanyAreaSchema,
    date: string().nullable(),
});

const BuildingSchema = object({
    id: APIIdString,
    address: AddressSchema,
    completion_date: string().nullable(),
    building_identifier: string().nullable(),
    apartment_count: number(),
});

const BuildingWritableSchema = BuildingSchema.pick({building_identifier: true}).and(
    object({
        id: APIIdString.optional(),
        address: object({street_address: string()}),
        real_estate_id: string().nullable(),
    })
);

const RealEstateSchema = object({
    id: APIIdString,
    property_identifier: string(),
    address: AddressSchema,
    buildings: BuildingSchema.array(),
});

const HousingCompanyDetailsSchema = object({
    id: APIIdString,
    name: object({official: string(), display: string()}),
    business_id: string().nullable(),
    state: HousingCompanyStateSchema,
    address: AddressSchema,
    area: HousingCompanyAreaSchema,
    date: string().nullable(),
    financing_method: CodeSchema,
    building_type: CodeSchema,
    developer: CodeSchema,
    property_manager: PropertyManagerSchema.nullable(),
    acquisition_price: number(),
    primary_loan: number().optional(),
    sales_price_catalogue_confirmation_date: string().nullable(),
    release_date: string().nullable(),
    archive_id: number(),
    notes: string().nullable(),
    last_modified: object({
        user: object({
            user: string().nullable(),
            first_name: string().nullable(),
            last_name: string().nullable(),
        }),
        datetime: z.date(),
    }),
    real_estates: RealEstateSchema.array(),
    summary: object({
        average_price_per_square_meter: number(),
        realized_acquisition_price: number(),
        total_shares: number(),
        total_surface_area: number(),
    }),
    improvements: object({
        market_price_index: MarketPriceIndexImprovementSchema.array(),
        construction_price_index: ImprovementSchema.array(),
    }),
});

const HousingCompanyWritableSchema = HousingCompanyDetailsSchema.pick({
    name: true,
    business_id: true,
    state: true,
    address: true,
    acquisition_price: true,
    primary_loan: true,
    sales_price_catalogue_confirmation_date: true,
    notes: true,
    improvements: true,
}).merge(
    object({
        id: APIIdString.optional(),
        financing_method: object({id: string()}),
        building_type: object({id: string()}),
        developer: object({id: string()}),
        property_manager: object({id: string()}).nullable(),
    })
);

// ********************************
// * Apartment Schemas
// ********************************

const ApartmentAddressSchema = object({
    street_address: string(),
    postal_code: string().optional(),
    city: string().optional(), // Read only
    apartment_number: writableRequiredNumber,
    floor: nullishNumber,
    stair: string().min(1, "Pakollinen kenttä!"),
});

const ApartmentLinkedModelSchema = object({id: string(), link: string()});

const ApartmentLinkedModelsSchema = object({
    housing_company: ApartmentLinkedModelSchema.merge(object({display_name: string()})),
    real_estate: ApartmentLinkedModelSchema,
    building: ApartmentLinkedModelSchema.merge(object({street_address: string()})),
    apartment: ApartmentLinkedModelSchema,
});

const ownerSchema = object({
    id: APIIdString.optional(),
    name: string({required_error: errorMessages.required}).min(2, errorMessages.stringLength),
    identifier: string({required_error: errorMessages.required}),
    email: string({required_error: errorMessages.required}).email(errorMessages.emailInvalid).nullable(),
});

const ownershipSchema = object({
    owner: ownerSchema,
    percentage: z
        .number({invalid_type_error: errorMessages.numberType, required_error: errorMessages.required})
        .positive(errorMessages.numberPositive)
        .max(100, errorMessages.numberMax),
    key: z.any(),
    starting_date: string().optional(),
});

const ownershipsSchema = ownershipSchema.array();

const OwnershipFormSchema = ownershipSchema
    .omit({owner: true})
    .and(object({owner: object({id: string()})}))
    .array();

const ownerAPISchema = addAPIId(ownerSchema);

// Condition of Sale
const CreateConditionOfSaleSchema = object({
    household: string().array(), // List of owner IDs
});

const ApartmentConditionOfSaleSchema = object({
    id: string(),
    owner: ownerSchema.omit({id: true}).and(object({id: string()})),
    apartment: object({
        id: string(),
        address: ApartmentAddressSchema,
        housing_company: ApartmentLinkedModelSchema.and(object({display_name: string()})),
    }),
    grace_period: z.enum(["not_given", "three_months", "six_months"]),
    fulfilled: string().nullable(),
    sell_by_date: string().nullable(), // Read only
});

const ConditionOfSaleSchema = object({
    id: string(),
    new_ownership: ownershipSchema.and(
        object({
            apartment: object({
                id: string(),
                address: ApartmentAddressSchema,
                housing_company: ApartmentLinkedModelSchema.and(object({display_name: string()})),
            }),
        })
    ),
    old_ownership: ownershipSchema.and(
        object({
            apartment: object({
                id: string(),
                address: ApartmentAddressSchema,
                housing_company: ApartmentLinkedModelSchema.and(object({display_name: string()})),
            }),
        })
    ),
    grace_period: z.enum(["not_given", "three_months", "six_months"]),
    fulfilled: string().nullable(),
});
const ApartmentUnconfirmedMaximumPriceSchema = object({maximum: boolean(), value: number()});

const ApartmentUnconfirmedMaximumPriceIndicesSchema = object({
    construction_price_index: ApartmentUnconfirmedMaximumPriceSchema,
    market_price_index: ApartmentUnconfirmedMaximumPriceSchema,
    surface_area_price_ceiling: ApartmentUnconfirmedMaximumPriceSchema,
});

const ApartmentConfirmedMaximumPriceSchema = object({
    id: string().optional(),
    calculation_date: string(),
    confirmed_at: string(),
    created_at: string(),
    maximum_price: number(),
    valid: object({is_valid: boolean(), valid_until: string()}),
}).nullable();

const ApartmentPricesSchema = object({
    first_sale_purchase_price: number().nullable(), // Read only
    first_sale_share_of_housing_company_loans: number().nullable(), // Read only
    first_sale_acquisition_price: number().optional(), // Read only. (purchase_price + share_of_housing_company_loans)
    first_purchase_date: string().nullable(), // Read only
    latest_sale_purchase_price: number().nullable(), // Read only
    latest_purchase_date: string().nullable(), // Read only
    catalog_purchase_price: number().nullable(), // Read only
    catalog_share_of_housing_company_loans: number().nullable(), // Read only
    catalog_acquisition_price: number().nullable(), // Read only. (purchase_price + share_of_hosing_company_loans)
    construction: object({
        loans: nullishNumber,
        additional_work: nullishNumber,
        interest: object({
            rate_6: nullishNumber,
            rate_14: nullishNumber,
        }).optional(),
        debt_free_purchase_price: nullishNumber,
    }),
    maximum_prices: object({
        // Read only
        confirmed: ApartmentConfirmedMaximumPriceSchema,
        unconfirmed: object({
            onwards_2011: ApartmentUnconfirmedMaximumPriceIndicesSchema,
            pre_2011: ApartmentUnconfirmedMaximumPriceIndicesSchema,
        }),
    }),
});

const ApartmentWritablePricesSchema = ApartmentPricesSchema.omit({
    first_sale_purchase_price: true,
    first_sale_share_of_housing_company_loans: true,
    first_sale_acquisition_price: true,
    first_purchase_date: true,
    latest_sale_purchase_price: true,
    latest_purchase_date: true,
    maximum_prices: true,
    catalog_purchase_price: true,
    catalog_share_of_housing_company_loans: true,
    catalog_acquisition_price: true,
});

const ApartmentSharesSchema = object({
    start: nullishPositiveNumber,
    end: nullishPositiveNumber,
    total: number(),
});

const ApartmentSchema = object({
    id: string().nullable(),
    state: z.enum(apartmentStates),
    type: string(),
    surface_area: number(),
    rooms: number().nullable(),
    address: ApartmentAddressSchema,
    completion_date: number().nullable(),
    housing_company: string(),
    ownerships: ownershipsSchema,
    links: ApartmentLinkedModelsSchema,
    has_conditions_of_sale: boolean(),
    has_grace_period: boolean(),
    sell_by_date: string().nullable(),
});

const ApartmentDetailsSchema = object({
    id: APIIdString,
    state: z.enum(apartmentStates),
    type: CodeSchema,
    surface_area: number(),
    rooms: number().nullable(),
    shares: ApartmentSharesSchema,
    address: ApartmentAddressSchema,
    prices: ApartmentPricesSchema,
    completion_date: string().nullable(),
    ownerships: ownershipsSchema,
    notes: string(),
    improvements: object({
        market_price_index: MarketPriceIndexImprovementSchema.array(),
        construction_price_index: ApartmentConstructionPriceIndexImprovementSchema.array(),
    }),
    links: ApartmentLinkedModelsSchema,
    conditions_of_sale: ApartmentConditionOfSaleSchema.array(),
    sell_by_date: string().nullable(),
});

const ApartmentWritableSchema = object({
    id: APIIdString.optional(),
    state: z.enum(apartmentStates).nullable(),
    type: object({id: string()}).nullable(),
    surface_area: nullishNumber,
    rooms: nullishNumber,
    shares: ApartmentSharesSchema.omit({total: true}),
    address: ApartmentAddressSchema,
    prices: ApartmentWritablePricesSchema,
    completion_date: string().nullish(),
    building: object({id: string()}),
    notes: string(),
    improvements: object({
        market_price_index: MarketPriceIndexImprovementSchema.array(),
        construction_price_index: ApartmentConstructionPriceIndexImprovementSchema.array(),
    }),
});

const ApartmentWritableFormSchema = ApartmentWritableSchema.omit({
    building: true,
    address: true,
}).and(
    object({
        building: object({label: string(), value: string()}),
        address: ApartmentAddressSchema.omit({street_address: true, city: true}),
    })
);

// Writable Apartment Sale Form
const ApartmentSaleFormSchema = object({
    key: string().optional(),
    notification_date: z
        .string({required_error: errorMessages.required})
        .regex(/^\d{4}-\d{2}-\d{2}$/, errorMessages.dateFormat),
    purchase_date: z
        .string({required_error: errorMessages.required})
        .regex(/^\d{4}-\d{2}-\d{2}$/, errorMessages.dateFormat),
    purchase_price: z
        .number({invalid_type_error: errorMessages.numberType, required_error: errorMessages.required})
        .nonnegative(errorMessages.priceMin)
        .max(999999, errorMessages.priceMax)
        .nullish(),
    apartment_share_of_housing_company_loans: z
        .number({invalid_type_error: errorMessages.numberType, required_error: errorMessages.required})
        .gte(0, errorMessages.loanShareMin)
        .nullish(),
    exclude_from_statistics: boolean(),
});

// Writable list of ownerships
const OwnershipsListSchema = object({
    owner: object({id: APIIdString.optional().or(z.literal(""))}),
    percentage: number(),
})
    .array()
    .superRefine((elements, ctx) => {
        // Can't have an empty ownerships list
        if (!elements.length) {
            ctx.addIssue({
                code: z.ZodIssueCode.custom,
                message: errorMessages.noOwnerships,
            });
            return;
        }

        // Check for duplicates
        const ownerIds = elements.filter((e) => e.owner.id).map((e) => e.owner.id);
        if (ownerIds.length !== new Set(ownerIds).size) {
            ctx.addIssue({
                code: z.ZodIssueCode.custom,
                message: errorMessages.ownershipDuplicate,
            });
        }

        // Prevent empty fields
        if (elements.filter((e) => !e.owner.id).length) {
            ctx.addIssue({
                code: z.ZodIssueCode.custom,
                message: "Tyhjä omistaja kenttä",
            });
            return;
        }
        if (elements.filter((e) => !e.percentage).length) {
            ctx.addIssue({
                code: z.ZodIssueCode.custom,
                message: "Prosenttikentän arvo on 0",
            });
            return;
        }

        // Sum of percentages must be 100
        const percentages = elements.map((e) => e.percentage);
        const percentagesSum = percentages.reduce((a, b) => a + b, 0);
        if (percentagesSum !== 0 && percentagesSum !== 100) {
            ctx.addIssue({
                code: z.ZodIssueCode.custom,
                message: errorMessages.ownershipPercent,
            });
        }
    });

// Apartment Sale Form that can be submitted.
// Other validations still need to be done, but those are out of scope for this schema.
const ApartmentSaleSchema = ApartmentSaleFormSchema.omit({purchase_price: true})
    .and(
        object({
            id: string().optional(),
            purchase_price: z
                .number({invalid_type_error: errorMessages.numberType, required_error: errorMessages.required})
                .nonnegative(errorMessages.priceMin)
                .max(999999, errorMessages.priceMax),
            ownerships: OwnershipsListSchema,
        })
    )
    .superRefine((data, ctx) => {
        // Price can be zero, but it can't be nullish.
        if (data.purchase_price === undefined || data.purchase_price === null) {
            ctx.addIssue({
                code: z.ZodIssueCode.custom,
                path: ["purchase_price"],
                message: errorMessages.required,
            });
        }
        // Price can be zero only if sale is excluded from statistics.
        if (!data.exclude_from_statistics && data.purchase_price === 0) {
            ctx.addIssue({
                code: z.ZodIssueCode.custom,
                path: ["purchase_price"],
                message: "Pakollinen jos kauppa tilastoidaan.",
            });
        }
    });

const ApartmentSaleCreatedSchema = object({
    id: string(),
    ownerships: object({owner: object({id: APIIdString}), percentage: number()}).array(),
    notification_date: string(),
    purchase_date: string(),
    purchase_price: number(),
    apartment_share_of_housing_company_loans: number(),
    exclude_from_statistics: boolean(),
    conditions_of_sale_created: boolean(),
});

// ********************************
// * Maximum price schemas
// ********************************

// Maximum Price Fields

const IndexCalculationSchema = object({
    maximum_price: number(),
    valid_until: string(),
    maximum: boolean(),
    calculation_variables: z.unknown(),
});

// Used in both MPI and RKI before and after 2011
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

// Maximum Price Schemas

const ApartmentMaximumPrice2011OnwardsSchema = object({
    new_hitas: literal(true),
    calculations: object({
        construction_price_index: IndexCalculation2011OnwardsSchema,
        market_price_index: IndexCalculation2011OnwardsSchema,
        surface_area_price_ceiling: SurfaceAreaPriceCeilingCalculationSchema,
    }),
});

const ApartmentMaximumPricePre2011Schema = object({
    new_hitas: literal(false),
    calculations: object({
        construction_price_index: IndexCalculationConstructionPriceIndexBefore2011Schema,
        market_price_index: IndexCalculationMarketPriceIndexBefore2011Schema,
        surface_area_price_ceiling: SurfaceAreaPriceCeilingCalculationSchema,
    }),
});

const Split2011Schema = ApartmentMaximumPrice2011OnwardsSchema.or(ApartmentMaximumPrice2011OnwardsSchema);

const ApartmentMaximumPriceSchema = object({
    id: string(),
    index: z.enum(indexNames),
    maximum_price: number(),
    maximum_price_per_square: number(),
    created_at: string(),
    confirmed_at: string().nullable(),
    calculation_date: string(),
    valid_until: string(),
    additional_info: string(),
    apartment: object({
        address: ApartmentAddressSchema,
        type: string(),
        ownerships: object({
            name: string(),
            percentage: number(),
        }).array(),
        rooms: number().nullable(),
        shares: ApartmentSharesSchema,
        surface_area: number(),
    }),
    housing_company: object({
        archive_id: number(),
        official_name: string(),
        property_manager: object({
            name: string(),
            street_address: string(),
        }),
    }),
}).and(Split2011Schema);

const ApartmentMaximumPriceWritableSchema = object({
    calculation_date: string().nullable(),
    apartment_share_of_housing_company_loans: number().nullable(),
    apartment_share_of_housing_company_loans_date: string().nullable(),
    additional_info: string(),
});

const IndexSchema = object({indexType: string(), month: string(), value: number().nullable()});

const QuarterSchema = string().regex(/\d{4}Q\d/);
const ExternalSalesQuarterSchema = object({
    quarter: QuarterSchema,
    areas: object({
        postal_code: string().regex(/\d{3}/),
        sale_count: number(),
        price: number(),
    }).array(),
});
const ExternalSalesDataResponseSchema = object({
    calculation_quarter: QuarterSchema,
    quarter_1: ExternalSalesQuarterSchema,
    quarter_2: ExternalSalesQuarterSchema,
    quarter_3: ExternalSalesQuarterSchema,
    quarter_4: ExternalSalesQuarterSchema,
});

// ********************************
// * Request / Response schemas
// ********************************

// General

const PageInfoSchema = object({
    size: number(),
    total_items: number(),
    current_page: number(),
    total_pages: number(),
    links: object({
        next: string().nullable(),
        previous: string().nullable(),
    }),
});

// List responses

const HousingCompanyListResponseSchema = object({
    page: PageInfoSchema,
    contents: HousingCompanySchema.array(),
});

const ApartmentListResponseSchema = object({
    page: PageInfoSchema,
    contents: ApartmentSchema.array(),
});

const CodeResponseSchema = object({
    page: PageInfoSchema,
    contents: CodeSchema.array(),
});

const PostalCodeResponseSchema = object({
    page: PageInfoSchema,
    contents: PostalCodeSchema.array(),
});

const IndexResponseSchema = object({
    page: PageInfoSchema,
    contents: IndexSchema.array(),
});

// Query Parameters

const HousingCompanyApartmentQuerySchema = object({
    housingCompanyId: string(),
    params: object({
        page: number(),
    }),
});

const ApartmentQuerySchema = object({
    housingCompanyId: string(),
    apartmentId: string(),
});

const IndexQuerySchema = object({
    indexType: string(),
    params: object({
        page: number(),
        limit: number(),
        year: string(),
    }),
});

// ********************************
// * Exports
// ********************************

// Schemas
export {
    AddressSchema,
    PostalCodeSchema,
    UserInfoSchema,
    HousingCompanySchema,
    BuildingWritableSchema,
    HousingCompanyWritableSchema,
    ApartmentPricesSchema,
    ApartmentSharesSchema,
    ApartmentSchema,
    ApartmentDetailsSchema,
    ApartmentWritableSchema,
    ApartmentWritableFormSchema,
    ApartmentMaximumPriceSchema,
    ApartmentMaximumPrice2011OnwardsSchema,
    ApartmentMaximumPricePre2011Schema,
    ApartmentMaximumPriceWritableSchema,
    HousingCompanyListResponseSchema,
    ApartmentListResponseSchema,
    CodeResponseSchema,
    PostalCodeResponseSchema,
    IndexResponseSchema,
    HousingCompanyApartmentQuerySchema,
    ApartmentQuerySchema,
    IndexQuerySchema,
    ApartmentSaleFormSchema,
    ownerSchema,
    OwnershipFormSchema,
    ownerAPISchema,
    ownershipsSchema,
    ApartmentSaleSchema,
    OwnershipsListSchema,
};

// Types (i.e. models)
export type IAddress = z.infer<typeof AddressSchema>;
export type IImprovement = z.infer<typeof ImprovementSchema>;
export type IHousingCompany = z.infer<typeof HousingCompanySchema>;
export type IHousingCompanyDetails = z.infer<typeof HousingCompanyDetailsSchema>;
export type IHousingCompanyWritable = z.infer<typeof HousingCompanyWritableSchema>;
export type IRealEstate = z.infer<typeof RealEstateSchema>;
export type IBuilding = z.infer<typeof BuildingSchema>;
export type IBuildingWritable = z.infer<typeof BuildingWritableSchema>;
export type IApartmentAddress = z.infer<typeof ApartmentAddressSchema>;
export type IApartmentLinkedModel = z.infer<typeof ApartmentLinkedModelSchema>;
export type IApartmentLinkedModels = z.infer<typeof ApartmentLinkedModelsSchema>;
export type IApartmentUnconfirmedMaximumPrice = z.infer<typeof ApartmentUnconfirmedMaximumPriceSchema>;
export type IApartmentUnconfirmedMaximumPriceIndices = z.infer<typeof ApartmentUnconfirmedMaximumPriceIndicesSchema>;
export type IApartmentConfirmedMaximumPrice = z.infer<typeof ApartmentConfirmedMaximumPriceSchema>;
export type IApartmentPrices = z.infer<typeof ApartmentPricesSchema>;
export type IMarketPriceIndexImprovement = z.infer<typeof MarketPriceIndexImprovementSchema>;
export type IApartmentConstructionPriceIndexImprovement = z.infer<
    typeof ApartmentConstructionPriceIndexImprovementSchema
>;
export type IApartment = z.infer<typeof ApartmentSchema>;
export type IApartmentDetails = z.infer<typeof ApartmentDetailsSchema>;
export type IApartmentWritable = z.infer<typeof ApartmentWritableSchema>;
export type IApartmentWritableForm = z.infer<typeof ApartmentWritableFormSchema>;
export type IApartmentSale = z.infer<typeof ApartmentSaleSchema>;
export type IApartmentSaleForm = z.infer<typeof ApartmentSaleFormSchema>;
export type IApartmentSaleCreated = z.infer<typeof ApartmentSaleCreatedSchema>;
export type IIndexCalculation = z.infer<typeof IndexCalculationSchema>;
export type ICommonCalculationVars = z.infer<typeof CommonCalculationVarsSchema>;
export type ICalculationVars2011Onwards = z.infer<typeof CalculationVars2011OnwardsSchema>;
export type IIndexCalculation2011Onwards = z.infer<typeof IndexCalculation2011OnwardsSchema>;
export type IIndexCalculationMarketPriceIndexBefore2011 = z.infer<
    typeof IndexCalculationMarketPriceIndexBefore2011Schema
>;
export type IIndexCalculationConstructionPriceIndexBefore2011 = z.infer<
    typeof IndexCalculationConstructionPriceIndexBefore2011Schema
>;
export type SurfaceAreaPriceCeilingCalculation = z.infer<typeof SurfaceAreaPriceCeilingCalculationSchema>;
export type IApartmentMaximumPrice = z.infer<typeof ApartmentMaximumPriceSchema>;
export type IApartmentMaximumPrice2011Onwards = z.infer<typeof ApartmentMaximumPrice2011OnwardsSchema>;
export type IApartmentMaximumPricePre2011 = z.infer<typeof ApartmentMaximumPricePre2011Schema>;
export type IApartmentMaximumPriceWritable = z.infer<typeof ApartmentMaximumPriceWritableSchema>;
export type IIndex = z.infer<typeof IndexSchema>;
export type ICode = z.infer<typeof CodeSchema>;
export type IPostalCode = z.infer<typeof PostalCodeSchema>;
export type IPropertyManager = z.infer<typeof PropertyManagerSchema>;
export type IOwner = z.infer<typeof ownerSchema>;
export type IOwnership = z.infer<typeof ownershipSchema>;

// Query/list responses & paging
export type PageInfo = z.infer<typeof PageInfoSchema>;
export type IUserInfoResponse = z.infer<typeof UserInfoSchema>;
export type IHousingCompanyListResponse = z.infer<typeof HousingCompanyListResponseSchema>;
export type IApartmentListResponse = z.infer<typeof ApartmentListResponseSchema>;
export type ICodeResponse = z.infer<typeof CodeResponseSchema>;
export type IPostalCodeResponse = z.infer<typeof PostalCodeResponseSchema>;
export type IIndexResponse = z.infer<typeof IndexResponseSchema>;
export type IHousingCompanyApartmentQuery = z.infer<typeof HousingCompanyApartmentQuerySchema>;
export type IApartmentQuery = z.infer<typeof ApartmentQuerySchema>;
export type IIndexQuery = z.infer<typeof IndexQuerySchema>;

export type IExternalSalesDataResponse = z.infer<typeof ExternalSalesDataResponseSchema>;
export type IApartmentConditionOfSale = z.infer<typeof ApartmentConditionOfSaleSchema>;
export type IConditionOfSale = z.infer<typeof ConditionOfSaleSchema>;
export type ICreateConditionOfSale = z.infer<typeof CreateConditionOfSaleSchema>;
