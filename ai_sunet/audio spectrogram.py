import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
import librosa
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Dropout, Flatten, Dense
from tensorflow import keras
import matplotlib.pyplot as plt
import librosa.display

def extract_features(file_path, n_mfcc=40, max_len=100):
    y, sr = librosa.load(file_path, sr=None)
    mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=n_mfcc)
    if mfccs.shape[1] < max_len:
        pad_width = max_len - mfccs.shape[1]
        mfccs = np.pad(mfccs, pad_width=((0, 0), (0, pad_width)), mode='constant')
    else:
        mfccs = mfccs[:, :max_len]
    mfccs = np.expand_dims(mfccs, axis=-1)
    return mfccs


# Load the dataset
dataset = pd.read_csv("dataset.csv")

# Extract features and labels
X = []
y = []
label_map = {'toot': 0, 'normal': 1, 'angry': 2}

for index, row in dataset.iterrows():
    file_path = row["File_Path"]
    label = row["Label"]
    try:
        features = extract_features(file_path)
        X.append(features)
        y.append(label_map[label])
    except Exception as e:
        print(f"Error processing {file_path}: {e}")

X = np.array(X)
y = np.array(y)

# Train-test split
X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)

# Build the model
model_path = "trained_model.keras"
if os.path.exists(model_path):
    model = keras.models.load_model(model_path)
    print(f"Model loaded from {model_path}")
else:
    model = Sequential([
        Conv2D(32, (3, 3), activation='relu', input_shape=(X_train.shape[1], X_train.shape[2], 1)),
        MaxPooling2D((2, 2)),
        Conv2D(64, (3, 3), activation='relu'),
        MaxPooling2D((2, 2)),
        Dropout(0.5),
        Flatten(),
        Dense(128, activation='relu'),
        Dropout(0.5),
        Dense(3, activation='softmax')
    ])

    model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
    history = model.fit(X_train, y_train, epochs=50, validation_data=(X_val, y_val))
    model.save(model_path)

    # Plot training history
    plt.plot(history.history['loss'], label='loss')
    plt.plot(history.history['val_loss'], label='val_loss')
    plt.legend()
    plt.show()

    plt.plot(history.history['accuracy'], label='accuracy')
    plt.plot(history.history['val_accuracy'], label='val_accuracy')
    plt.legend()
    plt.show()

# Prediction on a new file
input_file_path = "sounds/nuhuh.wav"
y, sr = librosa.load(input_file_path, sr=None)
features = extract_features(input_file_path)
features = np.expand_dims(features, axis=0)
prediction = model.predict(features)
predicted_class_index = np.argmax(prediction)
predicted_class_name = list(label_map.keys())[predicted_class_index]
accuracy = np.max(prediction)
print(f"Predicted class: {predicted_class_name}, Accuracy: {accuracy}")
