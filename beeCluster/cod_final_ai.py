import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
import sys
import sqlite3
import warnings
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
from PyQt5.QtCore import *
from PyQt5.QtGui import QFont, QIcon
from datetime import datetime
from PyQt5.QtWidgets import *
import numpy as np
import pandas as pd
from tensorflow import keras


warnings.filterwarnings("ignore")

def generate_random_graphs(num_samples=100000, num_values=15, min_value=50, max_value=600):
    X = []
    y = []
    for _ in range(num_samples):
        graph = np.random.randint(min_value, max_value, size=num_values)
        X.append(graph)
        variation = np.max(graph) - np.min(graph)
        if variation >= 200:
            y.append(1)
        else:
            y.append(0)
    return np.array(X), np.array(y)
def save_dataset_to_file(X, y, filename="dataset_cnn.csv"):
    df = pd.DataFrame(np.column_stack([X, y]), columns=[f"val_{i+1}" for i in range(15)] + ["variation_met"])
    df.to_csv(filename, index=False)
    print(f"Dataset saved to {filename}")
dataset_file = "dataset_cnn.csv"
dataset_file_dnn = "random_graph_dataset.csv"
if not os.path.exists(dataset_file):
    X_train, y_train = generate_random_graphs()
    save_dataset_to_file(X_train, y_train, dataset_file)
else:
    df = pd.read_csv(dataset_file)
    X_train = df.iloc[:, :-1].values
    y_train = df.iloc[:, -1].values
    X_train = X_train.reshape(-1, 15, 1, 1)

if not os.path.exists(dataset_file_dnn):
    X_train, y_train = generate_random_graphs()
    df = pd.DataFrame(np.column_stack([X_train, y_train]),
                      columns=[f"val_{i + 1}" for i in range(15)] + ["variation_met"])
    df.to_csv(dataset_file_dnn, index=False)
else:
    df = pd.read_csv(dataset_file_dnn)
    X_train = df.iloc[:, :-1].values
    y_train = df.iloc[:, -1].values

model_file_dnn = "trained_model.keras"
if os.path.exists(model_file_dnn):
    model = keras.models.load_model(model_file_dnn)
    print(f"Model loaded from {model_file_dnn}")
else:
    model = keras.Sequential([
        keras.layers.Input(shape=(15,)),
        keras.layers.Dense(64, activation='relu'),
        keras.layers.Dense(64, activation='relu'),
        keras.layers.Dense(1, activation='sigmoid')
    ])
    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
    model.fit(X_train, y_train, epochs=10, batch_size=32, validation_split=0.2)
    model.save(model_file_dnn)


model = keras.Sequential([
    keras.layers.Conv2D(32, (3, 1), activation='relu', padding='same', input_shape=(15, 1, 1)),
    keras.layers.MaxPooling2D((2, 1)),
    keras.layers.Conv2D(64, (3, 1), activation='relu', padding='same'),
    keras.layers.MaxPooling2D((2, 1)),
    keras.layers.Conv2D(128, (3, 1), activation='relu', padding='same'),
    keras.layers.MaxPooling2D((2, 1)),
    keras.layers.Flatten(),
    keras.layers.Dense(64, activation='relu'),
    keras.layers.Dense(1, activation='sigmoid')
])

model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

model_file = "train_cnn.keras"
if not os.path.exists(model_file):
    model.fit(X_train, y_train, epochs=10, batch_size=32)
    model.save(model_file)
    print(f"Model saved to {model_file}")
else:
    model = keras.models.load_model(model_file)
    print(f"Model loaded from {model_file}")


