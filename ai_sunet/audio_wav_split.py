from pydub import AudioSegment
import os


def split_wav_file(input_file, output_folder, segment_duration_ms):
    # Load the audio file
    audio = AudioSegment.from_wav(input_file)

    # Calculate the number of segments
    total_length_ms = len(audio)
    num_segments = total_length_ms // segment_duration_ms

    # Create the output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Split the audio into segments
    for i in range(num_segments + 1):
        start_time = i * segment_duration_ms
        end_time = min(start_time + segment_duration_ms, total_length_ms)

        # Extract the segment
        segment = audio[start_time:end_time]

        # Save the segment as a new wav file
        segment_filename = os.path.join(output_folder, f'segment_{i + 1}.wav')
        segment.export(segment_filename, format="wav")
        print(f'Saved {segment_filename}')


# Parameters
input_file = 'test2.wav'  # Replace with your input wav file path
output_folder = 'split/angry'  # Folder to save the output segments
segment_duration_ms = 5000  # Segment duration in milliseconds (5000 ms = 5 seconds)

# Run the function
split_wav_file(input_file, output_folder, segment_duration_ms)
