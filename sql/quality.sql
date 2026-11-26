CREATE VIEW quality_completeness AS
SELECT s.vintage,s.member,p.field,p.denominator,p.present,p.valid,
       1.0*p.present/NULLIF(p.denominator,0) AS completeness_rate,
       1.0*p.valid/NULLIF(p.denominator,0) AS parse_valid_rate
FROM quality_profile p JOIN source s ON s.id=p.source_id;

CREATE VIEW quality_report AS
SELECT s.vintage,s.member,q.field,q.issue,q.count,
       COALESCE(p.denominator,s.records) AS denominator,
       1.0*q.count/NULLIF(COALESCE(p.denominator,s.records),0) AS issue_rate,
       1.0*p.present/NULLIF(p.denominator,0) AS completeness_rate,
       CASE
         WHEN q.issue='row_excluded_missing_identifier' THEN 'critical_error'
         WHEN q.issue IN ('invalid','below_base_price','exceeds_list','field_count_mismatch',
                          'unknown_or_mismatch','conflicting_country_name','without_base_price')
           THEN 'invalid_value'
         WHEN q.issue='missing' AND q.field IN ('sale_price','sale_price_usd','price_max',
                                               'sku_id','variant_sku_ids','variant_count','variation_type')
           THEN 'expected_optional_missing'
         WHEN q.issue IN ('missing','absent','unavailable') THEN 'unknown_or_unavailable'
         ELSE 'quality_warning'
       END AS classification,
       CASE
         WHEN q.issue='row_excluded_missing_identifier' THEN 'critical'
         WHEN q.issue='missing' AND q.field IN ('sale_price','sale_price_usd','price_max',
                                               'sku_id','variant_sku_ids','variant_count','variation_type')
           THEN 'info'
         WHEN q.issue='unavailable' THEN 'info'
         ELSE 'warning'
       END AS severity,
       CASE
         WHEN q.issue='row_excluded_missing_identifier' THEN 'Review source row identifiers before interpreting coverage.'
         WHEN q.issue IN ('exceeds_list','below_base_price','without_base_price') THEN 'Check source price definitions and preserve the raw observation.'
         WHEN q.field='rating' AND q.issue='invalid' THEN 'Inspect the raw rating distribution for possible sentinels.'
         WHEN q.issue IN ('missing','absent','unavailable') THEN 'Keep unknown values blank and report known coverage.'
         ELSE 'Inspect source values and definitions before using affected metrics.'
       END AS recommended_action
FROM quality q JOIN source s ON s.id=q.source_id
LEFT JOIN quality_profile p ON p.source_id=q.source_id AND p.field=q.field;
