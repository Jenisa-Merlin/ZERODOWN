# geographical spread 
'''
1) Visualize the distribution of markets using latitude and longitude
2) Analyse and visualize the spread of markets across different regions or states
3) Calculate and visualize Area covered by each market
'''

# import necessary libraries
import geopandas as gpd
import matplotlib.pyplot as plt
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
    gdf.plot()
    plt.title('Distribution of Markets')
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.show()

# Function to analyze the spread of markets across different regions or states
def analyze_market_spread(gdf):
    state_counts = gdf.groupby('state').size()
    print("Market Distribution by State:")
    print(state_counts)
    state_counts = gdf.groupby('state').size()
    state_counts.plot(kind='bar', figsize=(10, 6))
    plt.xlabel('State')
    plt.ylabel('Number of Markets')
    plt.title('Market Distribution by State')
    plt.show()


# Function to calculate the area covered by each market
def calculate_market_areas(gdf):
    # Calculate the area covered by each market using the geom column
    gdf['area_sq_mi'] = gdf['geom'].area / 2589988.1103  # Convert from square meters to square miles
    market_areas = gdf[['market_id', 'area_sq_mi']]
    print("Area Covered by Each Market:")
    print(market_areas)
    gdf.plot(column='area_sq_mi', legend=True, figsize=(10, 6))
    plt.title('Area Covered by Each Market')
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.show()


if __name__ == "__main__":
    # Read data from the market_geom table
    gdf = fetch_market_geom_data()
    if gdf is not None:
        # Visualize the distribution of markets on a map
        visualize_market_distribution(gdf)
        
        # Analyze the spread of markets across different regions or states
        analyze_market_spread(gdf)

        # Calculate the area covered by each market
        calculate_market_areas(gdf)
