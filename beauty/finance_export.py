"""Export the simulated planning facts used by Power BI and the case study."""
from pathlib import Path
import csv

from .finance import Drivers, SCENARIOS, SEASONALITY, SKU_MIX, channels, forecast, promotion, pvm, ratio, variance

def build(target):
    target.mkdir(parents=True, exist_ok=True)
    d = Drivers()
    cases = {name: list(forecast(d,*drivers)) for name,drivers in SCENARIOS.items()}
    def write(name, rows):
        rows = list(rows)
        with (target/f"{name}.csv").open("w",newline="",encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f,fieldnames=["evidence", *rows[0]])
            writer.writeheader()
            writer.writerows({"evidence":"SIMULATED",**row} for row in rows)
    write("finance_assumptions", (dict(driver=k,value=v) for k,v in vars(d).items()))
    write("fact_simulated_finance", (dict(scenario=name,month=month,**numbers)
                                    for name, rows in cases.items() for month,numbers,_ in rows))
    write("fact_simulated_sku", (dict(scenario=name,month=month,sku=sku,**row)
                                for name, rows in cases.items() for month,_,details in rows
                                for sku,row in details.items()))
    write("fact_simulated_channel", (dict(channel=name,**row) for name,row in channels(d).items()))
    def bridge():
        for (month,_,base_skus),(_,_,actual_skus) in zip(cases["Base"],cases["Bull"]):
            def units_and_prices(skus, growth):
                return {sku: (units, ratio(row["net_revenue"],units) or 0)
                        for sku,row in skus.items()
                        for units in (d.units*(1+growth)*SEASONALITY[month-1]*SKU_MIX[sku][0],)}
            yield dict(month=month, budget_case="Base", simulated_actual_case="Bull",
                       **pvm(units_and_prices(base_skus, SCENARIOS["Base"][0]),
                             units_and_prices(actual_skus, SCENARIOS["Bull"][0])))
    write("fact_simulated_pvm", bridge())
    write("fact_simulated_promotion", (dict(discount=x,uplift=y,**{k:v for k,v in
        promotion(d,x,y,1500).items() if k not in {"before","after"}})
        for x in (0,.05,.10,.15,.20,.25,.30) for y in (0,.10,.20,.30,.40)))
    ytd = {}
    def variances():
        for (month,budget,_),(_,actual,_) in zip(cases["Base"],cases["Bull"]):
            for key,(delta,pct,status) in variance(budget,actual).items():
                ytd[key] = ytd.get(key,0)+delta
                yield dict(month=month,metric=key,budget=budget[key],simulated_actual=actual[key],
                           variance=delta,variance_pct=pct,direction=status,ytd_variance=ytd[key])
    write("fact_simulated_variance", variances())

if __name__ == "__main__":
    build(Path("output/finance"))
