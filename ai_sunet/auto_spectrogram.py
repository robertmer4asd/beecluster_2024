import os
import librosa
import numpy as np
import matplotlib.pyplot as plt
import librosa.display

# Function to create and save a spectrogram
def save_spectrogram(y, sr, output_path):
    # Generate the spectrogram
    S = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=128)
    S_DB = librosa.power_to_db(S, ref=np.max)

    # Create a plot
    plt.figure(figsize=(10, 4))
    librosa.display.specshow(S_DB, sr=sr, x_axis='time', y_axis='mel')
    plt.colorbar(format='%+2.0f dB')
    plt.title('Mel-frequency spectrogram')
    plt.tight_layout()

    # Save the plot to the specified path
    plt.savefig(output_path)
    plt.close()

# Function to process all wav files in a directory
def process_wav_files(input_folder, output_folder):
    # Create the output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Process each wav file in the input folder
    for file_name in os.listdir(input_folder):
        if file_name.endswith('.wav'):
            file_path = os.path.join(input_folder, file_name)
            y, sr = librosa.load(file_path, sr=None)
            output_path = os.path.join(output_folder, f"{os.path.splitext(file_name)[0]}.png")
            save_spectrogram(y, sr, output_path)
            print(f"Saved spectrogram for {file_name} to {output_path}")

# Define input and output folders
input_folder = "split/angry"
output_folder = "spectrograms/angry"

# Process all wav files
process_wav_files(input_folder, output_folder)

print("Spectrograms have been generated and saved.")
