-- One product row per snapshot first. Do not sum repeated counts across flag metrics.
SELECT market, snapshot, segment, products, assortment_share, median_price
FROM commercial_kpi WHERE dimension='category' AND metric='promotion';

-- Observed review lexicon aggregates, historical only.
SELECT r.product, r.reviews, r.mean_rating, t.topic, t.mentions
FROM review_summary r JOIN review_topic t USING(product) ORDER BY t.mentions DESC;

-- Matched list price coverage by method and review status.
SELECT * FROM match_coverage ORDER BY comparison, status, method;

-- Published currency and date must be present for normalized market comparisons.
SELECT * FROM price_comparison WHERE comparison='cross_market' AND fx IS NOT NULL;
