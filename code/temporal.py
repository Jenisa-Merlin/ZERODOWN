import pandas as pd
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

# Function to fetch listing contract dates, on market dates, and off market dates
def fetch_temporal_data():
    conn = connect_to_database()
    if conn is None:
        return None

    try:
        # Fetch data from the home_info table
        df = pd.read_sql_query(
            "SELECT listing_contract_date, on_market_date, off_market_date, listing_price, last_sold_price FROM home_info;",
            conn
        )

        # Convert date columns to datetime format
        df['listing_contract_date'] = pd.to_datetime(df['listing_contract_date'])
        df['on_market_date'] = pd.to_datetime(df['on_market_date'])
        df['off_market_date'] = pd.to_datetime(df['off_market_date'])

        return df
    finally:
        conn.close()

# Function to analyze the distribution of temporal dates
def analyze_temporal_spread(df):
    # Plot histograms for listing contract date, on market date, and off market date
    plt.figure(figsize=(12, 6))
    plt.subplot(1, 3, 1)
    sns.histplot(df['listing_contract_date'].dropna(), kde=True, color='blue')
    plt.title('Distribution of Listing Contract Date')
    plt.xlabel('Date')
    plt.ylabel('Frequency')

    plt.subplot(1, 3, 2)
    sns.histplot(df['on_market_date'].dropna(), kde=True, color='green')
    plt.title('Distribution of On Market Date')
    plt.xlabel('Date')
    plt.ylabel('Frequency')

    plt.subplot(1, 3, 3)
    sns.histplot(df['off_market_date'].dropna(), kde=True, color='red')
    plt.title('Distribution of Off Market Date')
    plt.xlabel('Date')
    plt.ylabel('Frequency')

    plt.tight_layout()
    plt.show()

# Function for additional temporal spread EDA
def additional_temporal_eda(df):
    # Time Series Analysis
    plt.figure(figsize=(12, 6))
    plt.subplot(2, 1, 1)
    plt.plot(df['listing_contract_date'], df['listing_price'], color='blue')
    plt.title('Listing Price Trend Over Time')
    plt.xlabel('Date')
    plt.ylabel('Listing Price')

    plt.subplot(2, 1, 2)
    plt.plot(df['listing_contract_date'], df['last_sold_price'], color='green')
    plt.title('Last Sold Price Trend Over Time')
    plt.xlabel('Date')
    plt.ylabel('Last Sold Price')

    plt.tight_layout()
    plt.show()

    # Seasonality Analysis
    df['month'] = df['listing_contract_date'].dt.month
    plt.figure(figsize=(10, 6))
    sns.boxplot(data=df, x='month', y='listing_price')
    plt.title('Seasonality in Listing Prices')
    plt.xlabel('Month')
    plt.ylabel('Listing Price')
    plt.show()

    # Day of the Week Analysis
    df['day_of_week'] = df['listing_contract_date'].dt.day_name()
    plt.figure(figsize=(10, 6))
    sns.countplot(data=df, x='day_of_week', order=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])
    plt.title('Distribution of Listing Contract Dates by Day of the Week')
    plt.xlabel('Day of the Week')
    plt.ylabel('Count')
    plt.show()

    # Time to Sale Analysis
    df['time_to_sale'] = (df['off_market_date'] - df['on_market_date']).dt.days
    plt.figure(figsize=(10, 6))
    sns.histplot(df['time_to_sale'].dropna(), kde=True, color='red')
    plt.title('Distribution of Time to Sale')
    plt.xlabel('Days to Sale')
    plt.ylabel('Frequency')
    plt.show()

if __name__ == "__main__":
    # Fetch temporal data from the database
    df_temporal = fetch_temporal_data()
    if df_temporal is not None:
        # Analyze the distribution of temporal dates
        analyze_temporal_spread(df_temporal)
        additional_temporal_eda(df_temporal)
