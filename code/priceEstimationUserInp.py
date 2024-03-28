# MILESTONE 5
'''
Price Estimation: Given home attributes(bed, bath, city/zipcode etc...) estimate price
based on sold homes.
'''

# import necessary libraries
import psycopg2
import db

def get_estimated_price(bedrooms, bathrooms, city_market_id, zipcode_market_id):
    # Establishing a connection to the PostgreSQL database
    conn = db.connect_to_database()

    # Creating a cursor object using the cursor() method
    cursor = conn.cursor()

    # Preparing the SQL query with placeholders for user input
    sql_query = """
    SELECT AVG(last_sold_price) AS estimated_price
    FROM home_info
    WHERE bedrooms = %s
        AND bathrooms = %s
        AND (city_market_id = %s OR zipcode_market_id = %s)
        AND last_sold_price IS NOT NULL;
    """

    # Executing the SQL query with user input parameters
    cursor.execute(sql_query, (bedrooms, bathrooms, city_market_id, zipcode_market_id))

    # Fetching the result
    result = cursor.fetchone()

    # Closing the cursor and connection
    cursor.close()
    conn.close()

    # Returning the estimated price
    return result[0] if result else None

# Taking user input for bedrooms, bathrooms, city_market_id, and zipcode_market_id
bedrooms = int(input("Enter the number of bedrooms: "))
bathrooms = int(input("Enter the number of bathrooms: "))
city_market_id = int(input("Enter the city market ID: "))
zipcode_market_id = int(input("Enter the zip code market ID: "))

# Calling the function to get the estimated price
estimated_price = get_estimated_price(bedrooms, bathrooms, city_market_id, zipcode_market_id)

# Displaying the result
if estimated_price is not None:
    print(f"The estimated price for a {bedrooms}-bedroom, {bathrooms}-bathroom home is ${estimated_price:.2f}")
else:
    print("No data found for the provided criteria.")
