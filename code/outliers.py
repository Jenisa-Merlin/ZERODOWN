# MILESTONE 2
'''
Identify outlier homes and homes with incorrect data
'''
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import psycopg2

# Database connection parameters
DB_NAME = 'ZERODOWN'
DB_USER = 'postgres'
DB_PASSWORD = 'Jeni3604'
DB_HOST = 'localhost'
DB_PORT = '5432'

# Function to establish database connection
def connect_to_database():
    try:
        # Establish connection to PostgreSQL database
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        print("Connection to database established successfully!")
        return conn
    except psycopg2.Error as e:
        print("Error: Unable to connect to the database.")
        print(e)
        return None

# Function to fetch data from the home_info table
def fetch_data():
    conn = connect_to_database()
    if conn is None:
        return None

    try:
        # Fetch data from the home_info table
        df = pd.read_sql_query(
            "SELECT * FROM home_info WHERE listing_price > (SELECT AVG(listing_price) * 3 FROM home_info) OR listing_price < (SELECT AVG(listing_price) / 3 FROM home_info) OR finished_sqft > (SELECT AVG(finished_sqft) * 3 FROM home_info) OR finished_sqft < (SELECT AVG(finished_sqft) / 3 FROM home_info);",
            conn
        )

        return df
    finally:
        conn.close()

# Function to identify outliers using statistical methods
def identify_outliers(df):
    # Define numerical columns for outlier detection
    numerical_columns = ['listing_price', 'finished_sqft', 'lot_size_sqft', 'bedrooms', 'bathrooms', 'year_built', 'last_sold_price']

    # Calculate z-score for each numerical column
    z_scores = df[numerical_columns].apply(lambda x: np.abs((x - x.mean()) / x.std()))

    # Define threshold for outlier detection (e.g., z-score > 3)
    outlier_threshold = 3

    # Flag outliers based on z-score
    outliers = z_scores > outlier_threshold
    print(outliers)
    return outliers

# Function to visualize outliers
def visualize_outliers(df, outliers):
    # Boxplot for numerical features with outliers
    plt.figure(figsize=(12, 8))
    numerical_columns = df.select_dtypes(include=[np.number]).columns
    num_plots = min(len(numerical_columns), 9)
    for i, col in enumerate(numerical_columns[:num_plots]):
        plt.subplot(3, 3, i+1)
        sns.boxplot(data=df, y=col, showfliers=False)
        plt.title(f'Boxplot of {col}')
    plt.tight_layout()
    plt.show()

# Function to identify homes with incorrect data
def identify_incorrect_data(df):
    # Example: Identify homes where the number of bathrooms exceeds the number of bedrooms
    incorrect_data = df[df['bathrooms'] > df['bedrooms']]

    # Check for unrealistic property sizes
    incorrect_data = incorrect_data[(incorrect_data['finished_sqft'] <= 0) | (incorrect_data['lot_size_sqft'] <= 0)]
    
    # Verify property age
    incorrect_data = incorrect_data[(incorrect_data['year_built'] < 1800) | (incorrect_data['year_built'] > 2022)]  # Assuming the current year is 2022

    # Verify listing and selling prices
    incorrect_data = incorrect_data[(incorrect_data['listing_price'] <= 0) | (incorrect_data['last_sold_price'] <= 0)]

    return incorrect_data

if __name__ == "__main__":
    # Fetch data from the database
    df = fetch_data()
    if df is not None:
        # Identify outliers using statistical methods
        outliers = identify_outliers(df)

        # Visualize outliers
        visualize_outliers(df, outliers)

        # Identify homes with incorrect data
        incorrect_data = identify_incorrect_data(df)

        # Display homes with incorrect data
        print("Homes with Incorrect Data:")
        print(incorrect_data)
