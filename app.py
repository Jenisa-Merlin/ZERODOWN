from flask import Flask, render_template, request
import subprocess
import psycopg2 
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import geopandas as gpd


app = Flask(__name__)

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
    
@app.route('/')
def index():
    heading = "PriceProbe: Predicting Property Values"
    description = ("In the dynamic realm of US real estate, accurate pricing stands as the cornerstone "
                   "of successful transactions. With the market constantly evolving and property values "
                   "fluctuating, the ability to determine fair and competitive prices is paramount. Using "
                   "the partial raw market data provided, your task is to predict home prices for properties "
                   "listed for sale, by progressing through the following milestones")
    milestones = [
        "Milestone 1: ERD",
        "Milestone 2: EDA",
        "Milestone 3: Home Deduplication",
        "Milestone 4: Home Comparables",
        "Milestone 5: Price Estimation"
    ]
    return render_template('index.html', heading=heading, description=description, milestones=milestones)

@app.route('/eda')
def eda():
    return render_template('eda.html')

def connect_to_db():
    try:
        connection = connect_to_database()
        return connection
    except psycopg2.Error as e:
        print("Error connecting to PostgreSQL database:", e)

def execute_query(connection, query):
    try:
        cursor = connection.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        cursor.close()
        return rows
    except psycopg2.Error as e:
        print("Error executing query:", e)

@app.route('/execute_queries')
def execute_queries():
    connection = connect_to_db()
    if connection:
        # Query 1: Absolute duplicates
        query_absolute_duplicates = """
        SELECT 
            h1.address
        FROM 
            home_info h1
        INNER JOIN 
            home_info h2 ON h1.address = h2.address
        WHERE 
            h1.id <> h2.id 
            AND ABS(h1.listing_price - h2.listing_price) <= 1000 -- Price difference threshold
            AND ABS(EXTRACT(epoch FROM h1.last_sold_date - h2.last_sold_date)) <= 3600; -- Within 30 days difference
            """
        absolute_duplicates = execute_query(connection, query_absolute_duplicates)

        # Query 2: Pseudo duplicates
        query_pseudo_duplicates = """
        SELECT 
            h1.address
        FROM 
            home_info h1
        INNER JOIN 
            home_info h2 ON h1.address = h2.address
        WHERE 
            h1.id <> h2.id 
            AND ABS(h1.listing_price - h2.listing_price) <= 1000 -- Price difference threshold
            AND ABS(EXTRACT(epoch FROM h1.last_sold_date - h2.last_sold_date)) > 3600; -- Within 30 days difference
            """
        pseudo_duplicates = execute_query(connection, query_pseudo_duplicates)

        connection.close()

        return render_template('homeDuplicates.html', absolute_duplicates=absolute_duplicates, pseudo_duplicates=pseudo_duplicates)


def get_estimated_price(bedrooms, bathrooms, city_market_id, zipcode_market_id):
    conn = connect_to_database()
    cursor = conn.cursor()

    sql_query = """
    SELECT AVG(last_sold_price) AS estimated_price
    FROM home_info
    WHERE bedrooms = %s
        AND bathrooms = %s
        AND (city_market_id = %s OR zipcode_market_id = %s)
        AND last_sold_price IS NOT NULL;
    """

    cursor.execute(sql_query, (bedrooms, bathrooms, city_market_id, zipcode_market_id))
    result = cursor.fetchone()

    cursor.close()
    conn.close()

    return result[0] if result else None

@app.route('/price_estimation', methods=['GET', 'POST'])
def price_estimation():
    if request.method == 'POST':
        bedrooms = int(request.form['bedrooms'])
        bathrooms = int(request.form['bathrooms'])
        city_market_id = int(request.form['city_market_id'])
        zipcode_market_id = int(request.form['zipcode_market_id'])

        estimated_price = get_estimated_price(bedrooms, bathrooms, city_market_id, zipcode_market_id)

        return render_template('priceEstResult.html', estimated_price=estimated_price)

    return render_template('priceEst.html')

@app.route('/milestone5')
def milestone5():
    return render_template('priceEst.html')

@app.route('/milestone4')
def milestone4():
    return render_template('homeComp.html')

