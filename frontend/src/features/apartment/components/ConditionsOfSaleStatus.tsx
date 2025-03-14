import {IconLock, IconLockOpen, IconSize, StatusLabel} from "hds-react";

import {IApartment, IApartmentConditionOfSale, IApartmentDetails} from "../../../common/schemas";
import {formatDate} from "../../../common/utils";

type IConditionsOfSaleStatus = (
    | {
          apartment: IApartment | IApartmentDetails;
          conditionOfSale?: never;
      }
    | {
          apartment?: never;
          conditionOfSale: IApartmentConditionOfSale;
      }
) & {
    withSellByDate?: boolean;
};

const ConditionsOfSaleStatusText = ({hasGracePeriod, sellByDate}) => {
    return (
        <>
            {hasGracePeriod ? "+" : null}
            <span className="sell-by-date">&nbsp;{formatDate(sellByDate)}</span>
        </>
    );
};

// Only either apartment or conditionOfSale should be passed as props
const ConditionsOfSaleStatus = ({apartment, conditionOfSale, withSellByDate = true}: IConditionsOfSaleStatus) => {
    let sellByDate;
    let hasGracePeriod;
    let fulfilled;

    if (apartment) {
        sellByDate = apartment.sell_by_date;
        // IApartment
        if ("has_grace_period" in apartment) {
            if (!apartment.has_conditions_of_sale) {
                return null;
            }
            hasGracePeriod = apartment.has_grace_period;
            fulfilled = false; // Never fulfilled in apartment list api, any fulfilled COS are not shown.
        }
        // IApartmentDetails
        else {
            hasGracePeriod = !!apartment.conditions_of_sale.find((cos) => cos.grace_period !== "not_given");
            fulfilled = !apartment.conditions_of_sale.find((cos) => cos.fulfilled === null);
        }
    } else {
        sellByDate = conditionOfSale.sell_by_date;
        hasGracePeriod = conditionOfSale.grace_period !== "not_given";
        fulfilled = conditionOfSale.fulfilled;
    }

    const getConditionsOfSaleStatusLabelType = () => {
        if (!!fulfilled || sellByDate === null) return "neutral";
        const sbd = new Date(sellByDate);
        const today = new Date();
        if (today >= sbd) return "error";
        sbd.setMonth(sbd.getMonth() - 1);
        if (today >= sbd) return "alert";
        return "neutral";
    };

    return (
        <StatusLabel
            className={`conditions-of-sale-status${withSellByDate ? " conditions-of-sale-status--with-date" : ""}`}
            type={getConditionsOfSaleStatusLabelType()}
            iconStart={fulfilled ? <IconLockOpen size={IconSize.Small} /> : <IconLock size={IconSize.Small} />}
        >
            {withSellByDate ? (
                <ConditionsOfSaleStatusText
                    hasGracePeriod={hasGracePeriod}
                    sellByDate={sellByDate}
                />
            ) : null}
        </StatusLabel>
    );
};

export default ConditionsOfSaleStatus;
