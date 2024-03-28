import psycopg2
import db

def connect_to_db():
    try:
        connection = db.connect_to_database()
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

def main():
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
        print("Absolute Duplicates:")
        print(absolute_duplicates)

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
        print("Pseudo Duplicates:")
        print(pseudo_duplicates)

        connection.close()

if __name__ == "__main__":
    main()