# Route for the home search form
@app.route('/home_comparables', methods=['GET', 'POST'])
def home_comparables():
    if request.method == 'POST':
        home_id = request.form['home_id']
        bedrooms = request.form['bedrooms']
        bathrooms = request.form['bathrooms']
        city_code = request.form['city_code']

        conn = connect_to_database()
        cursor = conn.cursor()
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
        result = execute_query(conn,sql_query)

        return render_template('homeCompResult.html', result=result)

    return render_template('homeComp.html')


# Function to fetch data from the home_info table
def fetch_data():
    conn = connect_to_database()
    if conn is None:
        return None

    try:
        # Fetch data from the home_info table
        df = pd.read_sql_query(
            "SELECT * FROM home_info;",
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
    plt.savefig('img/outliers.png')  # Save the plot as a static file
    plt.close()

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

@app.route('/outliers')
def outliers():
    # Fetch data from the database
    df = fetch_data()
    if df is not None:
        # Identify outliers using statistical methods
        outliers = identify_outliers(df)

        # Visualize outliers
        visualize_outliers(df, outliers)

        # Identify homes with incorrect data
        incorrect_data = identify_incorrect_data(df)

        return render_template('outliers.html', outliers=outliers, incorrect_data=incorrect_data)
    else:
        return "Error fetching data from the database"

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
    plt.savefig('static/temporal_distribution.png')  # Save the plot as a static file
    plt.close()

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
    plt.savefig('static/temporal_price_trend.png')  # Save the plot as a static file
    plt.close()

    # Seasonality Analysis
    df['month'] = df['listing_contract_date'].dt.month
    plt.figure(figsize=(10, 6))
    sns.boxplot(data=df, x='month', y='listing_price')
    plt.title('Seasonality in Listing Prices')
    plt.xlabel('Month')
    plt.ylabel('Listing Price')
    plt.savefig('static/seasonality_listing_prices.png')  # Save the plot as a static file
    plt.close()

    # Day of the Week Analysis
    df['day_of_week'] = df['listing_contract_date'].dt.day_name()
    plt.figure(figsize=(10, 6))
    sns.countplot(data=df, x='day_of_week', order=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])
    plt.title('Distribution of Listing Contract Dates by Day of the Week')
    plt.xlabel('Day of the Week')
    plt.ylabel('Count')
    plt.savefig('static/day_of_week_distribution.png')  # Save the plot as a static file
    plt.close()

    # Time to Sale Analysis
    df['time_to_sale'] = (df['off_market_date'] - df['on_market_date']).dt.days
    plt.figure(figsize=(10, 6))
    sns.histplot(df['time_to_sale'].dropna(), kde=True, color='red')
    plt.title('Distribution of Time to Sale')
    plt.xlabel('Days to Sale')
    plt.ylabel('Frequency')
    plt.savefig('static/time_to_sale_distribution.png')  # Save the plot as a static file
    plt.close()

# Route for temporal analysis
@app.route('/temporal_analysis')
def temporal_analysis():
    # Fetch temporal data from the database
    df_temporal = fetch_temporal_data()
    if df_temporal is not None:
        # Analyze the distribution of temporal dates
        analyze_temporal_spread(df_temporal)
        # Additional temporal EDA
        additional_temporal_eda(df_temporal)
        return render_template('temporal_analysis.html')
    else:
        return "Error fetching data from the database"

# Function to fetch state information for each market from the market table
def get_state_for_market(market_id, conn):
    cur = conn.cursor()
    cur.execute(f"SELECT state FROM market WHERE id = {market_id};")
    state = cur.fetchone()[0]  # Assuming state information is available for each market
    cur.close()
    return state

# Read data from the market_geom table
def fetch_market_geom_data():
    conn = connect_to_database()
    if conn is None:
        return None

    try:
        gdf = gpd.read_postgis(
            "SELECT market_id, geom FROM market_geom",
            con=conn,
            geom_col='geom'
        )

        # Fetch state information for each market
        gdf['state'] = gdf['market_id'].apply(lambda x: get_state_for_market(x, conn))

        return gdf
    finally:
        conn.close()

# Function to visualize the distribution of markets on a map
def visualize_market_distribution(gdf):
    plt.figure(figsize=(10, 6))
    gdf.plot()
    plt.title('Distribution of Markets')
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.savefig('static/market_distribution.png')  # Save the plot as a static file
    plt.close()

