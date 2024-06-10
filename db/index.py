import psycopg2
from psycopg2 import pool
from pkg.shared import config as cfg

# Initialize the connection pool globally
try:
    connection_pool = psycopg2.pool.SimpleConnectionPool(1, 20,
                        host=cfg.db_host,
                        port=cfg.db_port,
                        database=cfg.db_name,
                        user=cfg.db_user,
                        password=cfg.db_pw)
    if connection_pool:
        print("Connection pool created successfully")
except Exception as e:
    print(f"Error creating connection pool: {str(e)}")
    connection_pool = None

def fetch_email_list():
    """
    Fetches a list of email addresses from the database.

    Returns:
        list: A list of email addresses.
    """
    if not connection_pool:
        print("Connection pool is not available.")
        return []

    try:
        conn = connection_pool.getconn()
        if conn:
            cur = conn.cursor()
            cur.execute(cfg.db_statement)
            receiver_emails = cur.fetchall()
            return receiver_emails
    except Exception as e:
        # Handle the exception here
        print(f"An error occurred: {str(e)}")
        return []
    finally:
        # Ensure the cursor and connection are closed in the finally block
        try:
            if cur:
                cur.close()
        except NameError:
            pass  # cur was not assigned, ignore
        try:
            if conn:
                connection_pool.putconn(conn)
        except NameError:
            pass  # conn was not assigned, ignore