class DatabaseViewer(QMainWindow):
    def __init__(self, title):
        super().__init__()
        self.setWindowTitle(title)
        self.setGeometry(100, 100, 400, 300)

        self.setWindowIcon(QIcon('icon.png'))

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        self.central_widget.setLayout(layout)
        self.setStyleSheet("background-color: rgb(255, 170, 0);")


        self.title_label = QLabel("BeeCluster", self)
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setFont(QFont("Arial", 20))
        layout.addWidget(self.title_label)

        self.database_status_label = QLabel("Databases not loaded.")
        self.database_status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.database_status_label)

        button_labels = [
            "Load Weight Database",
            "Load Temperature Database",
            "Load Humidity Database",
            "Load Frequency Database",
            "Show Databases",
            "Generate Graph",
            "Generate Frequency Graph",
            "Predict Possible Events (CNN)",
            "Predict Possible Events (DNN)",
            "Exit"
        ]
        self.buttons = []
        for label in button_labels:
            button = QPushButton(label, self)
            button.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; border: none; padding: 10px 24px; font-size: 14px; border-radius: 12px; }"
                                 "QPushButton:hover { background-color: #45a049; }"
                                 "QPushButton:pressed { background-color: #3c8c40; }")
            self.buttons.append(button)
            layout.addWidget(button)

        self.buttons[0].clicked.connect(self.load_weight_database)
        self.buttons[1].clicked.connect(self.load_temperature_database)
        self.buttons[2].clicked.connect(self.load_humidity_database)
        self.buttons[3].clicked.connect(self.load_freq_database)
        self.buttons[4].clicked.connect(self.show_databases)
        self.buttons[5].clicked.connect(self.generate_graph)
        self.buttons[6].clicked.connect(self.generate_freq_graph)
        self.buttons[7].clicked.connect(self.cnn_graph)
        self.buttons[8].clicked.connect(self.dnn_graph)
        self.buttons[9].clicked.connect(self.close)

        self.connection_weight = None
        self.connection_temperature = None
        self.connection_humidity = None
        self.connection_location = None

    def load_weight_database(self):
        try:
            file_path, _ = QFileDialog.getOpenFileName(self, "Open Weight Database File", "",
                                                       "SQLite Database Files (*.db)")
            if file_path:
                self.connection_weight = sqlite3.connect(file_path)
                self.database_status_label.setText("Weight Database loaded successfully.")
            else:
                self.database_status_label.setText("No file selected for Weight Database.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error loading Weight Database: {str(e)}")

    def load_temperature_database(self):
        try:
            file_path, _ = QFileDialog.getOpenFileName(self, "Open Temperature Database File", "",
                                                       "SQLite Database Files (*.db)")
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
                QMessageBox.information(self, "Success", "Frequency Database loaded successfully.")
            else:
                QMessageBox.warning(self, "Warning", "No file selected for Frequency Database.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error loading Frequency Database: {str(e)}")
    def close(self):
        sys.exit(0)
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

    def generate_graph(self):
        try:
            if self.connection_weight and self.connection_temperature and self.connection_humidity:
                cursor_weight = self.connection_weight.cursor()
                cursor_weight.execute("SELECT timestamp, message FROM messages ORDER BY timestamp")
                rows_weight = cursor_weight.fetchall()
                timestamps_weight = [datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S') for row in rows_weight]
                values_weight = [float(row[1]) for row in rows_weight]

                cursor_temperature = self.connection_temperature.cursor()
                cursor_temperature.execute("SELECT timestamp, message FROM messages ORDER BY timestamp")
                rows_temperature = cursor_temperature.fetchall()
                timestamps_temperature = [datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S') for row in rows_temperature]
                values_temperature = [float(row[1]) for row in rows_temperature]

                cursor_humidity = self.connection_humidity.cursor()
                cursor_humidity.execute("SELECT timestamp, message FROM messages ORDER BY timestamp")
                rows_humidity = cursor_humidity.fetchall()
                timestamps_humidity = [datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S') for row in rows_humidity]
                values_humidity = [float(row[1]) for row in rows_humidity]

                plt.figure(figsize=(10, 6))

                plt.plot(timestamps_weight, values_weight, marker='o', linestyle='-', color='b', linewidth=2,
                         label='Weight Data')

                plt.plot(timestamps_temperature, values_temperature, marker='o', linestyle='-', color='r', linewidth=2,
                         label='Temperature Data')

                plt.plot(timestamps_humidity, values_humidity, marker='o', linestyle='-', color='g', linewidth=2,
                         label='Humidity Data')

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
                plt.xticks(fontsize=8)
                plt.tight_layout()

                threshold = 2.0
                changes_detected = False
                changes_info = ""
                for data, timestamps, label, color in zip([values_weight, values_temperature, values_humidity],
                                                          [timestamps_weight, timestamps_temperature,
                                                           timestamps_humidity],
                                                          ['Weight Data', 'Temperature Data', 'Humidity Data'],
                                                          ['b', 'r', 'g']):
                    diffs = np.diff(data)
                    sudden_indices = np.where(np.abs(diffs) > threshold)[0] + 1
                    if len(sudden_indices) > 0:
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

    def cnn_graph(self):
        print(f"Working with CNN(Convultional Neural Network")
        try:
            if self.connection_location:
                cursor_location = self.connection_location.cursor()
                cursor_location.execute("SELECT message FROM messages ORDER BY timestamp DESC LIMIT 1")
                row_location = cursor_location.fetchone()
                if row_location:
                    last_array = np.array([float(value) for value in row_location[0].split() if value.strip()])

                    timestamps = np.arange(len(last_array))
                    variation_preset_graph = np.max(last_array) - np.min(last_array)
                    plt.figure(figsize=(10, 6))
                    plt.plot(timestamps, last_array, color='blue', marker='o', markersize=5, label='Frequency',
                             linewidth=2)

                    plt.xlabel('Index', fontsize=12, fontweight='bold')
                    plt.ylabel('Frequency', fontsize=12, fontweight='bold')
                    plt.title('Frequency Variation CNN Predict', fontsize=14, fontweight='bold')
                    plt.grid(True, linestyle='--', linewidth=0.5, alpha=0.5)
                    plt.xticks(fontsize=10)
                    plt.yticks(fontsize=10)
                    plt.legend(fontsize=10)
                    plt.tight_layout()

                    plt.grid(True, which='both', linestyle='-', linewidth=0.5, alpha=0.5)
                    plt.minorticks_on()
                    plt.grid(True, which='minor', linestyle=':', linewidth=0.5, alpha=0.3)
                    if variation_preset_graph >= 200:
                        print("Variation detected!")
                        plt.text(10, 300, "Variation detected!", fontsize=12, color='red',
                                 bbox=dict(facecolor='white', alpha=0.5))
                    else:
                        print("Variation not detected. Not displaying text.")
                        plt.text(10, 300, "Variation not detected!", fontsize=12, color='red',
                                 bbox=dict(facecolor='white', alpha=0.5))
                    plt.show()
                else:
                    print("Insufficient data arrays in data.txt to generate the graph.")
            else:
                print("data.txt not found.")
        except Exception as e:
            print(f"An error occurred while generating the frequency graph: {str(e)}")
    def dnn_graph(self):
        print(f"Working on DNN(Deep Neural Network)")
        dataset_file = "random_graph_dataset.csv"
        if not os.path.exists(dataset_file):
            X_train, y_train = generate_random_graphs()
            df = pd.DataFrame(np.column_stack([X_train, y_train]),
                              columns=[f"val_{i + 1}" for i in range(15)] + ["variation_met"])
            df.to_csv(dataset_file, index=False)
        else:
            df = pd.read_csv(dataset_file)
            X_train = df.iloc[:, :-1].values
            y_train = df.iloc[:, -1].values

        model_file = "trained_model.keras"
        if os.path.exists(model_file):
            model = keras.models.load_model(model_file)
        else:
            model = keras.Sequential([
                keras.layers.Input(shape=(15,)),
                keras.layers.Dense(64, activation='relu'),
                keras.layers.Dense(64, activation='relu'),
                keras.layers.Dense(1, activation='sigmoid')
            ])
            model.compile(optimizer='adam',
                          loss='binary_crossentropy',
                          metrics=['accuracy'])
            model.fit(X_train, y_train, epochs=10, batch_size=32, validation_split=0.2)
            model.save(model_file)
        try:
            if self.connection_location:
                cursor_location = self.connection_location.cursor()
                cursor_location.execute("SELECT message FROM messages ORDER BY timestamp DESC LIMIT 1")
                row_location = cursor_location.fetchone()
                if row_location:
                    last_array = np.array([float(value) for value in row_location[0].split() if value.strip()])
                    timestamps = np.arange(len(last_array))
                    variation_dnn = np.max(last_array) - np.min(last_array)
                    plt.figure(figsize=(10, 6))
                    plt.plot(timestamps, last_array, color='blue', marker='o', markersize=5, label='Frequency',
                             linewidth=2)

                    plt.xlabel('Index', fontsize=12, fontweight='bold')
                    plt.ylabel('Frequency', fontsize=12, fontweight='bold')
                    plt.title('Frequency Variation DNN Predict', fontsize=14, fontweight='bold')
                    plt.grid(True, linestyle='--', linewidth=0.5, alpha=0.5)
                    plt.xticks(fontsize=10)
                    plt.yticks(fontsize=10)
                    plt.legend(fontsize=10)
                    plt.tight_layout()

                    plt.grid(True, which='both', linestyle='-', linewidth=0.5, alpha=0.5)
                    plt.minorticks_on()
                    plt.grid(True, which='minor', linestyle=':', linewidth=0.5, alpha=0.3)
                    if variation_dnn >= 200:
                        print("Variation detected!")
                        plt.text(10, 300, "Variation detected!", fontsize=12, color='red',
                                 bbox=dict(facecolor='white', alpha=0.5))
                    else:
                        print("Variation not detected. Not displaying text.")
                        plt.text(10, 300, "Variation not detected!", fontsize=12, color='red',
                                 bbox=dict(facecolor='white', alpha=0.5))
                    plt.show()
                else:
                    print("Insufficient data arrays in data.txt to generate the graph.")
            else:
                print("data.txt not found.")
        except Exception as e:
            print(f"An error occurred while generating the frequency graph: {str(e)}")

    def generate_freq_graph(self):
        try:
            if self.connection_location:
                cursor_location = self.connection_location.cursor()
                cursor_location.execute("SELECT message FROM messages ORDER BY timestamp DESC LIMIT 1")
                row_location = cursor_location.fetchone()

                if row_location:
                    freq_values = [float(value) for value in row_location[0].split() if value.strip()]
                    max_value = max(freq_values)
                    min_value = min(freq_values)
                    print(f"Maximum value in the database: {max_value}")
                    print(f"Minimum value in the database: {min_value}")

                    num_values = len(freq_values)
                    timestamps = np.arange(num_values)

                    plt.figure(figsize=(10, 6))
                    plt.plot(timestamps, freq_values, linestyle='-', linewidth=2, color='blue', alpha=0.8,
                             label='Data Line')
                    plt.scatter(timestamps, freq_values, color='blue', s=50, label='Data Points')

                    max_index = freq_values.index(max_value)
                    max_timestamp = timestamps[max_index]
                    plt.scatter(max_timestamp, max_value, color='red', s=100,
                                label=f'Max Value: ({max_timestamp}, {max_value})')

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