# Function to analyze the spread of markets across different regions or states
def analyze_market_spread(gdf):
    state_counts = gdf.groupby('state').size()
    plt.figure(figsize=(10, 6))
    state_counts.plot(kind='bar')
    plt.xlabel('State')
    plt.ylabel('Number of Markets')
    plt.title('Market Distribution by State')
    plt.savefig('static/market_distribution_by_state.png')  # Save the plot as a static file
    plt.close()

# Function to calculate the area covered by each market
def calculate_market_areas(gdf):
    gdf['area_sq_mi'] = gdf['geom'].area / 2589988.1103  # Convert from square meters to square miles
    market_areas = gdf[['market_id', 'area_sq_mi']]
    print("Area Covered by Each Market:")
    print(market_areas)
    plt.figure(figsize=(10, 6))
    gdf.plot(column='area_sq_mi', legend=True)
    plt.title('Area Covered by Each Market')
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.savefig('static/market_areas.png')  # Save the plot as a static file
    plt.close()

@app.route('/geographical_spread')
def geographical_spread():
    # Read data from the market_geom table
    gdf = fetch_market_geom_data()
    if gdf is not None:
        # Visualize the distribution of markets on a map
        visualize_market_distribution(gdf)
        
        # Analyze the spread of markets across different regions or states
        analyze_market_spread(gdf)

        # Calculate the area covered by each market
        calculate_market_areas(gdf)

        return render_template('geographical_spread.html')
    else:
        return "Error fetching data from the database"

# Function to check for missing values in each column
def check_missing_values(df):
    return df.isnull().sum()

# Function to check unique values and their counts for each attribute
def unique_value_counts(df, attributes):
    unique_counts = {}
    for attribute in attributes:
        unique_counts[attribute] = df[attribute].value_counts().to_dict()
    return unique_counts

# Function to plot distribution of numeric attributes
def plot_numeric_distribution(df, numeric_attributes):
    for attribute in numeric_attributes:
        plt.figure(figsize=(8, 6))
        sns.histplot(df[attribute], bins=20, kde=True, color='skyblue')
        plt.title(f'Distribution of {attribute}')
        plt.xlabel(attribute)
        plt.ylabel('Frequency')
        plt.savefig(f'static/{attribute}_distribution.png')  # Save the plot as a static file
        plt.close()

# Function to explore correlations between numeric attributes
def explore_correlations(df, numeric_attributes):
    numeric_df = df[numeric_attributes]
    correlation_matrix = numeric_df.corr()
    plt.figure(figsize=(10, 8))
    sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm')
    plt.title('Correlation Matrix')
    plt.savefig('static/correlation_matrix.png')  # Save the plot as a static file
    plt.close()

# Function to identify outliers or anomalies in the data
def identify_outliers(df, numeric_attributes):
    plt.figure(figsize=(12, 6))
    sns.boxplot(data=df[numeric_attributes])
    plt.title('Boxplots of Numeric Attributes')
    plt.savefig('static/boxplots.png')  # Save the plot as a static file
    plt.close()

# Function to perform summary statistics for numeric attributes
def summary_statistics(df, numeric_attributes):
    return df[numeric_attributes].describe()

@app.route('/home_eda')
def data_analysis():
    # Fetch data from the database
    df = fetch_data()
    if df is not None:
        # Check for missing values
        missing_values = check_missing_values(df)
        
        # Check unique values and their counts for selected attributes
        selected_attributes = ['source_system', 'status', 'home_type', 'bedrooms', 'bathrooms', 'year_built', 'new_construction', 'has_pool']
        unique_counts = unique_value_counts(df, selected_attributes)

        # Plot distribution of numeric attributes
        numeric_attributes = ['finished_sqft', 'lot_size_sqft', 'bedrooms', 'bathrooms', 'year_built']
        plot_numeric_distribution(df, numeric_attributes)

        # Explore correlations between numeric attributes
        explore_correlations(df, numeric_attributes)

        # Identify outliers or anomalies in the data
        identify_outliers(df, numeric_attributes)

        # Perform summary statistics for numeric attributes
        stats = summary_statistics(df, numeric_attributes)

        return render_template('home_eda.html', missing_values=missing_values, unique_counts=unique_counts, stats=stats)
    else:
        return "Error fetching data from the database"

