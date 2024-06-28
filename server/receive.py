import socket

# Socket server details
host = '0.0.0.0'  # Listen on all available interfaces
port = 12345


# Function to receive the database files
def receive_database_files():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((host, port))
            s.listen(2)  # Listen for two incoming connections
            print(f"Socket server listening on {host}:{port}")

            for i in range(2):  # Receive two database files
                print(f"Waiting for connection {i + 1}...")
                conn, addr = s.accept()
                print(f"Connection {i + 1} established from {addr}")

                file_name = f"received_db_{i + 1}.db"
                with open(file_name, 'wb') as file:
                    while True:
                        data = conn.recv(1024)
                        if not data:
                            break
                        file.write(data)

                print(f"Database file {file_name} received and saved.")

    except Exception as e:
        print("Error receiving database file:", e)
def show_databases():
    try:
        for i in range(2):  # Iterate over the received database files
            file_name = f"received_db_{i + 1}.db"
            print(f"Contents of {file_name}:")
            conn = sqlite3.connect(file_name)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM messages")
            rows = cursor.fetchall()
            for row in rows:
                print(row)
            conn.close()
    except Exception as e:
        print("Error showing database contents:", e)

# Show the contents of the received databases
show_databases()


# Receive the database files
receive_database_files()
