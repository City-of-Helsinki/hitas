export const isApartmentMaxPriceCalculationValid = (apartment, purchaseDate: string | undefined | null) => {
    if (apartment.prices.maximum_prices.confirmed) {
        const comparisonDate = purchaseDate ? new Date(purchaseDate) : new Date();
        return comparisonDate <= new Date(apartment.prices.maximum_prices.confirmed.valid.valid_until);
    }
    return false;
};
