import sys
import sqlite3
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget, QMessageBox, QFileDialog


class DatabaseViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Database Viewer")
        self.setGeometry(100, 100, 400, 300)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        layout = QVBoxLayout()
        self.central_widget.setLayout(layout)

        # Label to display database status
        self.database_status_label = QLabel("Database not loaded.")
        layout.addWidget(self.database_status_label)

        # Button to load database file
        self.load_database_button = QPushButton("Load Database")
        self.load_database_button.clicked.connect(self.load_database)
        layout.addWidget(self.load_database_button)

        # Button to show database contents
        self.show_database_button = QPushButton("Show Database")
        self.show_database_button.clicked.connect(self.show_database)
        layout.addWidget(self.show_database_button)

        # Button to clear database
        self.clear_database_button = QPushButton("Clear Database")
        self.clear_database_button.clicked.connect(self.clear_database)
        layout.addWidget(self.clear_database_button)

        # Button to generate graph
        self.generate_graph_button = QPushButton("Generate Graph")
        self.generate_graph_button.clicked.connect(self.generate_graph)
        layout.addWidget(self.generate_graph_button)

        # Exit button
        self.exit_button = QPushButton("Exit")
        self.exit_button.clicked.connect(self.close)
        layout.addWidget(self.exit_button)

        # Database connection
        self.connection = None

    def load_database(self):
        try:
            file_path, _ = QFileDialog.getOpenFileName(self, "Open Database File", "", "SQLite Database Files (*.db)")
            if file_path:
                self.connection = sqlite3.connect(file_path)
                self.database_status_label.setText("Database loaded successfully.")
            else:
                self.database_status_label.setText("No file selected.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error loading database: {str(e)}")

    def show_database(self):
        try:
            if self.connection:
                cursor = self.connection.cursor()
                cursor.execute("SELECT * FROM messages")
                rows = cursor.fetchall()
                for row in rows:
                    print(row)
            else:
                QMessageBox.warning(self, "Warning", "Please load the database first.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error showing database: {str(e)}")

    def clear_database(self):
        try:
            if self.connection:
                cursor = self.connection.cursor()
                cursor.execute("DELETE FROM messages")
                self.connection.commit()
                QMessageBox.information(self, "Success", "Database cleared successfully.")
            else:
                QMessageBox.warning(self, "Warning", "Please load the database first.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error clearing database: {str(e)}")

    def generate_graph(self):
        try:
            if self.connection:
                cursor = self.connection.cursor()
                cursor.execute("SELECT timestamp, message FROM messages WHERE topic='/Cantar/Robert/Masa'")
                rows = cursor.fetchall()

                timestamps, values = zip(*rows)

                # Convert timestamps to strings for better formatting
                timestamps_str = [str(ts) for ts in timestamps]

                # Plot the data with different line styles, colors, and markers
                plt.plot(timestamps_str, values, linestyle='-', color='blue', marker='o', markersize=6, linewidth=2, label='Masa Data')

                # You can add more lines for additional data points if needed
                # For example:
                # plt.plot(timestamps_str, values2, linestyle='--', color='red', marker='x', markersize=8, linewidth=1.5, label='Another Data')

                plt.xlabel("Timestamp", fontsize=12)
                plt.ylabel("Value", fontsize=12)
                plt.title("Variation of Messages from /Cantar/Robert/Masa over Time", fontsize=14)
                plt.legend()

                # Add grid and rotate x-axis labels for better readability
                plt.grid(True, linestyle='--', alpha=0.7)
                plt.xticks(rotation=45, ha='right')

                # Set background color
                plt.gca().set_facecolor('#f0f0f0')

                plt.show()
            else:
                QMessageBox.warning(self, "Warning", "Please load the database first.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error generating graph: {str(e)}")

class AnotherDatabaseViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Another Database Viewer")
        self.setGeometry(100, 100, 400, 300)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        layout = QVBoxLayout()
        self.central_widget.setLayout(layout)

        # Label to display database status
        self.database_status_label = QLabel("Another Database not loaded.")
        layout.addWidget(self.database_status_label)

        # Button to load database file
        self.load_database_button = QPushButton("Load Another Database")
        self.load_database_button.clicked.connect(self.load_database)
        layout.addWidget(self.load_database_button)

        # Button to generate graph
        self.generate_graph_button = QPushButton("Generate Graph")
        self.generate_graph_button.clicked.connect(self.generate_graph)
        layout.addWidget(self.generate_graph_button)

        # Exit button
        self.exit_button = QPushButton("Exit")
        self.exit_button.clicked.connect(self.close)
        layout.addWidget(self.exit_button)

        # Database connection
        self.connection = None

    def load_database(self):
        try:
            self.connection = sqlite3.connect("another_database.db")
            self.database_status_label.setText("Another Database loaded successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error loading another database: {str(e)}")

    def generate_graph(self):
        try:
            if self.connection:
                cursor = self.connection.cursor()
                cursor.execute("SELECT timestamp, value FROM sensor_data")
                rows = cursor.fetchall()

                timestamps, values = zip(*rows)

                # Plot the data
                plt.plot(timestamps, values, linestyle='-', color='green', marker='o', markersize=6, linewidth=2, label='Sensor Data')

                plt.xlabel("Timestamp", fontsize=12)
                plt.ylabel("Value", fontsize=12)
                plt.title("Variation of Sensor Data over Time", fontsize=14)
                plt.legend()

                plt.grid(True, linestyle='--', alpha=0.7)
                plt.xticks(rotation=45, ha='right')

                plt.gca().set_facecolor('#f0f0f0')

                plt.show()
            else:
                QMessageBox.warning(self, "Warning", "Please load the another database first.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error generating graph: {str(e)}")



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DatabaseViewer()
    window.show()
    app2 = QApplication(sys.argv)
    windo2 = AnotherDatabaseViewer()
    windo2.show()
    sys.exit(app.exec_())
    sys.exit(app2.exec_())
