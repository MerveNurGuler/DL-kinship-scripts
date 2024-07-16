import os
import pandas as pd
import statistics

# Define the base path
path = "/path/to/normalization_files/files/"
output_csv_path = "/path/to/normalization_files/normalization_wl200ws50.csv"

# Define suffix values for original and downsampled versions
suffix_values = ["original", 1000, 1500, 2000, 2500, 3000, 3500, 4000, 4500, 5000, 6000, 7000, 8000, 10000, 12500, 15000, 20000, 25000, 30000, 35000, 40000, 50000]
data_frames = []

# List all files in the directory
files = os.listdir(path)

# Iterate through each suffix value
for suffix in suffix_values:
    mean_values = []

    # Iterate through each file
    for filename in files:
        filepath = os.path.join(path, filename)

        # Iterate through each chromosome
        for chr in range(1, 23):
            # Handle the "original" condition
            if suffix == "original" and filepath.endswith(f"_baseline_wl200_ws50_{chr}.bsl"):
                with open(filepath) as file:
                    file = file.readlines()[1:]
                    baseline_values = [float(line.split('\t')[2].strip()) for line in file if len(line.split('\t')) >= 3]

                if baseline_values:
                    mean_value = statistics.mean(baseline_values)
                    mean_values.append(mean_value)
                else:
                    print(f"No valid data in file: {filepath}")

            # Handle other suffix values
            elif filepath.endswith(f"_baseline_wl200_ws50_{suffix}_{chr}.bsl"):
                with open(filepath) as file:
                    file = file.readlines()[1:]
                    baseline_values = [float(line.split('\t')[2].strip()) for line in file if len(line.split('\t')) >= 3]

                if baseline_values:
                    mean_value = statistics.mean(baseline_values)
                    mean_values.append(mean_value)
                else:
                    print(f"No valid data in file: {filepath}")

    # Convert the list of mean values to a DataFrame
    df_norm_means = pd.DataFrame(mean_values, columns=['Mean'])
    data_frames.append(df_norm_means)

# Concatenate all DataFrames
all_norm = pd.concat(data_frames, axis=1, join='inner')

# Rename columns based on suffix values
all_norm.columns = suffix_values

# Write the DataFrame to CSV file
all_norm.to_csv(output_csv_path, index=False)
