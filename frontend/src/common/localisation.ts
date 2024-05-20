import {IApartment, IApartmentConditionOfSale, IApartmentDetails} from "./schemas";

export const getHousingCompanyHitasTypeName = (state) => {
    switch (state) {
        case "non_hitas":
            return "Ei Hitas";
        case "hitas_1":
            return "Hitas I";
        case "hitas_2":
            return "Hitas II";
        case "hitas_1_no_interest":
            return "Hitas I, Ei korkoja";
        case "hitas_2_no_interest":
            return "Hitas II, Ei korkoja";
        case "new_hitas_1":
            return "Uusi Hitas I";
        case "new_hitas_2":
            return "Uusi Hitas II";
        case "half_hitas":
            return "Puolihitas";
        case "rental_hitas_1":
            return "Vuokratalo Hitas I";
        case "rental_hitas_2":
            return "Vuokratalo Hitas II";
        case "rr_new_hitas":
            return "RR Uusi Hitas";
        default:
            return "VIRHE";
    }
};

export const getHousingCompanyRegulationStatusName = (state) => {
    switch (state) {
        case "regulated":
            return "Ei vapautunut";
        case "released_by_hitas":
            return "Vapautunut vertailussa";
        case "released_by_plot_department":
            return "Vapautunut tontit-yksikön päätöksellä";
        default:
            return "VIRHE";
    }
};

export function getIndexType(indexType: string) {
    switch (indexType) {
        case "market_price_index":
            return "markkinahintaindeksi";
        case "construction_price_index":
            return "rakennuskustannusindeksi";
        case "surface_area_price_ceiling":
            return "rajaneliöhintaindeksi";
        default:
            return "VIRHE";
    }
}

export const getApartmentSoldStatusLabel = (apartment: IApartment | IApartmentDetails) => {
    if (apartment.is_sold) {
        return "Myyty";
    }
    return "Vapaa";
};

export const getConditionOfSaleGracePeriodLabel = (conditionOfSale: IApartmentConditionOfSale) => {
    switch (conditionOfSale.grace_period) {
        case "three_months":
            return "3kk";
        case "six_months":
            return "6kk";
        default:
            return "Ei lisäaikaa";
    }
};
