import {IconLock, IconLockOpen, StatusLabel} from "hds-react";

import {IApartment, IApartmentConditionOfSale, IApartmentDetails} from "../../../common/schemas";
import {formatDate} from "../../../common/utils";

type IConditionsOfSaleStatus =
    | {
          apartment: IApartment | IApartmentDetails;
          conditionOfSale?: never;
      }
    | {
          apartment?: never;
          conditionOfSale: IApartmentConditionOfSale;
      };

const ConditionsOfSaleStatus = ({apartment, conditionOfSale}: IConditionsOfSaleStatus) => {
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
        if (sellByDate === null) return "neutral";
        const sbd = new Date(sellByDate);
        const today = new Date();
        if (today >= sbd) return "error";
        sbd.setMonth(sbd.getMonth() - 1);
        if (today >= sbd) return "alert";
        return "neutral";
    };

    return (
        <StatusLabel
            className="conditions-of-sale-status"
            type={getConditionsOfSaleStatusLabelType()}
            iconLeft={fulfilled ? <IconLockOpen size="s" /> : <IconLock size="s" />}
        >
            {hasGracePeriod ? "+" : null}
            <span className="sell-by-date">&nbsp;{formatDate(sellByDate)}</span>
        </StatusLabel>
    );
};

export default ConditionsOfSaleStatus;
