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