# Function to fetch data from the database into a DataFrame
def fetch_data():
    conn = connect_to_database()
    if conn is None:
        return None
    try:
        # Fetch data from the market_geom table
        df = pd.read_sql_query("SELECT * FROM market_geom;", conn)
        return df
    finally:
        conn.close()

# Function to perform exploratory data analysis (EDA)
def perform_eda(df):
    # Display the first few rows of the DataFrame
    print("\nFirst few rows of the DataFrame:")
    print(df.head())

    # Check for missing values
    missing_values = df.isnull().sum()

    # Plot distribution of numeric attributes
    numeric_attributes = ['longitude', 'latitude', 'area_in_sq_mi']
    for attribute in numeric_attributes:
        plt.figure(figsize=(8, 6))
        sns.histplot(df[attribute], bins=20, kde=True, color='skyblue')
        plt.title(f'Distribution of {attribute}')
        plt.xlabel(attribute)
        plt.ylabel('Frequency')
        plt.show()

    # Explore correlations between numeric attributes
    numeric_df = df[numeric_attributes]
    correlation_matrix = numeric_df.corr()
    plt.figure(figsize=(10, 8))
    sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm')
    plt.title('Correlation Matrix')
    plt.show()

    # Perform summary statistics for numeric attributes
    summary_statistics = df[numeric_attributes].describe()

    return missing_values, summary_statistics

@app.route('/matchGeom_eda')
def matchGeom_eda():
    # Fetch data from the market_geom table
    df = fetch_data()
    if df is not None:
        # Perform exploratory data analysis (EDA)
        missing_values, summary_statistics = perform_eda(df)
        return render_template('matchGeom_attr.html', missing_values=missing_values, summary_statistics=summary_statistics)
    else:
        return "Error fetching data from the database"

# Function to fetch data from the database into a DataFrame
def fetch_data_market():
    conn = connect_to_database()
    if conn is None:
        return None
    try:
        # Fetch data from the market table
        df = pd.read_sql_query("SELECT * FROM market;", conn)
        return df
    finally:
        conn.close()

# Function to perform exploratory data analysis (EDA)
def perform_eda_market(df):
    # Display the first few rows of the DataFrame
    print("\nFirst few rows of the DataFrame:")
    print(df.head())

    # Check for missing values
    missing_values = df.isnull().sum()

    # Check unique values and their counts for selected attributes
    selected_attributes = ['name', 'market_level', 'state', 'city', 'zipcode', 'neighborhood', 'neighborhood_source']
    unique_values_counts = {}
    for attribute in selected_attributes:
        unique_values_counts[attribute] = df[attribute].value_counts()

    # Check for duplicate entries
    duplicate_entries = df[df.duplicated(subset=['name', 'state', 'market_level', 'city', 'neighborhood_source'], keep=False)]

    # Plot distribution of market levels
    plt.figure(figsize=(8, 6))
    df['market_level'].value_counts().plot(kind='bar', color='skyblue')
    plt.title('Distribution of Market Levels')
    plt.xlabel('Market Level')
    plt.ylabel('Frequency')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('static/market_level_distribution.png')  # Save the plot as a static file
    plt.close()

    # Explore correlations between numerical attributes
    numeric_df = df.select_dtypes(include=['float64', 'int64']) 
    correlation_matrix = numeric_df.corr()

    # Perform summary statistics for numerical attributes
    summary_statistics = df.describe()

    return missing_values, unique_values_counts, duplicate_entries, correlation_matrix, summary_statistics

@app.route('/market_eda')
def market_eda():
    # Fetch data from the market table
    df = fetch_data_market()
    if df is not None:
        # Perform exploratory data analysis (EDA)
        missing_values, unique_values_counts, duplicate_entries, correlation_matrix, summary_statistics = perform_eda_market(df)
        return render_template('market.html', missing_values=missing_values, unique_values_counts=unique_values_counts, duplicate_entries=duplicate_entries, correlation_matrix=correlation_matrix, summary_statistics=summary_statistics)
    else:
        return "Error fetching data from the database"

if __name__ == "__main__":
    app.run(debug=True)
