#MILESTONE 2
'''
Range of attributes EDA for market table attributes
'''

# import necessary libraries
import pandas as pd
import matplotlib.pyplot as plt
import db
import geopandas as gpd
import seaborn as sns

# Function to fetch data from the home_info table
def fetch_data():
    conn = db.connect_to_database()
    if conn is None:
        return None
    try:
        # Fetch data from the home_info table
        df = pd.read_sql_query(
            "SELECT * FROM market;",
            conn
        )
        return df
    finally:
        conn.close()

def perform_eda(df):
    # Display the first few rows of the DataFrame
    print("\nFirst few rows of the DataFrame:")
    print(df.head())

    # Check for missing values
    print("\nMissing values in each column:")
    print(df.isnull().sum())

    # Check unique values and their counts
    print("\nUnique values and their counts for 'name':")
    print(df['name'].value_counts())

    print("\nUnique values and their counts for 'market_level':")
    print(df['market_level'].value_counts())

    print("\nUnique values and their counts for 'state':")
    print(df['state'].value_counts())

    print("\nUnique values and their counts for 'city':")
    print(df['city'].value_counts())

    print("\nUnique values and their counts for 'zipcode':")
    print(df['zipcode'].value_counts())

    print("\nUnique values and their counts for 'neighborhood':")
    print(df['neighborhood'].value_counts())

    print("\nUnique values and their counts for 'neighborhood_source':")
    print(df['neighborhood_source'].value_counts())

    # Check for duplicate entries
    duplicate_entries = df[df.duplicated(subset=['name', 'state', 'market_level', 'city', 'neighborhood_source'], keep=False)]
    if len(duplicate_entries) > 0:
        print("\nDuplicate entries based on the unique constraint:")
        print(duplicate_entries)
    else:
        print("\nNo duplicate entries found.")

    # Plot distribution of market levels
    plt.figure(figsize=(8, 6))
    df['market_level'].value_counts().plot(kind='bar', color='skyblue')
    plt.title('Distribution of Market Levels')
    plt.xlabel('Market Level')
    plt.ylabel('Frequency')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

    # Explore correlations between attributes
    numeric_df = df.select_dtypes(include=['float64', 'int64']) 
    correlation_matrix = numeric_df.corr()
    sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm')
    plt.title('Correlation Matrix')
    plt.show()

    # Perform summary statistics for numerical attributes
    summary_statistics = df.describe()
    print(summary_statistics)

if __name__ == "__main__":
    df = fetch_data()
    if df is not None:
        perform_eda(df)

