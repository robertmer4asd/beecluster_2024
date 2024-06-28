import sqlite3

# Connect to the database
conn = sqlite3.connect('freq_data.db')
cursor = conn.cursor()

# Array to insert
values = [32, 100, 69, 5, 220, 50, 87, 300, 34, 64, 41, 180, 43, 200, 92]

# Convert the array to a string
values_str = ' '.join(map(str, values))

# Execute the SQL update statement to insert the values
cursor.execute("UPDATE messages SET message = ? WHERE id = (SELECT MAX(id) FROM messages)", (values_str,))

# Commit the transaction
conn.commit()

# Close the connection
conn.close()
