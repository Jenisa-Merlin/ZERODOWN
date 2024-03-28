import psycopg2
import pandas as pd
import db
# Establish a connection to the database
conn = db.connect_to_database()

# Define the SQL query
sql_query = """
SELECT
    bedrooms,
    bathrooms,
    city_market_id,
    zipcode_market_id,
    AVG(last_sold_price) AS average_sold_price
FROM
    home_info
GROUP BY
    bedrooms,
    bathrooms,
    city_market_id,
    zipcode_market_id;
"""

# Execute the query and fetch the results into a pandas DataFrame
df = pd.read_sql_query(sql_query, conn)

# Close the database connection
conn.close()

# Display the DataFrame
print(df)
