import sqlite3

def view_database(db_file, limit=None):
    try:
        # Connect to the SQLite database file
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()

        # Execute a SELECT query to fetch rows from the 'messages' table
        query = "SELECT * FROM messages"
        if limit is not None:
            query += f" LIMIT {limit}"
        cursor.execute(query)
        rows = cursor.fetchall()

        # Print the fetched rows
        if len(rows) == 0:
            print("No data found in the 'messages' table.")
        else:
            for row in rows:
                print(row)

        # Close the cursor and connection
        cursor.close()
        conn.close()

    except sqlite3.Error as e:
        print("SQLite error:", e)

# View contents of mqtt_messages.db, limiting to 32 rows
view_database('mqtt_tempDB.db', limit=None)
