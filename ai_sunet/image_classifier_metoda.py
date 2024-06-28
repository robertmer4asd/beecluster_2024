import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

import cv2 as cv
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from tensorflow.keras import layers, models
from sklearn.model_selection import train_test_split
from tensorflow import keras

import tensorflow as tf
tf.get_logger().setLevel('ERROR')

dataset = pd.read_csv('image_dataset.csv')

images = []
labels = []

label_map = {'toot': 0, 'normal': 1, 'angry': 2}

for index, row in dataset.iterrows():
    img = cv.imread(row['File_Paths'])
    img = cv.cvtColor(img, cv.COLOR_BGR2RGB)
    img_resized = cv.resize(img, (1000, 400))
    img_normalized = img_resized / 255.0
    images.append(img_normalized)
    labels.append(label_map[row['Labels']])

images = np.array(images)
labels = np.array(labels)

X_train, X_test, y_train, y_test = train_test_split(images, labels, test_size=0.2, random_state=42)

print("Training images shape:", X_train.shape)
print("Testing images shape:", X_test.shape)

model_path = 'image_classifier_precise.keras'
if os.path.exists(model_path):
    model = keras.models.load_model(model_path)
    print(f"Model loaded from {model_path}")
else:
    model = models.Sequential()
    model.add(layers.Input(shape=(400, 1000, 3)))
    model.add(layers.Conv2D(32, (3, 3), activation='relu'))
    model.add(layers.MaxPooling2D((2, 2)))
    model.add(layers.Conv2D(64, (3, 3), activation='relu'))
    model.add(layers.MaxPooling2D((2, 2)))
    model.add(layers.Conv2D(64, (3, 3), activation='relu'))
    model.add(layers.Flatten())
    model.add(layers.Dense(64, activation='relu'))
    model.add(layers.Dense(3, activation='softmax'))  # 3 classes: toot, normal, angry

    model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])

    r = model.fit(X_train, y_train, epochs=50, validation_data=(X_test, y_test), batch_size=10)

    loss, accuracy = model.evaluate(X_test, y_test)
    print(f"Loss: {loss}")
    print(f"Accuracy: {accuracy}")

    model.save('image_classifier_precise.keras')
    plt.plot(r.history['loss'], label='loss')
    plt.plot(r.history['val_loss'], label='val_loss')
    plt.legend()
    plt.show()
    plt.plot(r.history['accuracy'], label='accuracy')
    plt.plot(r.history['val_accuracy'], label='val_accuracy')
    plt.legend()
    plt.show()

input_file_path = 'spectrograms/normal/segment_1.png'
img = cv.imread(input_file_path)
img = cv.cvtColor(img, cv.COLOR_BGR2RGB)
img_resized = cv.resize(img, (1000, 400))
img_normalized = img_resized / 255.0

plt.imshow(img, cmap=plt.cm.binary)
plt.show()

prediction = model.predict(np.array([img_normalized]))
index = np.argmax(prediction)

predicted_class = list(label_map.keys())[index]
print(f"Prediction is {predicted_class}")
