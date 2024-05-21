import {boolean, number, object, string, z} from "zod";
import {APIIdString, errorMessages, PageInfoSchema} from "./common";

// ********************************
// * Owner
// ********************************

export const OwnerSchema = object({
    id: APIIdString,
    name: string({required_error: errorMessages.required})
        .min(2, errorMessages.stringLength)
        .max(256, errorMessages.stringMaxIs + "256"),
    identifier: string({required_error: errorMessages.required})
        .min(1, errorMessages.required)
        .max(11, errorMessages.stringMaxIs + "11"),
    email: string().email(errorMessages.emailInvalid).nullish().or(z.literal("")),
    non_disclosure: boolean(),
});
export type IOwner = z.infer<typeof OwnerSchema>;

// ********************************
// * Ownership
// ********************************

export const OwnershipSchema = object({
    key: z.any().optional(),
    owner: OwnerSchema,
    percentage: z
        .number({invalid_type_error: errorMessages.numberType, required_error: errorMessages.required})
        .positive(errorMessages.numberPositive)
        .max(100, errorMessages.numberMax),
});
export type IOwnership = z.infer<typeof OwnershipSchema>;

// Writable list of ownerships
export const OwnershipsListSchema = object({
    owner: object({id: APIIdString.optional().or(z.literal(""))}, {required_error: errorMessages.ownerIsRequired}),
    percentage: number({invalid_type_error: errorMessages.numberType, required_error: errorMessages.required})
        .multipleOf(0.01, errorMessages.maxTwoDecimalPlaces)
        .positive(errorMessages.numberPositive),
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
                message: errorMessages.ownerIsRequired,
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
                message: errorMessages.ownershipPercentSum,
            });
        }
    });

// ********************************
// * API
// ********************************

export const OwnersResponseSchema = object({
    page: PageInfoSchema,
    contents: OwnerSchema.array(),
});
export type IOwnersResponse = z.infer<typeof OwnersResponseSchema>;

export const FilterOwnersQuerySchema = object({
    name: string().optional(),
    identifier: string().optional(),
    email: string().optional(),
    limit: number().int().optional(),
    page: number().int().optional(),
});
export type IFilterOwnersQuery = z.infer<typeof FilterOwnersQuerySchema>;

export const OwnerMergeDataSchema = object({
    first_owner_id: APIIdString,
    second_owner_id: APIIdString,
    should_use_second_owner_name: boolean(),
    should_use_second_owner_identifier: boolean(),
    should_use_second_owner_email: boolean(),
});
export type IOwnerMergeData = z.infer<typeof OwnerMergeDataSchema>;
