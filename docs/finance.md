# Commercial finance model

USD is the functional currency. Operating inputs are illustrative modeled assumptions. Any CAD view uses a hypothetical rate.

| Component | Calculation and business use |
|---|---|
| Gross sales | Ordered units × list price |
| Discounts | Gross sales × discount rate |
| Returns | Discounted sales × return rate. Returned demand is assumed restockable |
| Net revenue | Gross sales less discounts and returns |
| COGS | Unit cost × ordered units × retained fraction |
| Gross profit | Net revenue less COGS |
| Gross margin | Gross profit ÷ net revenue. Blank on zero revenue |
| Variable selling costs | Online units × fulfillment cost, plus payment fees and variable costs on net revenue, handling cost on returns and marketing |
| Contribution profit | Gross profit less variable selling costs |
| Operating profit | Contribution less fixed operating costs |
| Budget variance | Simulated actual less Base budget. Positive movement is favorable for profits and revenue, unfavorable for expense. Divide by absolute budget if nonzero |
| Forecast | Monthly baseline demand × annual case growth factor × monthly seasonal factor, then allocate by adjustable Core/Premium mix. Apply case cost inflation and discount movement |
| SKU economics | Modeled price and cost by SKU. Test a 10% cost increase. Evaluate gross profit contribution before invoking popularity |
| Channel contribution | Shared price and gross-margin assumptions. Allocate orders and marketing by online share; fulfillment applies only to online orders |
| Promotion ROI | Incremental contribution after campaign expense ÷ campaign cost. This may be negative despite incremental revenue |
| Breakeven volume | Baseline contribution plus post-promotion marketing, divided by contribution per promotional unit before marketing. A nonpositive unit contribution has no standard finite target |
| Breakeven discount | Solve participation contribution equal to baseline at projected volume and fixed campaign cost. Report only feasible rates from 0 to 100% |
| PVM | Shared mix uses baseline net prices. Volume uses baseline average price, price uses actual units, mix takes the remaining shared unit dispersion. Separately add new product revenue and deduct removed product revenue |

Costs and deductions appear as positive magnitudes. Annual margins use annual numerator and denominator instead of averaging monthly percentages. Budget and scenario operating profit bridges reconcile through gross profit and expense variances. The workbook uses two shared illustrative SKUs; Python PVM also handles new and removed product effects. Forecast cases are planning assumptions. Use margin and return evidence from transactions to recalibrate the forecast or the promotion model.

Open Excel and calculate with **F9** when opening or editing the generated workbook. The model checks tab contains five reconciliations. The Steamlit simulator applies independent volume response, displays scenario comparisons and provides an explicit hypothetical inventory buffer. The positioning pressure heuristic measures only the discount settings in the simulator.
