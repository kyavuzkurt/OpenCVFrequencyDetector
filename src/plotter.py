import os
import glob
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# Get all CSV files in the directory
list_of_files = glob.glob('../output_csvs/*.csv')

# Create output directory if it doesn't exist
output_dir = '../plots'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Iterate over each file and plot the data
for file in list_of_files:
    df = pd.read_csv(file)
    df = df[df['Y'] != 0]
    unique_ids = df['ID'].unique()
    
    # Create a new figure for each file
    plt.figure(figsize=(15, 10))
    
    for unique_id in unique_ids:
        subset = df[df['ID'] == unique_id]
        plt.plot(subset['Frame'], subset['Y'], label=f'ID {unique_id} ({os.path.basename(file)})')
    
    # Set plot labels and title
    plt.xlabel('Frame')
    plt.ylabel('Y')
    plt.title(f'Frame vs Y for each ID in {os.path.basename(file)}')
    plt.legend()
    
    # Save the plot
    base_filename = os.path.basename(file)
    filename_eps = f'plot_{base_filename.replace(".csv", ".eps")}'
    plt.savefig(os.path.join(output_dir, filename_eps))
    plt.close()  # Close the figure to free memory

    print(f"Plot saved to {output_dir}/{filename_eps}")