import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import db
import psycopg2

# function to exploratory data analysis on range of attributes
def attributeRange():
    # Establish connection to database
    conn = db.connect_to_database()
    if conn is None:
        return None
    
    # Create a cursor object using the connection
    cur = conn.cursor()

    # sql query to execute
    query = """
    SELECT listing_price, finished_sqft, lot_size_sqft, bedrooms, bathrooms, year_built, original_listing_price, last_sold_price
    FROM home_info;
    """

    try:
        # Execute the query
        cur.execute(query)

        # Fetch the result into a DataFrame
        df = pd.DataFrame(cur.fetchall(), columns=['listing_price', 'finished_sqft', 'lot_size_sqft', 'bedrooms', 'bathrooms', 'year_built', 'original_listing_price', 'last_sold_price'])

        # Range of Listing Prices
        listing_price_range = df['listing_price'].agg(['min', 'max'])
        print("Range of Listing Prices:", listing_price_range)

        # Distribution of Finished Sqft and Lot Size Sqft
        plt.figure(figsize=(10, 6))
        sns.histplot(data=df, x='finished_sqft', bins=30, kde=True, color='blue', label='Finished Sqft')
        sns.histplot(data=df, x='lot_size_sqft', bins=30, kde=True, color='red', label='Lot Size Sqft')
        plt.xlabel('Square Feet')
        plt.ylabel('Frequency')
        plt.title('Distribution of Property Sizes')
        plt.legend()
        plt.show()

        # Variation in Bedrooms and Bathrooms
        plt.figure(figsize=(10, 6))
        sns.countplot(data=df, x='bedrooms', palette='viridis')
        plt.xlabel('Number of Bedrooms')
        plt.ylabel('Count')
        plt.title('Variation in Number of Bedrooms')
        plt.show()

        plt.figure(figsize=(10, 6))
        sns.countplot(data=df, x='bathrooms', palette='magma')
        plt.xlabel('Number of Bathrooms')
        plt.ylabel('Count')
        plt.title('Variation in Number of Bathrooms')
        plt.show()

        # Range of Year Built
        year_built_range = df['year_built'].agg(['min', 'max'])
        print("Range of Year Built:", year_built_range)

    except psycopg2.Error as e:
        print("Error: Unable to execute query.")
        print(e)
    finally:
        # Close cursor and connection
        cur.close()
        conn.close()

if __name__ == "__main__":
    attributeRange()
