import psycopg2

from pkg.shared import config as cfg

def connect():
    """
    Connects to the database.

    Returns:
        psycopg2.connection: A database connection.
    """
    return psycopg2.connect(
        host=cfg.db_host,   
        port=cfg.db_port,
        database=cfg.db_name,
        user=cfg.db_user,
        password=cfg.db_pw
    )

def fetch_email_list():
    """
    Fetches a list of email addresses from the database.

    Returns:
        list: A list of email addresses.
    """
    try:
        conn = connect()
        cur = conn.cursor()
        cur.execute(cfg.db_statement)
        receiver_emails = cur.fetchall()
        return receiver_emails
    except Exception as e:
        # Handle the exception here
        print(f"An error occurred: {str(e)}")
    finally:
        # Close the cursor and connection in the finally block
        cur.close()
        conn.close()