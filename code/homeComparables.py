import psycopg2
import db

# Connect to the PostgreSQL database
conn = db.connect_to_database()

# Function to execute the SQL query
def execute_query(query):
    cur = conn.cursor()
    cur.execute(query)
    rows = cur.fetchall()
    return rows

# Get user input for home ID, number of bedrooms, number of bathrooms, and city code
home_id = input("Enter the home ID: ")
bedrooms = input("Enter the number of bedrooms: ")
bathrooms = input("Enter the number of bathrooms: ")
city_code = input("Enter the city code: ")

# Construct the SQL query with user input
sql_query = f"""
WITH input_home AS (
    SELECT
        id,
        bedrooms,
        bathrooms,
        city_market_id,
        zipcode_market_id,
        finished_sqft,
        lot_size_sqft,
        home_type
    FROM
        home_info
    WHERE
        id = {home_id} AND
        bedrooms = {bedrooms} AND
        bathrooms = {bathrooms} AND
        city_market_id = {city_code}
),
similarity_scores AS (
    SELECT
        hi.id,
        SQRT(
            POWER(hi.bedrooms - ih.bedrooms, 2) +
            POWER(hi.bathrooms - ih.bathrooms, 2) +
            POWER(hi.city_market_id - ih.city_market_id, 2) +
            POWER(hi.zipcode_market_id - ih.zipcode_market_id, 2) +
            POWER(hi.finished_sqft - ih.finished_sqft, 2) +
            POWER(hi.lot_size_sqft - ih.lot_size_sqft, 2)
        ) AS similarity_score
    FROM
        home_info hi,
        input_home ih
    WHERE
        hi.id <> ih.id
)
SELECT
    id,
    similarity_score
FROM
    similarity_scores
ORDER BY
    similarity_score
LIMIT 10;
"""

# Execute the SQL query
result = execute_query(sql_query)
print(result)

# Close the database connection
conn.close()
