# ZERODOWN

# 21PW08 - JENISA MERLIN D

Problem Statement 1

PriceProbe: Predicting Property Values

In the dynamic realm of US real estate, accurate pricing stands as the cornerstone of successful
transactions. With the market constantly evolving and property values fluctuating, the ability to
determine fair and competitive prices is paramount. Using the partial raw market data
provided, your task is to predict home prices for properties listed for sale, by progressing
through the following milestones.

Milestones:
1. ERD: Add entity relationship diagram based on DDL statements provided.
2. EDA:
● Range of attributes
● Geographical spread
● Temporal spread
● Identify outlier homes and homes with incorrect data
3. Homes Deduplication: Devise an scalable algorithm to identify duplicate homes.
Duplicates can be classified into 2 types, identify both separately.
● Absolute duplicate - same home, listed in the market at almost same time.
● Pseudo duplicate - same home, listed at different points in time.
4. Home Comparables: Given a home id, devise an algorithm to provide a list of similar
homes.
5. Price Estimation: Given home attributes(bed, bath, city/zipcode etc...) estimate price
based on sold homes.

Note:
1. For comparables & price estimation, bed, bath, city/zipcode will be mandatory inputs.
Other attributes like finished_sqft, lot_size_sqft, home_type, etc… can be optional
inputs.
2. Preferably, use PostgreSQL database.

Data:
home_info.sql
market.sql
market_geom.sql

# MILESTONE 1
ERD is attached

* each market has one market_geom
* each market has one home_info
* market has market_geom and home_info

# MILESTONE 2
EDA: Exploratory Data Analysis

Attributes in the table,

1. Table: market
Attributes:
- id: SERIAL (auto-incrementing integer)
- name: VARCHAR(255) (name of the market)
- market_level: VARCHAR(255) (level of the market)
- state: VARCHAR(32) (state of the market)
- city: VARCHAR(100) (city of the market)
- zipcode: VARCHAR(10) (zipcode of the market)
- neighborhood: VARCHAR(255) (neighborhood of the market)
- neighborhood_source: VARCHAR(255) (source of neighborhood data)

2. Table: market_geom
Attributes:
- id: int4 (auto-incrementing integer)
- market_id: int4 (foreign key referencing the "id" column in the "market" table)
- longitude: numeric(11,8) (longitude coordinate)
- latitude: numeric(11,8) (latitude coordinate)
- geom: geometry(MultiPolygon,4269) (geometric data representing a MultiPolygon)
- area_in_sq_mi: float8 (area in square miles)
- centroid_geom: geometry(Point,4269) (geometric data representing a Point)

3. Table: home_info
Attributes:
- id: int4 (unique identifier for each home)
- listing_key: varchar(64) (key for the home listing)
- source_system: varchar(32) (source system of the listing)
- address: varchar(256) (address of the home)
- usps_address: varchar(256) (USPS standardized address)
- status: varchar(256) (status of the listing)
- listing_contract_date: timestamp (date of the listing contract)
- on_market_date: timestamp (date when the home was listed on the market)
- pending_date: timestamp (date when the listing became pending)
- last_sold_date: timestamp (date when the home was last sold)
- off_market_date: timestamp (date when the home was taken off the market)
- original_listing_price: numeric(12,2) (original listing price of the home)
- listing_price: numeric(12,2) (current listing price of the home)
- last_sold_price: numeric(12,2) (price at which the home was last sold)
- home_type: varchar(255) (type of home)
- finished_sqft: int4 (finished square footage of the home)
- lot_size_sqft: int4 (lot size in square footage)
- bedrooms: int4 (number of bedrooms)
- bathrooms: float4 (number of bathrooms)
- year_built: int4 (year the home was built)
- new_construction: bool (indicator if the home is new construction)
- has_pool: bool (indicator if the home has a pool)
- state_market_id: int4 (foreign key referencing a market in the "market" table)
- city_market_id: int4 (foreign key referencing a market in the "market" table)
- zipcode_market_id: int4 (foreign key referencing a market in the "market" table)
- neighborhood_level_1_market_id: int4 (foreign key referencing a market in the "market" table)
- neighborhood_level_2_market_id: int4 (foreign key referencing a market in the "market" table)
- neighborhood_level_3_market_id: int4 (foreign key referencing a market in the "market" table)
- long: numeric(11,8) (longitude coordinate of the home)
- lat: numeric(11,8) (latitude coordinate of the home)
- crawler: varchar(32) (source of the listing data)

1) Range of attributes
    *unique
    *null or missing values
    *numeric attributes
    *correlation
    *summary statistics
    
* Listing price: range of listing price to know the spread of property values
* Finished sqft and Lot size sqft: distribution of property sizes
* Bedrooms and bathrooms: variation in number of bedrooms and bathrooms
* Year built: age distribution by analysing range of construction years
* Original listing price and last sold price: changes in prices over time

2) Geographical Spread

* Visualize the distribution of markets using latitude and longitude
* Analyse and visualize the spread of markets across different regions or states
* Calculate and visualize Area covered by each market

3) Temporal Spread
* Analyze the distribution of Listing Contract Date, On Market Date, Off Market Date to understand listing durations and market trends over time.
* additionally, 
    * Time Series Analysis: Plotting trends of listing prices and last sold prices over time.
    * Seasonality Analysis: Analyzing seasonal patterns in listing prices.
    * Day of the Week Analysis: Analyzing the distribution of listing contract dates by day of the week.
    * Time to Sale Analysis: Analyzing the distribution of time to sale for properties.

4) Identify outlier homes and homes with incorrect data
* analyse outliers using **z-score** 
* visualize using **boxplots**
* print incorrect data from predefined conditions

# MILESTONE 3
Homes Deduplication: Devise an scalable algorithm to identify duplicate homes.
Duplicates can be classified into 2 types, identify both separately.
● Absolute duplicate - same home, listed in the market at almost same time.
● Pseudo duplicate - same home, listed at different points in time

# MILESTONE 4
Home Comparables: Given a home id, devise an algorithm to provide a list of similar
homes
Created a common table expression, from where similarity score is calculated using Euclidean distance b/w given home id and other homes and returning the top 10 homes

# MILESTONE 5
Price Estimation: Given home attributes(bed, bath, city/zipcode etc...) estimate price
based on sold homes.