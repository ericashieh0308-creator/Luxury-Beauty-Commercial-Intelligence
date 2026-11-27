# Learning and interview guide

Start with one source file and follow it into the snapshot table, the pricing exports, and the Power BI layout. In SQL, `WHERE` filters rows before aggregation, `GROUP BY` sets the grain, and a join is valid only when its keys preserve the intended number of rows. Run the query library and explain one row from each query in business language. Then open Excel, change the case selector, and trace one month's operating profit through discounts, costs and contribution. Use the simulator to change one driver at a time before interpreting joint sensitivity.

## Read the exhibits

The median price tells you where the typical listed product sits, whereas a histogram shows whether several clusters or a long tail drive the distribution. Brand-category cells show breadth by portfolio segment. Price–rating scatter and engagement matrices describe catalog associations. Matched-gap charts summarize pairs that passed comparability checks. Always read match coverage with the distribution. A P&L waterfall displays the arithmetic deductions from sales to profit. Scenario lines show the modeled path under different assumptions. The sensitivity grid highlights which discount/volume combinations would create or destroy contribution.

## Sample questions and answers

1. **What decision does this support?** It tests how price mix and promotion assumptions affect simulated contribution and separates that decision from catalog observations.
2. **Why beauty retail?** Assortments combine market-specific price ladders, promotional practices and brand positioning, which makes merchandising and finance inseparable.
3. **What is the grain of an input snapshot row?** One file record, carrying local market, product and where present SKU identifiers, with source lineage.
4. **What is assortment share?** Segment product representatives divided by all included product representatives in the same cohort.
5. **How do you handle duplicated keys?** Preserve source rows, emit a diagnostic and avoid treating ambiguous parents as known product representatives.
6. **How do nulls affect KPIs?** Shares use known flag responses and disclose coverage. Prices exclude invalid or currency-incompatible observations.
7. **Why report median price?** It is a central measure less sensitive to long premium price tails; show dispersion too.
8. **How do you define premium?** Within eligible category cohorts, use quartile bands and a documented price-rank and exclusivity proxy.
9. **What would cause an unstable tier?** Small cohorts, repeated prices and changing assortment. Fixed baseline cutpoints help assess migration.
10. **How do you interpret bestseller flags?** Treat flags as source-provided popularity signals. Actual units require transaction data.
11. **How is discount depth calculated?** One minus sale price divided by positive list price, conditional on a comparable sale observation.
12. **Why block matching by brand?** It reduces unrelated candidates and supports defensible product identity comparison.
13. **How do fuzzy matches enter the comparison?** Similarity only creates review candidates; ambiguous or unverified pairs stay out of quantitative results.
14. **How do you control for product size?** Require exact normalized size strings, including units, and inspect variant and packaging changes.
15. **Why can matched inflation differ from an assortment average?** It holds product identity more consistently and adjusts the matched price ratio by the CPI ratio.
16. **How do you convert Canadian prices?** Multiply CAD list by dated USD per CAD and compare with USD list for the same matched item and date.
17. **What if no rate is available?** Keep native prices and leave converted gaps blank pending a dated reference.
18. **How does FX sensitivity work?** Apply ±5% to USD per CAD, keeping matched native list prices fixed.
19. **How do you identify review pain points?** Count transparent topic terms per product and verify context in a locally reviewed sample.
20. **Why validate sentiment manually?** Lexicon scores miss negation and context, and stars represent an imperfect proxy for text sentiment.
21. **How do you get net revenue?** Deduct the discount from gross sales, then apply returns to the resulting discounted sales.
22. **How do gross and contribution margin differ?** Gross margin deducts product cost; contribution also deducts the variable selling expenses defined in the model.
23. **How do you calculate annual gross margin?** Divide total annual gross profit by total annual net revenue.
24. **When is an expense variance favorable?** When simulated actual expense is below budget, given the defined spending scope.
25. **What does the forecast predict?** A conditional financial outcome given case drivers and seasonal factors. It has no estimated accuracy against company results.
26. **Why separate online and store?** The model can isolate fulfillment and allocation costs even when shared prices and COGS are assumed.
27. **Can higher revenue hurt a promotion?** Yes. Discounts and campaign costs can outweigh incremental unit contribution.
28. **What is the promotion ROI denominator?** Incremental campaign cost. Incremental contribution already includes that cost.
29. **What does contribution breakeven mean here?** The units needed to achieve baseline contribution after the campaign expense at the proposed price.
30. **Explain PVM.** Volume uses average baseline price, mix uses baseline price dispersion, and price uses actual units. Reconcile all effects to actual minus budget revenue.
31. **What is tested in the workbook?** Formulas, required tabs, case output agreement with Python and five financial reconciliations after headless recalculation.
32. **What would you request before making a retailer recommendation?** Transactions, returns, landed costs, channel fees, inventory and a credible experiment for volume response.

## Project pitches

**30 seconds.** I built an independent beauty retail decision platform that pairs conservative catalog price analytics with a simulated planning model. I use Python and SQLite for source validation and matching, then Excel and Streamlit to test whether a promotion generates enough contribution to justify the spend.

**60 seconds.** I wanted to connect merchandising questions to financial decisions. The pipeline preserves local currency, data lineage and unknown flags. It compares products that match on size and variant and flags ambiguous matches for review. The financial model builds P&L and forecast scenarios from explicit assumed costs and units. In the base promotion example, modeled revenue increases by about $6,100 while contribution declines about $455. That illustrates why I would require evidence about volume response before spending.

**Three minutes.** Start with the commercial decision. A planning team wants to find price and portfolio opportunities while protecting margin. The platform first validates source schemas, prices and review fields and tracks the file and record behind each output. Walk through the price ladder: within a snapshot, markets and categories define price cohorts and quartiles. Show how currency, size, variant and date controls reduce misleading cross-market comparisons. Explain that two catalog snapshots and platform engagement cannot reveal demand elasticity.

Next walk through the financial decision. The workbook models an illustrative retailer, starting with ordered units and list price, then discounts and returns. From net revenue it deducts retained-unit COGS and variable selling costs to get contribution, then fixed costs to get operating profit. Demonstrate the model in Streamlit by changing volume response while holding the campaign discount fixed. Explain that at 15% discount and 20% more orders, the example lifts sales but falls short of contribution breakeven. At least 1,219 modeled whole units are needed.

Close with verification and next steps. Python and recalculated spreadsheet outputs agree across the three scenarios, and the match logic is tested with synthetic data. Real catalog evidence needs documented dates, licensing and schema checks. Real promotion adoption would require actual costs, transaction-level returns and experimental response evidence.

**How do you explain a header-only price comparison file?** Check `comparison_coverage` before drawing a conclusion. Candidate pairs measure what merits examination. Accepted pairs require corroborated specifications and mutual uniqueness. Price gaps additionally need point prices, correct currency and, for cross-market gaps, a dated FX observation. A blank gap means insufficient evidence.

**What do you do with a 0-star source entry?** Check the raw distribution and source definition. The 1–5 model excludes zero from rated denominators and preserves the original value locally. Treat it as a possible sentinel until the provider confirms the meaning.
