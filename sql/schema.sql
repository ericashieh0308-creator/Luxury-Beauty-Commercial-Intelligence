PRAGMA foreign_keys=ON;
CREATE TABLE source (id INTEGER PRIMARY KEY, vintage TEXT NOT NULL, member TEXT NOT NULL, sha256 TEXT NOT NULL, headers TEXT NOT NULL);
CREATE TABLE dim_brand (brand TEXT PRIMARY KEY);
CREATE TABLE dim_category (category TEXT PRIMARY KEY);
CREATE TABLE dim_market (market TEXT PRIMARY KEY, currency TEXT NOT NULL);
INSERT INTO dim_market VALUES ('US','USD'),('CA','CAD');
CREATE TABLE fact_product_snapshot (
 id INTEGER PRIMARY KEY, source_id INTEGER NOT NULL REFERENCES source, line INTEGER NOT NULL,
 snapshot TEXT, market TEXT NOT NULL, currency TEXT, product TEXT NOT NULL, sku TEXT, brand TEXT,
 name TEXT, category TEXT, subcategory TEXT, size TEXT, variant TEXT, price REAL, sale REAL,
 rating REAL, engagement INTEGER, exclusive INTEGER, online INTEGER, limited INTEGER,
 bestseller INTEGER, new_arrival INTEGER, promotion INTEGER, out_of_stock INTEGER, UNIQUE(source_id,line)
);
CREATE TABLE fact_review (
 source_id INTEGER NOT NULL REFERENCES source, line INTEGER NOT NULL, product TEXT NOT NULL,
 rating REAL, review_date TEXT, sentiment INTEGER, PRIMARY KEY(source_id,line)
);
CREATE TABLE review_topic (product TEXT NOT NULL, topic TEXT NOT NULL, mentions INTEGER NOT NULL,
 PRIMARY KEY(product,topic));
CREATE TABLE quality (source_id INTEGER NOT NULL REFERENCES source, field TEXT NOT NULL,
 issue TEXT NOT NULL, count INTEGER NOT NULL, PRIMARY KEY(source_id,field,issue));
CREATE TABLE bridge_product_match (
 left_id INTEGER NOT NULL REFERENCES fact_product_snapshot, right_id INTEGER NOT NULL REFERENCES fact_product_snapshot,
 comparison TEXT NOT NULL, method TEXT NOT NULL, status TEXT NOT NULL, PRIMARY KEY(left_id,right_id,comparison));
CREATE TABLE fact_industry_benchmark (
 organization TEXT, title TEXT, publication_date TEXT, measurement_period TEXT, geography TEXT,
 metric TEXT, value REAL, units TEXT, url TEXT, access_date TEXT, limitations TEXT);
CREATE VIEW fact_sku_snapshot AS SELECT * FROM fact_product_snapshot WHERE sku IS NOT NULL;
CREATE VIEW dim_product AS SELECT DISTINCT market,product,brand,name FROM fact_product_snapshot;
CREATE VIEW dim_date AS SELECT DISTINCT snapshot FROM fact_product_snapshot WHERE snapshot IS NOT NULL;
