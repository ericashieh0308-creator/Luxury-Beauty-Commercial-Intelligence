"""Illustrative USD model. Expenses and deductions are positive magnitudes."""
from dataclasses import dataclass, replace
from math import isfinite

@dataclass(frozen=True)
class Drivers:
    price: float = 65
    cost: float = 23
    units: float = 1000
    discount: float = .08
    returns: float = .06
    online: float = .40
    fulfillment: float = 4
    fees: float = .025
    other_variable: float = .04
    fixed: float = 16000
    marketing: float = 700
    return_handling: float = 2

    def __post_init__(self):
        for name, value in vars(self).items():
            if not isfinite(value) or value < 0:
                raise ValueError(f"{name} must be finite and nonnegative")
            if name in {"discount", "returns", "online", "fees", "other_variable"} and value > 1:
                raise ValueError(f"{name} must be a fraction from 0 to 1")

def ratio(numerator, denominator):
    return numerator / denominator if denominator else None

def pnl(d):
    gross = d.price * d.units
    discounts = gross * d.discount
    returns = (gross - discounts) * d.returns
    revenue = gross - discounts - returns
    cogs = d.cost * d.units * (1 - d.returns)
    gp = revenue - cogs
    fulfillment = d.units * d.online * d.fulfillment
    fees = revenue * d.fees
    handling = d.units * d.returns * d.return_handling
    variable = fulfillment + fees + handling + revenue * d.other_variable + d.marketing
    contribution = gp - variable
    operating = contribution - d.fixed
    return dict(gross_sales=gross, discounts=discounts, returns=returns, net_revenue=revenue,
                cogs=cogs, gross_profit=gp, gross_margin=ratio(gp, revenue), fulfillment=fulfillment,
                payment_fees=fees, return_handling=handling, marketing=d.marketing,
                variable_expenses=variable, contribution=contribution, fixed=d.fixed,
                operating_profit=operating, operating_margin=ratio(operating, revenue))

def channels(d):
    return {name: pnl(replace(d, units=d.units * share, online=online, fixed=0,
                              marketing=d.marketing * share))
            for name, share, online in (("Store", 1-d.online, 0), ("E-commerce", d.online, 1))}

SCENARIOS = {"Base": (.04, .03, 0), "Bull": (.12, .01, -.02), "Bear": (-.08, .09, .05)}
SEASONALITY = (.86, .88, .94, .95, .97, .98, .95, .97, 1, 1.04, 1.17, 1.29)
SKU_MIX = {"Core": (.70, .90, .91), "Premium": (.30, 1.23, 1.21)}

def forecast(d, growth, inflation, discount_delta=0, seasonality=1, premium_mix=.30):
    if not 0 <= premium_mix <= 1 or not 0 <= seasonality <= 1:
        raise ValueError("Premium mix and seasonality must be between 0 and 1")
    for month, index in enumerate(SEASONALITY, 1):
        sku_rows = {}
        for name, (_, price_factor, cost_factor) in SKU_MIX.items():
            mix = premium_mix if name == "Premium" else 1 - premium_mix
            sku_rows[name] = pnl(replace(d, price=d.price * price_factor,
                cost=d.cost * cost_factor * (1 + inflation), discount=min(1, max(0, d.discount + discount_delta)),
                units=d.units * (1 + growth) * (1 + seasonality * (index - 1)) * mix,
                fixed=d.fixed * mix, marketing=d.marketing * mix))
        total = {k: sum(row[k] for row in sku_rows.values()) for k in sku_rows["Core"]
                 if k not in {"gross_margin", "operating_margin"}}
        total["gross_margin"] = ratio(total["gross_profit"], total["net_revenue"])
        total["operating_margin"] = ratio(total["operating_profit"], total["net_revenue"])
        yield month, total, sku_rows

def variance(budget, actual):
    return {key: (actual[key] - value, ratio(actual[key] - value, abs(value)),
                  "Favorable" if (actual[key] - value) * sign > 0 else
                  "Unfavorable" if actual[key] != value else "On plan")
            for key, sign in (("net_revenue", 1), ("gross_profit", 1),
                              ("variable_expenses", -1), ("fixed", -1), ("operating_profit", 1))
            for value in (budget[key],)}

def promotion(d, discount, response, campaign):
    if response < -1 or not isfinite(response) or campaign < 0 or not isfinite(campaign):
        raise ValueError("Invalid volume response or campaign cost")
    proposed = replace(d, discount=discount, units=d.units * (1 + response), marketing=d.marketing + campaign)
    before, after = pnl(d), pnl(proposed)
    unit = pnl(replace(proposed, units=1, marketing=0))["contribution"]
    required = before["contribution"] + proposed.marketing
    breakeven = max(0, required / unit) if unit > 0 else None
    retained = proposed.units * (1 - proposed.returns)
    coefficient = proposed.price * retained * (1 - proposed.fees - proposed.other_variable)
    undiscounted = pnl(replace(proposed, discount=0))["contribution"]
    max_discount = ratio(undiscounted - before["contribution"], coefficient) if coefficient > 0 else None
    delta = after["contribution"] - before["contribution"]
    return dict(before=before, after=after, incremental_units=proposed.units - d.units,
                incremental_revenue=after["net_revenue"]-before["net_revenue"],
                incremental_gp=after["gross_profit"]-before["gross_profit"],
                incremental_contribution=delta, roi=ratio(delta, campaign), breakeven_units=breakeven,
                required_uplift=breakeven / d.units - 1 if breakeven is not None and d.units else None,
                breakeven_discount=max_discount if max_discount is not None and 0 <= max_discount <= 1 else None,
                margin_dilution=after["gross_margin"]-before["gross_margin"]
                if after["gross_margin"] is not None and before["gross_margin"] is not None else None)

def pvm(budget, actual):
    """Map SKU to (units, net price). Allocate shared SKU variance volume-first."""
    shared = budget.keys() & actual.keys()
    bu = sum(budget[k][0] for k in shared)
    au = sum(actual[k][0] for k in shared)
    br = sum(budget[k][0] * budget[k][1] for k in shared)
    avg = br / bu if bu else 0
    volume = (au-bu)*avg
    mix = sum(actual[k][0]*budget[k][1] for k in shared) - br - volume
    price = sum(actual[k][0]*(actual[k][1]-budget[k][1]) for k in shared)
    new = sum(actual[k][0]*actual[k][1] for k in actual.keys()-shared)
    removed = -sum(budget[k][0]*budget[k][1] for k in budget.keys()-shared)
    delta = sum(u*p for u,p in actual.values()) - sum(u*p for u,p in budget.values())
    return dict(price=price, volume=volume, mix=mix, new=new, removed=removed,
                total=delta, residual=delta-price-volume-mix-new-removed)
