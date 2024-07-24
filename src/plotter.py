import os
import glob
import pandas as pd
import matplotlib.pyplot as plt


list_of_files = glob.glob('../output_csvs/*.csv')
latest_file = max(list_of_files, key=os.path.getctime)


df = pd.read_csv(latest_file)


df = df[df['Y'] != 0]


plt.figure(figsize=(15, 10))

unique_ids = df['ID'].unique()


for unique_id in unique_ids:
    subset = df[df['ID'] == unique_id]
    plt.plot(subset['Frame'], subset['Y'], label=f'ID {unique_id}')


plt.xlabel('Frame')
plt.ylabel('Y')
plt.title('Frame vs Y for each ID')
plt.legend()

plt.savefig('output_plot.png')