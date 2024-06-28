import os
import pandas as pd

# Define the base path and the categories
base_path = 'split'
categories = ['toot', 'normal', 'angry']

# Create an empty list to store the data
data = []

# Loop through each category and get the file paths
for category in categories:
    category_path = os.path.join(base_path, category)
    for filename in os.listdir(category_path):
        if filename.endswith('.wav'):
            file_path = os.path.join(category_path, filename)
            data.append([file_path, category])

# Create a DataFrame
df = pd.DataFrame(data, columns=['File_Path', 'Label'])

# Save the DataFrame to a CSV file
df.to_csv('dataset.csv', index=False)
