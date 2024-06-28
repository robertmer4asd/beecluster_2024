import sys
import sqlite3
import warnings
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
from PyQt5.QtCore import *
from PyQt5.QtGui import QFont
from datetime import datetime
from PyQt5.QtWidgets import *
import numpy as np
from scipy.interpolate import UnivariateSpline



warnings.filterwarnings("ignore")


class DatabaseViewer(QMainWindow):
    def __init__(self, title):
        super().__init__()
        self.setWindowTitle(title)
        self.setGeometry(100, 100, 400, 300)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 50, 20, 20)
        self.central_widget.setLayout(layout)

        self.title_label = QLabel("BeeCluster", self)
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setFont(QFont("Arial", 15))
        layout.addWidget(self.title_label)

        self.database_status_label = QLabel("Databases not loaded.")
        self.database_status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.database_status_label)

        self.load_weight_button = QPushButton("Load Weight Database")
        self.load_weight_button.clicked.connect(self.load_weight_database)
        layout.addWidget(self.load_weight_button)

        self.load_temperature_button = QPushButton("Load Temperature Database")
        self.load_temperature_button.clicked.connect(self.load_temperature_database)
        layout.addWidget(self.load_temperature_button)

        self.load_humidity_button = QPushButton("Load Humidity Database")
        self.load_humidity_button.clicked.connect(self.load_humidity_database)
        layout.addWidget(self.load_humidity_button)

        self.load_frequency_button = QPushButton("Load Frequency Database")
        self.load_frequency_button.clicked.connect(self.load_freq_database)
        layout.addWidget(self.load_frequency_button)

        self.show_database_button = QPushButton("Show Databases")
        self.show_database_button.clicked.connect(self.show_databases)
        layout.addWidget(self.show_database_button)

        self.clear_database_button = QPushButton("Clear Databases")
        self.clear_database_button.clicked.connect(self.clear_databases)
        layout.addWidget(self.clear_database_button)

        self.generate_graph_button = QPushButton("Generate Graph")
        self.generate_graph_button.clicked.connect(self.generate_graph)
        layout.addWidget(self.generate_graph_button)

        self.load_freq = QPushButton("Load Frequency Graph")
        self.load_freq.clicked.connect(self.generate_freq_graph)
        layout.addWidget(self.load_freq)

        self.exit_button = QPushButton("Exit")
        self.exit_button.clicked.connect(self.close)
        layout.addWidget(self.exit_button)

        self.connection_weight = None
        self.connection_temperature = None
        self.connection_humidity = None

    def load_weight_database(self):
        try:
            file_path, _ = QFileDialog.getOpenFileName(self, "Open Weight Database File", "", "SQLite Database Files (*.db)")
            if file_path:
                self.connection_weight = sqlite3.connect(file_path)
                self.database_status_label.setText("Weight Database loaded successfully.")
            else:
                self.database_status_label.setText("No file selected for Weight Database.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error loading Weight Database: {str(e)}")

    def load_temperature_database(self):
        try:
            file_path, _ = QFileDialog.getOpenFileName(self, "Open Temperature Database File", "", "SQLite Database Files (*.db)")
            if file_path:
                self.connection_temperature = sqlite3.connect(file_path)
                self.database_status_label.setText("Temperature Database loaded successfully.")
            else:
                self.database_status_label.setText("No file selected for Temperature Database.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error loading Temperature Database: {str(e)}")

    def load_humidity_database(self):
        try:
            file_path, _ = QFileDialog.getOpenFileName(self, "Open Humidity Database File", "",
                                                       "SQLite Database Files (*.db)")
            if file_path:
                self.connection_humidity = sqlite3.connect(file_path)
                self.database_status_label.setText("Humidity Database loaded successfully.")
            else:
                self.database_status_label.setText("No file selected for Humidity Database.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error loading Humidity Database: {str(e)}")

    def load_freq_database(self):
        try:
            file_path, _ = QFileDialog.getOpenFileName(self, "Open Frequency Database File", "",
                                                       "SQLite Database Files (*.db)")
            if file_path:
                self.connection_location = sqlite3.connect(file_path)
                self.database_status_label.setText("Location Database loaded successfully.")
            else:
                self.database_status_label.setText("No file selected for Location Database.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error loading Location Database: {str(e)}")

    def show_databases(self):
        try:
            if self.connection_weight and self.connection_temperature and self.connection_humidity:
                cursor_weight = self.connection_weight.cursor()
                cursor_weight.execute("SELECT * FROM messages")
                rows_weight = cursor_weight.fetchall()
                print("Weight Database:")
                for row in rows_weight:
                    print(row)

                cursor_temperature = self.connection_temperature.cursor()
                cursor_temperature.execute("SELECT * FROM messages")
                rows_temperature = cursor_temperature.fetchall()
                print("Temperature Database:")
                for row in rows_temperature:
                    print(row)

                cursor_humidity = self.connection_humidity.cursor()
                cursor_humidity.execute("SELECT * FROM messages")
                rows_humidity = cursor_humidity.fetchall()
                print("Humidity Database:")
                for row in rows_humidity:
                    print(row)
            else:
                QMessageBox.warning(self, "Warning", "Please load all databases first.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error showing databases: {str(e)}")

    def clear_databases(self):
        try:
            if self.connection_weight and self.connection_temperature and self.connection_humidity:
                cursor_weight = self.connection_weight.cursor()
                cursor_weight.execute("DELETE FROM messages")
                self.connection_weight.commit()

                cursor_temperature = self.connection_temperature.cursor()
                cursor_temperature.execute("DELETE FROM messages")
                self.connection_temperature.commit()

                cursor_humidity = self.connection_humidity.cursor()
                cursor_humidity.execute("DELETE FROM messages")
                self.connection_humidity.commit()

                QMessageBox.information(self, "Success", "Databases cleared successfully.")
            else:
                QMessageBox.warning(self, "Warning", "Please load all databases first.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error clearing databases: {str(e)}")

    def generate_graph(self):
        try:
            if self.connection_weight and self.connection_temperature and self.connection_humidity:
                # Fetch data from weight database
                cursor_weight = self.connection_weight.cursor()
                cursor_weight.execute("SELECT timestamp, message FROM messages ORDER BY timestamp")
                rows_weight = cursor_weight.fetchall()
                timestamps_weight = [datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S') for row in rows_weight]
                values_weight = [float(row[1]) for row in rows_weight]

                # Fetch data from temperature database
                cursor_temperature = self.connection_temperature.cursor()
                cursor_temperature.execute("SELECT timestamp, message FROM messages ORDER BY timestamp")
                rows_temperature = cursor_temperature.fetchall()
                timestamps_temperature = [datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S') for row in rows_temperature]
                values_temperature = [float(row[1]) for row in rows_temperature]

                # Fetch data from humidity database
                cursor_humidity = self.connection_humidity.cursor()
                cursor_humidity.execute("SELECT timestamp, message FROM messages ORDER BY timestamp")
                rows_humidity = cursor_humidity.fetchall()
                timestamps_humidity = [datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S') for row in rows_humidity]
                values_humidity = [float(row[1]) for row in rows_humidity]

                plt.figure(figsize=(10, 6))  # Adjust figure size here

                # Plot weight data
                plt.plot(timestamps_weight, values_weight, marker='o', linestyle='-', color='b', linewidth=2,
                         label='Weight Data')

                # Plot temperature data
                plt.plot(timestamps_temperature, values_temperature, marker='o', linestyle='-', color='r', linewidth=2,
                         label='Temperature Data')

                # Plot humidity data
                plt.plot(timestamps_humidity, values_humidity, marker='o', linestyle='-', color='g', linewidth=2,
                         label='Humidity Data')

                # Find the highest and lowest points for weight
                max_weight_idx = np.argmax(values_weight)
                min_weight_idx = np.argmin(values_weight)

                max_temp_idx = np.argmax(values_temperature)
                min_temp_idx = np.argmin(values_temperature)

                max_hum_idx = np.argmax(values_humidity)
                min_hum_idx = np.argmin(values_humidity)
                plt.scatter(timestamps_weight[max_weight_idx], values_weight[max_weight_idx], color='b', s=100,
                            label='Max Weight')
                plt.scatter(timestamps_weight[min_weight_idx], values_weight[min_weight_idx], color='b', s=100,
                            label='Min Weight')

                plt.scatter(timestamps_temperature[max_temp_idx], values_temperature[max_temp_idx], color='r', s=100,
                            label='Max Temperature')
                plt.scatter(timestamps_temperature[min_temp_idx], values_temperature[min_temp_idx], color='r', s=100,
                            label='Min Temperature')

                plt.scatter(timestamps_humidity[max_hum_idx], values_humidity[max_hum_idx], color='g', s=100,
                            label='Max Humidity')
                plt.scatter(timestamps_humidity[min_hum_idx], values_humidity[min_hum_idx], color='g', s=100,
                            label='Min Humidity')

                plt.xlabel('Timestamp', fontsize=12)
                plt.ylabel('Value', fontsize=12)
                plt.title('Weight, Temperature, and Humidity Variation Over Time', fontsize=14)
                plt.legend(fontsize=10)
                plt.grid(True, linestyle='--', alpha=0.7)
                plt.xticks(rotation=45, ha='right')
                plt.gca().xaxis.set_major_formatter(DateFormatter('%Y-%m-%d %H:%M:%S'))
                plt.xticks(fontsize=8)  # Adjust font size of timestamp labels
                plt.tight_layout()  # Adjust layout for better fitting

                # Check for sudden rise or drop in temperature, weight, and humidity
                threshold = 2.0  # Higher threshold for lower sensitivity
                changes_detected = False
                changes_info = ""
                for data, timestamps, label, color in zip([values_weight, values_temperature, values_humidity],
                                                          [timestamps_weight, timestamps_temperature,
                                                           timestamps_humidity],
                                                          ['Weight Data', 'Temperature Data', 'Humidity Data'],
                                                          ['b', 'r', 'g']):
                    diffs = np.diff(data)
                    sudden_indices = np.where(np.abs(diffs) > threshold)[0] + 1
                    if len(sudden_indices) > 0:  # Check if the array is not empty
                        changes_detected = True
                        for index in sudden_indices:
                            changes_info += f"Sudden change detected in {label} at {timestamps[index]}: {data[index]}\n"

                if changes_detected:
                    msg_box = QMessageBox()
                    msg_box.setIcon(QMessageBox.Warning)
                    msg_box.setText("Sudden changes detected!")
                    msg_box.setInformativeText(changes_info)
                    msg_box.setStandardButtons(QMessageBox.Ok)
                    msg_box.exec_()
                plt.show()

            else:
                QMessageBox.warning(self, "Warning", "Please load all databases first.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred while generating the graph: {str(e)}")
            print(f"Error occurred while generating the graph: {str(e)}")

    def generate_freq_graph(self):
        try:
            if self.connection_location:
                cursor_location = self.connection_location.cursor()
                cursor_location.execute("SELECT message FROM messages ORDER BY timestamp DESC LIMIT 1")
                row_location = cursor_location.fetchone()

                if row_location:  # Check if there is a row
                    freq_values = [float(value) for value in row_location[0].split() if value.strip()]
                    max_value = max(freq_values)
                    min_value = min(freq_values)
                    print(f"Maximum value in the database: {max_value}")
                    print(f"Minimum value in the database: {min_value}")

                    num_values = len(freq_values)
                    timestamps = np.arange(num_values)

                    plt.figure(figsize=(10, 6))
                    plt.plot(timestamps, freq_values, linestyle='', marker='o', markersize=8, color='blue',
                             label='Data Points')

                    # Plot maximum value point
                    max_index = freq_values.index(max_value)
                    max_timestamp = timestamps[max_index]
                    plt.scatter(max_timestamp, max_value, color='red', s=100,
                                label=f'Max Value: ({max_timestamp}, {max_value})')

                    # Plot minimum value point
                    min_index = freq_values.index(min_value)
                    min_timestamp = timestamps[min_index]
                    plt.scatter(min_timestamp, min_value, color='green', s=100,
                                label=f'Min Value: ({min_timestamp}, {min_value})')

                    plt.xlabel('Index', fontsize=12, fontweight='bold')
                    plt.ylabel('Frequency', fontsize=12, fontweight='bold')
                    plt.title('Frequency Variation', fontsize=14, fontweight='bold')
                    plt.grid(True, linestyle='--', linewidth=0.5, alpha=0.5)
                    plt.xticks(fontsize=10)
                    plt.yticks(fontsize=10)
                    plt.legend(fontsize=10)
                    plt.tight_layout()

                    # Customize grid
                    plt.grid(True, which='both', linestyle='-', linewidth=0.5, alpha=0.5)
                    plt.minorticks_on()
                    plt.grid(True, which='minor', linestyle=':', linewidth=0.5, alpha=0.3)

                    plt.show()
                else:
                    QMessageBox.warning(self, "Warning", "No data found in the frequency database.")
            else:
                QMessageBox.warning(self, "Warning", "Please load the frequency database first.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred while generating the frequency graph: {str(e)}")
            print(f"Error occurred while generating the frequency graph: {str(e)}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DatabaseViewer("Database Viewer")
    window.show()
    sys.exit(app.exec_())